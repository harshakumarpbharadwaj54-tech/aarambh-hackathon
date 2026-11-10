# VehicleGPT

VehicleGPT is a local vehicle-insights demo. It reads sample trip records from a CSV file, stores them in SQLite, calculates trip and energy-use summaries, and answers supported questions through a small web interface. A locally hosted, OpenAI-compatible language-model service can turn the calculated results into a short explanation.

> **Current prototype scope:** This repository uses simulated trip data. It does not currently connect to a vehicle CAN bus, SOME/IP, Android Vehicle HAL, QNX, ADAS, or diagnostic hardware. The language-model server and its model files are separate from this repository.

## Project files

```text
VehicleGPT/
├── README.md
├── data/
│   ├── trips.csv          # Sample trip records used to seed the database
│   └── vehiclegpt.db      # Local SQLite database
└── src/
    ├── app.py             # FastAPI application and HTTP endpoints
    ├── assistant.py       # Question handling and local model request
    ├── analytics.py       # Trip summaries and period comparisons
    ├── storage.py         # SQLite creation, CSV import, and trip loading
    └── static/
        ├── index.html     # Web interface
        ├── app.js         # Browser-side requests and display updates
        └── styles.css     # Web interface styling
```

## What the database contains

`data/vehiclegpt.db` is a SQLite database with a `trips` table. The current database contains eight sample trip records. The table fields are:

| Field            | Meaning                                              |
| ---------------- | ---------------------------------------------------- |
| `trip_id`        | Unique trip identifier and primary key               |
| `date`           | Trip date in `YYYY-MM-DD` format                     |
| `trip_type`      | Trip category, such as `city` or `highway`           |
| `distance_km`    | Trip distance in kilometres                          |
| `energy_kwh`     | Energy used during the trip, in kilowatt-hours       |
| `ambient_temp_c` | Ambient temperature in degrees Celsius; may be empty |
| `battery_temp_c` | Battery temperature in degrees Celsius; may be empty |
| `event`          | Event label associated with the trip; may be empty   |

`src/storage.py` creates the table if needed and imports rows from `data/trips.csv` using `INSERT OR IGNORE`. This means the app can populate a new database from the CSV, and repeated loads will not duplicate rows whose `trip_id` already exists. The CSV is the sample-data source; the database is the local query store.

## Run from VS Code

Open the `VehicleGPT` folder in VS Code, then open a PowerShell terminal in that folder. Create and activate a virtual environment, and install the app dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install fastapi uvicorn pydantic
```

Start the web application from the `src` folder:

```powershell
cd src
uvicorn app:app --reload
```

Open <http://127.0.0.1:8000> in a browser. Use `Ctrl+C` in the terminal to stop the development server.

## Local language-model service

The web app and its data processing run locally. For generated explanations, `src/assistant.py` sends requests to this loopback endpoint:

```text
http://127.0.0.1:8081/v1/chat/completions
```

The service must accept an OpenAI-compatible chat-completions request and recognize the model name `local-model` (or the value configured in `assistant.py`). Start that service separately before asking questions. This repository does not include model weights or a model-server launcher. If the service is unavailable, VehicleGPT returns the locally calculated figures with a message that the model could not be reached.

## Supported API routes

- `GET /` serves the VehicleGPT web interface.
- `GET /api/summary` returns trip count, date coverage, total distance, and average energy use per 100 km.
- `POST /api/ask` accepts a JSON body such as `{"question":"Compare recent and earlier energy use"}` and returns an answer in offline mode.
- `GET /docs` opens FastAPI's interactive API documentation while the server is running.

The question handler currently recognizes questions containing `range`, `energy`, `consumption`, or `efficiency`. Its comparison uses the latest 14 days of available trips and the preceding 14-day period. Other question types are not analyzed yet.

## Calculations and answer limits

The analytics code calculates total distance and energy, average trip length, city-trip share, and energy use in kWh per 100 km. For supported questions, it compares recent and earlier periods. The local language model is instructed to explain those calculated values and avoid claiming causes that the records do not prove.

The sample contains only trip-level records, so it cannot answer event-sequence questions such as what occurred immediately before a warning unless those events are added to the data model and query logic. The current demo also has no direct camera-feed or vehicle-network ingestion.

## Privacy and safety

The demo uses local sample data and contacts the model service through `127.0.0.1`. It does not include vehicle-control commands or interfaces. Treat this as a prototype: production deployment would need authenticated data adapters, access controls, retention policy, security review, and a formally isolated read-only path from safety-critical vehicle networks.
