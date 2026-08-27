# Status — Weather Trends Analyzer

**Phase:** 1 — CLI Script
**Last updated:** 2026-08-28

## Current State

Phase 1 refactor **complete**. The `weather_trend.py` monolith has been fully extracted into `src/`:

- **Data layer (v0.2.0):** `config.py` (`LOCATIONS`, API settings, `OUTPUT_DIR`, `CHART_DPI`), `fetcher.py` (`WeatherDataFetcher` on httpx, retry/backoff, `RateLimitExceededError`), `mock_data.py` (`MockDataGenerator`), `models/` (Pydantic v2: `Location`, `DailyTemperatureRecord`, `YearlyAnomaly`, `TrendResult`).
- **Analysis (v0.3.0):** `analyzer.py` — `TrendAnalyzer` computes yearly anomalies + 95% CI and fits the trend via `scipy.stats.linregress`, returning an `AnalysisResult` aggregate (frozen dataclass co-located with its producer).
- **Visualization (v0.3.0):** `visualizer.py` — `TrendVisualizer` saves the trend (with 95% CI) and distribution to `output/temperature_trend.png` at 300 DPI on the headless Agg backend. No more `plt.show()`.
- **Entry point (v0.3.0):** `cli.py` — `python -m src.cli` orchestrates fetch → analyze → visualize → summary report, with `--mock`, `--start-date`, `--end-date` (ISO-validated via `iso_date_argument`), `--output-dir`. Falls back to `MockDataGenerator` on a rate-limit error.

59 tests pass at 100% coverage. The `Dockerfile` CMD (`python -m src.cli`) now resolves — previously it pointed at a module that did not exist.

The original `weather_trend.py` prototype is now redundant. It and the `COPY weather_trend.py .` line in the `Dockerfile` are safe to delete; left in place for manual git cleanup (git is user-managed).

## Security

### Verified state (2026-08-28)

Every CI stage was reproduced locally against the current tree, each with its real command and its exit code captured unpiped:

- **`lint` — clean.** `ruff check .` (select includes `S`) passes.
- **`sast` — clean.** Semgrep: 0 findings over 47 files / 186 rules, with all four configs (`auto`, `p/owasp-top-ten`, `p/python`, `p/docker`) resolving anonymously — matching the runner, which sets no `SEMGREP_APP_TOKEN`, so `auto` contributes no registry-only rules there either. gitleaks: 0 leaks across full history and across both the push and PR commit ranges the action actually scans. `pip-audit`: "No known vulnerabilities found" after the `idna` / `pillow` lock bump described in `versions.md`.
- **`test` / `build` — clean.** 59 tests at 100% coverage (288 statements, 0 missed); `uv build` produces sdist + wheel.
- **`docker-build` — clean, and reachable for the first time.** The image builds, and Trivy v0.70.0 — the engine `aquasecurity/trivy-action@v0.36.0` pins — reports 0 HIGH/CRITICAL with `--ignore-unfixed` and the repo `.trivyignore`. This job had never executed in CI: its Trivy step carried an unresolvable action ref, and the job was skipped behind the failing `sast` job on every run since the step was added.
- **Both suppressions re-verified load-bearing, not stale.** Stripping the `# nosemgrep: dockerfile.security.missing-user.missing-user` comment makes that rule fire as ERROR/blocking on the `CMD` line. Removing `.trivyignore` turns the Trivy scan red with exactly its two documented entries, `GHSA-6v7p-g79w-8964` (msgpack 1.1.2) and `CVE-2025-47273` (setuptools 70.3.0).
- CodeQL is the one stage not reproducible locally; it has passed on every run, including the two red ones.

### Known CI gaps (identified 2026-08-28, not fixed — none blocks a green pipeline today)

- **The image does not use the audited lock.** The `Dockerfile` copies only `pyproject.toml` and runs `uv sync --no-dev`, so it resolves fresh from PyPI at build time. The dependency set that ships is therefore not the set `pip-audit` gates, and it already drifts from `uv.lock` (e.g. matplotlib 3.11.1 in-image vs 3.10.8 locked). Copying `uv.lock` and using `uv sync --frozen --no-dev` would close it.
- **Two unpinned CI tool versions** resolve at run time and can turn a stage red with no repo change: `gitleaks-action` sets no `GITLEAKS_VERSION` (currently resolves 8.30.1), and the same class of drift applies to any fresh transitive resolve. Dependabot on the `uv` ecosystem would surface lockfile advisories as PRs instead of as pipeline failures.
- **The documented local gitleaks parity command is noisy.** `gitleaks detect --no-git --redact` (section 8a) does not honour `.gitignore`, so it walks the local `.venv` and reports 6 generic-api-key hits in numpy's PRNG test vectors. CI is unaffected — the action never passes `--no-git`, and no `.venv` exists in a fresh checkout — but the command as written exits 1 on a clean workstation.
- **The Semgrep gate has a confusing failure mode.** If Semgrep ever exits nonzero *before* writing `semgrep.sarif`, the intervening `upload-sarif` step fails first, so the job still goes red but surfaces "SARIF file not found" instead of the real cause.
- **Deprecation warnings, not yet failures:** `actions/checkout@v4`, `actions/setup-python@v5`, and `gitleaks-action@v2` run on Node 20 (forced onto Node 24), and CodeQL Action v3 is deprecated in December 2026.

- Requirements documented in `CLAUDE.md` / `AGENTS.md` section 8a `<security>` (SAST stage, input-boundary inventory, injection-class defenses) and master plan section 10; SAST + input-boundary gate lines on every phase gate list.
- Wired: `sast` job in `.github/workflows/ci.yml` (CodeQL, Semgrep SARIF, gitleaks, pip-audit; `lint -> sast -> test`), Trivy in `docker-build`, ruff `S` rules in `pyproject.toml`, ISO validation of `--start-date`/`--end-date` in `cli.py`, `timeout=30` on the legacy prototype's request.
- Pending (later phases only): Phase 2 Streamlit allowlist/validation boundaries; Phase 3 ESLint security plugins, `pnpm audit`, and nginx CSP headers if a React frontend is introduced.

## What's Next

1. Delete `weather_trend.py` and remove the `COPY weather_trend.py .` line from the `Dockerfile` (user git cleanup).
2. Close the image/lock gap: `COPY uv.lock` and switch to `uv sync --frozen --no-dev` so the container ships the dependency set `pip-audit` actually gates. See "Known CI gaps" above.
3. Validate the Docker build runs `python -m src.cli` end-to-end and produces `output/temperature_trend.png`.
4. *(Optional, deferred)* Expand visualization to the full set in CLAUDE.md §9 — per-city comparison and decade-average bar chart.
5. **Phase 2:** Streamlit dashboard for interactive exploration (date range, city filtering), per the master plan.

## Architectural Decisions

- **httpx** replaces `requests` for the HTTP client (modern, async-capable).
- **seaborn + matplotlib** for visualization (preferred over plotly); headless **Agg** backend, charts saved to `output/` — never `plt.show()`.
- **pandas** for DataFrames (preferred over polars).
- **Pydantic v2** for data models and configuration.
- **scipy.stats.linregress** for the trend fit — a hard dependency, so no homegrown fallback.
- **uv** for package management.
- `AnalysisResult` is a frozen dataclass co-located in `analyzer.py` (its producer) — an internal aggregate, not a cross-service wire contract.
