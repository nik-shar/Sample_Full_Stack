from __future__ import annotations

import os


def _parse_csv_env(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def get_cors_allowed_origins() -> list[str]:
    raw_value = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173",
    )
    return _parse_csv_env(raw_value)


def get_cors_allowed_origin_regex() -> str | None:
    raw_value = os.getenv("CORS_ALLOWED_ORIGIN_REGEX", "").strip()
    return raw_value or None
