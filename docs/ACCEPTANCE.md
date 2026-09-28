# DOGFOOD Portal — Acceptance Specification

## Status

The source defines seven machine checks: three for T1 and four for T2. `run.py` is the authoritative executable specification, but it is not present. This document records every behavior stated in the available material and marks missing protocol details as TBD.

## Common preconditions

1. Portal starts from a seeded state with `docker compose up`.
2. The fixture event and identities are loaded.
3. `.dogfood.toml` contains the portal base URL, tier claims, four auth headers, and route mappings.
4. The checker can reach the local portal.
5. Exact request bodies and parsing rules come from `run.py` when supplied.

## AC-T1-001 — Gallery is public

| Field | Specification |
|---|---|
| Purpose | Verify unauthenticated public access. |
| Preconditions | Portal running; `routes.gallery` configured. |
| Input | No authentication header. |
| Request | Base URL + configured gallery route; exact method defined by `run.py` (absent). |
| Expected response | Publicly accessible gallery representation. Exact status/media type TBD. |
| Expected state | No state mutation. |
| Failure condition | Authentication required, route unreachable, or checker rejects response. |
| Related requirements | FR-008, TR-012, AZ-001 |
| Related test | TC-T1-001 |
| Source | `main.tex` § All seven machine checks |

## AC-T1-002 — Fixture projects shown

| Field | Specification |
|---|---|
| Purpose | Verify fixture seed integrity and gallery integration. |
| Preconditions | AC-T1-001; fixture data loaded. |
| Input | No authentication header. |
| Request | Configured gallery request. |
| Expected response | Contains the fixture projects expected by `run.py`. Exact identifiers/content absent. |
| Expected state | No mutation. |
| Failure condition | Fixture projects missing or response not parseable by checker. |
| Related requirements | FR-009, TR-002, TR-030 |
| Related test | TC-T1-002, TC-FIX-001 |
| Source | Acceptance and fixture sections |

## AC-T1-003 — Closed event refuses submissions

| Field | Specification |
|---|---|
| Purpose | Verify server-side deadline enforcement. |
| Preconditions | Fixture event loaded with its own `submissions_close`; `routes.submit` configured; required actor/header and payload available to checker. |
| Input | Checker fixture submission request. Exact payload absent. |
| Request | Configured submission route; exact method/body defined by `run.py`. |
| Expected response | Submission is refused. Exact status/body TBD. |
| Expected state | No accepted post-close submission is created/updated. |
| Failure condition | Request is accepted or source timestamp was replaced by a generated date. |
| Related requirements | FR-007, NFR-008, TR-013, TR-029 |
| Related test | TC-T1-003, TC-FIX-002 |
| Source | Acceptance checker and fixture date warning |

## AC-T2-001 — Judge sees own scores

| Field | Specification |
|---|---|
| Purpose | Verify authorized judge score access. |
| Preconditions | Judge fixture identity and score records loaded; `routes.judge_scores` configured. |
| Input | Appropriate judge auth header. |
| Request | Configured judge-score route; exact method/parameters defined by `run.py`. |
| Expected response | Authenticated judge's own score records. Exact schema/status TBD. |
| Expected state | No mutation for retrieval. |
| Failure condition | Judge cannot retrieve own expected scores or receives peer data. |
| Related requirements | FR-012, TR-014, TR-024 |
| Related test | TC-AUTHZ-001 |
| Source | T2 acceptance checks |

## AC-T2-002 — Judge cannot see peer scores

| Field | Specification |
|---|---|
| Purpose | Verify backend object-level isolation. |
| Preconditions | Distinct `judge_a` and `judge_b`; peer-targeting route configured. |
| Input | Authenticate as `judge_b`; target `judge_a` scores. |
| Request | Base URL + `routes.peer_scores`; sample `/api/judge/scores?judge=judge_a`. Exact method defined by checker. |
| Expected response | `401 Unauthorized` or `403 Forbidden`; no peer score data. |
| Expected state | No mutation. |
| Failure condition | `200`, peer score data, or authorization enforced only in UI. |
| Related requirements | FR-013, NFR-004, TR-023, TR-025, AZ-004/005 |
| Related test | TC-AUTHZ-002 |
| Source | Critical authorization section |

## AC-T2-003 — Participant blocked

| Field | Specification |
|---|---|
| Purpose | Verify participant cannot access judge-only behavior/data. |
| Preconditions | Participant identity and judge route/resource available. |
| Input | Participant auth header. |
| Request | Exact route/method/body defined by `run.py`; likely reuses a judge route, but this is unverified. |
| Expected response | Denial and no protected data. Exact status TBD. |
| Expected state | No protected mutation. |
| Failure condition | Participant receives judge data or performs judge action. |
| Related requirements | FR-014, TR-023, TR-026 |
| Related test | TC-AUTHZ-003 |
| Source | T2 acceptance checks |

## AC-T2-004 — CSV export works

| Field | Specification |
|---|---|
| Purpose | Verify data portability endpoint. |
| Preconditions | Seeded data; `routes.csv_export` configured; required checker header known. |
| Input | Exact actor/parameters defined by `run.py`; unavailable. |
| Request | Configured CSV route; exact method TBD. |
| Expected response | Functioning CSV accepted by checker. Schema/status/media type assertions TBD. |
| Expected state | No mutation expected. |
| Failure condition | Route error, unauthorized under checker actor, malformed CSV, or checker rejection. |
| Related requirements | FR-018, TR-016, TR-041 |
| Related test | TC-CSV-001 |
| Source | T2 acceptance checks |

## Manual acceptance areas

T3 and T4 are judged manually. No detailed manual protocol is supplied. Manual review should verify claimed features only and apply the source's “correctness over breadth” and honest-gap principles.

## Acceptance report

The actual checker output must be committed as `acceptance-report.txt`, including failures. Do not replace failures with README claims. The checker/report format is unavailable until `run.py` is supplied.

## Traceability summary

| Check | Requirement | Test |
|---|---|---|
| AC-T1-001 | FR-008 | TC-T1-001 |
| AC-T1-002 | FR-009 | TC-T1-002 |
| AC-T1-003 | FR-007 | TC-T1-003 |
| AC-T2-001 | FR-012 | TC-AUTHZ-001 |
| AC-T2-002 | FR-013 | TC-AUTHZ-002 |
| AC-T2-003 | FR-014 | TC-AUTHZ-003 |
| AC-T2-004 | FR-018 | TC-CSV-001 |

## Blockers to exact acceptance documentation

- `run.py` absent;
- `.dogfood.toml` absent;
- `fixtures.json` absent;
- portal implementation absent;
- Compose configuration absent.