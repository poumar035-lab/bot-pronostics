# -*- coding: utf-8 -*-
import os
import requests
import sys


def input_utf8(prompt):
    if sys.version_info >= (3, 0):
        return input(prompt)
    return raw_input(prompt)


def save_env(config):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    lines = []
    for key, value in config.items():
        lines.append(f"{key}={value}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n✅ Fichier .env créé avec succès : {path}")


def test_telegram_token(token):
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{token}/getMe", timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            if data.get("ok"):
                bot_info = data["result"]
                print(
                    f"   ✅ Bot vérifié : @{bot_info.get('username', '?')} "
                    f"({bot_info.get('first_name', '?')})"
                )
                return True
        print("   ❌ Token invalide ou bot introuvable.")
        return False
    except Exception as e:
        print(f"   ❌ Erreur de connexion : {e}")
        return False


def test_football_api(token):
    try:
        r = requests.get(
            "https://api.football-data.org/v4/competitions/2001/teams",
            headers={"X-Auth-Token": token},
            timeout=10,
        )
        if r.status_code == 200:
            print("   ✅ Clé API football validée (Champions League OK)")
            return True
        elif r.status_code == 403:
            print("   ❌ Clé API invalide (403 Forbidden)")
            return False
        else:
            print(f"   ⚠️ Réponse inattendue ({r.status_code}), mais on continue")
            return True
    except Exception as e:
        print(f"   ❌ Erreur de connexion : {e}")
        return False


def main():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass

    print("=" * 55)
    print("  ⚽ BOT PRONOSTICS FOOTBALL - CONFIGURATION")
    print("  Prépare ton bot en 2 minutes")
    print("=" * 55)
    print()

    config = {}

    # Étape 1 : nom du bot
    print("📛 ÉTAPE 1/3 - NOM DU BOT")
    print("-" * 55)
    print("C'est le nom affiché aux utilisateurs.")
    default_name = os.getenv("BOT_NAME", "Toshiba Prono")
    name = input_utf8(f"Nom du bot (ENTREE pour '{default_name}') : ").strip()
    config["BOT_NAME"] = name if name else default_name
    print()

    # Étape 2 : token Telegram
    print("🔑 ÉTAPE 2/3 - TOKEN TELEGRAM")
    print("-" * 55)
    print("Comment obtenir ton token :")
    print("   1. Ouvre Telegram et cherche @BotFather")
    print("   2. Envoie /newbot et suis les instructions")
    print("   3. Copie le token (format: 123456:ABC-DEF...)\n")

    while True:
        token = input_utf8("Token Telegram : ").strip()
        if not token:
            print("   ❌ Token vide. Réessaie.")
            continue
        if test_telegram_token(token):
            config["TELEGRAM_TOKEN"] = token
            break
        print("   Essaie de copier le token exactement.")
    print()

    # Étape 3 : clé API football
    print("🔑 ÉTAPE 3/3 - CLÉ API FOOTBALL-DATA.ORG")
    print("-" * 55)
    print("Comment obtenir ta clé (gratuite) :")
    print("   1. Va sur https://www.football-data.org/client/register")
    print("   2. Crée un compte (tu reçois la clé par email)")
    print("   3. Copie-la ici\n")

    while True:
        api_key = input_utf8("Clé API Football-Data : ").strip()
        if not api_key:
            print("   ❌ Clé vide. Réessaie.")
            continue
        if test_football_api(api_key):
            config["FOOTBALL_API_KEY"] = api_key
            break
        print("   Essaie de copier la clé exactement.")
    print()

    print("=== ENREGISTREMENT ===")
    print("-" * 55)
    save_env(config)
    print()

    print("=" * 55)
    print("  ✅ CONFIGURATION TERMINÉE !")
    print("=" * 55)
    print("  Pour lancer ton bot :")
    print("     • Clique sur 'demarrer.bat' ")
    print("     • Ou tape : python bot.py")
    print()
    print("  Ensuite sur Telegram :")
    print("     • Cherche ton bot et envoie /start")
    print()
    print("  ⚠️ Joue toujours de manière responsable.")
    print()


if __name__ == "__main__":
    main()