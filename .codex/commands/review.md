---
name: review
description: Review changed code against project standards
---

# Review Command

Before anything else:
1. Re-read `AGENTS.md` in full.
2. Re-read `docs/WEATHER_TRENDS_MASTER_PLAN.md`.

## Steps

1. Run `git diff` to see all changed files.
2. Read every changed file in full.
3. Produce a checklist-style report with file:line references and severity.

## Checklist

For each changed file, check:

### Critical (blocks commit)
- [ ] Type annotations on all function signatures
- [ ] No `Any` without justification
- [ ] No bare `except:` clauses
- [ ] No hard-coded domain values (locations, URLs, dates) outside `config.py`
- [ ] No `requests` usage (must be `httpx`)
- [ ] No `plotly` usage (must be `seaborn` + `matplotlib`)
- [ ] No dead code or commented-out blocks
- [ ] No `# TODO` without linked task
- [ ] Corresponding test file exists and covers new logic
- [ ] Pydantic models unchanged without approval

### Should-fix
- [ ] Docstrings on public functions
- [ ] Numerical comparisons use `np.testing.assert_allclose` (not `==`)
- [ ] Explicit numpy dtypes on array operations
- [ ] Chart output uses 300 DPI, saves to `output/`
- [ ] `from __future__ import annotations` at module top

### Minor
- [ ] Naming follows conventions (snake_case functions, PascalCase classes)
- [ ] Import ordering (ruff handles this)
- [ ] Line length <= 120

## Output

Do NOT fix anything automatically. Report findings only. Let the user decide what to address.