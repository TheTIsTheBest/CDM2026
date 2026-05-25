from flask import Flask, jsonify
from datetime import datetime, timedelta
import requests
import random

app = Flask(__name__)


FIFA_CALENDAR_URL = 'https://api.fifa.com/api/v3/calendar/matches'


def parse_iso(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except Exception:
        return None


def safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def estimate_odds(home: str, away: str) -> dict:
    home_bonus = 0.0
    if any(x in home for x in ('United States', 'USA', 'Mexico', 'Canada')):
        home_bonus += 0.12
    home_value = max(1.4, 2.05 - home_bonus)
    away_value = max(1.6, 2.75 + home_bonus)
    draw = 3.2
    home_value = round(home_value + random.uniform(-0.08, 0.08), 2)
    away_value = round(away_value + random.uniform(-0.08, 0.08), 2)
    return {"home": home_value, "draw": draw, "away": away_value, "source": "estimated"}


def fetch_fifa_matches(limit=500, timeout=8):
    try:
        r = requests.get(FIFA_CALENDAR_URL, timeout=timeout)
        if not r.ok:
            return []
        data = r.json()
        raw = []
        for key in ('Results', 'Matches', 'matches', 'Response', 'results'):
            if isinstance(data, dict) and key in data and isinstance(data[key], list):
                raw = data[key]
                break
        if not raw and isinstance(data, list):
            raw = data

        out = []
        now = datetime.utcnow()
        for m in raw[:limit]:
            home = (m.get('HomeTeamName') or m.get('Home', {}).get('TeamName') or m.get('homeTeamName') or m.get('homeTeam') or '').strip()
            away = (m.get('AwayTeamName') or m.get('Away', {}).get('TeamName') or m.get('awayTeamName') or m.get('awayTeam') or '').strip()
            dt = m.get('Date') or m.get('DateUtc') or m.get('MatchDate') or m.get('date') or m.get('DateTime')
            try:
                if dt:
                    dt_parsed = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                    dt_iso = dt_parsed.isoformat()
                else:
                    dt_iso = None
            except Exception:
                dt_iso = None

            status = 'upcoming'
            score = ''
            if isinstance(m.get('HomeGoals'), int) and isinstance(m.get('AwayGoals'), int):
                score = f"{m.get('HomeGoals')} - {m.get('AwayGoals')}"
                status = 'finished'
            if m.get('MatchStatus') in (1, 'inprogress', 'live'):
                status = 'live'

            try:
                if dt_iso:
                    dt_obj = datetime.fromisoformat(dt_iso)
                    if dt_obj <= now <= dt_obj + timedelta(hours=2):
                        status = 'live'
            except Exception:
                pass

            out.append({
                'home': home or 'TBD',
                'away': away or 'TBD',
                'datetime': dt_iso,
                'stage': m.get('StageName') or m.get('CompetitionName') or m.get('Stage') or '',
                'group': m.get('Group') or m.get('group') or '',
                'status': status,
                'score': score,
            })
        return out
    except Exception:
        return []


def generate_placeholder_matches():
    groups = []
    matches = []
    base = datetime.utcnow() + timedelta(days=1)
    for gi in range(8):
        name = f'Groupe {chr(65+gi)}'
        teams = [f'Team {chr(65+gi)}{i+1}' for i in range(4)]
        groups.append({'name': name, 'teams': [{'slot': f'{chr(65+gi)}{i+1}', 'name': teams[i]} for i in range(4)]})
        idx = 0
        for i in range(4):
            for j in range(i+1, 4):
                dt = (base + timedelta(hours=idx * 6)).isoformat() + 'Z'
                matches.append({
                    'home': teams[i],
                    'away': teams[j],
                    'datetime': dt,
                    'stage': 'Group stage',
                    'group': name,
                    'status': 'upcoming',
                    'score': ''
                })
                idx += 1
    return groups, matches


@app.route('/api/live.json')
def api_live():
    now = datetime.utcnow()
    matches = fetch_fifa_matches()
    groups = []
    if not matches:
        groups, matches = generate_placeholder_matches()

    goals_total = 0
    for m in matches:
        m.setdefault('datetime', None)
        m['odds'] = estimate_odds(m.get('home', ''), m.get('away', ''))
        if m.get('score') and '-' in m['score']:
            try:
                hg, ag = [int(x.strip()) for x in m['score'].split('-')]
                goals_total += hg + ag
            except Exception:
                pass

    live_flag = any(m.get('status') == 'live' for m in matches)

    payload = {
        'live': live_flag,
        'last_updated': now.isoformat() + 'Z',
        'stats': {
            'matches_played': sum(1 for m in matches if m.get('status') == 'finished'),
            'goals': goals_total,
            'teams': 48,
            'host_cities': 16,
        },
        'groups': groups,
        'matches': matches,
        'scorers': {'goals': []},
    }
    resp = jsonify(payload)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
