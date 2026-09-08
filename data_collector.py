import requests
import json
import re
import unicodedata
from datetime import datetime, timedelta
from config import FOOTBALL_API_BASE, FOOTBALL_API_KEY, HEADERS, LEAGUES
from api_cache import cached_request, get_cached, set_cached

# Compétitions majeures à parcourir pour la recherche d'équipes
SEARCH_COMPETITIONS = [
    2001,  # Champions League
    2015,  # Ligue 1
    2021,  # Premier League
    2014,  # La Liga
    2019,  # Serie A
    2002,  # Bundesliga
    2003,  # Eredivisie
    2017,  # Primeira Liga
    2018,  # Super Lig
    2013,  # Série A Brasil
    2016,  # MLS
]

# Correspondance de noms: clé = terme que l'utilisateur envoie en français,
# valeur = substring qui matche le nom anglais de l'API
NAME_ALIASES = {
    "psg": "paris",
    "paris": "paris",
    "marseille": "marseille",
    "om": "marseille",
    "lyon": "lyon",
    "monaco": "monaco",
    "lille": "lille",
    "nice": "nice",
    "rennes": "rennais",
    "rennais": "rennais",
    "dortmund": "dortmund",
    "borussia": "dortmund",
    "bayern": "bayern",
    "munich": "bayern",
    "leipzig": "leipzig",
    "leverkusen": "leverkusen",
    "stuttgart": "stuttgart",
    "francfort": "frankfurt",
    "frankfurt": "frankfurt",
    "schalke": "schalke",
    "madrid": "real madrid",
    "real madrid": "real madrid",
    "atletico": "atletico madrid",
    "atletico madrid": "atletico madrid",
    "atlético": "atletico madrid",
    "barcelone": "barcelona",
    "barcelona": "barcelona",
    "barca": "barcelona",
    "sevilla": "sevilla",
    "seville": "sevilla",
    "valence": "valencia",
    "valencia": "valencia",
    "girona": "girona",
    "manchester city": "manchester city",
    "man city": "manchester city",
    "city": "manchester city",
    "manchester united": "manchester united",
    "man utd": "manchester united",
    "united": "manchester united",
    "liverpool": "liverpool",
    "chelsea": "chelsea",
    "arsenal": "arsenal",
    "tottenham": "tottenham",
    "newcastle": "newcastle",
    "villa": "aston villa",
    "aston villa": "aston villa",
    "juve": "juventus",
    "juventus": "juventus",
    "milan": "milan",
    "ac milan": "milan",
    "inter": "internazionale",
    "inter milan": "internazionale",
    "napo": "napoli",
    "napoli": "napoli",
    "roma": "roma",
    "latium": "lazio",
    "lazio": "lazio",
    "brugge": "brugge",
    "bruges": "brugge",
    "villarreal": "villarreal",
    "villareal": "villarreal",
    "porto": "porto",
    "benfica": "benfica",
    "sporting": "sporting",
    "galatasaray": "galatasaray",
    "fenerbahce": "fenerbahçe",
    "fenerbahçe": "fenerbahçe",
    "ajax": "ajax",
    "psv": "psv",
    "feyenoord": "feyenoord",
    "celtic": "celtic",
    "rangers": "rangers",
    "flamengo": "flamengo",
    "palmeiras": "palmeiras",
    "corinthians": "corinthians",
    "fluminense": "fluminense",
}


def _normalize(text):
    """Enlève les accents pour faciliter les recherches (Atletico, etc.)."""
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("ascii").lower()


class FootballDataCollector:
    def __init__(self):
        self.base_url = FOOTBALL_API_BASE
        self.headers = HEADERS
        self._teams_cache = None

    def _teams_cache_path(self):
        return "teams_cache.json"

    def _read_teams_cache(self):
        try:
            with open(self._teams_cache_path(), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _write_teams_cache(self, teams):
        try:
            with open(self._teams_cache_path(), "w", encoding="utf-8") as f:
                json.dump(teams, f, ensure_ascii=False)
        except Exception:
            pass

    def _load_all_teams(self, force=False):
        if self._teams_cache and not force:
            return self._teams_cache
        cached = self._read_teams_cache()
        if cached and not force:
            self._teams_cache = cached
            return cached
        all_teams = {}
        for comp_id in SEARCH_COMPETITIONS:
            url = f"{self.base_url}/competitions/{comp_id}/teams"
            key = f"comp_teams_{comp_id}"
            data = cached_request(key, url, self.headers, ttl=24 * 3600)
            if data is None:
                continue
            if isinstance(data, dict) and "error" in data:
                continue
            for team in data.get("teams", []):
                tid = team["id"]
                if tid not in all_teams:
                    all_teams[tid] = {
                        "id": tid,
                        "name": team["name"],
                        "short_name": team.get("shortName", team["name"]),
                        "tla": team.get("tla", ""),
                        "country": team.get("area", {}).get("name", "N/A"),
                        "founded": team.get("founded", "N/A"),
                        "venue": team.get("venue", "N/A"),
                    }
        self._teams_cache = list(all_teams.values())
        self._write_teams_cache(self._teams_cache)
        return self._teams_cache

    def search_teams(self, query):
        query = _normalize(query).strip()

        alias_target = _normalize(NAME_ALIASES.get(query, "")) or None
        search_terms = [query]
        if alias_target:
            search_terms.append(alias_target)

        teams = self._load_all_teams()

        # 1. Match exact d'un alias (prioritaire)
        if alias_target:
            for team in teams:
                if alias_target in _normalize(team["name"]):
                    return [team]

        # 1b. Tous les mots de l'alias présents dans le nom (ex: "atletico madrid")
        if alias_target:
            words = [w for w in alias_target.split() if w]
            if words:
                for team in teams:
                    norm = _normalize(team["name"])
                    if all(w in norm for w in words):
                        return [team]

        # 2. Correspondance logique
        for team in teams:
            lower_name = _normalize(team["name"])
            for term in search_terms:
                term_clean = term.lower()
                if term_clean == lower_name:
                    return [team]
                if len(term_clean) >= 4 and term_clean in lower_name:
                    return [team]
                words = [w for w in term_clean.split() if w]
                if len(words) >= 2 and all(w in lower_name for w in words):
                    return [team]

        # 3. Match partiel sur le TLA (sigle)
        for team in teams:
            if team.get("tla") and team["tla"].lower() == query:
                return [team]

        # 4. Return top 3 plus proches
        scored = []
        for team in teams:
            lower_name = _normalize(team["name"])
            score = 0
            if query in lower_name:
                score += len(query)
            if alias_target and alias_target in lower_name:
                score += len(alias_target)
            if score > 0:
                scored.append((score, team))
        scored.sort(key=lambda x: -x[0])
        return [t for _, t in scored[:3]]

    def get_team_matches(self, team_id, last_n=10):
        url = f"{self.base_url}/teams/{team_id}/matches?status=FINISHED&limit={last_n}"
        key = f"team{str(team_id)}_matches_{last_n}"
        data = cached_request(key, url, self.headers)
        if data is None:
            return {"error": "Erreur API (retry après 30s)"}
        if isinstance(data, dict) and "error" in data:
            return {"error": data["error"]}
        matches = []
        for m in data.get("matches", []):
            home = m["homeTeam"]
            away = m["awayTeam"]
            score = m.get("score", {})
            ft = score.get("fullTime", {})
            matches.append({
                "date": m["utcDate"][:10],
                "competition": m.get("competition", {}).get("name", "N/A"),
                "home_team": home["name"],
                "away_team": away["name"],
                "home_goals": ft.get("home"),
                "away_goals": ft.get("away"),
                "home_id": home["id"],
                "away_id": away["id"],
                "status": m.get("status"),
            })
        return matches

    def get_team_standings(self, team_id):
        key_neg = f"team{str(team_id)}_standing_neg"
        if get_cached(key_neg, ttl=60 * 60):
            return {"error": "Classement non dispo"}
        url = f"{self.base_url}/teams/{team_id}/standing"
        key = f"team{str(team_id)}_standing"
        data = cached_request(key, url, self.headers)
        if data is None:
            return {"error": "Erreur API (retry après 30s)"}
        if isinstance(data, dict) and "error" in data:
            if data.get("error") in (404, "404", 403):
                set_cached(key_neg, {"error": "neg"}, ttl=60 * 60)
            return {"error": "Classement non dispo"}
        standings = data.get("standings", [])
        for s in standings:
            if s.get("type") == "TOTAL":
                table = s.get("table", [])
                for entry in table:
                    if entry.get("team", {}).get("id") == team_id:
                        return {
                            "position": entry.get("position"),
                            "played": entry.get("playedGames"),
                            "won": entry.get("won"),
                            "draw": entry.get("draw"),
                            "lost": entry.get("lost"),
                            "goals_for": entry.get("goalsFor"),
                            "goals_against": entry.get("goalsAgainst"),
                            "goal_diff": entry.get("goalDifference"),
                            "points": entry.get("points"),
                            "form": entry.get("form", ""),
                        }
        return {"error": "Classement non trouvé"}

    def get_upcoming_matches(self, league_id=None, days_ahead=3):
        today = datetime.utcnow().date()
        end = today + timedelta(days=days_ahead)
        params = {
            "dateFrom": today.isoformat(),
            "dateTo": end.isoformat(),
            "status": "SCHEDULED",
        }
        if league_id:
            params["competitions"] = league_id
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{self.base_url}/matches?{qs}"
        key = f"upcoming_{today.isoformat()}_{end.isoformat()}_{league_id}"
        data = cached_request(key, url, self.headers)
        if data is None:
            return {"error": "Erreur API (retry après 30s)"}
        if isinstance(data, dict) and "error" in data:
            return {"error": data["error"]}
        matches = []
        for m in data.get("matches", []):
            matches.append({
                "id": m["id"],
                "date": m["utcDate"],
                "home": m["homeTeam"]["name"],
                "away": m["awayTeam"]["name"],
                "competition": m.get("competition", {}).get("name", ""),
                "home_id": m["homeTeam"]["id"],
                "away_id": m["awayTeam"]["id"],
            })
        return matches

    def get_h2h(self, team1_id, team2_id, limit=10):
        url = f"{self.base_url}/teams/{team1_id}/matches?status=FINISHED&limit=50"
        key = f"team{str(team1_id)}_matches_50"
        data = cached_request(key, url, self.headers)
        if data is None:
            return {"error": "Erreur API (retry après 30s)"}
        if isinstance(data, dict) and "error" in data:
            return {"error": data["error"]}
        h2h = []
        for m in data.get("matches", []):
            if m["homeTeam"]["id"] == team2_id or m["awayTeam"]["id"] == team2_id:
                ft = m.get("score", {}).get("fullTime", {})
                h2h.append({
                    "date": m["utcDate"][:10],
                    "home": m["homeTeam"]["name"],
                    "away": m["awayTeam"]["name"],
                    "home_goals": ft.get("home"),
                    "away_goals": ft.get("away"),
                    "result": m.get("score", {}).get("winner", ""),
                    "competition": m.get("competition", {}).get("name", ""),
                })
                if len(h2h) >= limit:
                    break
        return h2h

    def get_match_info(self, match_id):
        url = f"{self.base_url}/matches/{match_id}"
        key = f"match_{match_id}"
        data = cached_request(key, url, self.headers)
        if data is None:
            return {"error": "Erreur API (retry après 30s)"}
        if isinstance(data, dict) and "error" in data:
            return {"error": data["error"]}
        return data