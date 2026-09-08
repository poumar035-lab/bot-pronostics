# ⚽ Bot Pronostics Football — Clé en Main

Bot Telegram intelligent d'**analyse et pronostics football** basé sur des statistiques réelles et un modèle mathématique (loi de Poisson).

---

## ✨ Ce que le bot fait

Envoyez un match, il analyse **tout** et renvoie en quelques secondes :

| Fonction | Détail |
|----------|--------|
| 📊 **Score prédit** | Ex : 2-1 avec % de confiance |
| 🏠 **Buts équipe domicile** | Estimation précise |
| ✈️ **Buts équipe extérieur** | Estimation précise |
| ⚽ **Total de buts attendu** | Ex : ~2.6 buts |
| 🏆 **Vainqueur probable** | % victoire / nul / défaite |
| 🔀 **Double chance** | 1X, X2, 12 |
| 📈 **Over/Under** | 0.5 à 4.5 buts |
| 🎯 **BTTS** | Les deux équipes marquent ? |
| 🤝 **Confrontations directes** | Historique H2H |
| 🧠 **Forme des équipes** | Derniers matchs, V/N/D |
| 🏅 **Classement** | Position, points, buts |
| 💡 **Recommandation** | Conseils basés sur les stats |

---

## 🖥️ Commandes

- `/start` — Accueil
- `/help` — Guide d'utilisation
- `/matchs` — Prochains matchs (option: `/matchs ligue 1`)
- `/legues` — Ligues disponibles

---

## 📦 Contenu du pack

```
bot-pronostics/
├── bot.py              → Le bot Telegram
├── analyzer.py         → Moteur de prédiction (modèle Poisson)
├── data_collector.py   → Collecte de données temps réel
├── config.py           → Configuration
├── setup.py            → Assistant d'installation (guide pas à pas)
├── demarrer.bat        → Lanceur ONE-CLICK (Windows)
├── requirements.txt    → Dépendances
└── .env.example        → Exemple de configuration
```

---

## 🚀 Installation (2 minutes, aucune compétence requise)

### Étape 1 — Installer Python
1. Télécharge Python : **python.org/downloads**
2. Pendant l'installation, COCHE **"Add Python to PATH"** ✅

### Étape 2 — Lancer la configuration
1. Double-clique sur **`demarrer.bat`**
2. L'assistant te guide pour créer ton bot (2 étapes simples)

### Étape 3 — C'est prêt !
1. Sur Telegram, cherche ton bot et envoie `/start`
2. Envoie un match : **PSG vs Marseille**
3. Reçois ton pronostic détaillé instantanément ✅

---

## 🔑 Compte gratuit requis

| Service | Où ? | Coût |
|---------|------|------|
| **BotFather** (Telegram) | @BotFather | Gratuit |
| **Football-Data.org** | football-data.org/client/register | Gratuit |
| **Python** | python.org | Gratuit |

Rien d'autre. Aucun abonnement caché.

---

## 📲 Mode 24h/24 (optionnel)

Le bot tourne en local (gratuit). Pour le faire tourner **en ligne 24h/24** (sans PC allumé) :
- **Railway.app** — gratuit au démarrage (guide fourni sur demande)

---

## ❌ Ce que le bot N'est PAS

- Ce n'est pas une garantie de gains
- C'est un **outil d'analyse** basé sur des statistiques et des probabilités
- Aucun système ne prévoit le sport à 100%

> Jouez de manière responsable. Ne pariez jamais l'argent que vous ne pouvez pas perdre.

---

## ⚙️ Personnalisation

Modifiable dans `.env` :
| Variable | Rôle |
|----------|------|
| `BOT_NAME` | Nom affiché du bot |
| `TELEGRAM_TOKEN` | Token du bot |
| `FOOTBALL_API_KEY` | Clé API données football |

---

## 🛠️ Support & accompagnement inclus

- Installation assistée offerte
- Mises à jour disponibles