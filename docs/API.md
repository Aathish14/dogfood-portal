# DOGFOOD Portal — API and HTTP Interface Specification

## Status

No API implementation or `run.py` is present. The source defines **checker route keys** and sample paths, not a complete HTTP API contract. It also provides a separate **advisory proposed route set** for a possible implementation. This document keeps those categories separate.

## Contract classifications

- **CHECKER-REQUIRED:** a route location must be declared in `.dogfood.toml`; exact method/schema may depend on absent `run.py`.
- **SOURCE-DEFINED OUTCOME:** behavior explicitly required by acceptance material.
- **PROPOSED:** advisory route from `main.tex`; not an implemented endpoint.
- **TBD:** insufficient information.

## Authentication

The checker attaches one configured header value from `.dogfood.toml`:

- `organizer`
- `judge_a`
- `judge_b`
- `participant`

The sample uses `Cookie: session=...`, but header format and login/session mechanism are implementation-defined. Interactive login is not part of checker execution.

## Checker-discoverable route contracts

### `routes.gallery`

| Field | Specification |
|---|---|
| Classification | CHECKER-REQUIRED |
| Sample path | `/projects` |
| Method | TBD; determined by `run.py` (absent). The advisory API example uses GET. |
| Purpose | Public gallery and fixture-project visibility. |
| Authentication | None for the acceptance request. |
| Required role | Anonymous/public. |
| Authorization | Must not require authentication. |
| Parameters | TBD. |
| Request body | None expected for a retrieval operation, but authoritative checker contract is absent. |
| Response body | Project/gallery representation; media type/schema TBD. |
| Status codes | Exact expected status is in `run.py`; must be treated as publicly accessible. |
| Validation | N/A for read; filtering/pagination TBD. |
| Side effects | None expected. |
| Audit behavior | Not specified. |
| Acceptance checks | AC-T1-001, AC-T1-002. |

### `routes.submit`

| Field | Specification |
|---|---|
| Classification | CHECKER-REQUIRED |
| Sample path | `/projects/new` |
| Method | TBD; determined by `run.py`. |
| Purpose | Exercise project submission and closed-event refusal. |
| Authentication | Participant header for protected submission behavior; exact checker actor TBD. |
| Required role | Participant for ordinary submission. |
| Authorization | Participant/team ownership and event state; ownership mechanism recommended, exact checker rule absent. |
| Parameters | Event/project fields TBD. |
| Request body | Exact fixture payload absent. |
| Response body | TBD. |
| Status codes | Closed event must refuse; exact code is defined by absent `run.py`. |
| Validation | Must use fixture event's exact `submissions_close` and authoritative server state. |
| Side effects | Before close, may create/update submission; after close, must not accept the submission. |
| Audit behavior | Recommended for submission transitions; not baseline-specified. |
| Acceptance check | AC-T1-003. |

### `routes.judge_scores`

| Field | Specification |
|---|---|
| Classification | CHECKER-REQUIRED |
| Sample path | `/api/judge/scores` |
| Method | TBD; determined by `run.py`. Advisory example uses GET. |
| Purpose | Retrieve the authenticated judge's scores. |
| Authentication | Judge header, such as `judge_a`. |
| Required role | Judge. |
| Authorization | Return only score records owned by/assigned to the authenticated judge. |
| Parameters | TBD. |
| Request/response schemas | TBD; score schema absent. |
| Status codes | Success expectation defined by `run.py`; exact code/body absent. |
| Side effects | None for retrieval. |
| Audit behavior | Not specified; access logging optional/recommended. |
| Acceptance check | AC-T2-001. |

### `routes.peer_scores`

| Field | Specification |
|---|---|
| Classification | CHECKER-REQUIRED; critical SOURCE-DEFINED OUTCOME |
| Sample path | `/api/judge/scores?judge=judge_a` |
| Method | TBD; advisory example implies GET. |
| Purpose | Attempt cross-judge score access. |
| Authentication | The checker uses `judge_b` while targeting `judge_a`. |
| Required role | Judge, but object ownership fails. |
| Authorization | The authenticated judge may not read the targeted peer's scores. |
| Parameters | Sample query parameter `judge=judge_a`; actual path/query is implementation-defined and configured. |
| Request body | None expected; authoritative checker contract absent. |
| Response body | Must not contain peer score data. Error schema TBD. |
| Status codes | **Must be `401` or `403`; `200` is failure.** |
| Side effects | None. |
| Audit behavior | Recommended security event; not baseline-specified. |
| Acceptance check | AC-T2-002. |

### Participant-blocked request

The T2 checker includes a participant-blocked test, but `.dogfood.toml` has no separate route key for it. It likely reuses a judge route; exact route, method, body, and expected status are defined only by the absent `run.py`.

| Field | Specification |
|---|---|
| Authentication | `participant` header |
| Authorization | Participant must be denied judge-only data/behavior |
| Response | No protected score data; exact status/schema TBD |
| Acceptance check | AC-T2-003 |

### `routes.csv_export`

| Field | Specification |
|---|---|
| Classification | CHECKER-REQUIRED |
| Sample path | `/api/export.csv` |
| Method | TBD; advisory example uses GET. |
| Purpose | Return a functioning CSV export. |
| Authentication | Checker header/role not stated in the slide material; `.dogfood.toml` includes organizer credentials. |
| Required role | TBD. Organizer is recommended. |
| Authorization | Must follow selected export policy. |
| Parameters | Event/filter parameters TBD. |
| Request body | None expected for GET proposal; authoritative contract absent. |
| Response body | CSV; schema and row model TBD. |
| Status codes | Exact checker expectation absent. |
| Validation | Must produce syntactically valid CSV. |
| Side effects | None expected. |
| Audit behavior | Recommended for sensitive exports; not specified. |
| Acceptance check | AC-T2-004. |

## Advisory proposed endpoint inventory

These routes appear in `main.tex` under `IMPLEMENTATION GUIDANCE`. They are not existing or source-mandated paths.

| Method | Proposed path | Purpose | Proposed role | Status |
|---|---|---|---|---|
| GET | `/projects` | Public gallery | Public | Proposed/sample |
| POST | `/events/{id}/projects` | Create a team-owned project inside the window | Participant | Proposed |
| POST | `/events/{id}/submit` | Finalize/submit a project | Participant | Proposed |
| GET | `/judge/assignments` | List authenticated judge's assignments | Judge | Proposed |
| GET | `/judge/scores` | List authenticated judge's scores | Judge | Proposed |
| PUT | `/judge/reviews/{id}` | Save/submit an authorized review | Judge | Proposed |
| GET | `/organizer/progress` | Judging progress | Organizer | Proposed |
| POST | `/organizer/normalizations` | Run normalization | Organizer | Proposed |
| POST | `/organizer/results/publish` | Publish results | Organizer | Proposed |
| GET | `/api/export.csv` | CSV export | Organizer/checker | Proposed/sample |

Request/response schemas, validation, status codes, pagination, filtering, and audit behavior for all proposed routes are TBD.

## Tier 4 REST API requirements

When T4/API First is implemented:

1. Every UI action is available through a documented API for the bonus claim.
2. The same authentication/authorization policies apply to UI and API.
3. OpenAPI documents paths and schemas.
4. API versioning, pagination, errors, idempotency, bulk validation, and deprecation require decisions.

## Error model

No general error schema is source-defined. The only exact status rule is peer-score denial (`401` or `403`). A future implementation should define a stable error object and document it in `openapi.yaml`.

## API versioning

No versioning decision exists. See ADR-009.

## Open questions

Methods and payloads used by `run.py`, all resource schemas, organizer access policy, export authorization, error body, pagination, filtering, versioning, idempotency, and API-client credentials.