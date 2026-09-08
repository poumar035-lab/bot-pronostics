@echo off
echo ====================================
echo   Bot Pronostics Football
echo ====================================
echo.

REM Verifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python n'est pas installe !
    telecharge Python depuis: https://www.python.org/downloads/
    pause
    exit /b
)

REM Installer les dependances
echo Installation des dependances...
pip install -r requirements.txt
echo.

REM Verifier .env
if not exist .env (
    echo Fichier .env manquant !
    echo Copie .env.example en .env et remplis les cles.
    pause
    exit /b
)

REM Lancer le bot
echo Demarrage du bot...
python bot.py
pause
