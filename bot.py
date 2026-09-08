import sys
import io
import logging

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from analyzer import MatchAnalyzer
from data_collector import FootballDataCollector
from config import TELEGRAM_TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

analyzer = MatchAnalyzer()
collector = FootballDataCollector()


def format_prediction(result):
    if result.get("errors"):
        return "❌ Erreurs:\n" + "\n".join(result["errors"])

    pred = result["predictions"]
    analysis = result["analysis"]
    home = result["home_stats"]
    away = result["away_stats"]
    h2h = analysis.get("h2h_summary", "")

    msg = f"⚽ {'='*35}\n"
    msg += f"  {result['home_team']} vs {result['away_team']}\n"
    msg += f"{'='*35}\n\n"

    msg += f"📊 STATISTIQUES\n"
    msg += f"{'─'*35}\n"
    msg += f"🏠 {home.get('name', 'N/A')}\n"
    if home.get("position"):
        msg += f"   Position: {home['position']}e | Points: {home.get('points', 'N/A')}\n"
    msg += f"   Buts marqués/match (dom): {home.get('avg_goals_scored_home', 'N/A')}\n"
    msg += f"   Buts encaissés/match (dom): {home.get('avg_goals_conceded_home', 'N/A')}\n"
    msg += f"   Forme: {home.get('last_5_form', 'N/A')}\n"
    if home.get("won") is not None:
        msg += f"   V/N/D: {home['won']}/{home.get('draw', 0)}/{home.get('lost', 0)}\n"
    msg += f"\n✈️ {away.get('name', 'N/A')}\n"
    if away.get("position"):
        msg += f"   Position: {away['position']}e | Points: {away.get('points', 'N/A')}\n"
    msg += f"   Buts marqués/match (ext): {away.get('avg_goals_scored_away', 'N/A')}\n"
    msg += f"   Buts encaissés/match (ext): {away.get('avg_goals_conceded_away', 'N/A')}\n"
    msg += f"   Forme: {away.get('last_5_form', 'N/A')}\n"
    if away.get("won") is not None:
        msg += f"   V/N/D: {away['won']}/{away.get('draw', 0)}/{away.get('lost', 0)}\n"

    if h2h and isinstance(h2h, dict):
        msg += f"\n🤝 CONFRONTATIONS DIRECTES\n"
        msg += f"{'─'*35}\n"
        msg += f"   Matchs joués: {h2h.get('total_matchs', 0)}\n"
        msg += f"   V {home.get('short_name', 'DOM')}: {h2h.get('victoires_domicile', 0)} | "
        msg += f"Nuls: {h2h.get('nuls', 0)} | "
        msg += f"V {away.get('short_name', 'EXT')}: {h2h.get('victoires_exterieur', 0)}\n"
        msg += f"   Moyenne buts: {h2h.get('moyenne_buts', 'N/A')}\n"

    msg += f"\n🎯 PRÉDICTIONS\n"
    msg += f"{'─'*35}\n"
    msg += f"📊 Buts estimés: {analysis.get('estimated_home_goals', '?')} - {analysis.get('estimated_away_goals', '?')}\n"
    msg += f"   (Total attendu: ~{analysis.get('estimated_total_goals', '?')} buts)\n\n"
    msg += f"🏆 Score le plus probable: {pred.get('score_probable', 'N/A')}\n"
    msg += f"   Confiance: {pred.get('confiance_score', 0)}%\n\n"

    msg += f"📈 PROBABILITÉS\n"
    msg += f"{'─'*35}\n"
    msg += f"   🏠 Victoire domicile: {pred.get('victoire_domicile', 0)}%\n"
    msg += f"   🤝 Match nul: {pred.get('match_nul', 0)}%\n"
    msg += f"   ✈️ Victoire extérieur: {pred.get('victoire_exterieur', 0)}%\n\n"

    msg += f"🔀 DOUBLE CHANCE\n"
    msg += f"{'─'*35}\n"
    msg += f"   1X (dom ou nul): {pred.get('double_chance_1x', 0)}%\n"
    msg += f"   X2 (nul ou ext): {pred.get('double_chance_x2', 0)}%\n"
    msg += f"   12 (pas de nul): {pred.get('double_chance_12', 0)}%\n\n"

    msg += f"⚽ BTTS (Les 2 équipes marquent)\n"
    msg += f"{'─'*35}\n"
    msg += f"   OUI: {pred.get('btts_oui', 0)}%\n"
    msg += f"   NON: {pred.get('btts_non', 0)}%\n\n"

    msg += f"📊 OVER / UNDER\n"
    msg += f"{'─'*35}\n"
    msg += f"   Over 0.5: {pred.get('over_05', 0)}%\n"
    msg += f"   Over 1.5: {pred.get('over_15', 0)}%\n"
    msg += f"   Over 2.5: {pred.get('over_25', 0)}%\n"
    msg += f"   Over 3.5: {pred.get('over_35', 0)}%\n"
    msg += f"   Over 4.5: {pred.get('over_45', 0)}%\n"
    msg += f"   Under 2.5: {pred.get('under_25', 0)}%\n"
    msg += f"   Under 3.5: {pred.get('under_35', 0)}%\n\n"

    msg += f"🎲 PROBABILITÉS PAR SCORE\n"
    msg += f"{'─'*35}\n"
    probas = pred.get("probas_total", {})
    for n in range(6):
        if n in probas:
            msg += f"   {n} buts: {probas[n]}%\n"

    msg += f"\n💡 RECOMMANDATIONS\n"
    msg += f"{'─'*35}\n"
    for tip in pred.get("recommandation", []):
        msg += f"   ✅ {tip}\n"

    msg += f"\n{'='*35}\n"
    msg += f"⚠️ Pronostic indicatif. Joue responsable.\n"

    return msg


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import BOT_NAME
    welcome = (
        f"⚽ {BOT_NAME} ⚽\n\n"
        "Salut ! Envoie-moi un match et je te donne les pronostics détaillés.\n\n"
        "📋 Comment ça marche:\n"
        "   Envoie: NomEquipe1 vs NomEquipe2\n"
        "   Exemple: PSG vs Marseille\n\n"
        "🔧 Commandes:\n"
        "   /start - Afficher ce message\n"
        "   /matchs - Voir les prochains matchs\n"
        "   /help - Aide\n"
        "   /legues - Lire les ligues disponibles\n\n"
        "⚠️ Les pronostics sont basés sur des stats et du calcul.\n"
        "Ils ne garantissent aucun gain."
    )
    await update.message.reply_text(welcome)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📋 Comment prédire un match:\n\n"
        "1. Envoie le nom des 2 équipes séparées par 'vs':\n"
        "   Exemple: Real Madrid vs Barcelona\n\n"
        "2. Le bot analyse:\n"
        "   - Historique des matchs\n"
        "   - Buts marqués/encaissés\n"
        "   - Forme récente (5 derniers)\n"
        "   - Confrontations directes\n"
        "   - Classement\n\n"
        "3. Tu reçois un prono détaillé avec:\n"
        "   - Score probable\n"
        "   - % de victoire/nul/défaite\n"
        "   - Over/Under\n"
        "   - BTTS\n"
        "   - Double chance\n"
        "   - Recommandation\n\n"
        "💡 Conseil: Utilise les noms en anglais pour plus de précision.\n"
        "Ex: 'Manchester United' plutôt que 'Man Utd'"
    )
    await update.message.reply_text(help_text)


async def legues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import LEAGUES
    msg = "🏆 LIGUES DISPONIBLES:\n\n"
    for name, lid in LEAGUES.items():
        msg += f"   • {name.title()} (ID: {lid})\n"
    msg += "\n💡 Utilise /matchs <nom_ligue> pour voir les prochains matchs"
    await update.message.reply_text(msg)


async def matchs_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_text = update.message.text.replace("/matchs", "").strip()

    league_id = None
    if msg_text:
        from config import LEAGUES
        league_lower = msg_text.lower()
        for name, lid in LEAGUES.items():
            if league_lower in name or name in league_lower:
                league_id = lid
                break

    matches = collector.get_upcoming_matches(league_id=league_id, days_ahead=7)

    if isinstance(matches, dict) and "error" in matches:
        await update.message.reply_text(f"❌ {matches['error']}")
        return

    if not matches:
        await update.message.reply_text("Aucun match trouvé pour cette période.")
        return

    msg = f"📅 PROCHAINS MATCHS ({len(matches)} trouvés)\n{'─'*35}\n\n"
    for m in matches[:20]:
        date = m.get("date", "")[:10]
        comp = m.get("competition", "")
        msg += f"📆 {date}\n"
        msg += f"   🏠 {m['home']} vs {m['away']} ✈️\n"
        msg += f"   🏆 {comp}\n\n"

    msg += "💡 Envoie un match pour obtenir le pronostic:\n"
    msg += "Ex: PSG vs Marseille"
    await update.message.reply_text(msg)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "vs" not in text.lower():
        await update.message.reply_text(
            "Format incorrect.\n\n"
            "Envoie: NomEquipe1 vs NomEquipe2\n"
            "Exemple: PSG vs Marseille\n\n"
            "Utilise /help pour plus d'infos."
        )
        return

    parts = text.lower().split("vs")
    if len(parts) != 2:
        await update.message.reply_text("Format: Equipe1 vs Equipe2")
        return

    home_name = parts[0].strip()
    away_name = parts[1].strip()

    if not home_name or not away_name:
        await update.message.reply_text("Donne les noms des 2 équipes.")
        return

    await update.message.reply_text(
        f"🔍 Analyse en cours...\n"
        f"   {home_name.title()} vs {away_name.title()}\n"
        f"   ⏳ Récupération des données..."
    )

    try:
        result = analyzer.analyze_match(home_name, away_name)
        msg = format_prediction(result)

        if len(msg) > 4000:
            for i in range(0, len(msg), 4000):
                await update.message.reply_text(msg[i:i+4000])
        else:
            await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"❌ Erreur: {str(e)}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Erreur: {context.error}")
    if update and update.message:
        await update.message.reply_text("❌ Une erreur est survenue. Réessaie.")


def main():
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN manquant dans .env")
        print("Crée un bot via @BotFather sur Telegram et mets le token dans .env")
        return

    logger.info("Bot Pronostics en cours de démarrage...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("legues", legues))
    app.add_handler(CommandHandler("matchs", matchs_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("Bot démarré ! Envoie /start sur Telegram.")
    app.run_polling()
    logger.info("Bot arrêté. Redémarrage automatique dans 5s...")


if __name__ == "__main__":
    main()
