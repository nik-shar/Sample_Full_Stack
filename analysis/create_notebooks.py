from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def markdown_cell(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.strip().splitlines()],
    }


def code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.strip().splitlines()],
    }


def write_notebook(path: Path, cells: list[dict]) -> None:
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.13",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.write_text(json.dumps(notebook, indent=2) + "\n")


def build_forecast_error_notebook() -> list[dict]:
    return [
        markdown_cell(
            """
            # Forecast Error Analysis

            This notebook analyses UK national wind forecast performance using the
            challenge rule: for each target time, select the latest forecast
            published at least `h` hours before delivery.
            """
        ),
        markdown_cell(
            """
            ## Method

            1. Load cached analysis data from `analysis/data/`.
            2. If cached data does not exist, optionally fetch and rebuild it from BMRS.
            3. Evaluate signed error and absolute error overall, by forecast horizon,
               and by hour of day.
            """
        ),
        code_cell(
            """
            from pathlib import Path
            import sys

            import matplotlib.pyplot as plt
            import pandas as pd
            import seaborn as sns

            def find_repo_root() -> Path:
                candidates = [Path.cwd().resolve(), *Path.cwd().resolve().parents]
                for candidate in candidates:
                    if (candidate / "analysis" / "fetch_data" / "pipeline.py").exists():
                        return candidate
                raise FileNotFoundError("Could not locate repo root containing analysis/fetch_data/pipeline.py")

            ROOT = find_repo_root()
            DATA_DIR = ROOT / "analysis" / "data"
            FETCH_DIR = ROOT / "analysis" / "fetch_data"

            if str(FETCH_DIR) not in sys.path:
                sys.path.append(str(FETCH_DIR))

            from pipeline import fetch_clean_and_join, save_datasets

            sns.set_theme(style="whitegrid")
            pd.options.display.float_format = "{:,.2f}".format

            REFRESH_DATA = False
            PUBLISH_FROM = "2025-01-01T00:00:00Z"
            PUBLISH_TO = "2025-03-31T23:59:59Z"
            """
        ),
        code_cell(
            """
            joined_path = DATA_DIR / "joined_forecasts_actuals.csv"

            if REFRESH_DATA or not joined_path.exists():
                actuals, forecasts, joined = fetch_clean_and_join(
                    publish_from=PUBLISH_FROM,
                    publish_to=PUBLISH_TO,
                )
                save_datasets(actuals, forecasts, joined, output_dir=DATA_DIR)
            else:
                joined = pd.read_csv(joined_path, parse_dates=["target_time", "publish_time"])

            joined["error_mw"] = joined["forecast_mw"] - joined["actual_mw"]
            joined["abs_error_mw"] = joined["error_mw"].abs()

            print("Rows:", len(joined))
            print("Target time range:", joined["target_time"].min(), "to", joined["target_time"].max())
            joined.head()
            """
        ),
        markdown_cell(
            """
            ## Overall error summary

            Signed error shows whether the forecast tends to over- or under-predict.
            Absolute error captures magnitude regardless of direction.
            """
        ),
        code_cell(
            """
            overall_summary = pd.DataFrame(
                {
                    "metric": [
                        "mean_signed_error_mw",
                        "median_signed_error_mw",
                        "mean_abs_error_mw",
                        "median_abs_error_mw",
                        "p99_abs_error_mw",
                    ],
                    "value": [
                        joined["error_mw"].mean(),
                        joined["error_mw"].median(),
                        joined["abs_error_mw"].mean(),
                        joined["abs_error_mw"].median(),
                        joined["abs_error_mw"].quantile(0.99),
                    ],
                }
            )
            overall_summary
            """
        ),
        markdown_cell(
            """
            ## Error by forecast horizon

            This is the core behavioural view. If the selection logic is working,
            errors should generally worsen as the required look-ahead horizon grows.
            """
        ),
        code_cell(
            """
            horizon_summary = (
                joined.groupby("horizon")
                .agg(
                    sample_count=("target_time", "size"),
                    mean_signed_error_mw=("error_mw", "mean"),
                    median_signed_error_mw=("error_mw", "median"),
                    mean_abs_error_mw=("abs_error_mw", "mean"),
                    median_abs_error_mw=("abs_error_mw", "median"),
                    p99_abs_error_mw=("abs_error_mw", lambda s: s.quantile(0.99)),
                )
                .reset_index()
            )
            horizon_summary.head(10)
            """
        ),
        code_cell(
            """
            fig, axes = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)

            sns.lineplot(
                data=horizon_summary,
                x="horizon",
                y="mean_abs_error_mw",
                marker="o",
                ax=axes[0],
            )
            axes[0].set_title("Mean Absolute Error by Horizon")
            axes[0].set_xlabel("Forecast horizon (hours)")
            axes[0].set_ylabel("MW")

            sns.lineplot(
                data=horizon_summary,
                x="horizon",
                y="p99_abs_error_mw",
                marker="o",
                ax=axes[1],
            )
            axes[1].set_title("P99 Absolute Error by Horizon")
            axes[1].set_xlabel("Forecast horizon (hours)")
            axes[1].set_ylabel("MW")

            plt.show()
            """
        ),
        markdown_cell(
            """
            ## Error by time of day

            This view checks whether some delivery hours are materially harder
            to predict than others.
            """
        ),
        code_cell(
            """
            hour_summary = (
                joined.groupby("hour")
                .agg(
                    sample_count=("target_time", "size"),
                    mean_abs_error_mw=("abs_error_mw", "mean"),
                    median_abs_error_mw=("abs_error_mw", "median"),
                    p99_abs_error_mw=("abs_error_mw", lambda s: s.quantile(0.99)),
                )
                .reset_index()
            )
            hour_summary
            """
        ),
        code_cell(
            """
            plt.figure(figsize=(12, 5))
            sns.lineplot(data=hour_summary, x="hour", y="mean_abs_error_mw", marker="o")
            plt.title("Mean Absolute Error by Delivery Hour")
            plt.xlabel("Hour of day")
            plt.ylabel("MW")
            plt.xticks(range(24))
            plt.show()
            """
        ),
        markdown_cell(
            """
            ## Interpretation checklist

            Use the computed tables and plots above to answer:

            - Is there a material signed bias overall?
            - How quickly does error grow with horizon?
            - Which hours of day are the least reliable?
            - Is the tail risk small enough for your intended operational use?
            """
        ),
    ]


def build_wind_reliability_notebook() -> list[dict]:
    return [
        markdown_cell(
            """
            # Wind Reliability Recommendation

            This notebook estimates a conservative amount of UK wind generation
            that can be treated as reliably available using historical actuals.
            """
        ),
        markdown_cell(
            """
            ## Method

            The challenge asks for a recommendation in MW backed by explicit reasoning.
            This notebook uses a conservative percentile approach:

            - analyse historical actual generation only,
            - compute low-end percentiles overall and by month,
            - recommend a value that stays below the weakest monthly 10th percentile.
            """
        ),
        code_cell(
            """
            from pathlib import Path
            import sys

            import matplotlib.pyplot as plt
            import pandas as pd
            import seaborn as sns

            def find_repo_root() -> Path:
                candidates = [Path.cwd().resolve(), *Path.cwd().resolve().parents]
                for candidate in candidates:
                    if (candidate / "analysis" / "fetch_data" / "pipeline.py").exists():
                        return candidate
                raise FileNotFoundError("Could not locate repo root containing analysis/fetch_data/pipeline.py")

            ROOT = find_repo_root()
            DATA_DIR = ROOT / "analysis" / "data"
            FETCH_DIR = ROOT / "analysis" / "fetch_data"

            if str(FETCH_DIR) not in sys.path:
                sys.path.append(str(FETCH_DIR))

            from pipeline import fetch_clean_and_join, save_datasets

            sns.set_theme(style="whitegrid")
            pd.options.display.float_format = "{:,.2f}".format

            REFRESH_DATA = False
            PUBLISH_FROM = "2025-01-01T00:00:00Z"
            PUBLISH_TO = "2025-03-31T23:59:59Z"
            """
        ),
        code_cell(
            """
            actuals_path = DATA_DIR / "actuals.csv"

            if REFRESH_DATA or not actuals_path.exists():
                actuals, forecasts, joined = fetch_clean_and_join(
                    publish_from=PUBLISH_FROM,
                    publish_to=PUBLISH_TO,
                )
                save_datasets(actuals, forecasts, joined, output_dir=DATA_DIR)
            else:
                actuals = pd.read_csv(actuals_path, parse_dates=["target_time"])

            actuals["month"] = actuals["target_time"].dt.month
            actuals["hour"] = actuals["target_time"].dt.hour

            print("Rows:", len(actuals))
            print("Target time range:", actuals["target_time"].min(), "to", actuals["target_time"].max())
            actuals.head()
            """
        ),
        markdown_cell(
            """
            ## Distribution summary

            Low percentiles are the most relevant because the recommendation is
            about reliable availability, not average output.
            """
        ),
        code_cell(
            """
            overall_distribution = pd.DataFrame(
                {
                    "percentile": ["p01", "p05", "p10", "p25", "p50", "mean"],
                    "mw": [
                        actuals["actual_mw"].quantile(0.01),
                        actuals["actual_mw"].quantile(0.05),
                        actuals["actual_mw"].quantile(0.10),
                        actuals["actual_mw"].quantile(0.25),
                        actuals["actual_mw"].quantile(0.50),
                        actuals["actual_mw"].mean(),
                    ],
                }
            )
            overall_distribution
            """
        ),
        code_cell(
            """
            plt.figure(figsize=(12, 5))
            sns.histplot(actuals["actual_mw"], bins=40, kde=True)
            plt.title("Distribution of Actual Wind Generation")
            plt.xlabel("Actual generation (MW)")
            plt.ylabel("Count")
            plt.show()
            """
        ),
        markdown_cell(
            """
            ## Seasonal stress check

            The recommendation should not be based only on the full-sample p10 if
            one month is materially weaker than the rest.
            """
        ),
        code_cell(
            """
            monthly_summary = (
                actuals.groupby("month")
                .agg(
                    sample_count=("target_time", "size"),
                    mean_mw=("actual_mw", "mean"),
                    p10_mw=("actual_mw", lambda s: s.quantile(0.10)),
                    p05_mw=("actual_mw", lambda s: s.quantile(0.05)),
                    min_mw=("actual_mw", "min"),
                )
                .reset_index()
            )
            monthly_summary
            """
        ),
        code_cell(
            """
            plt.figure(figsize=(12, 5))
            sns.barplot(data=monthly_summary, x="month", y="p10_mw", color="#4c78a8")
            plt.title("Monthly 10th Percentile of Actual Wind Generation")
            plt.xlabel("Month")
            plt.ylabel("MW")
            plt.show()
            """
        ),
        markdown_cell(
            """
            ## Recommendation

            Recommendation rule used here:

            - start from the weakest monthly 10th percentile,
            - round down to the nearest 100 MW,
            - treat that as a conservative dependable MW estimate.
            """
        ),
        code_cell(
            """
            weakest_monthly_p10 = monthly_summary["p10_mw"].min()
            overall_p10 = actuals["actual_mw"].quantile(0.10)
            recommended_mw = int(weakest_monthly_p10 // 100 * 100)

            recommendation = pd.DataFrame(
                {
                    "metric": [
                        "overall_p10_mw",
                        "weakest_monthly_p10_mw",
                        "recommended_reliable_mw",
                    ],
                    "value": [
                        overall_p10,
                        weakest_monthly_p10,
                        recommended_mw,
                    ],
                }
            )
            recommendation
            """
        ),
        code_cell(
            """
            print(
                f"Recommended reliable wind availability: {recommended_mw:,} MW. "
                f"This is based on the weakest monthly 10th percentile "
                f"({weakest_monthly_p10:,.0f} MW), rounded down for conservatism."
            )
            """
        ),
        markdown_cell(
            """
            ## Limitations

            - If the historical sample is short, the recommendation is fragile.
            - A stricter operational planning standard may prefer p05 instead of p10.
            - This notebook uses delivered generation, so future fleet changes are not captured.
            """
        ),
    ]


def main() -> None:
    write_notebook(
        ROOT / "01_forecast_error_analysis.ipynb",
        build_forecast_error_notebook(),
    )
    write_notebook(
        ROOT / "02_wind_reliability_recommendation.ipynb",
        build_wind_reliability_notebook(),
    )


if __name__ == "__main__":
    main()
