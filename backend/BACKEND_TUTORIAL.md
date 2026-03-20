# FastAPI Backend Tutorial

## Purpose
This guide is for building the backend of the REint challenge using FastAPI. It is written for a beginner, and it focuses on what you need to build, why each part exists, and what order to follow.

This file is only a tutorial. It does not create any backend code for you.

## What the backend needs to do
Your backend should eventually handle these responsibilities:

1. Accept a request from the frontend with:
   - `start_time`
   - `end_time`
   - `forecast_horizon_hours`
2. Fetch actual wind generation data from BMRS.
3. Fetch forecast wind generation data from BMRS.
4. For each target time, select the latest forecast published at least `h` hours before that target time.
5. Return clean JSON that the frontend can plot.

## Recommended learning goal
Do not try to build the whole backend at once.

Build it in this order:

1. Create a minimal FastAPI app.
2. Add one test route like `/health`.
3. Learn how query parameters work.
4. Learn how to call an external API from FastAPI.
5. Learn how to clean and transform BMRS data.
6. Add the challenge-specific endpoint.

If you skip this order, you will likely get blocked by too many moving parts at once.

## Suggested backend structure
You do not need to create all of these files immediately. This is just the direction to work toward.

```text
backend/
  app/
    main.py
    routes/
      health.py
      generation.py
    services/
      bmrs.py
      forecast_selector.py
    models/
      generation.py
    core/
      config.py
  requirements.txt
```

## Step 1: Understand FastAPI at a high level
FastAPI is a Python framework for building APIs.

Important ideas:

- `app = FastAPI()` creates the application.
- A route is a URL like `/health` or `/generation`.
- A `GET` route is used when you are fetching data.
- FastAPI automatically converts Python dictionaries into JSON responses.
- FastAPI can validate inputs using type hints and Pydantic models.

For your project, the frontend will call the backend, and the backend will call BMRS.

So the backend acts like a middle layer:

```text
Frontend -> Your FastAPI backend -> BMRS API
```

## Step 2: Set up the Python environment
You already have a virtual environment in this project directory. Before doing backend work yourself, activate it.

Example:

```bash
source venv/bin/activate
```

Then install FastAPI and a server to run it:

```bash
pip install fastapi uvicorn requests
```

You may later also want:

```bash
pip install pandas python-dotenv
```

Why these packages:

- `fastapi`: API framework
- `uvicorn`: local development server
- `requests`: simple HTTP client for calling BMRS
- `pandas`: useful for time-series cleaning and analysis
- `python-dotenv`: optional, if you keep config in `.env`

## Step 3: Create the smallest possible FastAPI app
Your first goal is not the challenge logic. Your first goal is proving that FastAPI runs.

Start with a file like `backend/app/main.py`.

Inside it, you will eventually need:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Backend is running"}
```

Then run it with:

```bash
uvicorn app.main:app --reload
```

Important:

- Run this command from inside the `backend` directory.
- `app.main:app` means:
  - package/folder: `app`
  - file: `main.py`
  - variable inside file: `app`

If it works, open:

```text
http://127.0.0.1:8000
```

You should see JSON in the browser.

Also open:

```text
http://127.0.0.1:8000/docs
```

This is one of FastAPI’s best beginner features. It gives you auto-generated API documentation and lets you test routes in the browser.

## Step 4: Add a simple health route
Before building business logic, create a very simple route like `/health`.

Purpose:

- confirm the app is up
- confirm routing works
- give you a clean place to test deployment later

Example idea:

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

This route is useful even in production.

## Step 5: Learn query parameters
Your main challenge endpoint will probably be a `GET` endpoint with query parameters.

Example request shape:

```text
/generation?start_time=2025-01-10T00:00:00&end_time=2025-01-11T00:00:00&forecast_horizon_hours=4
```

This means the frontend is asking:

- show me data between these two timestamps
- when choosing forecast values, use a horizon of 4 hours

In FastAPI, query parameters can be read directly in function arguments.

Example idea:

```python
@app.get("/generation")
def get_generation(
    start_time: str,
    end_time: str,
    forecast_horizon_hours: int
):
    return {
        "start_time": start_time,
        "end_time": end_time,
        "forecast_horizon_hours": forecast_horizon_hours
    }
```

You should first test this route without any BMRS logic. Just make sure query parameters are being received correctly.

## Step 6: Understand the challenge data before coding
There are two datasets.

### Actual generation
Source: `FUELHH`

Relevant fields:

- `startTime`
- `generation`
- `fuelType`

You only want rows where:

- `fuelType == "WIND"`

### Forecast generation
Source: `WINDFOR`

Relevant fields:

- `startTime`
- `publishTime`
- `generation`

You only want:

- dates from January 2025 onward
- forecast horizon between 0 and 48 hours

### Most important business rule
For each target time:

- target time is the actual generation timestamp
- choose the latest forecast where:
  - `publishTime <= target_time - forecast_horizon`

Example:

- target time = `2025-05-24 18:00`
- forecast horizon = `4`
- cutoff time = `2025-05-24 14:00`
- choose the most recent forecast published on or before `14:00`

If there is no valid forecast for that target time, do not return a fake value.

## Step 7: Build the backend in layers
Do not put everything in one file. Even as a beginner, separating responsibilities will save you time.

Recommended separation:

### Route layer
This should:

- accept request inputs
- validate parameters
- call service functions
- return final JSON

Example files later:

- `routes/generation.py`
- `routes/health.py`

### Service layer
This should contain the real logic.

Example responsibilities:

- call BMRS APIs
- filter wind rows
- parse timestamps
- select the correct forecast per target time

Example files later:

- `services/bmrs.py`
- `services/forecast_selector.py`

### Model layer
This should describe the shape of your data.

For example:

- one model for a point in the chart
- one model for the full API response

This makes your API cleaner and safer.

## Step 8: Learn the BMRS API manually first
Before writing Python code, test the BMRS endpoints directly in the browser or with a tool like Postman/curl.

You need to understand:

- what format the response uses
- whether it is JSON or something else
- whether pagination exists
- what query parameters are required
- whether the timestamps include timezone information

Why this matters:

Many beginner bugs happen because you start coding before understanding the real response format.

When you inspect the BMRS response, write down:

1. the exact endpoint URL
2. the exact query parameters
3. the exact field names
4. example values for `startTime`, `publishTime`, and `generation`

## Step 9: Create a BMRS client function
Once you understand the BMRS API, write one simple function whose only job is to fetch data.

That function should not do forecast-selection logic yet.

Its job should be:

- accept request inputs like time range
- call BMRS
- return raw or lightly cleaned records

For example, later you may want separate functions:

- `fetch_actual_generation(...)`
- `fetch_forecast_generation(...)`

Keep them focused.

## Step 10: Normalize the timestamps
This part is very important.

You will be comparing:

- actual `startTime`
- forecast `startTime`
- forecast `publishTime`

If time parsing is inconsistent, your selection logic will be wrong.

You should make sure:

- all timestamps become Python `datetime` objects
- all timestamps use the same timezone handling strategy
- you know whether BMRS is returning UTC timestamps

Common beginner mistake:

- comparing strings instead of datetimes

Do not rely on raw string comparison for time logic.

## Step 11: Implement the forecast selection logic separately
Do not mix this logic into the route handler.

Create one function only for this rule:

Input:

- actual rows
- forecast rows
- forecast horizon in hours

Output:

- matched chart points where each target time contains:
  - actual generation
  - selected forecast generation, if one exists

High-level algorithm:

1. loop through each actual target time
2. compute `cutoff_time = target_time - horizon`
3. find forecasts for the same `startTime`
4. from those forecasts, keep only the ones with `publishTime <= cutoff_time`
5. choose the latest one among those
6. if none exist, leave forecast missing

This is the core of the challenge. Keep it isolated and testable.

## Step 12: Decide your response format
Your frontend needs clean JSON. Avoid returning raw BMRS output directly.

A good backend response is something like:

```json
{
  "meta": {
    "start_time": "...",
    "end_time": "...",
    "forecast_horizon_hours": 4
  },
  "data": [
    {
      "start_time": "...",
      "actual_generation": 1234.5,
      "forecast_generation": 1201.2
    }
  ]
}
```

Why this is better:

- frontend becomes simpler
- backend owns the business logic
- debugging becomes easier

## Step 13: Add input validation
Your endpoint should reject bad requests early.

Examples to validate:

- `start_time` must be before `end_time`
- `forecast_horizon_hours` must be between `0` and `48`
- date range should not be absurdly large for one request

FastAPI is good at validation, especially when you use typed parameters and Pydantic models.

This matters because validation errors are much easier to understand than silent bad output.

## Step 14: Add error handling
External APIs can fail.

Your backend should be ready for:

- BMRS timeout
- BMRS returning bad status codes
- unexpected empty responses
- malformed timestamps

Your job is not just to make happy-path code.

At minimum, think about:

- returning a clear error message
- logging what went wrong
- not crashing the whole server because one API call failed

## Step 15: Use FastAPI docs while building
During development, use `/docs` constantly.

It helps you:

- test query parameters
- see response shapes
- quickly check if a route works after changes

For a beginner, this is much faster than building the frontend immediately.

## Step 16: Test in small milestones
Use these milestones.

### Milestone A
FastAPI app starts and `/health` works.

### Milestone B
`/generation` accepts query parameters and returns dummy JSON.

### Milestone C
Backend successfully fetches actual BMRS data only.

### Milestone D
Backend successfully fetches forecast BMRS data only.

### Milestone E
Backend returns merged actual + selected forecast data.

### Milestone F
Backend handles invalid input and missing data cleanly.

If something breaks, go back only one milestone, not all the way back.

## Step 17: Good beginner workflow
A clean workflow for you:

1. write one small piece
2. run the server
3. test it in `/docs`
4. print/log a small sample of data
5. confirm the output shape
6. then move to the next piece

Do not build five files and only test at the end.

## Step 18: Suggested first backend tasks for you
Here is the exact order I recommend you personally follow:

1. Create `backend/app/main.py`
2. Make FastAPI start locally
3. Add `/health`
4. Add `/generation` with fake data
5. Inspect BMRS actual endpoint manually
6. Write a function to fetch actual wind data
7. Inspect BMRS forecast endpoint manually
8. Write a function to fetch forecast data
9. Parse timestamps into datetimes
10. Write the forecast-selection function
11. Return chart-ready JSON
12. Clean up with models and validation

## Step 19: Common mistakes to avoid
- Putting all logic inside `main.py`
- Comparing timestamps as strings
- Not checking timezone behavior
- Returning raw BMRS data directly to the frontend
- Trying to build frontend and backend at the same time
- Not testing the forecast-selection rule with a hand-worked example
- Ignoring missing forecast cases

## Step 20: What “done” looks like for the backend
Your backend is in good shape when:

- it starts cleanly with FastAPI
- `/health` works
- `/generation` accepts the required inputs
- it fetches actual and forecast data correctly
- it applies the forecast horizon rule correctly
- it returns clean JSON for the frontend
- bad inputs produce clear errors

## Suggested next step
Your next practical move should be:

1. activate the virtual environment
2. install `fastapi`, `uvicorn`, and `requests`
3. create `backend/app/main.py`
4. make `/` and `/health` work

That is the right starting point. Do not begin with BMRS integration yet.

## How I can help you next
When you are ready, I can help in a strictly guided way without taking over the project. For example, I can do any one of these:

1. review your planned backend folder structure
2. explain how to write `main.py`
3. explain how to run FastAPI locally
4. help you design the `/generation` endpoint inputs and output
5. explain the forecast-selection logic with a worked example

If you want, the next step can be just this: I explain exactly what to put inside `backend/app/main.py`, but I will wait for your permission before creating any code.
