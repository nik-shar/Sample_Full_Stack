# REint Wind Generation Dashboard

Full-stack challenge project for comparing UK wind generation actuals against
the latest valid forecast for a selected time range and forecast horizon.

## Current repo contents

- `backend/`: FastAPI API that fetches BMRS actual and forecast wind data and
  applies the forecast-selection rule.
- `frontend/`: React + Vite UI with time-range controls and a time-series chart.
- `ROADMAP.md`: delivery plan for the wider challenge scope.
- `VERCEL_DEPLOYMENT.md`: deployment notes for separate frontend and backend
  Vercel projects.

## How it works

The frontend sends:

- `start_time`
- `end_time`
- `forecast_horizon_hours`

The backend then:

1. Fetches actual wind generation from BMRS (`FUELHH`).
2. Fetches forecast wind generation from BMRS (`WINDFOR`).
3. For each target timestamp, selects the latest forecast published at least
   `h` hours before that target time.
4. Returns chart-ready JSON with actual and forecast values.

## Local setup

### Prerequisites

- Python 3.13
- Node.js 18+
- npm

### Backend

Install Python dependencies:

```bash
source venv/bin/activate
pip install -r backend/requirements.txt
```

Run the API:

```bash
cd backend
../venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

Install frontend dependencies:

```bash
cd frontend
npm install
```

Run the frontend:

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

### Makefile shortcuts

From the repo root:

```bash
make backend
make frontend
make dev
```

## Environment variables

### Backend

Copy from `backend/.env.example`:

- `CORS_ALLOWED_ORIGINS`
- `CORS_ALLOWED_ORIGIN_REGEX` (optional, useful for Vercel preview deployments)

### Frontend

Copy from `frontend/.env.example`:

- `VITE_API_BASE_URL`

Local default:

```text
http://127.0.0.1:8000
```

## API

### `GET /health`

Simple health check.

### `GET /generation`

Query parameters:

- `start_time`: ISO datetime
- `end_time`: ISO datetime
- `forecast_horizon_hours`: integer from `0` to `48`

Example:

```text
/generation?start_time=2025-01-01T00:00:00Z&end_time=2025-01-02T00:00:00Z&forecast_horizon_hours=4
```

## Deploying to Vercel

Deploy as two separate Vercel projects from the same GitHub repository:

- backend project with root directory `backend`
- frontend project with root directory `frontend`

Required environment variables:

- Backend: `CORS_ALLOWED_ORIGINS=https://your-frontend-project.vercel.app`
- Frontend: `VITE_API_BASE_URL=https://your-backend-project.vercel.app`

Optional backend preview support:

- `CORS_ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app`

See `VERCEL_DEPLOYMENT.md` for the deployment flow.

## Status

Implemented:

- FastAPI backend routes and BMRS integration
- Forecast-selection logic
- React frontend with controls and chart
- Vercel deployment configuration notes

Not yet included:

- analysis notebooks
- automated tests
- final submission assets
