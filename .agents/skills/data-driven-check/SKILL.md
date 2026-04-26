---
name: data-driven-check
description: Proactively applied when writing any analysis, fetching, or visualization code; flags hard-coded domain values that should come from config or data
---

# Data-Driven Check Skill

## When to Apply
- When editing any file in `src/` (especially `fetcher.py`, `analyzer.py`, `visualizer.py`, `mock_data.py`).
- When adding new functionality that references locations, dates, API endpoints, or physical parameters.

## Protocol

### Before writing code, verify:

1. **No hard-coded locations.** Latitude, longitude, and city names must come from `config.py` via the `Location` Pydantic model. Never scatter `40.7128` or `"New York"` through analysis code.

2. **No hard-coded API URLs.** The Open-Meteo base URL lives in `config.py`. Fetcher reads it from there.

3. **No hard-coded date ranges.** Start date (1940-01-01) and end date (2025-12-31) are config values, not string literals in fetcher/analyzer code. Tests may use specific dates — that's acceptable.

4. **No magic numbers in analysis:**
   - `1.96` (z-score for 95% CI) — acceptable as a named constant or inline with comment.
   - `52/12` or `365.25` — acceptable as standard calendar constants.
   - `0.02` (trend rate) — only in mock data generator and tests, never in analysis code.
   - `30` (days per month) — only in mock data, not in analysis.
   - Anything else: name it or source it from config.

5. **No hard-coded output paths.** Chart save paths come from config or CLI arguments.

### After writing code, grep for:
- Raw float literals that look like coordinates (e.g., `40.71`, `-74.00`, `51.50`)
- URL strings containing `open-meteo`
- Date strings matching `YYYY-MM-DD` pattern outside of tests and config
- Unnamed numerical constants in formulas