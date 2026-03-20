from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

try:
    from .clean_data import clean_actuals, clean_forecasts
    from .fetch_data import fetch_fuelhh_actuals, fetch_wind_forecasts
    from .helpers import build_full_dataset
except ImportError:
    from clean_data import clean_actuals, clean_forecasts
    from fetch_data import fetch_fuelhh_actuals, fetch_wind_forecasts
    from helpers import build_full_dataset


DEFAULT_PUBLISH_FROM = "2025-01-01T00:00:00Z"


def fetch_clean_and_join(
    publish_from: str = DEFAULT_PUBLISH_FROM,
    publish_to: str = "2025-12-31T23:59:59Z",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw_forecasts = fetch_wind_forecasts(
        publish_from=publish_from,
        publish_to=publish_to,
    )
    raw_actuals = fetch_fuelhh_actuals(
        publish_from=publish_from,
        publish_to=publish_to,
        fuel_type="WIND",
    )

    forecasts = clean_forecasts(raw_forecasts)
    actuals = clean_actuals(raw_actuals)
    joined = build_full_dataset(actuals, forecasts)

    return actuals, forecasts, joined


def _save_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def _save_parquet_if_available(df: pd.DataFrame, path: Path) -> bool:
    try:
        df.to_parquet(path, index=False)
        return True
    except ImportError:
        return False


def save_datasets(
    actuals: pd.DataFrame,
    forecasts: pd.DataFrame,
    joined: pd.DataFrame,
    output_dir: str | Path | None = None,
) -> dict[str, list[str]]:
    base_dir = Path(output_dir) if output_dir is not None else Path(__file__).resolve().parents[1] / "data"
    base_dir.mkdir(parents=True, exist_ok=True)

    csv_paths = {
        "actuals": base_dir / "actuals.csv",
        "forecasts": base_dir / "forecasts.csv",
        "joined": base_dir / "joined_forecasts_actuals.csv",
    }
    parquet_paths = {
        "actuals": base_dir / "actuals.parquet",
        "forecasts": base_dir / "forecasts.parquet",
        "joined": base_dir / "joined_forecasts_actuals.parquet",
    }

    _save_csv(actuals, csv_paths["actuals"])
    _save_csv(forecasts, csv_paths["forecasts"])
    _save_csv(joined, csv_paths["joined"])

    saved_parquet: list[str] = []
    for key, df in (
        ("actuals", actuals),
        ("forecasts", forecasts),
        ("joined", joined),
    ):
        if _save_parquet_if_available(df, parquet_paths[key]):
            saved_parquet.append(str(parquet_paths[key]))

    return {
        "csv": [str(path) for path in csv_paths.values()],
        "parquet": saved_parquet,
    }


def run_pipeline(
    publish_from: str = DEFAULT_PUBLISH_FROM,
    publish_to: str = "2025-12-31T23:59:59Z",
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    actuals, forecasts, joined = fetch_clean_and_join(
        publish_from=publish_from,
        publish_to=publish_to,
    )
    saved_files = save_datasets(
        actuals=actuals,
        forecasts=forecasts,
        joined=joined,
        output_dir=output_dir,
    )
    return {
        "actual_rows": len(actuals),
        "forecast_rows": len(forecasts),
        "joined_rows": len(joined),
        "saved_files": saved_files,
    }


if __name__ == "__main__":
    summary = run_pipeline()
    print(summary)
