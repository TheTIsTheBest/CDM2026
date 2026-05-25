import json
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from datetime import datetime

HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 8000))

def get_live_data():
    """
    Retourne les données du CDM 2026.
    À compléter avec les vrais matchs, cotes et buteurs au fur et à mesure du tournoi.
    
    Structure des matches:
    {
        dateLabel: str (ex: '11 Juin'),
        datetime: str (ISO 8601, ex: '2026-06-11T18:00:00'),
        home: str (équipe avec flag, ex: '🇺🇸 USA'),
        away: str (équipe avec flag),
        score: str ou None (ex: '2 - 0' ou None si à venir),
        scorers: [str] ou None (liste des buteurs),
        stage: str (ex: 'Groupes', '1/8 finale', etc),
        status: str (upcoming, live, finished),
        odds: {home: float, draw: float, away: float} ou None
    }
    """
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
            # À remplir avec les vrais matchs du CDM 2026 à partir du 11 juin
        ],
        'scorers': [
            # À remplir avec les vrais buteurs du tournoi: 
            # { name: str, country: str, val: int, img: str }
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
            
            data = get_live_data()
            self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
            return
        return super().do_GET()


def run_server():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, LiveRequestHandler)
    print(f'Serving on http://{HOST}:{PORT}/')
    print('API endpoint: /api/live.json')
    print('Mettez à jour get_live_data() avec les vrais matchs et données du CDM 2026')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nServeur arrêté')
        httpd.server_close()


if __name__ == '__main__':
    run_server()
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
