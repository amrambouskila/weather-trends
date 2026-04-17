# Versions — Weather Trends Analyzer

## v0.1.1 — Mock Seasonal Phase Fix

**Date:** 2026-04-16

- Fixed `MockDataGenerator` seasonal signal in `src/mock_data.py`: switched from `sin(2π·doy/365.25)` (peak in April, trough in October — wrong for winter/summer) to `-hemisphere_sign · cos(2π·doy/365.25)`, which peaks mid-year in the northern hemisphere and is orthogonal to `frac_year`.
- Removed now-unused `SOUTHERN_HEMISPHERE_PHASE_SHIFT_DAYS` constant.
- Resolves `test_hemisphere_seasonality_opposite_phase` (phase was inverted) and `test_trend_signal_is_recoverable` (seasonal/time correlation was biasing the fitted slope to ~half of planted).

## v0.1.0 — Project Infrastructure Scaffolding

**Date:** 2026-04-13

- Scaffolded full project infrastructure: `CLAUDE.md`, `README.md`, `docs/`, `.claude/`, Docker, CI/CD, launcher scripts.
- Created `pyproject.toml` with all dependencies (httpx, pandas, numpy, scipy, seaborn, matplotlib, pydantic).
- Created `Dockerfile` (python:3.13-slim) and `docker-compose.yml`.
- Created `.gitlab-ci.yml` with lint, test, coverage, build, docker-build stages.
- Created launcher scripts (`run_weather_trends.sh`, `run_weather_trends.bat`) with `[k]/[q]/[v]/[r]` loop.
- Original `weather_trend.py` prototype retained as reference; refactor into `src/` is the next task.