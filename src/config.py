from __future__ import annotations

import os
from pathlib import Path

from src.models import Location

API_BASE_URL: str = "https://archive-api.open-meteo.com/v1/archive"
DAILY_VARIABLE: str = "temperature_2m_mean"
API_TIMEZONE: str = "UTC"

DEFAULT_START_DATE: str = "1940-01-01"
DEFAULT_END_DATE: str = "2025-12-31"

RATE_LIMIT_BACKOFF_SECONDS: float = 60.0
MAX_RETRIES: int = 3
HTTP_TIMEOUT_SECONDS: float = 30.0

OUTPUT_DIR: Path = Path(os.environ.get("OUTPUT_DIR", "output"))

CHART_DPI: int = 300

LOCATIONS: list[Location] = [
    Location(name="New York", lat=40.7128, lon=-74.0060),
    Location(name="London", lat=51.5074, lon=-0.1278),
    Location(name="Tokyo", lat=35.6762, lon=139.6503),
    Location(name="Sydney", lat=-33.8688, lon=151.2093),
    Location(name="Cairo", lat=30.0444, lon=31.2357),
    Location(name="Rio de Janeiro", lat=-22.9068, lon=-43.1729),
    Location(name="Mumbai", lat=19.0760, lon=72.8777),
    Location(name="Moscow", lat=55.7558, lon=37.6173),
    Location(name="Beijing", lat=39.9042, lon=116.4074),
    Location(name="Cape Town", lat=-33.9249, lon=18.4241),
    Location(name="Los Angeles", lat=34.0522, lon=-118.2437),
    Location(name="Singapore", lat=1.3521, lon=103.8198),
]
