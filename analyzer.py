import math
import numpy as np
import pandas as pd
from datetime import datetime
from data_collector import FootballDataCollector


class MatchAnalyzer:
    def __init__(self):
        self.collector = FootballDataCollector()

    def _calc_avg_goals(self, matches, team_id, is_home=True):
        scored = []
        conceded = []
        for m in matches:
            if m.get("home_goals") is None:
                continue
            if is_home:
                if m["home_id"] == team_id:
                    scored.append(m["home_goals"])
                    conceded.append(m["away_goals"])
                else:
                    scored.append(m["away_goals"])
                    conceded.append(m["home_goals"])
            else:
                if m["home_id"] == team_id:
                    scored.append(m["home_goals"])
                    conceded.append(m["away_goals"])
                else:
                    scored.append(m["away_goals"])
                    conceded.append(m["home_goals"])
        if not scored:
            return {"scored": 0, "conceded": 0, "matches": 0}
        return {
            "scored": round(np.mean(scored), 2),
            "conceded": round(np.mean(conceded), 2),
            "matches": len(scored),
        }

    def _calc_form(self, matches, team_id):
        form = []
        for m in matches[-5:]:
            if m.get("home_goals") is None:
                continue
            if m["home_id"] == team_id:
                gf, ga = m["home_goals"], m["away_goals"]
            else:
                gf, ga = m["away_goals"], m["home_goals"]
            if gf > ga:
                form.append("V")
            elif gf == ga:
                form.append("N")
            else:
                form.append("D")
        return form

    def _poisson_probability(self, lam, k):
        return (lam ** k) * np.exp(-lam) / math.factorial(k)

    def _poisson_score_matrix(self, avg_home, avg_away, max_goals=6):
        matrix = np.zeros((max_goals + 1, max_goals + 1))
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                matrix[i][j] = (
                    self._poisson_probability(avg_home, i)
                    * self._poisson_probability(avg_away, j)
                )
        return matrix

    def analyze_match(self, home_team_name, away_team_name):
        result = {
            "home_team": home_team_name,
            "away_team": away_team_name,
            "predictions": {},
            "analysis": {},
            "h2h": [],
            "home_stats": {},
            "away_stats": {},
            "errors": [],
        }

        home_teams = self.collector.search_teams(home_team_name)
        away_teams = self.collector.search_teams(away_team_name)

        if isinstance(home_teams, dict) and "error" in home_teams:
            result["errors"].append(f"Équipe domicile: {home_teams['error']}")
            return result
        if isinstance(away_teams, dict) and "error" in away_teams:
            result["errors"].append(f"Équipe extérieur: {away_teams['error']}")
            return result
        if not home_teams:
            result["errors"].append(f"'{home_team_name}' non trouvée")
            return result
        if not away_teams:
            result["errors"].append(f"'{away_team_name}' non trouvée")
            return result

        home_id = home_teams[0]["id"]
        away_id = away_teams[0]["id"]

        result["home_team"] = home_teams[0]["name"]
        result["away_team"] = away_teams[0]["name"]

        home_matches = self.collector.get_team_matches(home_id, 15)
        away_matches = self.collector.get_team_matches(away_id, 15)
        home_standings = self.collector.get_team_standings(home_id)
        away_standings = self.collector.get_team_standings(away_id)
        h2h = self.collector.get_h2h(home_id, away_id, 10)

        if isinstance(home_matches, dict) and "error" in home_matches:
            result["errors"].append(home_matches["error"])
            return result
        if isinstance(away_matches, dict) and "error" in away_matches:
            result["errors"].append(away_matches["error"])
            return result

        home_avg_home = self._calc_avg_goals(home_matches, home_id, is_home=True)
        away_avg_away = self._calc_avg_goals(away_matches, away_id, is_home=False)
        home_form = self._calc_form(home_matches, home_id)
        away_form = self._calc_form(away_matches, away_id)

        result["home_stats"] = {
            "name": home_teams[0]["name"],
            "short_name": home_teams[0]["short_name"],
            "venue": home_teams[0]["venue"],
            "founded": home_teams[0]["founded"],
            "country": home_teams[0]["country"],
            "avg_goals_scored_home": home_avg_home["scored"],
            "avg_goals_conceded_home": home_avg_home["conceded"],
            "last_5_form": " ".join(home_form) if home_form else "N/A",
            "matches_analyzed": home_avg_home["matches"],
        }
        if isinstance(home_standings, dict) and "error" not in home_standings:
            result["home_stats"]["position"] = home_standings.get("position")
            result["home_stats"]["points"] = home_standings.get("points")
            result["home_stats"]["won"] = home_standings.get("won")
            result["home_stats"]["draw"] = home_standings.get("draw")
            result["home_stats"]["lost"] = home_standings.get("lost")
            result["home_stats"]["goals_for"] = home_standings.get("goals_for")
            result["home_stats"]["goals_against"] = home_standings.get("goals_against")
            result["home_stats"]["form"] = home_standings.get("form", "")

        result["away_stats"] = {
            "name": away_teams[0]["name"],
            "short_name": away_teams[0]["short_name"],
            "venue": away_teams[0]["venue"],
            "founded": away_teams[0]["founded"],
            "country": away_teams[0]["country"],
            "avg_goals_scored_away": away_avg_away["scored"],
            "avg_goals_conceded_away": away_avg_away["conceded"],
            "last_5_form": " ".join(away_form) if away_form else "N/A",
            "matches_analyzed": away_avg_away["matches"],
        }
        if isinstance(away_standings, dict) and "error" not in away_standings:
            result["away_stats"]["position"] = away_standings.get("position")
            result["away_stats"]["points"] = away_standings.get("points")
            result["away_stats"]["won"] = away_standings.get("won")
            result["away_stats"]["draw"] = away_standings.get("draw")
            result["away_stats"]["lost"] = away_standings.get("lost")
            result["away_stats"]["goals_for"] = away_standings.get("goals_for")
            result["away_stats"]["goals_against"] = away_standings.get("goals_against")
            result["away_stats"]["form"] = away_standings.get("form", "")

        result["h2h"] = h2h if isinstance(h2h, list) else []

        avg_home_goals = home_avg_home["scored"]
        avg_away_goals = away_avg_away["scored"]
        avg_home_conceded = home_avg_home["conceded"]
        avg_away_conceded = away_avg_away["conceded"]

        estimated_home = (avg_home_goals + avg_away_conceded) / 2
        estimated_away = (avg_away_goals + avg_home_conceded) / 2

        estimated_home = max(0.5, min(estimated_home, 4.5))
        estimated_away = max(0.5, min(estimated_away, 4.5))

        matrix = self._poisson_score_matrix(estimated_home, estimated_away, 7)

        p_home_win = 0
        p_draw = 0
        p_away_win = 0
        for i in range(8):
            for j in range(8):
                if i > j:
                    p_home_win += matrix[i][j]
                elif i == j:
                    p_draw += matrix[i][j]
                else:
                    p_away_win += matrix[i][j]

        total_probs = {}
        for n in range(8):
            prob = 0
            for i in range(8):
                for j in range(8):
                    if i + j == n:
                        prob += matrix[i][j]
            total_probs[n] = round(prob * 100, 1)

        p_over_05 = sum(total_probs[n] for n in range(1, 8))
        p_over_15 = sum(total_probs[n] for n in range(2, 8))
        p_over_25 = sum(total_probs[n] for n in range(3, 8))
        p_over_35 = sum(total_probs[n] for n in range(4, 8))
        p_over_45 = sum(total_probs[n] for n in range(5, 8))

        p_btts_yes = 0
        for i in range(1, 8):
            for j in range(1, 8):
                p_btts_yes += matrix[i][j]

        most_likely_score = None
        max_prob = 0
        for i in range(7):
            for j in range(7):
                if matrix[i][j] > max_prob:
                    max_prob = matrix[i][j]
                    most_likely_score = f"{i}-{j}"

        most_likely_total = max(total_probs.items(), key=lambda x: x[1])[0]

        expected_total = round(estimated_home + estimated_away, 2)
        expected_home = round(estimated_home, 2)
        expected_away = round(estimated_away, 2)

        h2h_analysis = self._analyze_h2h(result["h2h"], home_teams[0]["name"], away_teams[0]["name"])

        result["analysis"] = {
            "estimated_home_goals": expected_home,
            "estimated_away_goals": expected_away,
            "estimated_total_goals": expected_total,
            "h2h_summary": h2h_analysis,
        }

        result["predictions"] = {
            "score_probable": most_likely_score,
            "confiance_score": round(max_prob * 100, 1),
            "victoire_domicile": round(p_home_win * 100, 1),
            "match_nul": round(p_draw * 100, 1),
            "victoire_exterieur": round(p_away_win * 100, 1),
            "double_chance_1x": round((p_home_win + p_draw) * 100, 1),
            "double_chance_x2": round((p_draw + p_away_win) * 100, 1),
            "double_chance_12": round((p_home_win + p_away_win) * 100, 1),
            "btts_oui": round(p_btts_yes * 100, 1),
            "btts_non": round((1 - p_btts_yes) * 100, 1),
            "over_05": round(p_over_05, 1),
            "over_15": round(p_over_15, 1),
            "over_25": round(p_over_25, 1),
            "over_35": round(p_over_35, 1),
            "over_45": round(p_over_45, 1),
            "under_25": round(100 - p_over_25, 1),
            "under_35": round(100 - p_over_35, 1),
            "total_le_plus_probable": most_likely_total,
            "probas_total": total_probs,
            "recommandation": self._get_recommendation(
                p_home_win, p_draw, p_away_win, p_over_25, p_btts_yes,
                most_likely_score, expected_total
            ),
        }

        return result

    def _analyze_h2h(self, h2h, home_name, away_name):
        if not h2h:
            return "Aucun historique de confrontations directes trouvé."

        total = len(h2h)
        home_wins = 0
        away_wins = 0
        draws = 0
        total_goals = 0

        for m in h2h:
            if m.get("home_goals") is None:
                continue
            total_goals += m["home_goals"] + m["away_goals"]
            if m["home"] == home_name:
                if m["home_goals"] > m["away_goals"]:
                    home_wins += 1
                elif m["home_goals"] < m["away_goals"]:
                    away_wins += 1
                else:
                    draws += 1
            else:
                if m["away_goals"] > m["home_goals"]:
                    home_wins += 1
                elif m["away_goals"] < m["home_goals"]:
                    away_wins += 1
                else:
                    draws += 1

        played = [m for m in h2h if m.get("home_goals") is not None]
        avg_goals = round(total_goals / len(played), 2) if played else 0

        return {
            "total_matchs": total,
            "victoires_domicile": home_wins,
            "nuls": draws,
            "victoires_exterieur": away_wins,
            "moyenne_buts": avg_goals,
        }

    def _get_recommendation(self, p_home, p_draw, p_away, p_over25, p_btts, score, total):
        tips = []

        if p_home > 50:
            tips.append(f"VICTOIRE DOMICILE ({round(p_home)}%)")
        elif p_away > 50:
            tips.append(f"VICTOIRE EXTÉRIEUR ({round(p_away)}%)")
        else:
            tips.append("MATCH OUVERT - prudence")

        if p_over25 > 60:
            tips.append(f"OVER 2.5 (${round(p_over25)}%)")
        elif p_over25 < 40:
            tips.append(f"UNDER 2.5 ({round(100 - p_over25)}%)")

        if p_btts > 60:
            tips.append(f"BTTS OUI ({round(p_btts)}%)")

        if total >= 3.0:
            tips.append("Match riche en buts attendu")
        elif total <= 1.8:
            tips.append("Match fermé attendu")

        tips.append(f"Score le plus probable: {score}")

        return tips
