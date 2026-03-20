import pandas as pd


def build_dataset_for_horizon(
    actuals: pd.DataFrame,
    forecasts: pd.DataFrame,
    horizon_hours: int,
) -> pd.DataFrame:
    """
    For each target_time:
      choose latest forecast where publish_time <= target_time - horizon_hours
    Equivalent to:
      horizon_actual >= horizon_hours
      and among valid forecasts choose the latest publish_time
    """

    valid = forecasts[forecasts["horizon_hours"] >= horizon_hours].copy()

    # latest valid forecast per target_time
    chosen = (
        valid.sort_values(["target_time", "publish_time"])
        .groupby("target_time", as_index=False)
        .tail(1)
        .copy()
    )

    merged = actuals.merge(chosen, on="target_time", how="inner")

    merged["horizon"] = horizon_hours
    merged["error"] = merged["forecast_mw"] - merged["actual_mw"]
    merged["abs_error"] = merged["error"].abs()

    return merged.sort_values("target_time").reset_index(drop=True)


def build_full_dataset(actuals: pd.DataFrame, forecasts: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for h in range(0, 49):
        part = build_dataset_for_horizon(actuals, forecasts, h)
        parts.append(part)

    out = pd.concat(parts, ignore_index=True)

    out["hour"] = out["target_time"].dt.hour
    out["day_of_week"] = out["target_time"].dt.dayofweek
    out["month"] = out["target_time"].dt.month

    return out