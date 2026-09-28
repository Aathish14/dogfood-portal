# ADR-005 — Submission Deadline Semantics

## Status

Partially accepted; boundary details proposed/TBD

## Context

The checker verifies that a closed fixture event refuses submissions and depends on the fixture's own `submissions_close` value.

## Problem

Replacing the fixture timestamp or trusting client time can accept late submissions. The exact inclusive/exclusive boundary and response code are not specified.

## Decision

Accepted requirement: preserve `submissions_close` and enforce it on the backend using authoritative server time. Proposed: store/compare UTC instants. Exact behavior at equality, draft edits, organizer override, and error response remain TBD and must match `run.py`.

## Alternatives Considered

- Client-side timer/check (rejected).
- Generated “now plus N days” fixture dates (rejected).
- Server-side local timezone without explicit policy (not selected).

## Consequences

- Boundary/timezone tests are required.
- Fixture import must preserve the timestamp exactly.
- Override and finalization semantics require product decisions.