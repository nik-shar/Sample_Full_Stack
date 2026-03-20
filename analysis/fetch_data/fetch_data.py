import requests
import pandas as pd


BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets"


def _get_json(url: str, params: dict) -> list:
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()

    # Elexon responses are usually either:
    # - a list
    # - {"data": [...]}
    # - {"result": [...]}
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "data" in data:
            return data["data"]
        if "result" in data:
            return data["result"]

    raise ValueError(f"Unexpected response structure: {type(data)}")


def fetch_wind_forecasts(
    publish_from="2025-01-01T00:00:00Z",
    publish_to="2025-12-31T23:59:59Z",
):
    """
    Fetch WINDFOR forecast data.

    Expected key fields from API:
    - publishTime / publishDateTime
    - startTime / startDateTime / settlementPeriod start timestamp
    - forecast generation value
    """
    url = f"{BASE_URL}/WINDFOR/stream"
    params = {
        "publishDateTimeFrom": publish_from,
        "publishDateTimeTo": publish_to,
    }

    rows = _get_json(url, params)
    df = pd.json_normalize(rows)

    print("WINDFOR columns:", df.columns.tolist())

    return df


def fetch_fuelhh_actuals(
    publish_from="2025-01-01T00:00:00Z",
    publish_to="2025-12-31T23:59:59Z",
    settlement_from="",
    settlement_to="",
    fuel_type="WIND",
):
    """
    Fetch FUELHH actual generation data.
    """
    url = f"{BASE_URL}/FUELHH/stream"

    params = {
        "publishDateTimeFrom": publish_from,
        "publishDateTimeTo": publish_to,
        "fuelType": fuel_type,
    }

    rows = _get_json(url, params)
    df = pd.json_normalize(rows)

    print("FUELHH columns:", df.columns.tolist())

    return df