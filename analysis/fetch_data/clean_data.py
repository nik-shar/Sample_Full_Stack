import pandas as pd


def _find_first_present(df: pd.DataFrame, candidates: list[str], label: str) -> str:
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(f"Could not find a column for {label}. Available columns: {df.columns.tolist()}")


def clean_forecasts(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert raw WINDFOR into:
    - target_time
    - publish_time
    - forecast_mw
    """

    target_col = _find_first_present(
        raw_df,
        ["startTime", "startDateTime", "settlementPeriodStart", "deliveryStart"],
        "forecast target time",
    )
    publish_col = _find_first_present(
        raw_df,
        ["publishTime", "publishDateTime", "createdTime"],
        "forecast publish time",
    )
    value_col = _find_first_present(
        raw_df,
        ["quantity", "generation", "forecast", "level", "nationalForecast"],
        "forecast MW value",
    )

    df = raw_df.rename(
        columns={
            target_col: "target_time",
            publish_col: "publish_time",
            value_col: "forecast_mw",
        }
    ).copy()

    df["target_time"] = pd.to_datetime(df["target_time"], utc=True)
    df["publish_time"] = pd.to_datetime(df["publish_time"], utc=True)
    df["forecast_mw"] = pd.to_numeric(df["forecast_mw"], errors="coerce")

    df = df[["target_time", "publish_time", "forecast_mw"]].dropna()
    df = df.drop_duplicates(subset=["target_time", "publish_time"], keep="last")
    df = df.sort_values(["target_time", "publish_time"]).reset_index(drop=True)

    df["horizon_hours"] = (
        (df["target_time"] - df["publish_time"]).dt.total_seconds() / 3600
    )

    # keep only horizons requested in the prompt
    df = df[(df["horizon_hours"] >= 0) & (df["horizon_hours"] <= 48)].copy()

    return df


def clean_actuals(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert raw FUELHH into:
    - target_time
    - actual_mw
    """

    target_col = _find_first_present(
        raw_df,
        ["startTime", "startDateTime", "settlementPeriodStart"],
        "actual target time",
    )
    value_col = _find_first_present(
        raw_df,
        ["quantity", "generation", "output", "level"],
        "actual MW value",
    )

    df = raw_df.rename(
        columns={
            target_col: "target_time",
            value_col: "actual_mw",
        }
    ).copy()

    df["target_time"] = pd.to_datetime(df["target_time"], utc=True)
    df["actual_mw"] = pd.to_numeric(df["actual_mw"], errors="coerce")

    df = df[["target_time", "actual_mw"]].dropna()
    df = df.drop_duplicates(subset=["target_time"], keep="last")
    df = df.sort_values("target_time").reset_index(drop=True)

    return df