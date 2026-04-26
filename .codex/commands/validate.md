---
name: validate
description: Validate domain code for correctness, completeness, and data-driven compliance
---

# Validate Command

Before anything else:
1. Re-read `AGENTS.md` in full.
2. Re-read `docs/WEATHER_TRENDS_MASTER_PLAN.md`.

## Validation Layers

### 1. Structural Completeness
- All modules in `src/` exist per AGENTS.md Section 5.
- Each module has a corresponding test file in `tests/`.
- `__init__.py` files exist with content.
- Pydantic models defined for all data contracts (Location, DailyTemperatureRecord, YearlyAnomaly, TrendResult).

### 2. Numerical Correctness
- Anomaly calculation: verify formula matches spec (yearly mean - location baseline).
- Trend regression: verify `scipy.stats.linregress` is used (not manual polyfit fallback).
- CI calculation: verify `ci95 = 1.96 * std / sqrt(n)`.
- At least one test validates slope against a known synthetic dataset with documented tolerance.

### 3. Data-Driven Compliance
- Location list lives in `config.py` as Pydantic models, not scattered through code.
- API base URL in `config.py`, not hard-coded in fetcher.
- Date ranges configurable, not hard-coded.
- No magic numbers in analysis code (explain any literal that isn't 0, 1, 2, or pi).

### 4. Performance Compliance
- No Python `for` loops over daily temperature records in hot paths.
- pandas groupby/agg used for aggregation, not iterrows.
- numpy vectorized operations where applicable.

### 5. Reference Validation
- Check that at least one test compares computed results against:
  - A known analytical solution (e.g., synthetic data with exact 0.02 degC/year trend).
  - Or a published reference value.
- Report which tests serve as reference validations.

## Output

Report findings per layer. Do NOT auto-fix. Flag issues for the user to address.