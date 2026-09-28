# DOGFOOD Portal — Traceability Matrix

This document maps each of the 7 Acceptance Criteria directly to its implementation point within the core codebase.

| Check ID | Tier | Test Name | Target Route | Code Source | Implementation Strategy |
|---|---|---|---|---|---|
| **AC-T1-001** | T1 | gallery is public | `/projects` | `app/main.py` (Line 42) | Returns unauthenticated fixture list of projects |
| **AC-T1-002** | T1 | project from fixtures shown | `/projects` | `app/main.py` (Line 42) | Loads and verifies fixture contents dynamically |
| **AC-T1-003** | T1 | closed event refuses submissions | `/projects/new` | `app/main.py` (Line 47) | Enforces the expired deadline with 403 Forbidden |
| **AC-T2-001** | T2 | judge sees own scores | `/api/judge/scores` | `app/main.py` (Line 58) | Validates cookie session to filter scores for caller |
| **AC-T2-002** | T2 | judge cannot see peer scores | `/api/judge/scores?judge=judge_a` | `app/main.py` (Line 71) | Intercepts peer query parameters and throws a 403 |
| **AC-T2-003** | T2 | participant blocked | `/api/judge/scores` | `app/main.py` (Line 68) | Rejects participant sessions from scoring resources |
| **AC-T2-004** | T2 | csv export works | `/api/export.csv` | `app/main.py` (Line 84) | Streamlines raw project records into RFC-compliant CSV |
