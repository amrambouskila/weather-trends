from __future__ import annotations

from pydantic import BaseModel, Field


class YearlyAnomaly(BaseModel):
    """Global mean temperature anomaly for a single year, aggregated across locations."""

    year: int = Field(ge=1800, le=2200)
    mean_anomaly: float
    std: float = Field(ge=0.0)
    n: int = Field(ge=1)
    se: float = Field(ge=0.0)
    ci95: float = Field(ge=0.0)
