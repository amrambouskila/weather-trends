"""Pydantic data contracts — one model per file, re-exported here for ergonomic imports."""

from __future__ import annotations

from src.models.daily_temperature_record import DailyTemperatureRecord
from src.models.location import Location
from src.models.trend_result import TrendResult
from src.models.yearly_anomaly import YearlyAnomaly

__all__ = [
    "DailyTemperatureRecord",
    "Location",
    "TrendResult",
    "YearlyAnomaly",
]
