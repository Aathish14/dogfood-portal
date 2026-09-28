# DOGFOOD Portal — Integrations

## Status legend

- **REQUIRED:** source-defined baseline.
- **PLANNED:** Tier 4 or advisory capability, not implemented.
- **EXTERNAL / ABSENT:** expected organizer artifact not present in repository.
- **TBD:** design decision required.

## Integration inventory

| Integration | Status | Purpose | Authentication | Contract status |
|---|---|---|---|---|
| Acceptance checker (`run.py`) | REQUIRED; EXTERNAL / ABSENT | Verify seven T1/T2 checks | Four pre-supplied headers | Exact requests unavailable |
| `.dogfood.toml` | REQUIRED; ABSENT | Locate portal, tiers, actor headers, and routes | Contains sensitive header values | Sample structure known |
| `fixtures.json` | REQUIRED; EXTERNAL / ABSENT | Seed common event/project/judge/track/score data | N/A | Counts/edge cases known; schema unknown |
| CSV export | REQUIRED | Data portability and checker validation | Policy TBD | Schema unknown |
| REST API | PLANNED T4 | Programmatic UI-equivalent actions | TBD | No implemented contract |
| Webhooks | PLANNED T4 | Notify external consumers of domain events | Signature/secret recommended; TBD | Proposed events only |
| Bulk import/export | PLANNED T4 | Event data interchange | TBD | Formats unknown |
| Embeddable gallery | PLANNED T4 | Render projects on external sites | TBD | Contract unknown |
| Certificates | PLANNED T4 | Capability named by source | TBD | Meaning/schema unknown |
| Verifiable judge records | PLANNED T4 | Capability named by source | TBD | Verification model unknown |

## Acceptance checker integration

The checker is one Python standard-library file and does not perform login. It reads `.dogfood.toml`, attaches an actor header, and calls configured routes. `run.py` is the authoritative machine contract, but it is absent; therefore exact methods, payloads, parsing, and success criteria cannot be documented beyond [ACCEPTANCE.md](ACCEPTANCE.md).

## Fixture integration

The application must seed from the shared fixture dataset and preserve its `submissions_close`. The actual loader format and reset behavior are not available. See [FIXTURES.md](FIXTURES.md).

## REST API

T4 requires a REST API with webhooks. The API First bonus requires every UI action through a documented API and an OpenAPI specification. Current status: **PLANNED / not implemented**.

Required future decisions:

- resource paths and schemas;
- authentication and scopes;
- versioning;
- pagination/filtering;
- error format;
- idempotency;
- rate limits;
- bulk-operation behavior.

## Webhooks

Advisory proposed event names:

- `project.submitted`
- `project.eligibility_changed`
- `assignment.created`
- `review.submitted`
- `judging.completed`
- `results.published`

These are **PROPOSED**, not source-mandated names.

Recommended delivery contract fields include a unique delivery ID, event type, creation timestamp, versioned payload, and signature. Signature algorithm, secret distribution, timestamp tolerance, retries, maximum attempts, ordering, dead-letter handling, and retention are TBD.

## Signatures and replay protection

Recommended controls:

1. Sign a documented canonical representation.
2. Include delivery ID and creation timestamp.
3. Reject stale timestamps under a documented replay window.
4. Make retries idempotent.
5. Surface delivery failures to organizers.

No algorithm or header names may be claimed until adopted.

## Retry and idempotency behavior

Not specified. ADR-009 and an integration-specific decision must establish at-least-once/at-most-once behavior, backoff, ordering, idempotency keys, and consumer expectations.

## Import/export

CSV export is required. Bulk import/export is T4. Import validation must not bypass single-record authorization, validation, or audit policies (recommended). Formats, conflict handling, dry-run behavior, transactionality, and rollback are TBD.

## External dependencies

Core runtime must not depend on external cloud/SaaS accounts. Registration/Discord/spec links in the event deck are event destinations, not portal runtime integrations.

## Failure handling

| Integration | Required/recommended failure handling |
|---|---|
| Checker | Produce honest FAIL output and commit it; exact format comes from absent checker. |
| Fixture load | Fail visibly; do not silently substitute generated dates/data. |
| CSV | Return valid CSV or explicit failure; exact status TBD. |
| REST API | Stable sanitized errors once designed. |
| Webhook | Record attempts/failures and retry under documented policy (recommended). |
| Bulk import | Validate and report record-level/global failures; transaction policy TBD. |

## Open decisions

All T4 integration contracts, authentication/scopes, webhook signing/retry, import/export formats, embeddable-gallery security, certificate semantics, and verifiable-record model.