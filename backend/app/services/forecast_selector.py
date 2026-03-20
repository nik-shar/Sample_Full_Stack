from __future__ import annotations

from datetime import timedelta
from typing import Any


def select_latest_forecasts(
    actual_rows: list[dict[str, Any]],
    forecast_rows: list[dict[str, Any]],
    forecast_horizon_hours: int,
) -> list[dict[str, Any]]:
    """
    Match each actual row to the latest valid forecast using the challenge rule:
    choose the latest forecast published at least `forecast_horizon_hours`
    before the target time.

    Expected input shape:
    - actual row contains `startTimeDt`
    - forecast row contains `startTimeDt` and `publishTimeDt`
    """
    forecasts_by_target_time: dict[Any, list[dict[str, Any]]] = {}
    for forecast_row in forecast_rows:
        target_time = forecast_row.get("startTimeDt")
        if target_time is None:
            continue

        forecasts_by_target_time.setdefault(target_time, []).append(forecast_row)

    matched_rows: list[dict[str, Any]] = []
    horizon_delta = timedelta(hours=forecast_horizon_hours)

    for actual_row in actual_rows:
        target_time = actual_row.get("startTimeDt")
        if target_time is None:
            continue

        cutoff_time = target_time - horizon_delta
        candidate_forecasts = forecasts_by_target_time.get(target_time, [])

        valid_forecasts = [
            forecast_row
            for forecast_row in candidate_forecasts
            if forecast_row.get("publishTimeDt") is not None
            and forecast_row["publishTimeDt"] <= cutoff_time
        ]

        selected_forecast = None
        if valid_forecasts:
            selected_forecast = max(valid_forecasts, key=lambda row: row["publishTimeDt"])

        matched_rows.append(
            {
                "startTime": actual_row.get("startTime"),
                "startTimeDt": target_time,
                "actualGeneration": actual_row.get("generation"),
                "forecastGeneration": None if selected_forecast is None else selected_forecast.get("generation"),
                "forecastPublishTime": None if selected_forecast is None else selected_forecast.get("publishTime"),
                "forecastPublishTimeDt": None
                if selected_forecast is None
                else selected_forecast.get("publishTimeDt"),
                "cutoffTimeDt": cutoff_time,
            }
        )

    return matched_rows
