# REint Full Stack Challenge Roadmap

## Goal
Deliver a production-quality full stack application for UK national wind forecast monitoring, two analysis notebooks, and the required submission assets.

## Scope Summary
- Build a responsive web app that compares actual vs forecasted UK wind generation.
- Support a selectable time range and configurable forecast horizon from 0-48 hours.
- Use BMRS actuals (`FUELHH`, `fuelType=WIND`) and forecasts (`WINDFOR`) from January 2025 onward.
- Ignore missing forecast points instead of interpolating them.
- Produce two Jupyter notebooks:
  - Forecast error analysis
  - Historical wind availability recommendation in MW
- Deploy the app and prepare final submission materials.

## Delivery Phases

### Phase 1: Project setup
- Choose and initialize the stack for frontend, backend, and notebooks.
- Create repository structure for app, analysis, shared utilities, and docs.
- Add environment configuration, linting, formatting, and basic testing setup.
- Document key assumptions before implementation starts.

### Phase 2: Data access layer
- Study BMRS API behavior, pagination, limits, timestamp format, and failure modes.
- Implement clients for:
  - Actual generation data by date range
  - Forecast generation data by date range
- Normalize timestamps and generation values into a consistent internal schema.
- Filter forecast records to horizons between 0 and 48 hours.
- Add caching or pre-processing where needed to keep the app responsive.

### Phase 3: Forecast selection logic
- Implement the core rule:
  - For each target time, choose the latest forecast published at least `h` hours before the target time.
- Make forecast horizon configurable.
- Exclude target times with no qualifying forecast.
- Add unit tests for edge cases:
  - Exact publish-time boundary
  - Missing forecasts
  - Multiple forecasts for the same target time
  - Out-of-range forecast horizons

### Phase 4: Backend/API layer
- Expose an application endpoint that returns chart-ready actual and selected forecast data for a requested time window and forecast horizon.
- Validate request parameters and return clear error responses.
- Add observability basics: structured logging and simple error handling.
- Keep backend contracts stable so frontend and notebooks can reuse the same logic where practical.

### Phase 5: Frontend application
- Build a responsive interface for desktop and mobile.
- Add:
  - Start time picker
  - End time picker
  - Forecast horizon slider
  - Time-series chart with actual vs forecast values
- Handle loading, empty, and API failure states explicitly.
- Ensure chart legends, axes, labels, and time formatting are easy to read.
- Refine UX beyond the sample where it improves clarity without changing the core workflow.

### Phase 6: Forecast error notebook
- Create a notebook to characterize forecast error.
- Analyze metrics such as:
  - Mean error
  - Median error
  - p99 error
  - Error vs forecast horizon
  - Error vs time of day
- Explain methodology, assumptions, and trade-offs step by step.
- Conclude with clear takeaways about model behavior.

### Phase 7: Wind availability notebook
- Analyze historical actual wind generation.
- Quantify reliability using distributional views and conservative availability estimates.
- Develop a recommendation for how many MW of wind can be relied on to meet demand.
- Support the recommendation with explicit reasoning, evidence, and sensitivity discussion.

### Phase 8: Deployment and submission assets
- Deploy the application to Vercel, Heroku, or equivalent.
- Write a README covering:
  - Repository structure
  - Setup and run instructions
  - Deployment link
  - AI usage disclosure if applicable
- Prepare a short demo video covering frontend, backend, and analysis.
- Verify the git history is clean and meaningful.
- Package the repository as a zip including `.git`, upload it, and prepare the final submission link.

## Suggested Repository Structure
```text
app/
  frontend/
  backend/
analysis/
  forecast_error.ipynb
  wind_availability.ipynb
shared/
  data_models/
  bmrs_client/
docs/
README.md
```

## Key Risks
- BMRS API availability, response size, or undocumented quirks.
- Timezone and half-hour interval handling errors.
- Slow chart queries if raw API calls are made on every request.
- Notebook conclusions becoming weak if assumptions are not stated explicitly.

## Definition of Done
- App works on desktop and mobile.
- Forecast selection logic matches the challenge requirement.
- Missing forecasts are omitted correctly.
- Both notebooks are complete, reasoned, and reproducible.
- README, deployment, demo video, zip archive, and submission artifacts are ready.
