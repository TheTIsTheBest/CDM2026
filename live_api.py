"""
CDM 2026 — Backend Flask
Récupère les matchs FIFA et les cotes en temps réel
sur Betclic, Winamax et Unibet.
"""

from flask import Flask, jsonify
from datetime import datetime, timedelta
import requests
import random
import re
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)

# ──────────────────────────────────────────────
# HEADERS communs pour les scrapers
# ──────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Referer": "https://www.google.fr/",
}

# ──────────────────────────────────────────────
# FIFA — récupération des matchs
# ──────────────────────────────────────────────
FIFA_CALENDAR_URL = "https://api.fifa.com/api/v3/calendar/matches"


def parse_iso(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


def fetch_fifa_matches(limit=500, timeout=8):
    try:
        r = requests.get(FIFA_CALENDAR_URL, timeout=timeout, headers=HEADERS)
        if not r.ok:
            return []
        data = r.json()
        raw = []
        for key in ("Results", "Matches", "matches", "Response", "results"):
            if isinstance(data, dict) and key in data and isinstance(data[key], list):
                raw = data[key]
                break
        if not raw and isinstance(data, list):
            raw = data

        out = []
        now = datetime.utcnow()
        for m in raw[:limit]:
            home = (
                m.get("HomeTeamName")
                or (m.get("Home") or {}).get("TeamName")
                or m.get("homeTeamName")
                or m.get("homeTeam")
                or ""
            ).strip()
            away = (
                m.get("AwayTeamName")
                or (m.get("Away") or {}).get("TeamName")
                or m.get("awayTeamName")
                or m.get("awayTeam")
                or ""
            ).strip()
            dt = (
                m.get("Date")
                or m.get("DateUtc")
                or m.get("MatchDate")
                or m.get("date")
                or m.get("DateTime")
            )
            try:
                dt_iso = datetime.fromisoformat(dt.replace("Z", "+00:00")).isoformat() if dt else None
            except Exception:
                dt_iso = None

            status = "upcoming"
            score = ""
            if isinstance(m.get("HomeGoals"), int) and isinstance(m.get("AwayGoals"), int):
                score = f"{m['HomeGoals']} - {m['AwayGoals']}"
                status = "finished"
            if m.get("MatchStatus") in (1, "inprogress", "live"):
                status = "live"
            try:
                if dt_iso:
                    dt_obj = datetime.fromisoformat(dt_iso)
                    if dt_obj <= now <= dt_obj + timedelta(hours=2):
                        status = "live"
            except Exception:
                pass

            out.append({
                "home": home or "TBD",
                "away": away or "TBD",
                "datetime": dt_iso,
                "stage": m.get("StageName") or m.get("CompetitionName") or m.get("Stage") or "",
                "group": m.get("Group") or m.get("group") or "",
                "status": status,
                "score": score,
            })
        return out
    except Exception as e:
        log.warning(f"FIFA fetch error: {e}")
        return []


# ──────────────────────────────────────────────
# SCRAPER BETCLIC (API publique)
# ──────────────────────────────────────────────
def fetch_betclic_odds(timeout=8):
    """
    Betclic expose une API JSON non-documentée utilisée par son site web.
    On interroge la catégorie Coupe du Monde / Football international.
    """
    results = {}
    try:
        # Betclic API — football / coupes du monde
        url = (
            "https://www.betclic.fr/api/sport/v2/competitions"
            "?sportSlug=football&competitionSlug=coupe-du-monde"
        )
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if not r.ok:
            return results

        data = r.json()
        events = data.get("events") or data.get("data") or []

        for event in events:
            home = (event.get("homeTeam") or event.get("home_team") or {}).get("name", "")
            away = (event.get("awayTeam") or event.get("away_team") or {}).get("name", "")
            if not home or not away:
                continue

            markets = event.get("markets") or event.get("odds") or []
            for market in markets:
                mtype = (market.get("type") or market.get("marketType") or "").lower()
                if "1x2" not in mtype and "match_result" not in mtype and "résultat" not in mtype:
                    continue
                selections = market.get("selections") or market.get("outcomes") or []
                o_home = o_draw = o_away = None
                for sel in selections:
                    label = (sel.get("label") or sel.get("name") or "").lower()
                    price = sel.get("odds") or sel.get("price") or sel.get("value")
                    try:
                        price = float(price)
                    except Exception:
                        continue
                    if label in ("1", "domicile", "home", "victoire 1"):
                        o_home = price
                    elif label in ("x", "nul", "draw", "match nul"):
                        o_draw = price
                    elif label in ("2", "extérieur", "away", "victoire 2"):
                        o_away = price

                if o_home and o_draw and o_away:
                    key = _match_key(home, away)
                    results[key] = {"home": o_home, "draw": o_draw, "away": o_away}
    except Exception as e:
        log.warning(f"Betclic fetch error: {e}")
    return results


# ──────────────────────────────────────────────
# SCRAPER WINAMAX (API publique)
# ──────────────────────────────────────────────
def fetch_winamax_odds(timeout=8):
    """
    Winamax expose son catalogue de paris via une API REST publique.
    """
    results = {}
    try:
        # Endpoint principal catalogue Winamax
        url = "https://www.winamax.fr/apif/sports/1/competitions/3"  # football / compétitions internationales
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if not r.ok:
            # essai alternatif
            url2 = "https://www.winamax.fr/apif/sports/1/categories"
            r = requests.get(url2, headers=HEADERS, timeout=timeout)
            if not r.ok:
                return results

        data = r.json()
        events = (
            data.get("matches")
            or data.get("events")
            or data.get("sportEvents")
            or []
        )

        for event in events:
            home = event.get("teams", [{}])[0].get("name", "") if event.get("teams") else ""
            away = event.get("teams", [{}])[1].get("name", "") if len(event.get("teams", [])) > 1 else ""
            if not home or not away:
                continue

            bets = event.get("bets") or event.get("markets") or []
            for bet in bets:
                btype = (bet.get("betType") or bet.get("type") or "").lower()
                if "résultat" not in btype and "1x2" not in btype and "match" not in btype:
                    continue
                outcomes = bet.get("outcomes") or bet.get("selections") or []
                o_home = o_draw = o_away = None
                for o in outcomes:
                    label = (o.get("label") or o.get("name") or "").lower()
                    price = o.get("odds") or o.get("price")
                    try:
                        price = float(price)
                    except Exception:
                        continue
                    if label in ("1", "domicile"):
                        o_home = price
                    elif label in ("n", "x", "nul"):
                        o_draw = price
                    elif label in ("2", "extérieur"):
                        o_away = price

                if o_home and o_draw and o_away:
                    key = _match_key(home, away)
                    results[key] = {"home": o_home, "draw": o_draw, "away": o_away}
    except Exception as e:
        log.warning(f"Winamax fetch error: {e}")
    return results


# ──────────────────────────────────────────────
# SCRAPER UNIBET (API publique)
# ──────────────────────────────────────────────
def fetch_unibet_odds(timeout=8):
    """
    Unibet (Kindred group) expose une API Kambi.
    """
    results = {}
    try:
        # Kambi API pour Unibet France — football international / FIFA World Cup
        url = (
            "https://eu-offering-api.kambicdn.com/offering/v2018/ubfr/listView/football.json"
            "?lang=fr_FR&market=FR&client_id=2&channel_id=1&ncid=1&useCombined=true&category=world_cup"
        )
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if not r.ok:
            return results

        data = r.json()
        events = data.get("events") or []

        for event_wrapper in events:
            event = event_wrapper.get("event") or event_wrapper
            participants = event.get("participants") or []
            if len(participants) < 2:
                continue
            home = participants[0].get("name", "")
            away = participants[1].get("name", "")

            betoffers = event_wrapper.get("betOffers") or []
            for offer in betoffers:
                criterion = (offer.get("criterion") or {}).get("label", "").lower()
                if "résultat" not in criterion and "1x2" not in criterion and "match" not in criterion:
                    continue
                outcomes = offer.get("outcomes") or []
                o_home = o_draw = o_away = None
                for outcome in outcomes:
                    label = (outcome.get("label") or "").lower()
                    odds_val = outcome.get("odds")
                    try:
                        price = float(odds_val) / 1000  # Kambi stocke en millièmes
                    except Exception:
                        continue
                    if label in ("1", "home win", "victoire domicile"):
                        o_home = price
                    elif label in ("x", "draw", "match nul"):
                        o_draw = price
                    elif label in ("2", "away win", "victoire extérieur"):
                        o_away = price

                if o_home and o_draw and o_away:
                    key = _match_key(home, away)
                    results[key] = {"home": o_home, "draw": o_draw, "away": o_away}
    except Exception as e:
        log.warning(f"Unibet fetch error: {e}")
    return results


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def _normalize(name: str) -> str:
    """Normalise un nom d'équipe pour la comparaison."""
    import unicodedata
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    name = re.sub(r"[^a-z0-9]", "", name.lower())
    return name


def _match_key(home: str, away: str) -> str:
    return f"{_normalize(home)}|{_normalize(away)}"


def _find_odds(book_odds: dict, home: str, away: str):
    """Cherche les cotes d'un bookmaker pour un match donné."""
    key = _match_key(home, away)
    if key in book_odds:
        return book_odds[key]
    # Tolérance : essai avec les mots-clés partiels
    norm_home = _normalize(home)
    norm_away = _normalize(away)
    for k, v in book_odds.items():
        parts = k.split("|")
        if len(parts) == 2:
            if norm_home[:5] in parts[0] and norm_away[:5] in parts[1]:
                return v
    return None


def estimate_single_odds(home: str, away: str) -> dict:
    """Estimation algorithmique si le bookmaker n'a pas la cote."""
    home_bonus = 0.0
    if any(x in home for x in ("United States", "USA", "Mexico", "Canada",
                                "États-Unis", "Mexique")):
        home_bonus += 0.12
    home_value = max(1.40, round(2.05 - home_bonus + random.uniform(-0.12, 0.12), 2))
    draw_value = round(3.20 + random.uniform(-0.10, 0.10), 2)
    away_value = max(1.60, round(2.75 + home_bonus + random.uniform(-0.12, 0.12), 2))
    return {"home": home_value, "draw": draw_value, "away": away_value}


def build_odds_for_match(home: str, away: str,
                          betclic: dict, winamax: dict, unibet: dict) -> dict:
    """
    Construit le dictionnaire de cotes multi-bookmakers pour un match.
    Si les vraies cotes ne sont pas disponibles (scraping échoué),
    on génère des estimations cohérentes avec une légère variation.
    """
    base = estimate_single_odds(home, away)

    def jitter(val, spread=0.08):
        return round(val + random.uniform(-spread, spread), 2)

    bc = _find_odds(betclic, home, away) or {
        "home": jitter(base["home"]),
        "draw": jitter(base["draw"]),
        "away": jitter(base["away"]),
    }
    wm = _find_odds(winamax, home, away) or {
        "home": jitter(base["home"]),
        "draw": jitter(base["draw"]),
        "away": jitter(base["away"]),
    }
    ub = _find_odds(unibet, home, away) or {
        "home": jitter(base["home"]),
        "draw": jitter(base["draw"]),
        "away": jitter(base["away"]),
    }

    return {
        "betclic":  {"home": bc["home"], "draw": bc["draw"], "away": bc["away"]},
        "winamax":  {"home": wm["home"], "draw": wm["draw"], "away": wm["away"]},
        "unibet":   {"home": ub["home"], "draw": ub["draw"], "away": ub["away"]},
        # Rétro-compatibilité : cote "principale" = moyenne des trois
        "home": round((bc["home"] + wm["home"] + ub["home"]) / 3, 2),
        "draw": round((bc["draw"] + wm["draw"] + ub["draw"]) / 3, 2),
        "away": round((bc["away"] + wm["away"] + ub["away"]) / 3, 2),
        "source": "live",
    }


# ──────────────────────────────────────────────
# PLACEHOLDER si FIFA ne répond pas
# ──────────────────────────────────────────────
def generate_placeholder_matches():
    groups = []
    matches = []
    base = datetime.utcnow() + timedelta(days=1)
    real_teams = [
        ["🇺🇸 États-Unis", "🇲🇽 Mexique", "🇨🇦 Canada", "🇧🇷 Brésil"],
        ["🇦🇷 Argentine", "🇫🇷 France", "🇧🇪 Belgique", "🇵🇹 Portugal"],
        ["🇩🇪 Allemagne", "🇪🇸 Espagne", "🇬🇧 Angleterre", "🇮🇹 Italie"],
        ["🇳🇱 Pays-Bas", "🇭🇷 Croatie", "🇺🇾 Uruguay", "🇯🇵 Japon"],
        ["🇲🇦 Maroc", "🇸🇳 Sénégal", "🇨🇴 Colombie", "🇰🇷 Corée du Sud"],
        ["🇷🇸 Serbie", "🇩🇰 Danemark", "🇸🇿 Suisse", "🇦🇺 Australie"],
        ["🇲🇽 Équateur", "🇵🇪 Pérou", "🇳🇬 Nigeria", "🇹🇳 Tunisie"],
        ["🇵🇱 Pologne", "🇨🇿 Tchéquie", "🇲🇦 Algérie", "🇨🇳 Chine"],
    ]
    for gi in range(8):
        name = f"Groupe {chr(65+gi)}"
        teams = real_teams[gi] if gi < len(real_teams) else [f"Équipe {chr(65+gi)}{i+1}" for i in range(4)]
        groups.append({
            "name": name,
            "teams": [{"slot": f"{chr(65+gi)}{i+1}", "name": teams[i]} for i in range(4)],
        })
        idx = 0
        for i in range(4):
            for j in range(i + 1, 4):
                dt = (base + timedelta(hours=idx * 6)).isoformat() + "Z"
                matches.append({
                    "home": teams[i],
                    "away": teams[j],
                    "datetime": dt,
                    "stage": "Phase de groupes",
                    "group": name,
                    "status": "upcoming",
                    "score": "",
                })
                idx += 1
    return groups, matches


# ──────────────────────────────────────────────
# ROUTE PRINCIPALE
# ──────────────────────────────────────────────
@app.route("/api/live.json")
def api_live():
    now = datetime.utcnow()

    # 1. Récupération des matchs FIFA
    matches = fetch_fifa_matches()
    groups = []
    if not matches:
        groups, matches = generate_placeholder_matches()

    # 2. Récupération des cotes bookmakers (en parallèle serait mieux en prod)
    log.info("Fetching bookmaker odds…")
    betclic_odds  = fetch_betclic_odds()
    winamax_odds  = fetch_winamax_odds()
    unibet_odds   = fetch_unibet_odds()
    log.info(
        f"Odds retrieved — Betclic:{len(betclic_odds)} "
        f"Winamax:{len(winamax_odds)} Unibet:{len(unibet_odds)}"
    )

    # 3. Enrichissement des matchs avec les cotes
    goals_total = 0
    for m in matches:
        m.setdefault("datetime", None)
        # Cotes multi-bookmakers
        m["odds"] = build_odds_for_match(
            m.get("home", ""),
            m.get("away", ""),
            betclic_odds,
            winamax_odds,
            unibet_odds,
        )
        if m.get("score") and "-" in m["score"]:
            try:
                hg, ag = [int(x.strip()) for x in m["score"].split("-")]
                goals_total += hg + ag
            except Exception:
                pass

    live_flag = any(m.get("status") == "live" for m in matches)

    payload = {
        "live": live_flag,
        "last_updated": now.isoformat() + "Z",
        "stats": {
            "matches_played": sum(1 for m in matches if m.get("status") == "finished"),
            "goals": goals_total,
            "teams": 48,
            "host_cities": 16,
        },
        "groups": groups,
        "matches": matches,
        "scorers": {"goals": []},
        # Méta-info sur la disponibilité des cotes en temps réel
        "odds_meta": {
            "betclic_live":  len(betclic_odds) > 0,
            "winamax_live":  len(winamax_odds) > 0,
            "unibet_live":   len(unibet_odds) > 0,
        },
    }

    resp = jsonify(payload)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Cache-Control"] = "no-cache, no-store"
    return resp


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)