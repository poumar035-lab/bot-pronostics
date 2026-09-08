import requests
import json
from datetime import datetime, timedelta
from config import FOOTBALL_API_BASE, FOOTBALL_API_KEY, HEADERS, LEAGUES


class FootballDataCollector:
    def __init__(self):
        self.base_url = FOOTBALL_API_BASE
        self.headers = HEADERS

    def search_teams(self, query):
        url = f"{self.base_url}/teams"
        params = {"name": query}
        try:
            r = requests.get(url, headers=self.headers, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                teams = []
                for team in data.get("teams", [])[:5]:
                    teams.append({
                        "id": team["id"],
                        "name": team["name"],
                        "short_name": team.get("shortName", team["name"]),
                        "country": team.get("area", {}).get("name", "N/A"),
                        "founded": team.get("founded", "N/A"),
                        "venue": team.get("venue", "N/A"),
                    })
                return teams
            elif r.status_code == 429:
                return {"error": "Trop de requêtes. Attends 60 secondes."}
            else:
                return {"error": f"Erreur API: {r.status_code}"}
        except Exception as e:
            return {"error": f"Erreur connexion: {str(e)}"}

    def get_team_matches(self, team_id, last_n=10):
        url = f"{self.base_url}/teams/{team_id}/matches"
        params = {
            "status": "FINISHED",
            "limit": last_n
        }
        try:
            r = requests.get(url, headers=self.headers, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
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
            elif r.status_code == 429:
                return {"error": "Trop de requêtes. Attends 60s."}
            else:
                return {"error": f"Erreur API: {r.status_code}"}
        except Exception as e:
            return {"error": f"Erreur: {str(e)}"}

    def get_team_standings(self, team_id):
        url = f"{self.base_url}/teams/{team_id}/standing"
        try:
            r = requests.get(url, headers=self.headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
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
            elif r.status_code == 429:
                return {"error": "Rate limit. Attends 60s."}
            else:
                return {"error": f"Erreur API: {r.status_code}"}
        except Exception as e:
            return {"error": f"Erreur: {str(e)}"}

    def get_upcoming_matches(self, league_id=None, days_ahead=3):
        url = f"{self.base_url}/matches"
        today = datetime.utcnow().date()
        end = today + timedelta(days=days_ahead)
        params = {
            "dateFrom": today.isoformat(),
            "dateTo": end.isoformat(),
            "status": "SCHEDULED",
        }
        if league_id:
            params["competitions"] = league_id
        try:
            r = requests.get(url, headers=self.headers, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
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
            elif r.status_code == 429:
                return {"error": "Rate limit. Attends 60s."}
            else:
                return {"error": f"Erreur API: {r.status_code}"}
        except Exception as e:
            return {"error": f"Erreur: {str(e)}"}

    def get_h2h(self, team1_id, team2_id, limit=10):
        url = f"{self.base_url}/teams/{team1_id}/matches"
        try:
            r = requests.get(url, headers=self.headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                h2h = []
                for m in data.get("matches", []):
                    opponent_id = None
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
            elif r.status_code == 429:
                return {"error": "Rate limit."}
            else:
                return {"error": f"Erreur: {r.status_code}"}
        except Exception as e:
            return {"error": f"Erreur: {str(e)}"}

    def get_match_info(self, match_id):
        url = f"{self.base_url}/matches/{match_id}"
        try:
            r = requests.get(url, headers=self.headers, timeout=10)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                return {"error": "Rate limit."}
            else:
                return {"error": f"Erreur: {r.status_code}"}
        except Exception as e:
            return {"error": f"Erreur: {str(e)}"}
