# Versions — Weather Trends Analyzer

## v0.1.0 — Project Infrastructure Scaffolding

**Date:** 2026-04-13

- Scaffolded full project infrastructure: `CLAUDE.md`, `README.md`, `docs/`, `.claude/`, Docker, CI/CD, launcher scripts.
- Created `pyproject.toml` with all dependencies (httpx, pandas, numpy, scipy, seaborn, matplotlib, pydantic).
- Created `Dockerfile` (python:3.13-slim) and `docker-compose.yml`.
- Created `.gitlab-ci.yml` with lint, test, coverage, build, docker-build stages.
- Created launcher scripts (`run_weather_trends.sh`, `run_weather_trends.bat`) with `[k]/[q]/[v]/[r]` loop.
- Original `weather_trend.py` prototype retained as reference; refactor into `src/` is the next task.