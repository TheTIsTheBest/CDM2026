import json
import os
import urllib.request
import urllib.error
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from datetime import datetime

from bs4 import BeautifulSoup

HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 8000))

TARGET_URL = 'https://www.fifa.com/fifaplus/en/tournaments/mens/worldcup/2026/fixtures-results/'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'


def fetch_external_html(url):
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(request, timeout=20) as response:
        charset = response.headers.get_content_charset() or 'utf-8'
        return response.read().decode(charset, errors='replace')


def parse_live_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    matches = []
    odds = []
    stats = {
        'matches_played': 0,
        'goals': 0,
        'teams': 48,
        'host_cities': 16,
    }
    live = False

    # Tentative de lecture des matchs depuis la page FIFA+
    cards = soup.select('article, div.fi-mu, li.fi-fixture')

    for card in cards[:24]:
        text = card.get_text(separator=' ', strip=True)
        if 'vs' not in text and 'vs.' not in text and '-' not in text:
            continue

        home = None
        away = None
        score = None
        status = 'upcoming'
        date_label = None
        datetime_str = None

        # Recherche des équipes
        home_el = card.select_one('.fi-t__home, .home-team, .team-home')
        away_el = card.select_one('.fi-t__away, .away-team, .team-away')
        if home_el and away_el:
            home = home_el.get_text(strip=True)
            away = away_el.get_text(strip=True)
        else:
            teams = [t.get_text(strip=True) for t in card.select('.team-name, .fi-t__n') if t.get_text(strip=True)]
            if len(teams) >= 2:
                home, away = teams[:2]

        score_el = card.select_one('.fi-s__score, .score, .result')
        if score_el:
            score = score_el.get_text(strip=True)
            if score.lower().startswith('live') or 'ft' not in score.lower():
                status = 'live'
        elif ' - ' in text:
            possible = [part.strip() for part in text.split() if '-' in part]
            if possible:
                score = possible[0]

        if 'live' in text.lower() or 'en direct' in text.lower() or 'h live' in text.lower():
            status = 'live'
            live = True

        # Date heuristique
        date_el = card.select_one('time, .match-date, .fi-mu__date')
        if date_el:
            date_label = date_el.get_text(strip=True)
            datetime_str = date_el.get('datetime') or None

        if home and away:
            matches.append({
                'dateLabel': date_label or 'À venir',
                'datetime': datetime_str,
                'home': home,
                'away': away,
                'score': score or '•',
                'stage': 'Phase finale',
                'status': status,
            })

    if len(matches) < 4:
        raise ValueError('Aucun match valide trouvé')

    # Lecture des cotes bookmakers si disponibles
    odds_blocks = soup.select('.odds, .market-odds, .betting-odds')
    for block in odds_blocks[:6]:
        name = block.select_one('.bookmaker, .site-name')
        value = block.select_one('.odds-value, .price')
        if name and value:
            odds.append({
                'site': name.get_text(strip=True),
                'team': value.get_text(strip=True),
                'probability': None,
            })

    return {
        'live': live,
        'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
        'stats': stats,
        'matches': matches,
        'odds': odds,
    }


def default_live_data():
    return {
        'live': False,
        'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
        'stats': {
            'matches_played': 0,
            'goals': 0,
            'teams': 48,
            'host_cities': 16,
        },
        'matches': [
            {
                'dateLabel': '11 Juin',
                'datetime': '2026-06-11T18:00:00',
                'home': '🇺🇸 USA',
                'away': '🇲🇽 Mexique',
                'score': None,
                'stage': 'Groupes',
                'status': 'upcoming',
            },
            {
                'dateLabel': '12 Juin',
                'datetime': '2026-06-12T21:00:00',
                'home': '🇧🇷 Brésil',
                'away': '🇩🇪 Allemagne',
                'score': None,
                'stage': 'Groupes',
                'status': 'upcoming',
            },
            {
                'dateLabel': '14 Juin',
                'datetime': '2026-06-14T20:00:00',
                'home': '🇫🇷 France',
                'away': '🇦🇷 Argentine',
                'score': None,
                'stage': 'Groupes',
                'status': 'upcoming',
            },
        ],
        'odds': [
            {'site': 'Bet365', 'team': 'France 2.35', 'probability': 42},
            {'site': 'Winamax', 'team': 'Brésil 2.60', 'probability': 38},
            {'site': 'Unibet', 'team': 'Angleterre 2.10', 'probability': 45},
        ],
    }


class LiveRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/live.json':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            try:
                html = fetch_external_html(TARGET_URL)
                data = parse_live_data(html)
            except Exception:
                data = default_live_data()
            self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
            return
        return super().do_GET()


def run_server():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, LiveRequestHandler)
    print(f'Serving on http://{HOST}:{PORT}/')
    print('Démarrez la page avec ce serveur et actualisez pour obtenir les données scrappées.')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nArrêt du serveur')
        httpd.server_close()


if __name__ == '__main__':
    run_server()
