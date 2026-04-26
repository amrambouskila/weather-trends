---
name: phase-awareness
description: Proactively applied at session start and before any implementation work; orients Codex to the current phase and its explicit scope constraints
---

# Phase Awareness Skill

## When to Apply
- At session start, after reading `AGENTS.md` and `docs/status.md`.
- Before implementing any new feature or module.

## Protocol

1. **Identify the current phase** from `docs/status.md` and `AGENTS.md` Section 2.

2. **Enforce phase boundaries:**
   - **Phase 1 (CLI Script):** Only CLI-based analysis. No web UI, no database, no scheduled tasks. Output is PNG charts to `output/`.
   - **Phase 2 (Streamlit):** Web dashboard allowed. No database, no REST API, no scheduled collection.
   - **Phase 3 (FastAPI + DB):** Full stack. PostgreSQL, Redis, scheduled collection all in scope.

3. **Block out-of-phase work:**
   - If Phase 1: reject Streamlit components, FastAPI routes, database models, SQLAlchemy usage.
   - If Phase 2: reject FastAPI routes, database models, scheduled tasks.
   - Flag any import or code pattern that belongs to a future phase.

4. **Forward-compatibility check:**
   - Every data model and interface should be evaluated: "Will this still work in the next phase?"
   - Location config → must be loadable from both file and database.
   - Analyzer → must accept DataFrame from any source (API, mock, database query).
   - Visualizer → must work for both file output and in-browser rendering.