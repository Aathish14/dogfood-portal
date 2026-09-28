# DOGFOOD Portal — Product Requirements Document

## Document status

| Field | Value |
|---|---|
| Status | Requirements baseline derived from supplied source materials |
| Product implementation | Not present in the repository; implementation status is unverified |
| Primary source | `main.tex` |
| Supporting sources | `proofrank_solution.tex`, `proofrank_appendix.tex`, `Copy-of-DogFood-2026-Kickoff.pdf` |
| Missing referenced sources | `fixtures.json`, `run.py`, `.dogfood.toml`, Docker Compose configuration, and `main (2).tex` |
| Date | 2026-09-27 |

## Source classification

- **Source-defined:** stated as an official requirement in the kickoff-derived material.
- **Implementation-defined:** required capability whose concrete mechanism is deliberately left to the implementation.
- **Inferred:** a necessary interpretation, explicitly identified as such.
- **Recommended:** guidance from sections labeled `IMPLEMENTATION GUIDANCE`; not an additional competition rule.
- **Unknown / TBD:** not established by the supplied repository.

## Product overview

DOGFOOD requires a working, open-source hackathon submission and judging portal that an organizer can run locally with `docker compose up`, on a laptop, with the network disconnected. The product must connect registration, teams, submissions, eligibility, judging, normalization, results, and export into one operational system.

Tier 1 is a gate. Tier 2 is the central judging capability. Tiers 3 and 4 add public participation and platform/extensibility features.

## Problem statement

The source identifies four deficiencies in existing hackathon platforms:

1. Judging criteria cannot be weighted adequately, forcing spreadsheet-based judging.
2. Score normalization is advertised without transparent mathematics.
3. Community voting is vulnerable to manipulation.
4. Public APIs are absent, leaving organizers dependent on scraping and CSV downloads.

The product must replace fragmented and opaque event tooling with an integrated, inspectable, locally operable portal.

## Product goals

| ID | Goal |
|---|---|
| PG-001 | Provide one integrated portal for the complete hackathon lifecycle. |
| PG-002 | Make judging correct, secure, transparent, and defensible. |
| PG-003 | Run locally and offline from a seeded state using Docker Compose. |
| PG-004 | Make foundational behavior machine-verifiable through the supplied checker contract. |
| PG-005 | Produce an adoptable open-source system that another operator can understand and run. |
| PG-006 | Prefer correct, complete lower-tier functionality over partially implemented higher-tier functionality. |

## Non-goals

| ID | Non-goal |
|---|---|
| NG-001 | A design mockup or frontend backed by hardcoded data. |
| NG-002 | A product that requires a cloud account, hosted database, or hosted authentication provider. |
| NG-003 | An authentication demonstration that stops at the login screen. |
| NG-004 | A gallery without judging, or judging without a gallery. |
| NG-005 | Authorization enforced only by hiding frontend controls. |
| NG-006 | Closed-source software or a non-OSI license. |
| NG-007 | A renamed or superficial rewrite of an existing platform. |
| NG-008 | Undocumented generated code whose architecture and schema cannot be defended. |

## Target users and actors

| Actor | Source-defined need |
|---|---|
| Anonymous visitor | View the public gallery and fixture projects without authentication. |
| Participant | Register/authenticate, form or join a team, and submit a team-owned project within the event window. |
| Judge | Receive assignments, score assigned projects, and retrieve only that judge's scores. |
| Organizer | Create and operate events, configure judging, monitor progress, calculate results, and export data. |
| Community voter/commenter | Tier 3 actor who votes or comments under anti-abuse and result-visibility controls. |
| API client / webhook consumer | Tier 4 actor; exact identity and credential model are TBD. |
| Acceptance checker | Non-human actor that uses configured routes and pre-supplied authentication headers. |

## User personas

The source does not define named personas. The following role personas are inferred directly from required workflows:

- **Event organizer:** needs predictable offline startup, event configuration, assignment progress, transparent results, and exportability.
- **Participant/team member:** needs clear ownership and deadline behavior and must not receive judging data.
- **Judge:** needs an efficient assigned-review workflow and strong isolation from peer scores.
- **Public visitor:** needs unauthenticated gallery access without premature result disclosure.
- **Maintainer/evaluator:** needs reproducible startup, fixtures, documentation, and machine-verifiable behavior.

## User journeys

### Organizer journey

1. Start the seeded portal locally and offline.
2. Create or inspect an event and configure its windows and judging rubric.
3. Establish roles and usable checker identities.
4. Monitor teams and submissions.
5. Determine eligibility and handle duplicate submissions.
6. Invite judges and create assignments/review batches.
7. Monitor judging progress and incomplete batches.
8. Calculate raw and normalized results.
9. Publish results at the allowed time.
10. Export and archive event data.

Steps 2, 5, 8, 9, and 10 include recommended detail beyond the minimum checker contract; their exact implementation remains TBD.

### Participant journey

1. Register/authenticate.
2. Form or join a team.
3. Create and submit a project before `submissions_close`.
4. Receive refusal after the event is closed.
5. View projects in the public gallery.
6. Remain unable to access judge-only resources.

### Judge journey

1. Authenticate with the assigned judge identity.
2. View assigned projects.
3. Enter weighted rubric scores.
4. Monitor personal completion.
5. Retrieve personal scores.
6. Receive `401` or `403` when attempting to read another judge's scores.

## Core use cases

| ID | Use case | Primary actor | Tier |
|---|---|---|---|
| UC-001 | Start a seeded event portal offline | Organizer/evaluator | Gate |
| UC-002 | Register and form a team | Participant | T1 |
| UC-003 | Submit a project before the deadline | Participant | T1 |
| UC-004 | Refuse a submission after close | System | T1 |
| UC-005 | Browse fixture projects publicly | Anonymous visitor | T1 |
| UC-006 | Assign projects to judges | Organizer | T2 |
| UC-007 | Score through a weighted rubric | Judge | T2 |
| UC-008 | Isolate each judge's score records | System | T2 |
| UC-009 | Monitor judging completion | Organizer | T2 |
| UC-010 | Normalize cross-judge scores and rank projects | Organizer/system | T2 |
| UC-011 | Export event/judging data as CSV | Organizer/checker | T2 |
| UC-012 | Vote/comment with abuse controls | Community actor | T3 |
| UC-013 | Use programmatic APIs and webhooks | API client | T4 |

## Functional requirements

### Tier 1 and lifecycle requirements

| ID | Requirement | Classification | Source |
|---|---|---|---|
| FR-001 | The portal shall support participant registration and authentication sufficient to operate the product beyond a login demonstration. | Source-defined; mechanism implementation-defined | `main.tex` §§ Mission, Tier 1, Out of Scope |
| FR-002 | The portal shall support roles and enforce role-aware behavior. | Source-defined | Tier 1 |
| FR-003 | An organizer shall be able to create an event. | Source-defined | Tier 1 |
| FR-004 | Participants shall be able to form teams. | Source-defined | Tier 1 |
| FR-005 | Teams/participants shall be able to create and submit projects. | Source-defined | Tier 1 and mission lifecycle |
| FR-006 | The portal shall support eligibility as a distinct lifecycle stage. Exact eligibility rules are TBD. | Source-defined capability; rules unknown | Mission lifecycle |
| FR-007 | The backend shall enforce the event submission deadline using the fixture event's own `submissions_close` value. | Source-defined | Acceptance checker and fixture sections |
| FR-008 | The portal shall expose a public project gallery without requiring authentication. | Source-defined | Tier 1 and acceptance checker |
| FR-009 | The public gallery shall show the shared fixture projects. | Source-defined | Acceptance checker |

### Tier 2 judging requirements

| ID | Requirement | Classification | Source |
|---|---|---|---|
| FR-010 | Organizers shall be able to invite judges and assign projects/review batches. | Source-defined | Tier 2 |
| FR-011 | The judging workflow shall use a weighted scoring rubric. | Source-defined; formula implementation-defined | Tier 2 |
| FR-012 | A judge shall be able to retrieve that judge's own scores. | Source-defined | T2 acceptance check |
| FR-013 | A judge shall not be able to read another judge's scores through the UI or API; the peer-score request shall return `401` or `403`. | Source-defined, critical invariant | Authorization section and slide 8 |
| FR-014 | A participant shall be blocked from judge-only scoring behavior/data. | Source-defined | T2 acceptance check |
| FR-015 | Organizers shall have a judging progress dashboard. | Source-defined | Tier 2 |
| FR-016 | The portal shall implement and document cross-judge normalization. The algorithm is not specified. | Source-defined capability; algorithm TBD | Tier 2 and known ambiguities |
| FR-017 | The portal shall calculate rankings/results and control their visibility. Exact tie, missing-score, and publication rules are TBD. | Source-defined lifecycle; detailed policy unknown | Mission lifecycle; T3 result hiding |
| FR-018 | The configured CSV export route shall return a functioning CSV export. Columns and row granularity are TBD. | Source-defined | T2 acceptance check |

### Tier 3 public-participation requirements

| ID | Requirement | Classification | Source |
|---|---|---|---|
| FR-019 | The portal shall support community voting. | Source-defined, T3 | Tier 3 |
| FR-020 | The portal shall support comments. | Source-defined, T3 | Tier 3 |
| FR-021 | Results shall remain hidden until the applicable window closes. | Source-defined, T3 | Tier 3 |
| FR-022 | Ballot/project order shall be randomized for community voting. | Source-defined, T3 | Tier 3 |
| FR-023 | Community participation shall include anti-abuse controls and an audit trail. | Source-defined, T3 | Tier 3 |

### Tier 4 platform requirements

| ID | Requirement | Classification | Source |
|---|---|---|---|
| FR-024 | The platform shall provide a REST API and webhooks. | Source-defined, T4; contract TBD | Tier 4 |
| FR-025 | The platform shall support certificates. Exact certificate semantics are TBD. | Source-defined, T4 | Tier 4 |
| FR-026 | The platform shall provide verifiable judge records. The term is not defined in the source. | Source-defined, T4; definition TBD | Tier 4 and known ambiguities |
| FR-027 | The platform shall provide an embeddable project gallery. | Source-defined, T4 | Tier 4 |
| FR-028 | The platform shall provide bulk import and export. Formats are TBD. | Source-defined, T4 | Tier 4 |

### Checker and delivery requirements

| ID | Requirement | Classification | Source |
|---|---|---|---|
| FR-029 | The repository shall provide a root `.dogfood.toml` declaring `base_url`, claimed tiers, four authentication headers, and configured route locations. | Source-defined | `.dogfood.toml` section |
| FR-030 | The project shall run the supplied standard-library checker and commit its output as `acceptance-report.txt`, including failures. | Source-defined | Acceptance-report discipline and deliverables |

## Delivery requirements

| ID | Deliverable |
|---|---|
| DR-001 | Public repository with an OSI-approved license; MIT or Apache-2.0 preferred. |
| DR-002 | Seeded offline startup through `docker compose up`. |
| DR-003 | Root `.dogfood.toml` with honest tier claims. |
| DR-004 | Committed `acceptance-report.txt`. |
| DR-005 | `README.md` with operation and honest limitations. |
| DR-006 | `ARCHITECTURE.md` explaining system shape and rationale. |
| DR-007 | `DATA-MODEL.md` explaining schema and import/export paths. |
| DR-008 | `JUDGING.md` defending assignment, scoring, and normalization. |
| DR-009 | Five-minute video demonstrating one complete event lifecycle. |

## Non-functional requirements

| ID | Requirement | Classification |
|---|---|---|
| NFR-001 | `docker compose up` shall start a seeded, working portal. | Source-defined |
| NFR-002 | Core operation shall remain usable on a laptop with the network disconnected. | Source-defined |
| NFR-003 | The solution shall not require a cloud account, hosted database, or hosted authentication provider. | Source-defined |
| NFR-004 | Authorization shall be enforced in the backend, not solely in the frontend. | Source-defined |
| NFR-005 | The normalization method shall be documented and defensible. | Source-defined |
| NFR-006 | The solution shall be open source under an OSI-approved license. | Source-defined |
| NFR-007 | Tier claims and limitations shall be honest; acceptance failures shall not be concealed. | Source-defined |
| NFR-008 | The fixture event shall retain its supplied `submissions_close` value. | Source-defined |
| NFR-009 | The product shall be one integrated system rather than disconnected gallery and judging demos. | Source-defined |
| NFR-010 | Result and judging behavior shall be reproducible and auditable. | Recommended; partially implied by judging integrity |
| NFR-011 | Seed/startup behavior should be repeatable without duplicating fixture data. | Recommended |
| NFR-012 | Authoritative event timestamps should be stored/compared in UTC on the server. | Recommended |

No quantitative response-time, throughput, concurrency, availability, recovery-time, accessibility, localization, or browser-support targets are specified.

## Tiered feature scope

- **T1 — Core (gate):** FR-001 through FR-009.
- **T2 — Judging:** FR-010 through FR-018.
- **T3 — Public:** FR-019 through FR-023.
- **T4 — Stretch:** FR-024 through FR-028.
- **Cross-tier delivery/checker:** FR-029, FR-030, DR-001 through DR-009.

## Constraints

1. Seventy-two-hour event implementation window.
2. Offline laptop operation.
3. Docker Compose startup.
4. No mandatory external account or hosted service.
5. Shared fixtures and checker contract.
6. T1 is a judging gate.
7. Correctness is preferred over breadth.
8. T3 and T4 are manually evaluated.

## Assumptions

| ID | Assumption | Status |
|---|---|---|
| AS-001 | Route names may be chosen by the implementation and mapped in `.dogfood.toml`. | Source-supported |
| AS-002 | Authentication headers may use cookies or another header format accepted by the checker. | Source-supported |
| AS-003 | Event creation may be the unnamed tenth lifecycle stage. | Inferred; unresolved |
| AS-004 | Organizer access to individual judge scores is policy-dependent. | Unknown / TBD |
| AS-005 | The advisory entities and example API routes are conceptual, not implemented facts. | Confirmed by repository inspection |

## Acceptance criteria

| ID | Criterion |
|---|---|
| AC-T1-001 | The configured gallery is public. |
| AC-T1-002 | Fixture projects appear in the gallery. |
| AC-T1-003 | The closed fixture event refuses submissions. |
| AC-T2-001 | A judge can retrieve personal scores. |
| AC-T2-002 | `judge_b` cannot retrieve `judge_a` scores and receives `401` or `403`. |
| AC-T2-003 | A participant is blocked from judge-only behavior/data. |
| AC-T2-004 | The configured CSV export works. |

Exact request methods, payloads, and all response assertions except AC-T2-002 are defined by `run.py`, which is not present in the supplied repository.

## Definition of done

The product is done for submission when:

1. T1 is complete and passes its three checks.
2. Claimed higher-tier features work correctly and are documented honestly.
3. The portal starts seeded and offline with `docker compose up`.
4. Backend authorization enforces judge-score isolation and participant blocking.
5. The repository contains DR-001 through DR-009.
6. The acceptance report reflects the actual checker result.

## Future scope

Tier 4 features are future scope unless explicitly claimed and implemented. Pairwise judging using a Bradley–Terry model, a normalization proof, a formal threat model, and API First are bonus capabilities rather than baseline requirements.

## Open requirements decisions

See [DOCUMENTATION_AUDIT.md](DOCUMENTATION_AUDIT.md) for the consolidated open-question register. Key unresolved product decisions include normalization, ties, missing scores, eligibility, duplicate handling, assignment strategy, authentication mechanism, CSV schema, and API contract.