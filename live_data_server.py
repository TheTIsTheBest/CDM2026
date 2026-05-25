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
        'groups': [
            {'name': 'Groupe A', 'teams': [{'name': 'Team A1', 'slot': 'A1'}, {'name': 'Team A2', 'slot': 'A2'}, {'name': 'Team A3', 'slot': 'A3'}, {'name': 'Team A4', 'slot': 'A4'}]},
            {'name': 'Groupe B', 'teams': [{'name': 'Team B1', 'slot': 'B1'}, {'name': 'Team B2', 'slot': 'B2'}, {'name': 'Team B3', 'slot': 'B3'}, {'name': 'Team B4', 'slot': 'B4'}]},
            {'name': 'Groupe C', 'teams': [{'name': 'Team C1', 'slot': 'C1'}, {'name': 'Team C2', 'slot': 'C2'}, {'name': 'Team C3', 'slot': 'C3'}, {'name': 'Team C4', 'slot': 'C4'}]},
            {'name': 'Groupe D', 'teams': [{'name': 'Team D1', 'slot': 'D1'}, {'name': 'Team D2', 'slot': 'D2'}, {'name': 'Team D3', 'slot': 'D3'}, {'name': 'Team D4', 'slot': 'D4'}]},
            {'name': 'Groupe E', 'teams': [{'name': 'Team E1', 'slot': 'E1'}, {'name': 'Team E2', 'slot': 'E2'}, {'name': 'Team E3', 'slot': 'E3'}, {'name': 'Team E4', 'slot': 'E4'}]},
            {'name': 'Groupe F', 'teams': [{'name': 'Team F1', 'slot': 'F1'}, {'name': 'Team F2', 'slot': 'F2'}, {'name': 'Team F3', 'slot': 'F3'}, {'name': 'Team F4', 'slot': 'F4'}]},
            {'name': 'Groupe G', 'teams': [{'name': 'Team G1', 'slot': 'G1'}, {'name': 'Team G2', 'slot': 'G2'}, {'name': 'Team G3', 'slot': 'G3'}, {'name': 'Team G4', 'slot': 'G4'}]},
            {'name': 'Groupe H', 'teams': [{'name': 'Team H1', 'slot': 'H1'}, {'name': 'Team H2', 'slot': 'H2'}, {'name': 'Team H3', 'slot': 'H3'}, {'name': 'Team H4', 'slot': 'H4'}]},
        ],
        'last_updated': '2026-05-25T17:56:17.076463Z',
        'live': False,
        'matches': [
            {'away': 'Team A2', 'datetime': '2026-05-26T17:56:18.038982Z', 'group': 'Groupe A', 'home': 'Team A1', 'odds': {'away': 2.73, 'draw': 3.2, 'home': 1.98, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team A3', 'datetime': '2026-05-26T23:56:18.038982Z', 'group': 'Groupe A', 'home': 'Team A1', 'odds': {'away': 2.74, 'draw': 3.2, 'home': 2.0, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team A4', 'datetime': '2026-05-27T05:56:18.038982Z', 'group': 'Groupe A', 'home': 'Team A1', 'odds': {'away': 2.71, 'draw': 3.2, 'home': 2.1, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team A3', 'datetime': '2026-05-27T11:56:18.038982Z', 'group': 'Groupe A', 'home': 'Team A2', 'odds': {'away': 2.71, 'draw': 3.2, 'home': 2.13, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team A4', 'datetime': '2026-05-27T17:56:18.038982Z', 'group': 'Groupe A', 'home': 'Team A2', 'odds': {'away': 2.77, 'draw': 3.2, 'home': 2.03, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team A4', 'datetime': '2026-05-27T23:56:18.038982Z', 'group': 'Groupe A', 'home': 'Team A3', 'odds': {'away': 2.69, 'draw': 3.2, 'home': 2.06, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team B2', 'datetime': '2026-05-26T17:56:18.038982Z', 'group': 'Groupe B', 'home': 'Team B1', 'odds': {'away': 2.69, 'draw': 3.2, 'home': 2.06, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team B3', 'datetime': '2026-05-26T23:56:18.038982Z', 'group': 'Groupe B', 'home': 'Team B1', 'odds': {'away': 2.73, 'draw': 3.2, 'home': 2.11, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team B4', 'datetime': '2026-05-27T05:56:18.038982Z', 'group': 'Groupe B', 'home': 'Team B1', 'odds': {'away': 2.67, 'draw': 3.2, 'home': 2.11, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team B3', 'datetime': '2026-05-27T11:56:18.038982Z', 'group': 'Groupe B', 'home': 'Team B2', 'odds': {'away': 2.78, 'draw': 3.2, 'home': 2.03, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team B4', 'datetime': '2026-05-27T17:56:18.038982Z', 'group': 'Groupe B', 'home': 'Team B2', 'odds': {'away': 2.67, 'draw': 3.2, 'home': 1.98, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team B4', 'datetime': '2026-05-27T23:56:18.038982Z', 'group': 'Groupe B', 'home': 'Team B3', 'odds': {'away': 2.79, 'draw': 3.2, 'home': 2.04, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team C2', 'datetime': '2026-05-26T17:56:18.038982Z', 'group': 'Groupe C', 'home': 'Team C1', 'odds': {'away': 2.69, 'draw': 3.2, 'home': 2.05, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team C3', 'datetime': '2026-05-26T23:56:18.038982Z', 'group': 'Groupe C', 'home': 'Team C1', 'odds': {'away': 2.69, 'draw': 3.2, 'home': 2.1, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team C4', 'datetime': '2026-05-27T05:56:18.038982Z', 'group': 'Groupe C', 'home': 'Team C1', 'odds': {'away': 2.78, 'draw': 3.2, 'home': 2.12, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team C3', 'datetime': '2026-05-27T11:56:18.038982Z', 'group': 'Groupe C', 'home': 'Team C2', 'odds': {'away': 2.76, 'draw': 3.2, 'home': 2.07, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team C4', 'datetime': '2026-05-27T17:56:18.038982Z', 'group': 'Groupe C', 'home': 'Team C2', 'odds': {'away': 2.79, 'draw': 3.2, 'home': 2.01, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team C4', 'datetime': '2026-05-27T23:56:18.038982Z', 'group': 'Groupe C', 'home': 'Team C3', 'odds': {'away': 2.83, 'draw': 3.2, 'home': 2.01, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team D2', 'datetime': '2026-05-26T17:56:18.038982Z', 'group': 'Groupe D', 'home': 'Team D1', 'odds': {'away': 2.8, 'draw': 3.2, 'home': 2.12, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team D3', 'datetime': '2026-05-26T23:56:18.038982Z', 'group': 'Groupe D', 'home': 'Team D1', 'odds': {'away': 2.7, 'draw': 3.2, 'home': 2.12, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team D4', 'datetime': '2026-05-27T05:56:18.038982Z', 'group': 'Groupe D', 'home': 'Team D1', 'odds': {'away': 2.78, 'draw': 3.2, 'home': 2.12, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team D3', 'datetime': '2026-05-27T11:56:18.038982Z', 'group': 'Groupe D', 'home': 'Team D2', 'odds': {'away': 2.78, 'draw': 3.2, 'home': 2.13, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team D4', 'datetime': '2026-05-27T17:56:18.038982Z', 'group': 'Groupe D', 'home': 'Team D2', 'odds': {'away': 2.77, 'draw': 3.2, 'home': 2.02, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team D4', 'datetime': '2026-05-27T23:56:18.038982Z', 'group': 'Groupe D', 'home': 'Team D3', 'odds': {'away': 2.74, 'draw': 3.2, 'home': 2.09, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team E2', 'datetime': '2026-05-26T17:56:18.038982Z', 'group': 'Groupe E', 'home': 'Team E1', 'odds': {'away': 2.72, 'draw': 3.2, 'home': 2.01, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team E3', 'datetime': '2026-05-26T23:56:18.038982Z', 'group': 'Groupe E', 'home': 'Team E1', 'odds': {'away': 2.78, 'draw': 3.2, 'home': 2.04, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team E4', 'datetime': '2026-05-27T05:56:18.038982Z', 'group': 'Groupe E', 'home': 'Team E1', 'odds': {'away': 2.72, 'draw': 3.2, 'home': 2.09, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team E3', 'datetime': '2026-05-27T11:56:18.038982Z', 'group': 'Groupe E', 'home': 'Team E2', 'odds': {'away': 2.8, 'draw': 3.2, 'home': 2.09, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team E4', 'datetime': '2026-05-27T17:56:18.038982Z', 'group': 'Groupe E', 'home': 'Team E2', 'odds': {'away': 2.73, 'draw': 3.2, 'home': 2.13, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team E4', 'datetime': '2026-05-27T23:56:18.038982Z', 'group': 'Groupe E', 'home': 'Team E3', 'odds': {'away': 2.67, 'draw': 3.2, 'home': 1.98, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team F2', 'datetime': '2026-05-26T17:56:18.038982Z', 'group': 'Groupe F', 'home': 'Team F1', 'odds': {'away': 2.8, 'draw': 3.2, 'home': 1.98, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team F3', 'datetime': '2026-05-26T23:56:18.038982Z', 'group': 'Groupe F', 'home': 'Team F1', 'odds': {'away': 2.83, 'draw': 3.2, 'home': 2.01, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team F4', 'datetime': '2026-05-27T05:56:18.038982Z', 'group': 'Groupe F', 'home': 'Team F1', 'odds': {'away': 2.75, 'draw': 3.2, 'home': 2.1, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team F3', 'datetime': '2026-05-27T11:56:18.038982Z', 'group': 'Groupe F', 'home': 'Team F2', 'odds': {'away': 2.78, 'draw': 3.2, 'home': 2.12, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team F4', 'datetime': '2026-05-27T17:56:18.038982Z', 'group': 'Groupe F', 'home': 'Team F2', 'odds': {'away': 2.68, 'draw': 3.2, 'home': 1.99, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team F4', 'datetime': '2026-05-27T23:56:18.038982Z', 'group': 'Groupe F', 'home': 'Team F3', 'odds': {'away': 2.75, 'draw': 3.2, 'home': 1.99, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team G2', 'datetime': '2026-05-26T17:56:18.038982Z', 'group': 'Groupe G', 'home': 'Team G1', 'odds': {'away': 2.73, 'draw': 3.2, 'home': 2.1, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team G3', 'datetime': '2026-05-26T23:56:18.038982Z', 'group': 'Groupe G', 'home': 'Team G1', 'odds': {'away': 2.69, 'draw': 3.2, 'home': 2.13, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team G4', 'datetime': '2026-05-27T05:56:18.038982Z', 'group': 'Groupe G', 'home': 'Team G1', 'odds': {'away': 2.79, 'draw': 3.2, 'home': 1.97, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team G3', 'datetime': '2026-05-27T11:56:18.038982Z', 'group': 'Groupe G', 'home': 'Team G2', 'odds': {'away': 2.74, 'draw': 3.2, 'home': 2.1, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team G4', 'datetime': '2026-05-27T17:56:18.038982Z', 'group': 'Groupe G', 'home': 'Team G2', 'odds': {'away': 2.74, 'draw': 3.2, 'home': 2.13, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team G4', 'datetime': '2026-05-27T23:56:18.038982Z', 'group': 'Groupe G', 'home': 'Team G3', 'odds': {'away': 2.78, 'draw': 3.2, 'home': 2.1, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team H2', 'datetime': '2026-05-26T17:56:18.038982Z', 'group': 'Groupe H', 'home': 'Team H1', 'odds': {'away': 2.79, 'draw': 3.2, 'home': 2.09, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team H3', 'datetime': '2026-05-26T23:56:18.038982Z', 'group': 'Groupe H', 'home': 'Team H1', 'odds': {'away': 2.82, 'draw': 3.2, 'home': 2.12, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team H4', 'datetime': '2026-05-27T05:56:18.038982Z', 'group': 'Groupe H', 'home': 'Team H1', 'odds': {'away': 2.8, 'draw': 3.2, 'home': 1.97, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team H3', 'datetime': '2026-05-27T11:56:18.038982Z', 'group': 'Groupe H', 'home': 'Team H2', 'odds': {'away': 2.73, 'draw': 3.2, 'home': 2.1, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team H4', 'datetime': '2026-05-27T17:56:18.038982Z', 'group': 'Groupe H', 'home': 'Team H2', 'odds': {'away': 2.77, 'draw': 3.2, 'home': 2.12, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'},
            {'away': 'Team H4', 'datetime': '2026-05-27T23:56:18.038982Z', 'group': 'Groupe H', 'home': 'Team H3', 'odds': {'away': 2.73, 'draw': 3.2, 'home': 2.08, 'source': 'estimated'}, 'score': '', 'stage': 'Group stage', 'status': 'upcoming'}
        ],
        'scorers': {'goals': []},
        'stats': {'goals': 0, 'host_cities': 16, 'matches_played': 0, 'teams': 48}
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
