# Versions — Weather Trends Analyzer

## v0.3.1 — Security Documentation + SAST Stage Wiring

### CI green-pipeline fixes (2026-08-28)

- **`sast` failure fixed — vulnerable transitive dependencies.** `pip-audit` was the single failing step in both red runs (32659878026, 32749413247), reporting 22 advisories across 2 packages: `idna 3.11` (PYSEC-2026-215, fixed in 3.15) and `pillow 12.2.0` (21 PYSEC advisories, fixed in 12.3.0). Both are transitive — `idna` via `httpx` → `anyio`, `pillow` via `matplotlib` — so neither has a direct constraint to edit; `uv lock --upgrade-package idna --upgrade-package pillow` moved them to 3.19 and 12.3.0. `uv run --with pip-audit pip-audit` now reports "No known vulnerabilities found". The lock diff touches only those two packages.
- **`docker-build` was unrunnable — unresolvable action reference.** The Trivy step used `aquasecurity/trivy-action@0.28.0`. Upstream tags that action v-prefixed: `0.28.0` exists as neither tag, branch, nor commit (`gh api repos/aquasecurity/trivy-action/commits/0.28.0` → HTTP 422 "No commit found"), while `v0.28.0` resolves. GitHub resolves every `uses:` at job setup, before any step runs, so the job would have died with "Unable to resolve action" the moment it became reachable. It never was: the step landed in 2586279 and every run since has had `docker-build` skipped behind the failing `sast` job, so it has never executed once in CI. Pinned to `@v0.36.0`.
- **Engine choice, not just the typo.** `v0.28.0` pins Trivy v0.56.1, which does not enumerate pip's vendored SBOM at all — it passes the two `.trivyignore` entries vacuously and makes that file inert, a weaker gate than the one documented in section 8a. `v0.36.0` pins Trivy v0.70.0, the engine `.trivyignore` was written against. Verified against the built image: exit 0 with the ignorefile, exit 1 without it, reporting exactly `GHSA-6v7p-g79w-8964` (msgpack 1.1.2) and `CVE-2025-47273` (setuptools 70.3.0) — the two entries, still load-bearing, still accurate.
- **`trivyignores: .trivyignore` now passed explicitly.** The action exports `TRIVY_IGNOREFILE` only when that input is set; otherwise suppression depends on Trivy's implicit `./.trivyignore` lookup relative to the step's working directory. Both paths were verified green against the image; the explicit form is wired so the suppression cannot be silently dropped.
- **Whole-pipeline verification against the fixed tree** (each stage run with its real command, exit code captured unpiped): `ruff check .` clean; Semgrep 0 findings over 47 files / 186 rules with all four configs resolving anonymously exactly as the runner does; gitleaks 0 leaks across full history and both push/PR ranges; 59 tests passing at 100% coverage (288 statements, 0 missed); `uv build` producing sdist + wheel; `docker build` succeeding and Trivy v0.70.0 reporting 0 HIGH/CRITICAL. The `# nosemgrep: dockerfile.security.missing-user.missing-user` suppression was re-confirmed load-bearing — stripping it makes the rule fire as ERROR/blocking and turns the step red.

### CI hardening + dependency remediation (2026-08-24)

- **Semgrep invocation corrected.** The job used `semgrep ci` with `--severity` and `--error`, which that subcommand does not accept — it exits 2 with a usage error before scanning. Switched to `semgrep scan`, which supports both.
- **Release workflow hardened against script injection.** `${{ inputs.bump }}` and `${{ steps.bump.outputs.new_version }}` were interpolated directly into `run:` blocks, where the value becomes shell code. Both now pass through `env:` and are read as quoted shell variables. The input is `type: choice`, so this was not exploitable today — it is the pattern that breaks the moment the input type changes.
- **Base-image security patches in the Dockerfile.** The Debian slim bases ship a `util-linux` that Trivy flags HIGH (CVE-2026-53612..53615, fixed upstream in 2.41.5). Measured directly: `python:3.13-slim` carries 38 fixable HIGH/CRITICAL, `3.12-slim` 36, `3.11-slim` 38, while `nginx:alpine` is clean. These come from the base layer, so an `apt-get upgrade` step is required even where nothing else installs them.
- **`.trivyignore` added** for two findings with no in-image remediation: `CVE-2025-47273` (setuptools 70.3.0) and `GHSA-6v7p-g79w-8964` (msgpack 1.1.2). Both come from pip's vendored manifest in the base image, not from project dependencies — and setuptools 70.3.0 is not even installed (`find` finds nothing; the image ships 84.x). Upgrading pip does not rewrite that manifest. Each entry carries its justification inline.
- **Dockerfile `missing-user` suppressed with written justification**, per global CLAUDE.md section 9 (non-root is not required for personal local-dev containers). The nginx images additionally cannot run as non-root without the unprivileged image and a port change. Revisit before any deployment beyond localhost.


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