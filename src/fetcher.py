from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from typing import Any

import httpx
import pandas as pd

from src.config import (
    API_BASE_URL,
    API_TIMEZONE,
    DAILY_VARIABLE,
    HTTP_TIMEOUT_SECONDS,
    MAX_RETRIES,
    RATE_LIMIT_BACKOFF_SECONDS,
)
from src.models import Location

RATE_LIMIT_MARKERS: tuple[str, ...] = (
    "Hourly API request limit exceeded",
    "Daily API request limit exceeded",
)


class RateLimitExceededError(RuntimeError):
    """Raised when Open-Meteo signals the API rate limit has been hit."""


class WeatherFetchError(RuntimeError):
    """Raised when a non-rate-limit fetch failure persists past all retries."""


class WeatherDataFetcher:
    """Fetches daily temperature data from the Open-Meteo Archive API."""

    def __init__(
        self,
        client: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=HTTP_TIMEOUT_SECONDS)
        self._sleep = sleep

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def fetch_location(
        self,
        location: Location,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        params = {
            "latitude": location.lat,
            "longitude": location.lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": DAILY_VARIABLE,
            "timezone": API_TIMEZONE,
        }

        last_status: int | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            response = self._client.get(API_BASE_URL, params=params)
            last_status = response.status_code

            if response.status_code == 200:
                payload = response.json()
                return _payload_to_dataframe(payload, location)

            if any(marker in response.text for marker in RATE_LIMIT_MARKERS):
                raise RateLimitExceededError(
                    f"Open-Meteo rate limit exceeded for {location.name}",
                )

            if attempt < MAX_RETRIES:
                self._sleep(RATE_LIMIT_BACKOFF_SECONDS)

        raise WeatherFetchError(
            f"Failed to fetch {location.name} after {MAX_RETRIES} attempts (last status={last_status})",
        )

    def fetch_all(
        self,
        locations: Iterable[Location],
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        frames = [self.fetch_location(loc, start_date, end_date) for loc in locations]
        return pd.concat(frames, ignore_index=True)


def _payload_to_dataframe(payload: dict[str, Any], location: Location) -> pd.DataFrame:
    if "daily" not in payload:
        raise WeatherFetchError(f"Response for {location.name} missing 'daily' block")
    df = pd.DataFrame(payload["daily"])
    df["location"] = location.name
    df["lat"] = location.lat
    df["lon"] = location.lon
    return df
