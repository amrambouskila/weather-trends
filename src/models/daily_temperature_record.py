from __future__ import annotations

from pydantic import BaseModel, Field


class DailyTemperatureRecord(BaseModel):
    """One daily temperature observation for a single location, as returned by Open-Meteo."""

    time: str = Field(min_length=1)
    temperature_2m_mean: float | None
    location: str = Field(min_length=1)
    lat: float = Field(ge=-90.0, le=90.0)
    lon: float = Field(ge=-180.0, le=180.0)
