from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query

from app.services.bmrs import (
    MAX_FORECAST_HORIZON_HOURS,
    fetch_actual_wind_data,
    fetch_forecast_wind_data,
)
from app.services.forecast_selector import select_latest_forecasts


router = APIRouter()


@router.get("/generation")
def get_generation(
    start_time: datetime,
    end_time: datetime,
    forecast_horizon_hours: int = Query(..., ge=0, le=48),
):
    if start_time >= end_time:
        raise HTTPException(
            status_code=400,
            detail="start_time must be earlier than end_time",
        )

    try:
        forecast_publish_from_dt = start_time - timedelta(hours=MAX_FORECAST_HORIZON_HOURS)
        forecast_publish_to_dt = end_time

        actual_rows = fetch_actual_wind_data(start_time, end_time)
        forecast_rows = fetch_forecast_wind_data(
            forecast_publish_from_dt,
            forecast_publish_to_dt,
        )

        matched_rows = select_latest_forecasts(
            actual_rows=actual_rows,
            forecast_rows=forecast_rows,
            forecast_horizon_hours=forecast_horizon_hours,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch BMRS data: {exc}") from exc

    chart_rows = []
    for row in matched_rows:
        chart_rows.append(
            {
                "startTime": row.get("startTime"),
                "actualGeneration": row.get("actualGeneration"),
                "forecastGeneration": row.get("forecastGeneration"),
            }
        )

    matched_forecast_count = sum(
        1 for row in matched_rows if row.get("forecastGeneration") is not None
    )

    return {
            "meta": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "forecast_horizon_hours": forecast_horizon_hours,
                "forecast_publish_from": forecast_publish_from_dt.isoformat(),
                "forecast_publish_to": forecast_publish_to_dt.isoformat(),
                "note": "All actual timestamps are returned. Forecast selection is based on the latest forecast published on or before target_time minus horizon, using BMRS forecasts within the valid 0-48 hour horizon window.",
            },
        "actual_count": len(actual_rows),
        "forecast_count": len(forecast_rows),
        "matched_count": len(matched_rows),
        "matched_forecast_count": matched_forecast_count,
        "data": chart_rows,
    }
