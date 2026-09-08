@echo off
chcp 65001 >nul
echo ====================================
echo   Bot Pronostics Football
echo ====================================
echo.

REM Verifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python n'est pas installe !
    echo Telecharge Python sur: https://www.python.org/downloads/
    echo COCHE "Add Python to PATH" pendant l'installation.
    pause
    exit /b
)

REM Verifier si .env existe sinon lancer config
if not exist .env (
    echo Configuration initiale necessaire...
    python setup.py
    if errorlevel 1 (
        echo La configuration a echoue. Verifie que Python est installe.
        pause
        exit /b
    )
)

REM Installer les dependances
echo Installation/vérification des dependances...
python -m pip install -r requirements.txt
echo.

REM Lancer le bot
echo Demarrage du bot...
python bot.py
pause