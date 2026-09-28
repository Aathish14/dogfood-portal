# DOGFOOD Portal — Security and Threat Model

## Status

This threat model is derived from the actual required attack surfaces in the source. Controls explicitly required by the source are marked **Source-defined**; advisory controls are marked **Recommended**. No implementation exists to assess control effectiveness.

## Security goals

1. Preserve confidentiality of judge-specific score records.
2. Prevent participants and unauthorized actors from judge-only operations.
3. Enforce submission and result windows using authoritative server state.
4. Prevent public-voting abuse where Tier 3 is implemented.
5. Preserve trustworthy result calculation and audit/provenance.
6. Operate offline without transferring sensitive state to mandatory third parties.
7. Export data safely and only to authorized actors under the selected policy.

## Assets

- authentication credentials and fixture auth headers;
- user roles and event memberships;
- team/project ownership;
- project submissions and eligibility decisions;
- judge assignments, reviews, comments, and scores;
- rubric definitions and weights;
- raw and normalized results/rankings;
- result-release state;
- community votes/comments;
- audit events and result provenance;
- CSV/bulk exports;
- API/webhook secrets and deliveries;
- database/local persistent state.

## Trust boundaries

1. Untrusted browser/HTTP client to backend.
2. Anonymous vs authenticated actors.
3. Participant, judge, and organizer roles.
4. One judge's resources vs another judge's resources.
5. One team/project vs another team's resources.
6. One event vs another event (recommended scoping).
7. Portal vs acceptance checker/configured headers.
8. Portal vs Tier 4 API/webhook clients.
9. Application process vs persistence and local files.

## Threat actors

- anonymous external user;
- participant attempting judge/other-team access;
- judge attempting peer-score or organizer access;
- malicious or careless organizer;
- community voter controlling multiple identities;
- scripted voting client/bot;
- colluding judges;
- attacker with a leaked fixture/session/API/webhook secret;
- operator making accidental destructive/configuration changes.

## Attack surfaces

- public gallery and project identifiers;
- authentication/login/session handling;
- submission and deadline endpoints;
- judge score/review endpoints;
- organizer/admin and result-publication endpoints;
- CSV and bulk import/export;
- community voting/comments;
- REST API and OpenAPI-exposed actions;
- webhooks and retries;
- fixture seed/reset functions;
- logs, audit records, backups, and local volumes.

## Threat model

Likelihood is **Not assessed** because no implementation or deployment evidence is present.

| ID | Threat | Attack | Impact | Likelihood | Control | Verification |
|---|---|---|---|---|---|---|
| SEC-001 | Peer-score disclosure | `judge_b` supplies `judge_a` identifier to score endpoint | Compromised judging confidentiality/integrity | Not assessed | Backend identity + ownership check (**Source-defined**) | AC-T2-002; expect 401/403 |
| SEC-002 | Participant reaches judge data | Participant calls judge route directly | Confidential score disclosure or tampering | Not assessed | Backend role denial (**Source-defined**) | AC-T2-003 |
| SEC-003 | Frontend-only authorization | User calls hidden action through `curl` | Any protected operation may be bypassed | Not assessed | Central backend authorization (**Source-defined**) | Direct HTTP negative tests |
| SEC-004 | Cross-team object access | Participant replaces team/project ID | Unauthorized project read/write | Not assessed | Authenticated team ownership (**Recommended**) | ID substitution tests |
| SEC-005 | Deadline gaming | Client clock or crafted request submits after close | Unfair late submission | Not assessed | Server time + exact fixture `submissions_close` (**Source-defined/recommended mechanism**) | AC-T1-003; boundary tests |
| SEC-006 | Early result disclosure | Request UI/API/export/embed before release | Compromised judging process | Not assessed | Release-state check on every surface (**T3 source-defined**) | Pre-release surface tests |
| SEC-007 | Sybil voting | One person creates multiple voter identities | Manipulated community ranking | Not assessed | Identity policy, anomaly signals, audit trail (**Threat-model/T3**) | Repeated-identity scenarios |
| SEC-008 | Ballot stuffing | Script sends high-rate/repeated votes | Manipulated community ranking | Not assessed | Rate/deduplication controls and audit (**T3 source-defined in principle**) | Load/replay voting tests |
| SEC-009 | Ballot order bias | Projects always appear in fixed order | Systematic voting bias | Not assessed | Randomized ballot order (**Source-defined T3**) | Statistical/order test |
| SEC-010 | Judge collusion | Coordinated scoring to favor projects | Distorted results | Not assessed | Threat model, overlap/anomaly review; exact control TBD | Scenario analysis/manual review |
| SEC-011 | Rubric/result tampering | Silent weight/score/result changes | Unreproducible ranking | Not assessed | Version/freeze + audit/provenance (**Recommended**) | Change-history/recompute tests |
| SEC-012 | Zero-variance normalization failure | Constant judge causes divide by zero/NaN | Broken or misleading results | Not assessed | Explicit documented fallback/exclusion policy | Fixture edge-case test |
| SEC-013 | Duplicate submission distortion | Duplicate receives assignments/votes/ranking twice | Unfair result | Not assessed | Detect/reject/merge/flag; policy TBD | Fixture duplicate scenario |
| SEC-014 | CSV formula injection | Exported cell begins `=`, `+`, `-`, or `@` | Spreadsheet code/command risk | Not assessed | Neutralize/escape formula-like cells (**Recommended**) | Hostile export test |
| SEC-015 | CSV data leakage | Export route accessible to wrong role or includes sensitive fields | Confidentiality breach | Not assessed | Export authorization and field allowlist; policy TBD | Role and schema tests |
| SEC-016 | Session/secret leakage | Credentials committed, logged, or predictable | Account/role compromise | Not assessed | Random secrets, redaction, fixture-only separation (**Recommended**) | Secret scan/log review |
| SEC-017 | Webhook forgery | Attacker posts fabricated integration event | Downstream state corruption | Not assessed | Signature and scoped secret (**Recommended T4**) | Invalid-signature test |
| SEC-018 | Webhook replay | Valid delivery resent | Duplicate downstream effects | Not assessed | Event ID, timestamp window, idempotency (**Recommended T4**) | Replay/retry tests |
| SEC-019 | Unsafe seed/reset | Repeated startup duplicates or destructive reset erases state | Corruption/data loss | Not assessed | Idempotent seed; destructive reset opt-in (**Recommended**) | Restart/seed tests |
| SEC-020 | Error information disclosure | Stack trace/query/secret returned | Enables further attack | Not assessed | Sanitized failure responses (**Recommended**) | Fault-injection tests |

## Authentication security

The mechanism is TBD. It must work offline and produce usable headers for organizer, two judges, and participant. If cookies are selected, CSRF and cookie attributes require decisions. If bearer tokens are selected, issuance, scope, storage, expiration, and revocation require decisions. Example fixture cookies are not production secrets.

## Authorization security

Authorization is a backend responsibility. Policies must derive identity from the authenticated credential, not from a user-supplied judge/team ID. See [AUTHORIZATION.md](AUTHORIZATION.md) for the matrix and exact peer-score invariant.

## Input validation

Required validation surfaces include:

- event timestamps and state transitions;
- project/submission ownership and payload;
- rubric weights and score bounds;
- identifiers in paths, queries, and bodies;
- CSV/import data;
- comments and other public content if T3 is implemented;
- webhook URLs/payloads and signatures if T4 is implemented.

Exact schemas are unknown.

## Injection prevention

The source does not identify a programming language or database, so SQL/NoSQL/template/command controls cannot be specified as implemented facts. The future implementation must use its framework's safe parameterization/encoding and test all untrusted inputs. CSV formula injection is separately documented because CSV export is a source-defined surface.

## Webhook security and replay protection

Webhooks are T4. Recommended controls: per-client/endpoint secret, canonical signature input, timestamp tolerance, unique delivery ID, idempotent consumer semantics, bounded retries, and failure visibility. None is implemented or source-mandated in detail.

## Secret management

- Do not place actual credentials in documentation.
- Treat `.dogfood.toml` auth headers as sensitive local test configuration.
- Distinguish fixture credentials from production operation.
- Environment-variable/file/secret-store choice is TBD and must remain offline-capable.
- Logs and audit records should redact credentials.

## Information disclosure

Denials should not reveal peer-score existence. Unpublished results must be checked across UI, API, CSV, embed, and bulk exports. Error bodies must not expose stack traces, database details, or other users' data (recommended).

## Audit logging

T3 requires an audit trail for anti-abuse behavior. Recommended fields: event ID, timestamp, actor, role, action, target type/ID, outcome, metadata, and reason/old-new summary for sensitive changes. Retention, immutability, administrator visibility, and privacy policy are TBD.

## Rate limiting

No baseline rate limit is specified. Rate controls are relevant to community voting, comments, login, and APIs, but limits cannot be invented without product/deployment requirements.

## Data protection

No legal/privacy classification, encryption requirement, personal-data policy, or retention period is specified. The fixtures use no real names. A future implementation must document stored personal data and offline backup protection.

## Error handling

- Peer-score denial: 401 or 403.
- Participant denial: exact checker expectation unavailable.
- Closed submission: exact response unavailable.
- Validation failures: should be actionable without exposing internals.
- Unexpected errors: should be sanitized and logged locally.

## Security testing

Required test families are captured in [TESTING.md](TESTING.md), including role matrices, object-ID substitution, deadline boundaries, pre-release result access, fixture edge cases, CSV injection, secret scanning, webhook forgery/replay, and failure disclosure.

## Residual risks

Current residual risk is unbounded because no implementation exists. Design-level residual risks include organizer privilege, judge collusion, voter identity uncertainty, normalization-model limitations, audit mutability, local-device compromise, fixture credentials, and undefined data-retention/privacy rules.

## Security decisions required

Authentication/session mechanism, CSRF policy, password/credential handling, organizer visibility into judge scores, audit immutability/retention, voter identity, rate limits, API scopes, webhook signature scheme, encryption/backup protection, and security update process.