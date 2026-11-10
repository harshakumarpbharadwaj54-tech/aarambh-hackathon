from analytics import load_trips, summarize
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from assistant import answer_question


app = FastAPI(title="VehicleGPT")
STATIC_FOLDER = Path(__file__).parent / "static"

app.mount("/static", StaticFiles(directory=STATIC_FOLDER), name="static")


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=300)


@app.get("/")
def home():
    return FileResponse(STATIC_FOLDER / "index.html")


@app.get("/api/health")
@app.get("/api/summary")
def trip_summary():
    trips = load_trips()
    totals = summarize(trips)

    if totals is None:
        return {"trip_count": 0, "period": "No trip records"}

    first_date = min(trip["date"] for trip in trips)
    last_date = max(trip["date"] for trip in trips)
    days_covered = (last_date - first_date).days + 1
    weeks_covered = max(1, (days_covered + 6) // 7)

    return {
        "trip_count": totals["trip_count"],
        "weeks_covered": weeks_covered,
        "distance_km": round(totals["distance_km"], 1),
        "energy_per_100_km": round(totals["energy_per_100_km"], 1),
        "period": f"{first_date} to {last_date}",
    }
def health():
    return {"status": "ready", "assistant": "VehicleGPT", "mode": "offline"}


@app.post("/api/ask")
def ask_vehicle(question: Question):
    return {
        "answer": answer_question(question.question),
        "mode": "offline",
    }