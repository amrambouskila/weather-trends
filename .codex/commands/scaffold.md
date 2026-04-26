---
name: scaffold
description: Scaffold a new module or component for the weather-trends project
---

# Scaffold Command

Before anything else:
1. Re-read `AGENTS.md` in full.
2. Re-read `docs/WEATHER_TRENDS_MASTER_PLAN.md`.
3. Confirm the task scope with the user.

## Steps

1. **Identify what is being scaffolded** — a new module in `src/`, a new test file, or a new infrastructure component.

2. **For a new `src/` module:**
   - Create the module file in `src/` with:
     - `from __future__ import annotations` at the top.
     - Module docstring describing its purpose.
     - All function/class signatures with full type annotations.
     - Docstrings on public functions (one-line, with array shape/dtype/units where applicable).
     - NO implementation logic — signatures, types, and docstrings only.
   - Create the corresponding test file in `tests/` mirroring the module name (`src/foo.py` → `tests/test_foo.py`).
   - Add any new Pydantic models to the appropriate location.

3. **For infrastructure:**
   - Follow the project skeleton in AGENTS.md Section 5.
   - Use existing files as templates (adapt, don't copy blindly).

4. **Report** the files created and wait for review before implementing logic.

## Rules
- Do NOT implement business logic during scaffolding — signatures and types only.
- Do NOT create empty placeholder files — every file must have real content (at minimum, imports and typed signatures).
- Ensure `__init__.py` files exist and contain at least a module docstring.