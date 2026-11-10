import csv
import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
DATABASE_FILE = PROJECT_FOLDER / "data" / "vehiclegpt.db"
CSV_FILE = PROJECT_FOLDER / "data" / "trips.csv"


def initialize_database():
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(DATABASE_FILE)) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS trips (
                    trip_id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    trip_type TEXT NOT NULL,
                    distance_km REAL NOT NULL,
                    energy_kwh REAL NOT NULL,
                    ambient_temp_c REAL,
                    battery_temp_c REAL,
                    event TEXT
                )
            """)

            if CSV_FILE.exists():
                with CSV_FILE.open(
                    newline="",
                    encoding="utf-8",
                ) as csv_file:
                    for row in csv.DictReader(csv_file):
                        connection.execute("""
                            INSERT OR IGNORE INTO trips
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            row["trip_id"],
                            row["date"],
                            row["trip_type"],
                            float(row["distance_km"]),
                            float(row["energy_kwh"]),
                            float(row["ambient_temp_c"]),
                            float(row["battery_temp_c"]),
                            row["event"],
                        ))


def load_trips():
    initialize_database()

    with closing(sqlite3.connect(DATABASE_FILE)) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("""
            SELECT *
            FROM trips
            ORDER BY date
        """).fetchall()

    trips = []

    for row in rows:
        trip = dict(row)
        trip["date"] = date.fromisoformat(trip["date"])
        trips.append(trip)

    return trips