# -*- coding: utf-8 -*-
"""
Emballage du pack de vente "clé en main".
Génère bot-pronostics-VERSION.zip sans secrets ni fichiers internes.
"""
import os
import sys
import io
import zipfile
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
VERSION = datetime.now().strftime("%d-%m-%Y")
OUTPUT = os.path.join(ROOT, f"bot-pronostics-{VERSION}.zip")

# Fichiers à inclure dans le pack de vente
INCLUDE_FILES = [
    "bot.py",
    "analyzer.py",
    "data_collector.py",
    "api_cache.py",
    "daily.py",
    "config.py",
    "setup.py",
    "requirements.txt",
    "Procfile",
    "runtime.txt",
    "README.md",
    "demarrer.bat",
    "run.bat",
    ".env.example",
]

# Secrets/caches/logs qui ne doivent JAMAIS être dans le pack (noms exacts)
FORBIDDEN_FILES = {
    ".env",
    "teams_cache.json",
    "bot_log.txt",
    "bot_err.txt",
}


def main():
    files = []
    for f in INCLUDE_FILES:
        path = os.path.join(ROOT, f)
        if os.path.isfile(path):
            files.append(f)
        else:
            print(f"   (fichier manquant ignoré : {f})")

    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(os.path.join(ROOT, f), arcname=f)

    print(f"Pack créé : {OUTPUT}")
    print(f"{len(files)} fichiers inclus :")
    for f in files:
        size = os.path.getsize(os.path.join(ROOT, f))
        print(f"   - {f} ({size//1024} Ko)")

    # Vérification de sécurité : aucun fichier sensible inclus
    safe = True
    with zipfile.ZipFile(OUTPUT) as zf:
        names = zf.namelist()
        for forbidden in FORBIDDEN_FILES:
            if forbidden in names:
                print(f"ATTENTION : fichier sensible inclus ! {forbidden}")
                safe = False
    if safe:
        print("\nPack securise : aucun fichier sensible inclus.")


if __name__ == "__main__":
    main()