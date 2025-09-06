import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
import psycopg2
import pprint

load_dotenv()

MONGO_URI = os.getenv("DB_URL")
API_KEY = os.getenv("FOOTBALL_API_KEY")
POSTGRES_URI = os.getenv("POSTGRES_DB")

client = MongoClient(MONGO_URI)
db = client["sports_db"]

pg_conn = psycopg2.connect(POSTGRES_URI)
pg_cursor = pg_conn.cursor()

headers = {"x-apisports-key": API_KEY}

pp = pprint.PrettyPrinter(indent=2, width=120)

def get_football_matches(season: int, league: int = 39):
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"league": league, "season": season}
    res = requests.get(url, headers=headers, params=params)
    print("DEBUG Football - Status:", res.status_code)
    try:
        data = res.json()
    except Exception as e:
        print("⚠️ Error al parsear JSON:", e)
        print("Contenido crudo:", res.text[:500])
        return
    
    pp.pprint(data)  # Debug: ver toda la respuesta
    if "response" in data:
        if data["response"]:
            db.football_matches.insert_many(data["response"])
            print(f"Insertados {len(data['response'])} partidos de Football ({season}).")
        else:
            print("⚠️ Football: response vacío")
    else:
        print("⚠️ Error Football:", data)

def get_nba_games(season: str):
    url = "https://v2.nba.api-sports.io/games"
    params = {"season": season}
    res = requests.get(url, headers=headers, params=params)
    print("DEBUG NBA - Status:", res.status_code)
    try:
        data = res.json()
    except Exception as e:
        print("⚠️ Error al parsear JSON:", e)
        print("Contenido crudo:", res.text[:500])
        return
    
    pp.pprint(data)
    if "response" in data:
        if data["response"]:
            db.nba_games.insert_many(data["response"])
            print(f"Insertados {len(data['response'])} partidos de NBA ({season}).")
        else:
            print("⚠️ NBA: response vacío")
    else:
        print("⚠️ Error NBA:", data)

def get_f1_races(season: str):
    url = "https://v1.formula-1.api-sports.io/races"
    params = {"season": season}
    res = requests.get(url, headers=headers, params=params)
    print("DEBUG F1 - Status:", res.status_code)
    try:
        data = res.json()
    except Exception as e:
        print("⚠️ Error al parsear JSON:", e)
        print("Contenido crudo:", res.text[:500])
        return
    
    pp.pprint(data)
    if "response" in data:
        if data["response"]:
            db.f1_races.insert_many(data["response"])
            print(f"Insertadas {len(data['response'])} carreras de F1 ({season}).")
        else:
            print("⚠️ F1: response vacío")
    else:
        print("⚠️ Error F1:", data)

# Example usage:
season = 2022
#get_football_matches(season)
#get_nba_games(str(season))
#get_f1_races(str(season))


def migrate_football():
    matches = list(mongo_db.football_matches.find())
    for match in matches:
        fixture = match.get("fixture", {})
        teams = match.get("teams", {})
        goals = match.get("goals", {})

        pg_cursor.execute("""
            INSERT INTO football_matches (fixture_id, date, venue, home_team, away_team, home_goals, away_goals)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (fixture_id) DO NOTHING;
        """, (
            fixture.get("id"),
            fixture.get("date"),
            fixture.get("venue", {}).get("name"),
            teams.get("home", {}).get("name"),
            teams.get("away", {}).get("name"),
            goals.get("home"),
            goals.get("away"),
        ))
    pg_conn.commit()
    print(f"✅ Migrados {len(matches)} partidos de Football a PostgreSQL")


def migrate_nba():
    games = list(mongo_db.nba_games.find())
    for game in games:
        teams = game.get("teams", {})
        scores = game.get("scores", {})

        pg_cursor.execute("""
            INSERT INTO nba_games (game_id, date, arena, home_team, away_team, home_score, away_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (game_id) DO NOTHING;
        """, (
            game.get("id"),
            game.get("date"),
            game.get("arena"),
            teams.get("home", {}).get("name"),
            teams.get("visitors", {}).get("name"),
            scores.get("home", {}).get("points"),
            scores.get("visitors", {}).get("points"),
        ))
    pg_conn.commit()
    print(f"✅ Migrados {len(games)} partidos de NBA a PostgreSQL")


def migrate_f1():
    races = list(mongo_db.f1_races.find())
    for race in races:
        circuit = race.get("circuit", {})

        pg_cursor.execute("""
            INSERT INTO f1_races (race_id, name, date, circuit_name, location)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (race_id) DO NOTHING;
        """, (
            race.get("id"),
            race.get("name"),
            race.get("date"),
            circuit.get("name"),
            circuit.get("location", {}).get("country"),
        ))
    pg_conn.commit()
    print(f"✅ Migradas {len(races)} carreras de F1 a PostgreSQL")


migrate_football()
migrate_nba()
migrate_f1()
 
client.close()
pg_cursor.close()
pg_conn.close()