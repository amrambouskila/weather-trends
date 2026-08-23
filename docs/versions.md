# Versions — Weather Trends Analyzer

## v0.3.1 — Security Documentation + SAST Stage Wiring

**Date:** 2026-08-20

- Security documentation added:
  - `CLAUDE.md` / `AGENTS.md` section 8a `<security>` — SAST stage requirement, tool set, provider wiring, input-boundary inventory (API response, outbound URL, CLI args, `OUTPUT_DIR`, chart output) with injection classes and defenses, and the Phase 2/3 boundaries that will join the table.
  - `docs/WEATHER_TRENDS_MASTER_PLAN.md` section 10 "Security" (SAST-as-mandatory-stage, pipeline Mermaid diagram, per-component injection-safety principles) plus the two SAST/input-boundary gate lines on every phase gate list.
  - `.codex/commands/pre-commit.md` — SAST audit step and verdict-table row.
- SAST stage wired in `.github/workflows/ci.yml`: new `sast` job (`needs: lint`, `test` now `needs: sast`) running CodeQL, Semgrep (SARIF upload, fails on findings), `gitleaks`, and `pip-audit`; `aquasecurity/trivy-action` (HIGH/CRITICAL, exit-code 1) added to `docker-build`.
- `pyproject.toml`: ruff `S` (flake8-bandit) rules enabled; `S101` added to the `tests/*` per-file-ignores.
- `src/cli.py`: `--start-date` / `--end-date` validated as ISO `YYYY-MM-DD` via `iso_date_argument` (argparse `type=`), so malformed dates are a CLI error instead of being forwarded to the API.
- `weather_trend.py` (legacy prototype): `timeout=30` added to the `requests.get` call (ruff `S113`).
- **Dependency-audit scope correction.** The `sast` job ran `uvx pip-audit`, which audits pip-audit's own isolated tool environment rather than this project's dependencies -- verified locally: `uvx pip-audit` reports 28 packages, `uv run --with pip-audit pip-audit` reports 59. The job would therefore have passed with a known-vulnerable dependency. Changed to `uv run --with pip-audit pip-audit`.
- Tests added for the date validation; suite now 59 tests, 100% coverage.
- Docs corrected to name the real CI provider: the pipeline is GitHub Actions (`.github/workflows/ci.yml`), not GitLab, in `CLAUDE.md` / `AGENTS.md` section 8, the master plan (gantt, Phase 1 deliverables, tech table), and `README.md`. The v0.1.0 entry below refers to `.gitlab-ci.yml`; the file committed was in fact the GitHub workflow.

## v0.3.0 — Analyzer / Visualizer / CLI Extraction (Refactor Complete)

**Date:** 2026-06-08

- Completed the Phase 1 refactor by extracting the remaining logic from the `weather_trend.py` prototype into `src/`:
  - `src/analyzer.py` — `TrendAnalyzer` (yearly anomaly aggregation, 95% CI, `scipy.stats.linregress` trend) and the `AnalysisResult` aggregate. Drops the prototype's SciPy try/except polyfit fallback (SciPy is a hard dependency) and emits a dedicated `mean_anomaly` column instead of overloading `temperature_2m_mean`.
  - `src/visualizer.py` — `TrendVisualizer` renders the trend (with 95% CI) and distribution to `output/temperature_trend.png` at 300 DPI on the headless Agg backend, replacing the prototype's `plt.show()`.
  - `src/cli.py` — `python -m src.cli` entry point (fetch → analyze → visualize → summary report) with `--mock`, `--start-date`, `--end-date`, `--output-dir`; falls back to `MockDataGenerator` on `RateLimitExceededError`. This is the module the `Dockerfile` CMD already targeted.
- Correctness fix: single-location years now report `std`/`se`/`ci95` as `0.0` instead of `NaN`, satisfying the `YearlyAnomaly` contract.
- Added `tests/test_analyzer.py`, `tests/test_visualizer.py`, `tests/test_cli.py` (14 tests). Suite now at 56 tests, 100% coverage maintained.
- `weather_trend.py` and the `COPY weather_trend.py .` line in the `Dockerfile` are now redundant and removable (left for manual git cleanup).

## v0.2.0 — OOP Extraction: Fetcher, Config, Models (Backfilled)

**Date:** 2026-04-26

- Extracted the data and configuration layers from the `weather_trend.py` prototype into `src/`:
  - `src/config.py` — `LOCATIONS` (as `Location` models), API settings, default date range, `OUTPUT_DIR`, `CHART_DPI`.
  - `src/fetcher.py` — `WeatherDataFetcher` on httpx (replacing `requests`), with retry/backoff and `RateLimitExceededError` / `WeatherFetchError`.
  - `src/mock_data.py` — `MockDataGenerator` class form of the synthetic-data generator.
  - `src/models/` — Pydantic v2 contracts: `Location`, `DailyTemperatureRecord`, `YearlyAnomaly`, `TrendResult`.
- Added the pytest suite (httpx `MockTransport` for fetcher tests) at 100% coverage, plus the Codex harness wiring and GitHub CI fixes.
- Released as v0.2.0 (`release: v0.2.0`, 2026-04-26). Changelog entry backfilled in v0.3.0 — it had been omitted at release time.

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