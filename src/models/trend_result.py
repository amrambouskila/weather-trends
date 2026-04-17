from __future__ import annotations

from pydantic import BaseModel, Field


class TrendResult(BaseModel):
    """Linear regression result for a yearly anomaly time series."""

    slope: float
    intercept: float
    r_squared: float = Field(ge=0.0, le=1.0)
    p_value: float = Field(ge=0.0, le=1.0)
    slope_unit: str = "degC/year"
