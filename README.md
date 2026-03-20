# REint Wind Generation Dashboard

Full-stack challenge project for comparing UK wind generation actuals against
the latest valid forecast for a selected time range and forecast horizon,
alongside two analysis deliverables:

- forecast error analysis
- wind reliability / dependable capacity recommendation

The system is split into:

- `backend/`: FastAPI service that fetches BMRS data and applies the forecast
  selection rule
- `frontend/`: React + Vite dashboard for querying and visualising the data
- `analysis/`: notebooks and reusable data-preparation code for the analytical
  tasks

## What The App Does

The dashboard lets a user:

- choose a start time
- choose an end time
- choose a forecast horizon from `0` to `48` hours
- compare actual wind generation against the latest forecast that was available
  at least `h` hours before the target time

The frontend calls the backend, the backend fetches BMRS data, selects the
correct forecast per target timestamp, and returns chart-ready JSON.

## Core Business Rule

For each target timestamp `t` and requested horizon `h`:

- find forecasts with the same `startTime = t`
- keep only forecasts where `publishTime <= t - h`
- among those, choose the latest `publishTime`
- if no such forecast exists, keep the actual point and leave the forecast
  value empty

This rule is implemented in the backend and mirrored in the analysis pipeline.

## Data Sources

### Actual generation

BMRS dataset: `FUELHH`

Relevant fields:

- `startTime`: target / delivery timestamp at 30-minute resolution
- `fuelType`: filtered to `WIND`
- `generation`: actual wind generation in MW

### Forecast generation

BMRS dataset: `WINDFOR`

Relevant fields:

- `startTime`: forecast target / delivery timestamp
- `publishTime`: forecast creation timestamp
- `generation`: forecast wind generation in MW

Applied constraints:

- use data from January 2025 onward
- keep forecasts only where horizon is between `0` and `48` hours
- ignore missing forecasts instead of filling or interpolating them

## Repository Structure

```text
.
├── analysis/
│   ├── 01_forecast_error_analysis.ipynb
│   ├── 02_wind_reliability_recommendation.ipynb
│   ├── create_notebooks.py
│   ├── data/
│   ├── fetch_data/
│   └── requirements.txt
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── routes/
│   │   └── services/
│   ├── .env.example
│   ├── .python-version
│   ├── index.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── styles/
|   |   ├── app.jsx
|   |   └── main.jsx
│   ├── .env.example
│   └── package.json
├── Makefile
└── README.md
```

## Architecture

### Frontend

The frontend is a React + Vite single-page application.

Responsibilities:

- collect user input for time range and forecast horizon
- call the backend `/generation` endpoint
- render the resulting actual and forecast series on a line chart
- show empty, loading, and error states

Time handling:

- form inputs are `datetime-local`
- selected values are converted to UTC before the API request
- chart labels and tooltips are rendered in UTC so they align with backend and
  analysis outputs


### Backend

The backend is a FastAPI service deployed separately from the frontend.

Responsibilities:

- validate request parameters
- fetch actual wind data from BMRS
- fetch forecast wind data from BMRS
- enforce the `0-48` hour forecast-horizon rule
- select the latest valid forecast per target time
- return chart-ready JSON for the frontend

### Analysis

The analysis area contains:

- a reusable fetch / clean / join pipeline
- a notebook for forecast error analysis
- a notebook for wind reliability recommendation

The notebooks are backed by code in `analysis/fetch_data/` so the logic is not
buried in ad hoc notebook cells.


## Backend API

### `GET /health`

Health check endpoint.

Example response:

```json
{"status":"ok"}
```

### `GET /generation`

Query parameters:

- `start_time`: ISO datetime
- `end_time`: ISO datetime
- `forecast_horizon_hours`: integer from `0` to `48`

Example:

```text
/generation?start_time=2025-01-01T00:00:00Z&end_time=2025-01-02T00:00:00Z&forecast_horizon_hours=4
```

Response shape:

- `meta`: request metadata and selection-window info
- `actual_count`: number of actual rows fetched
- `forecast_count`: number of forecast rows fetched
- `matched_count`: number of actual timestamps returned
- `matched_forecast_count`: number of timestamps with a valid forecast match
- `data`: chart rows with:
  - `startTime`
  - `actualGeneration`
  - `forecastGeneration`

## Local Setup

### Prerequisites

- Python `3.13`
- Node.js `18+`
- npm

### Backend setup

```bash
source venv/bin/activate
pip install -r backend/requirements.txt
```

Run the backend:

```bash
cd backend
../venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend setup

```bash
cd frontend
npm install
```

Run the frontend:

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

### Analysis setup

```bash
source venv/bin/activate
pip install -r analysis/requirements.txt
```

Generate analysis datasets:

```bash
python analysis/fetch_data/pipeline.py
```

Regenerate notebooks from the notebook builder:

```bash
python analysis/create_notebooks.py
```

Then open the notebooks in JupyterLab or VS Code and run them.

### Makefile shortcuts

From the repository root:

```bash
make backend
make frontend
make dev
```

## Environment Variables

### Backend

Defined in backend/.env.example

- `CORS_ALLOWED_ORIGINS`
- `CORS_ALLOWED_ORIGIN_REGEX`

Typical local value:

```text
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

### Frontend

Defined in frontend/.env.example

- `VITE_API_BASE_URL`

Typical local value:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Deployment

This repository is deployed to Vercel as two separate projects:

- backend project with root directory `backend`
- frontend project with root directory `frontend`

Deployment sequence:

1. deploy backend
2. copy backend URL
3. configure frontend `VITE_API_BASE_URL`
4. deploy frontend
5. update backend CORS to the final frontend URL if needed

See VERCEL_DEPLOYMENT.md for
the exact setup.

## Analysis Deliverables

The analysis portion is intentionally separate from the live application.

Deliverables:

- `01_forecast_error_analysis.ipynb`
- `02_wind_reliability_recommendation.ipynb`

### Analysis pipeline

The reusable pipeline performs three stages:

1. fetch raw BMRS actual and forecast data
2. clean and standardise the raw fields into a common schema
3. build joined datasets using the same forecast-selection rule as the backend

The default outputs are saved into `analysis/data/`:

- `actuals.csv`
- `forecasts.csv`
- `joined_forecasts_actuals.csv`

If `pyarrow` is available, matching parquet files can also be written.

### Forecast error analysis

Purpose:

- quantify signed forecast error
- quantify absolute forecast error
- understand how error changes with forecast horizon
- understand whether certain times of day are harder to forecast

Current notebook structure:

- load cached prepared data or optionally rebuild it
- calculate overall summary metrics
- calculate summary metrics by horizon
- calculate summary metrics by hour of day
- visualise error trends
- document interpretation prompts for final written conclusions

### Wind reliability recommendation

Purpose:

- analyse the historical distribution of actual wind output
- estimate a conservative dependable MW value
- support the recommendation with explicit reasoning rather than a single
  unexplained statistic

Current notebook structure:

- load cached actual generation data or optionally rebuild it
- inspect overall generation distribution
- compare low-end percentiles by month
- derive a conservative recommendation based on the weakest monthly low-end
  percentile
- document limitations and assumptions

## Analysis Reasoning Expectations

The problem statement explicitly asks for first-principles analytical thinking
and clear documentation of reasoning.

This repository is set up to support that expectation, not to hide it.

For the analysis portion, the intended standard is:

- document each transformation step clearly
- explain why each metric is being used
- state assumptions explicitly
- discuss trade-offs instead of implying a single obvious answer
- connect conclusions back to the underlying data behaviour
- show the path from raw data to recommendation



## Assumptions And Trade-Offs

### Shared assumptions

- BMRS timestamps are interpreted in UTC
- `startTime` is treated as the target time for both actuals and forecasts
- forecasts outside the `0-48` hour horizon window are out of scope
- missing forecasts are left missing rather than filled

### Backend trade-offs

- the backend fetches forecasts across the full valid `48`-hour lookback window
  so early points in a requested range do not miss valid older forecasts
- the response keeps actual rows even when no matching forecast exists so the
  frontend can show gaps correctly
- lightweight in-memory processing was preferred over adding a persistence layer
  at this stage

### Analysis trade-offs

- CSV is the default persisted output because it works even without parquet
  dependencies
- parquet is optional for better performance when `pyarrow` is installed
- notebook generation is script-driven so structure is reproducible, but
  interpretive commentary still belongs in the notebooks themselves

## Current Status

Implemented:

- responsive frontend with controls and chart
- FastAPI backend with BMRS integration
- aligned forecast-selection logic between backend and analysis
- UTC-safe frontend timestamp display
- Vercel deployment setup for frontend and backend
- reusable analysis pipeline
- notebook deliverable scaffolding for both analysis tasks

Not yet fully complete:

- richer notebook commentary and final written analytical conclusions
- automated tests for backend and analysis logic
- final submission assets such as demo video and packaged archive


### AI usage disclosure for analysis

The challenge requirement says AI can be used for low-level help only, such as:

- fixing bugs
- giving the final touch(including the documentation)
- handling library usage
- Almost half of the frontend is completed through use of AI 
- improving implementation details

## Notes

- Generated analysis datasets are ignored in Git by default.
- The chart displays times in UTC so they match backend and analysis outputs.
- If values differ between the app and analysis, first compare the same UTC
  timestamp and the same horizon before investigating logic.
