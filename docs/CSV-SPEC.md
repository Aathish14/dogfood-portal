# DOGFOOD Portal — CSV Export Specification

## Status

CSV export is a source-defined T2 requirement and machine check. The supplied sources do not define the CSV filename, columns, row granularity, delimiter/dialect, encoding, timestamp format, null behavior, or authorization role. No implementation exists.

## Normative minimum

| Requirement | Status |
|---|---|
| A route location is declared as `.dogfood.toml` `routes.csv_export`. | Source-defined |
| The configured route returns a functioning CSV export. | Source-defined |
| Exact checker assertions come from `run.py`. | Source-defined, but file absent |
| CSV schema/row model | TBD |

## Export types

Only one generic CSV export is required by the checker. The advisory material suggests that a richer organizer export may include projects, teams, roles, assignments, criterion scores, normalized results, and audit events. Those are recommendations, not existing export types.

## Proposed export catalog

| Export | Status | Proposed row grain |
|---|---|---|
| Checker CSV export | Required; schema TBD | TBD |
| Projects | Recommended future | One row per project |
| Teams | Recommended future | One row per team |
| Assignments | Recommended future | One row per judge-project assignment |
| Criterion scores | Recommended future | One row per review criterion score |
| Results | Recommended future | One row per project per result run |
| Audit events | Recommended/T3 | One row per audit event |

## Columns and data types

No normative columns can be declared without `run.py`, `fixtures.json`, or implementation models.

The source advisory suggests the following **non-binding** content for a useful judging export:

- stable identifiers;
- project metadata;
- track;
- assignment status;
- raw criterion scores;
- criterion weights;
- raw aggregate;
- normalized aggregate;
- ranking;
- timestamps.

All names, types, requiredness, and sensitive-field policy remain TBD.

## Filename

Not specified. The sample path is `/api/export.csv`, which is a route example rather than a required downloaded filename.

## Encoding and dialect

Not specified. Recommended decisions to record:

- UTF-8 encoding;
- comma delimiter and RFC 4180-compatible quoting, or another explicitly documented dialect;
- stable header row;
- CRLF vs LF;
- byte-order mark policy.

These are recommendations, not source-defined facts.

## Identifiers and ordering

Stable identifiers and deterministic ordering are recommended for reproducibility. Exact keys and sort order are TBD.

## Null and missing behavior

Not specified. The implementation must distinguish absent review/score, intentionally blank comment, not-applicable field, and numeric zero. Empty-string vs explicit sentinel policy must be documented.

## Timestamps

Not specified. UTC/ISO 8601 is recommended by the advisory time policy; exact precision and formatting are TBD.

## Escaping

The serializer must correctly quote delimiters, quotes, and embedded line breaks according to the selected dialect.

## Formula injection protection

Recommended: neutralize or safely encode untrusted cells beginning with spreadsheet formula characters such as `=`, `+`, `-`, or `@`. The exact strategy must preserve data meaning and be documented.

## Authorization

The exact checker identity and production export role are not stated. Organizer-only export is recommended, but must not be presented as source-defined until `run.py` or implementation policy establishes it.

## Export consistency

Recommended: generate from a consistent event/result snapshot so rows do not combine different rubric/result states. Record result-run/version identifiers where relevant.

## Large-export considerations

No scale target exists beyond the reported fixture dataset. Streaming, pagination, compression, and asynchronous export are implementation decisions and should not be added without requirements.

## Verification

| Test ID | Scenario | Expected |
|---|---|---|
| TC-CSV-001 | Call configured export route | Checker accepts functioning CSV |
| TC-CSV-002 | Parse commas, quotes, and line breaks | Selected parser reads expected cells |
| TC-CSV-003 | Export null, zero, and blank values | Semantics match documented policy |
| TC-CSV-004 | Export formula-like user text | No unintended spreadsheet formula execution under selected protection policy |
| TC-CSV-005 | Call as unauthorized role | Denied under selected authorization policy |
| TC-CSV-006 | Repeat export without data changes | Deterministic content/order where promised |

## Decisions required

Row grain, files/types, columns, data types, dialect, encoding, filename, timestamp format, null policy, ordering, authorization, sensitive fields, formula protection, and consistency snapshot.