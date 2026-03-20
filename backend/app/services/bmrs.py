from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests


BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"
ACTUALS_STREAM_URL = f"{BASE_URL}/datasets/FUELHH/stream"
FORECAST_STREAM_URL = f"{BASE_URL}/datasets/WINDFOR/stream"
REQUEST_TIMEOUT_SECONDS = 30


def _format_api_datetime(value: str | datetime) -> str:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat().replace("+00:00", "Z")
    return value


def _parse_api_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _extract_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, list):
            return data
    raise ValueError("Unexpected BMRS response shape. Expected list or {'data': [...]}.")


def _get_json(url: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    print("REQUEST URL:", response.url)
    response.raise_for_status()
    return _extract_records(response.json())


def fetch_actual_wind_data(start_from: str | datetime, start_to: str | datetime) -> list[dict[str, Any]]:
    """
    Fetch actual wind generation rows for a delivery/start-time range.
    """
    params = {
        "publishDateTimeFrom": _format_api_datetime(start_from),
        "publishDateTimeTo": _format_api_datetime(start_to),
    }

    records = _get_json(ACTUALS_STREAM_URL, params=params)

    actual_wind_rows: list[dict[str, Any]] = []
    for row in records:
        start_time_value = row.get("startTime")
        fuel_type = row.get("fuelType")
        generation_value = row.get("generation")

        if fuel_type != "WIND" or not start_time_value or generation_value is None:
            continue

        actual_wind_rows.append(
            {
                "startTime": start_time_value,
                "startTimeDt": _parse_api_datetime(start_time_value),
                "generation": generation_value,
                "fuelType": fuel_type,
            }
        )

    return actual_wind_rows


def fetch_forecast_wind_data(
    publish_from: str | datetime,
    publish_to: str | datetime,
) -> list[dict[str, Any]]:
    """
    Fetch wind forecast rows published in a given publish-time window.
    Keep only forward-looking forecasts.
    """
    params = {
        "publishDateTimeFrom": _format_api_datetime(publish_from),
        "publishDateTimeTo": _format_api_datetime(publish_to),
    }

    records = _get_json(FORECAST_STREAM_URL, params=params)

    forecast_rows: list[dict[str, Any]] = []
    for row in records:
        start_time_value = row.get("startTime")
        publish_time_value = row.get("publishTime")
        generation_value = row.get("generation")

        if not start_time_value or not publish_time_value or generation_value is None:
            continue

        target_time = _parse_api_datetime(start_time_value)
        publish_time = _parse_api_datetime(publish_time_value)
        forecast_horizon_hours = (target_time - publish_time).total_seconds() / 3600

        if forecast_horizon_hours < 0:
            continue

        forecast_rows.append(
            {
                "startTime": start_time_value,
                "startTimeDt": target_time,
                "publishTime": publish_time_value,
                "publishTimeDt": publish_time,
                "generation": generation_value,
                "forecastHorizonHours": forecast_horizon_hours,
            }
        )

    return forecast_rows