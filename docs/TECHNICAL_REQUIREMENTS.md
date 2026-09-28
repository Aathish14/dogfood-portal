# DOGFOOD Portal — Technical Requirements

## Status and interpretation

This document translates [PRD.md](PRD.md) into engineering-verifiable requirements. It does not claim that an application implementation exists. Repository inspection found documentation sources only; therefore implementation status is **Not implemented / not verifiable from supplied files** unless stated otherwise.

Priority values:

- **Gate:** required to be judged.
- **Must:** source-defined requirement for the applicable tier.
- **Stretch:** T3/T4 source-defined capability.
- **Recommended:** advisory guidance, not an official requirement.

## Runtime and deployment requirements

| ID | Requirement | Rationale | Priority | Verification | Source reference |
|---|---|---|---|---|---|
| TR-001 | The repository shall provide a Docker Compose definition that starts the portal with `docker compose up`. | Required evaluator/operator entry point. | Gate | Run from a clean checkout. | NFR-001; `main.tex` § Operational acceptance |
| TR-002 | Startup shall produce a seeded, working portal. | The checker expects fixture-backed behavior immediately. | Gate | Start with empty persistent state and inspect fixture data. | FR-009; NFR-001 |
| TR-003 | The portal shall remain usable with outbound networking disabled. | Adoption requires laptop/offline operation. | Gate | Disconnect/block networking and execute critical workflows. | NFR-002, NFR-003 |
| TR-004 | Runtime dependencies required for core operation shall be available locally after the permitted build/pull process. | Remote CDNs/services would break offline behavior. | Must | Inspect network requests during offline operation. | NFR-002; recommended runbook |
| TR-005 | Persistent data shall survive an ordinary stop/start cycle. | A working event portal must not lose event state on restart. | Recommended | Submit data, restart Compose, verify persistence. | Advisory operations guidance |
| TR-006 | Repeated startup/seed execution should not duplicate fixture records. | Evaluators need repeatable state. | Recommended | Start/seed twice and compare stable counts/IDs. | NFR-011 |

## Application requirements

| ID | Requirement | Rationale | Priority | Verification | Source reference |
|---|---|---|---|---|---|
| TR-007 | The application shall implement registration/authentication, event creation, team formation, submission, deadline enforcement, and a public gallery as one integrated portal. | Defines the T1 product floor. | Gate | End-to-end lifecycle test. | FR-001–FR-009 |
| TR-008 | The application shall represent eligibility as part of the lifecycle. | Eligibility is explicitly named by the mission. | Must | Demonstrate eligibility state/decision once policy is defined. | FR-006 |
| TR-009 | The application shall support judge invitation/identity and project assignment. | Required T2 workflow. | Must | Organizer creates assignments; judge sees assigned work. | FR-010 |
| TR-010 | The application shall expose judging progress to organizers. | Enables incomplete-batch management. | Must | Compare dashboard totals with assignments/reviews. | FR-015 |
| TR-011 | The application shall calculate results/rankings from judging data. | Results are an explicit lifecycle stage. | Must | Recompute a known example. | FR-017 |

## API and checker-interface requirements

| ID | Requirement | Rationale | Priority | Verification | Source reference |
|---|---|---|---|---|---|
| TR-012 | The implementation shall expose a public gallery route and declare it as `routes.gallery` in `.dogfood.toml`. | Enables AC-T1-001/002. | Gate | Run checker; unauthenticated request. | FR-008, FR-009, FR-029 |
| TR-013 | The implementation shall expose a submission route and declare it as `routes.submit`. | Enables closed-event verification. | Gate | Run checker against fixture event. | FR-005, FR-007, FR-029 |
| TR-014 | The implementation shall expose a judge-score route and declare it as `routes.judge_scores`. | Enables own-score verification. | Must | Request with configured judge header. | FR-012, FR-029 |
| TR-015 | The implementation shall declare a peer-score request location as `routes.peer_scores`. | Enables object-level authorization verification. | Must | Request with `judge_b` header. | FR-013, FR-029 |
| TR-016 | The implementation shall expose a CSV route and declare it as `routes.csv_export`. | Enables export verification. | Must | Run checker and parse output. | FR-018, FR-029 |
| TR-017 | Concrete HTTP methods, request bodies, and schemas shall conform to `run.py`. | The checker is the authoritative machine contract. | Gate | Inspect/run `run.py`. Currently blocked: file absent. | Acceptance-checker section |
| TR-018 | A T4/API First implementation shall document every UI action through an API and OpenAPI definition. | Source-defined bonus/stretch behavior. | Stretch | Compare UI actions with OpenAPI paths. | FR-024; API First bonus |

## Authentication requirements

| ID | Requirement | Rationale | Priority | Verification | Source reference |
|---|---|---|---|---|---|
| TR-019 | The application shall authenticate organizer, `judge_a`, `judge_b`, and participant fixture identities. | The checker requires four usable identities. | Gate/Must | Use each configured auth header. | FR-001, FR-029 |
| TR-020 | The seed/startup process shall make the four working authentication headers available to the evaluator. | The checker does not perform login. | Must | Observe documented startup output or equivalent. | Official preparation advice |
| TR-021 | The authentication mechanism may be implementation-defined, but shall operate offline. | Source deliberately permits any login mechanism. | Must | Authenticate with network disabled. | NFR-002, NFR-003 |
| TR-022 | Actual secrets shall not be committed to documentation; fixture credentials shall be clearly fixture-only. | Prevents credential disclosure. | Recommended | Repository secret scan and documentation review. | Advisory security guidance |

## Authorization requirements

| ID | Requirement | Rationale | Priority | Verification | Source reference |
|---|---|---|---|---|---|
| TR-023 | Authorization decisions shall be enforced by the backend for every protected request. | Frontend hiding is explicitly insufficient. | Gate/Must | Direct HTTP requests bypassing UI. | FR-013, FR-014, NFR-004 |
| TR-024 | A judge shall be allowed to read that judge's own score records. | Required T2 check. | Must | Request with owner judge header. | FR-012 |
| TR-025 | A judge requesting another judge's scores shall receive `401` or `403`, never `200`. | Critical isolation invariant. | Must | `judge_b` requests `judge_a` scores. | FR-013; AC-T2-002 |
| TR-026 | A participant shall be denied judge-only data/behavior. | Required T2 check. | Must | Repeat judge request using participant header. | FR-014 |
| TR-027 | Participant project operations should validate authenticated team ownership rather than trusting a supplied team/project identifier. | Prevents cross-team modification. | Recommended | Object-ID substitution tests. | Advisory authorization guidance |
| TR-028 | Protected actions should be evaluated using actor, event-scoped role, resource ownership, and event state. | Provides a consistent authorization model. | Recommended | Policy/unit tests. | Recommended invariant in `main.tex` |

## Data and integrity requirements

| ID | Requirement | Rationale | Priority | Verification | Source reference |
|---|---|---|---|---|---|
| TR-029 | The implementation shall load the shared fixture event without changing its supplied `submissions_close` value. | AC-T1-003 depends on it. | Gate | Compare seeded value to fixture. Currently blocked: fixture absent. | FR-007, NFR-008 |
| TR-030 | The fixture-backed state shall include the source-reported 40 projects, 30 judges, 8 tracks, and score set. | Required common dataset. | Gate/Must | Count fixture entities. Currently blocked. | Fixture section |
| TR-031 | The implementation shall preserve/handle the constant-scoring judge, two unfinished batches, and duplicate submission represented by fixtures. | These cases intentionally test real behavior. | Must | Fixture-specific scenario tests. Currently blocked. | Fixture section |
| TR-032 | Stable identifiers and relational constraints are implementation decisions that shall be documented once selected. | Required for reproducibility/import/export. | Recommended | Schema and migration review. | Advisory data model |
| TR-033 | Authoritative event instants should be stored and compared in UTC on the server. | Prevents client-clock/timezone deadline errors. | Recommended | Boundary tests across timezones. | NFR-012 |

## Judging and scoring requirements

| ID | Requirement | Rationale | Priority | Verification | Source reference |
|---|---|---|---|---|---|
| TR-034 | Rubric criteria shall carry weights that affect score calculation. | Weighted judging is the central product problem. | Must | Known weighted-score test. | FR-011 |
| TR-035 | The exact score scale, rounding, missing-criterion behavior, and rubric-edit policy shall be documented before implementation is considered complete. | Source does not define them. | Must decision | Review `JUDGING.md`; boundary tests. | Known ambiguities; advisory judging section |
| TR-036 | Cross-judge normalization shall be implemented and documented, including treatment of zero-variance judges. | Fixture includes a constant-scoring judge. | Must | Raw/normalized comparison and constant-judge test. | FR-016; fixture edge case |
| TR-037 | The chosen normalization method shall expose enough detail to reproduce the result. | Opaque normalization is a stated problem. | Must | Independent recomputation. | NFR-005 |
| TR-038 | Incomplete review batches shall be visible; final-result behavior with incomplete reviews shall be documented. | Two fixture batches are unfinished. | Must decision | Incomplete-batch test. | FR-015; fixture edge case |
| TR-039 | Tie handling and missing-score handling shall be explicitly defined. | Source leaves these decisions open. | Must decision | Worked examples and tests. | Advisory judging guidance |
| TR-040 | Result publication shall enforce the configured release/window state on every relevant surface. | T3 requires hidden results until close. | Stretch | Request UI/API/export/embed before release. | FR-021 |

## Export and integration requirements

| ID | Requirement | Rationale | Priority | Verification | Source reference |
|---|---|---|---|---|---|
| TR-041 | The configured export route shall return syntactically valid CSV. | Machine-verified T2 requirement. | Must | Parse with a standards-compliant CSV reader. | FR-018 |
| TR-042 | CSV row model, columns, encoding, null behavior, ordering, and timestamps shall be documented once decided. | Not specified by source. | Must decision | Compare implementation with `CSV-SPEC.md`. | FR-018; unknown schema |
| TR-043 | CSV fields beginning with spreadsheet formula characters should be neutralized or otherwise safely handled. | Prevents formula injection. | Recommended | Export hostile values and inspect. | Advisory threat model |
| TR-044 | T4 webhooks should be signed, replay-resistant, retryable, and idempotent. | Protects planned integration surface. | Recommended/Stretch | Invalid-signature, replay, and retry tests. | Advisory integration guidance |
| TR-045 | Bulk operations shall apply the same validation, authorization, and audit rules as single-record operations. | Prevents bypass through import/export. | Recommended/Stretch | Compare bulk and single-operation tests. | Advisory Tier 4 guidance |

## Security and audit requirements

| ID | Requirement | Rationale | Priority | Verification | Source reference |
|---|---|---|---|---|---|
| TR-046 | Tier 3 voting shall include anti-abuse controls and an audit trail. | Source-defined public-voting requirement. | Stretch | Abuse scenarios and audit inspection. | FR-023 |
| TR-047 | The threat model shall address Sybil voting, ballot stuffing, judge collusion, and deadline gaming when the bonus is claimed. | Explicit bonus definition. | Stretch | Threat-model review. | Threat Model bonus |
| TR-048 | Sensitive audit/log output shall not contain passwords, session headers, or unnecessary personal data. | Prevents secondary disclosure. | Recommended | Log inspection and secret scanning. | Advisory security guidance |
| TR-049 | Authorization errors should avoid revealing protected-record existence and unexpected errors should not expose stack traces/secrets. | Limits information disclosure. | Recommended | Negative API tests. | Advisory failure behavior |

## Observability, reliability, and recovery requirements

| ID | Requirement | Rationale | Priority | Verification | Source reference |
|---|---|---|---|---|---|
| TR-050 | The organizer shall be able to identify unstarted, in-progress, and completed judging work. | Required progress capability. | Must | Compare dashboard to known assignments. | FR-015 |
| TR-051 | A health/readiness mechanism, log format, backup method, and restoration method should be documented once implemented. | Required for adoptability; specifics absent. | Recommended | Operational drill. | Advisory operations section |
| TR-052 | Result/normalization runs should record method/version, inputs, parameters, initiator, timestamp, outputs, and warnings. | Supports reproducibility and audit. | Recommended | Inspect persisted run record. | Advisory result provenance |

## Configuration requirements

| ID | Requirement | Rationale | Priority | Verification | Source reference |
|---|---|---|---|---|---|
| TR-053 | `.dogfood.toml` shall contain `[portal].base_url`. | Locates the running portal. | Gate | Parse configuration. | FR-029 |
| TR-054 | `.dogfood.toml` shall contain `[tiers].claimed` with honest claims. | Controls checker scope and integrity. | Gate | Compare claims to implementation/report. | FR-029, NFR-007 |
| TR-055 | `.dogfood.toml` shall contain organizer, `judge_a`, `judge_b`, and participant auth headers. | Enables role-specific tests. | Gate/Must | Attach each header to requests. | FR-029 |
| TR-056 | `.dogfood.toml` shall map `gallery`, `submit`, `judge_scores`, `peer_scores`, and `csv_export` routes. | Enables seven machine checks. | Gate/Must | Parse and invoke mapped routes. | FR-029 |
| TR-057 | Environment variables, database settings, ports, feature flags, and secrets are TBD because no implementation configuration is present. | Prevents fabricated configuration. | Decision required | Inspect future source/configuration. | Repository audit |

## Additional tier and delivery requirements

| ID | Requirement | Rationale | Priority | Verification | Source reference |
|---|---|---|---|---|---|
| TR-058 | A claimed T3 implementation shall provide comments under a documented identity, authorization, validation, and moderation policy. | Comments are a source-defined T3 capability; details are absent. | Stretch | Comment create/read/abuse tests after policy selection. | FR-020 |
| TR-059 | A claimed T3 implementation shall randomize ballot/project ordering according to a documented method. | Reduces order bias. | Stretch | Repeated ballot-order test. | FR-022 |
| TR-060 | A claimed T4 implementation shall provide certificates under a documented issuance, content, and verification model. | Certificates are named but undefined. | Stretch/Decision required | Contract and lifecycle tests after definition. | FR-025 |
| TR-061 | A claimed T4 implementation shall define and provide verifiable judge records. | Capability is named but undefined. | Stretch/Decision required | Verification-model tests after definition. | FR-026 |
| TR-062 | A claimed T4 implementation shall provide an embeddable gallery with documented data exposure and release controls. | Embeddable gallery is source-defined T4 scope. | Stretch | Embed access/release/security tests. | FR-027 |
| TR-063 | The actual checker output shall be committed as `acceptance-report.txt` without concealing failures. | Honest evidence is a submission requirement. | Gate/Delivery | Compare committed report with checker execution. | FR-030, DR-004 |
| TR-064 | The public repository shall use an OSI-approved license; MIT or Apache-2.0 is preferred. | Source-defined adoption/legal requirement. | Gate/Delivery | License-file review. | NFR-006, DR-001 |
| TR-065 | The repository shall contain README, architecture, data-model, and judging documents matching the implementation and honest limitations. | Documentation is scored and required for adoption. | Delivery | Documentation/code consistency review. | DR-005–DR-008 |
| TR-066 | The submission shall include a five-minute video demonstrating one complete event lifecycle. | Source-defined delivery artifact. | Delivery | Video review against lifecycle. | DR-009 |

## Performance requirements

No quantitative performance requirement is defined. Response time, concurrent participant/judge counts, dataset growth, export size, and webhook throughput require product decisions before measurable technical requirements can be added.

## PRD-to-technical requirement index

### Functional requirements

| PRD ID | Technical requirement IDs |
|---|---|
| FR-001 | TR-007, TR-019–TR-022 |
| FR-002 | TR-007, TR-023–TR-028 |
| FR-003 | TR-007 |
| FR-004 | TR-007 |
| FR-005 | TR-007, TR-013 |
| FR-006 | TR-008 |
| FR-007 | TR-013, TR-029, TR-033 |
| FR-008 | TR-012 |
| FR-009 | TR-002, TR-012, TR-030 |
| FR-010 | TR-009 |
| FR-011 | TR-034, TR-035 |
| FR-012 | TR-014, TR-024 |
| FR-013 | TR-015, TR-023, TR-025 |
| FR-014 | TR-023, TR-026 |
| FR-015 | TR-010, TR-050 |
| FR-016 | TR-036, TR-037 |
| FR-017 | TR-011, TR-038–TR-040 |
| FR-018 | TR-016, TR-041–TR-043 |
| FR-019 | TR-046, TR-047 |
| FR-020 | TR-058 |
| FR-021 | TR-040 |
| FR-022 | TR-059 |
| FR-023 | TR-046–TR-049 |
| FR-024 | TR-018, TR-044 |
| FR-025 | TR-060 |
| FR-026 | TR-061 |
| FR-027 | TR-062 |
| FR-028 | TR-045 |
| FR-029 | TR-053–TR-057 |
| FR-030 | TR-063 |

### Non-functional and delivery requirements

| PRD ID | Technical requirement IDs |
|---|---|
| NFR-001 | TR-001, TR-002 |
| NFR-002 | TR-003, TR-004 |
| NFR-003 | TR-003 |
| NFR-004 | TR-023–TR-028 |
| NFR-005 | TR-036, TR-037 |
| NFR-006 | TR-064 |
| NFR-007 | TR-054, TR-063, TR-065 |
| NFR-008 | TR-029 |
| NFR-009 | TR-007 |
| NFR-010 | TR-052 |
| NFR-011 | TR-006 |
| NFR-012 | TR-033 |
| DR-001 | TR-064 |
| DR-002 | TR-001–TR-004 |
| DR-003 | TR-053–TR-056 |
| DR-004 | TR-063 |
| DR-005 | TR-065 |
| DR-006 | TR-065 |
| DR-007 | TR-065 |
| DR-008 | TR-065 |
| DR-009 | TR-066 |

## Requirement status summary

- Source-defined requirements: documented above; no application implementation is available to verify them.
- Recommended requirements: traceable to advisory sections and clearly marked.
- Blocked verification: fixture-dependent and checker-exact behavior cannot be validated because `fixtures.json` and `run.py` are absent.
- Implementation decisions required: framework, database, authentication mechanism, schema, normalization, API schemas, and operations tooling.