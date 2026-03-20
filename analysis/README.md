# Analysis Data

This directory stores generated analysis datasets.

Primary outputs written by `analysis/fetch_data/pipeline.py`:

- `actuals.csv`
- `forecasts.csv`
- `joined_forecasts_actuals.csv`

If `pyarrow` is installed, matching parquet files may also be written.

Do not rely on the zero-byte placeholder files that previously existed here.
