from __future__ import annotations

from pydantic import BaseModel, Field


class Location(BaseModel):
    """A geographic point identified by name and WGS84 coordinates (decimal degrees)."""

    name: str = Field(min_length=1)
    lat: float = Field(ge=-90.0, le=90.0)
    lon: float = Field(ge=-180.0, le=180.0)
