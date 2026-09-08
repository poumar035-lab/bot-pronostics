# -*- coding: utf-8 -*-
"""Pronos du jour + abonnés pour le push quotidien."""
import json
import os
import datetime
from analyzer import MatchAnalyzer

SUBSCRIBERS_FILE = "subscribers.json"


def load_subscribers():
    try:
        with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_subscribers(subscribers):
    with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(subscribers, f)


def is_subscribed(chat_id):
    return str(chat_id) in [str(s) for s in load_subscribers()]


def add_subscriber(chat_id, username=""):
    subs = [str(s) for s in load_subscribers()]
    if str(chat_id) not in subs:
        subs.append(str(chat_id))
        save_subscribers(subs)
        return True
    return False


def remove_subscriber(chat_id):
    subs = [str(s) for s in load_subscribers()]
    if str(chat_id) in subs:
        subs.remove(str(chat_id))
        save_subscribers(subs)
        return True
    return False


def get_todays_matches():
    from data_collector import FootballDataCollector
    collector = FootballDataCollector()
    matches = collector.get_upcoming_matches(days_ahead=1)
    return matches


def build_daily_prediction():
    """Analyse le principal match du jour et renvoie le texte du prono."""
    analyzer = MatchAnalyzer()
    matches = get_todays_matches()
    if isinstance(matches, dict) and "error" in matches:
        return None, None
    if not matches:
        return None, None

    # On prend le premier match à venir (le + important / proche)
    match = matches[0]
    home_name = match["home"]
    away_name = match["away"]

    result = analyzer.analyze_match(home_name, away_name)
    if result.get("errors"):
        return None, None
    return format_daily_prediction(result), result

def format_daily_prediction(result):
    pred = result["predictions"]
    analysis = result["analysis"]
    home = result["home_stats"]
    away = result["away_stats"]

    lines = [
        "🔥 PRONO DU JOUR 🔥",
        "═══════════════════════════════",
        f"🏟️ {home.get('name', result['home_team'])} vs {away.get('name', result['away_team'])}",
        "═══════════════════════════════",
        "",
        f"🎯 Score prédit : {pred.get('score_probable', 'N/A')} ({pred.get('confiance_score', 0)}%)",
        f"⚽ Buts attendus : {analysis.get('estimated_home_goals', '?')} - {analysis.get('estimated_away_goals', '?')}",
        f"   Total : ~{analysis.get('estimated_total_goals', '?')}",
        f"🏆 Victoire : Dom {pred.get('victoire_domicile', 0)}% | Nul {pred.get('match_nul', 0)}% | Ext {pred.get('victoire_exterieur', 0)}%",
        f"🔀 Double chance : {pred.get('double_chance_1x', 0)}% (1X) / {pred.get('double_chance_12', 0)}% (12)",
        f"⚽ BTTS Oui : {pred.get('btts_oui', 0)}%",
        f"📈 Over 2.5 : {pred.get('over_25', 0)}% | Under 2.5 : {pred.get('under_25', 0)}%",
        "",
        "💡 RECO :",
    ]
    for tip in pred.get("recommandation", []):
        lines.append(f"   ✅ {tip}")
    lines.append("")
    lines.append("⚠️ Joue responsable. Prono indicatif.")
    return "\n".join(lines)


def next_run(hour, minute, tz_name="UTC"):
    """Prochain déclenchement du push quotidien (texte lisible)."""
    now = datetime.datetime.now(datetime.timezone.utc)
    today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if today <= now:
        today += datetime.timedelta(days=1)
    return today.strftime("%d/%m à %H:%M UTC")