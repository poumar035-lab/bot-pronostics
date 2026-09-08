import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY", "")

FOOTBALL_API_BASE = "https://api.football-data.org/v4"

LEAGUES = {
    "ligue 1": 2015,
    "premier league": 2021,
    "la liga": 2014,
    "serie a": 2019,
    "bundesliga": 2002,
    "champions league": 2001,
    "europa league": 2146,
    "eredivisie": 2003,
    "primeira liga": 2017,
    "super lig": 2018,
    "serie a brésil": 2013,
    "mls": 2016,
    "world cup": 2000,
    "euro": 2018,
    "ligue des champions": 2001,
    "coupe du monde": 2000,
}

HEADERS = {"X-Auth-Token": FOOTBALL_API_KEY}
