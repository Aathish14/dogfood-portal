# DOGFOOD Portal — Fixture and Seed Data

## Artifact status

`fixtures.json` is referenced by the source but is **not present in the supplied repository**. Therefore this document cannot provide the actual JSON schema, field names, IDs, relationships, exact score records, team count, event timestamp value, or loader behavior.

This absence is a documentation blocker, not permission to invent the dataset.

## Fixture purpose

The shared fixture dataset gives every team the same event data and intentionally contains difficult real-world cases. It supports deterministic evaluation and at least one date-dependent acceptance check.

## Source-reported contents

| Item | Reported value | Verification status |
|---|---:|---|
| Projects | 40 | Cannot verify; file absent |
| Judges | 30 | Cannot verify; file absent |
| Tracks | 8 | Cannot verify; file absent |
| Scores | Described as a full set/collection | Cannot verify; file absent |
| Real names | None | Cannot verify; file absent |
| Event `submissions_close` | Present and must be preserved | Exact value unknown; file absent |

## Reported entities

At minimum, the descriptions imply:

- fixture event;
- projects/submissions;
- judges;
- tracks;
- score records;
- review batches or assignment/batch state.

Users, teams, criteria/rubrics, assignments, and other entities may also exist, but their presence and shape cannot be confirmed without the file.

## Relationships

Source-supported relationships are conceptual only:

- projects belong to the fixture event;
- judges score or are assigned to projects;
- projects relate to one or more of eight tracks;
- scores relate judges and projects, likely through assignments/reviews;
- review batches group judging work.

Cardinalities, key fields, and nesting/normalization are unknown.

## Fixture schema

Unknown. Do not rely on a fabricated schema.

When `fixtures.json` becomes available, update this document with:

1. top-level JSON type and keys;
2. per-entity objects and required fields;
3. identifier/reference rules;
4. enum/state values;
5. timestamps and timezone format;
6. score/rubric structure;
7. duplicates and intentionally missing/incomplete records;
8. a machine-readable schema if feasible.

## Intentional test scenarios

| ID | Reported edge case | Required observation/decision |
|---|---|---|
| FX-001 | One judge gave every project the same score | Variance-based normalization must avoid divide-by-zero and apply a documented policy. |
| FX-002 | Two review batches were never finished | Progress must expose incomplete work; result/publication policy must be defined. |
| FX-003 | Duplicate submission | The portal must not silently distort assignments, voting, or ranking; exact duplicate policy is TBD. |
| FX-004 | Closed event timestamp | Seed must preserve the event's own `submissions_close`; a generated replacement can fail acceptance. |
| FX-005 | No real names | Fixture identities must remain synthetic; exact fields unknown. |

## Potential source tension

The dataset is described as containing a “full set of scores” while also containing two unfinished review batches. This may mean scores are complete for recorded reviews while assignments/batches remain incomplete, or it may reflect another fixture structure. The conflict cannot be resolved without the JSON.

## Seed behavior

### Source-defined

- Load the shared dataset.
- Preserve the fixture event's exact `submissions_close`.
- Make fixture projects visible in the public gallery.
- Provide working organizer, two judge, and participant authentication headers.

### Recommended

- Use stable fixture identifiers.
- Make seeding deterministic/idempotent.
- Print or clearly expose the four checker headers at startup.
- Fail visibly rather than substituting generated dates/data.

### Unknown

- seed command or startup hook;
- reset procedure;
- database transaction behavior;
- duplicate handling during repeated seed;
- whether fixture data may be edited;
- persistence across restart;
- exact authentication records.

## Fixture loading

No loader exists in the repository. The future implementation must document the exact command/process in [OPERATIONS.md](OPERATIONS.md) and keep it consistent with Docker Compose startup.

## Fixture reset

Not specified. A destructive reset should be opt-in and documented (recommended). Test that reset restores the exact fixture timestamp and intentional edge cases.

## Acceptance dependencies

| Acceptance check | Fixture dependency |
|---|---|
| AC-T1-001 | Gallery route may be exercised against seeded event. |
| AC-T1-002 | Requires the fixture projects to appear publicly. |
| AC-T1-003 | Depends directly on the fixture event's `submissions_close`. |
| AC-T2-001 | Requires a fixture judge with personal scores. |
| AC-T2-002 | Requires distinct `judge_a` and `judge_b` identities and targetable score ownership. |
| AC-T2-003 | Requires participant identity and judge-only resource. |
| AC-T2-004 | Export likely serializes seeded data; exact assertion unknown. |

## Fixture tests

| Test ID | Scenario | Expected result |
|---|---|---|
| TC-FIX-001 | Load dataset into empty persistence | Reported entities load without generated replacements. |
| TC-FIX-002 | Load/seed twice | No unintended duplicate fixture records (recommended). |
| TC-FIX-003 | Compare stored close timestamp | Exact source `submissions_close` preserved. |
| TC-FIX-004 | Query public gallery | Fixture projects visible. |
| TC-FIX-005 | Run normalization with constant judge | No divide-by-zero; documented policy applied. |
| TC-FIX-006 | Inspect incomplete batches | Dashboard/result behavior matches documented policy. |
| TC-FIX-007 | Inspect duplicate submission | Documented duplicate policy applied. |

## Required follow-up

Add the actual `fixtures.json`, then regenerate this document from the file and validate all reported counts, fields, relationships, timestamps, and edge cases.