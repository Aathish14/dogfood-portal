# ADR-008 — Audit and Result Provenance Design

## Status

Proposed

## Context

T3 requires anti-abuse with an audit trail. Judging transparency also benefits from result-run provenance.

## Problem

No audit schema, immutability model, retention, privacy, administrator access, or deletion policy is specified.

## Decision

Proposed: store append-oriented audit events containing event, time, actor, role, action, target, outcome, and safe metadata; store result-run method/inputs/parameters/outputs/warnings separately or as linked provenance. Final storage/immutability policy remains TBD.

## Alternatives Considered

- Application logs only.
- Mutable audit table.
- Append-only database records.
- Hash-chained/verifiable audit records.

## Consequences

- Sensitive data must be redacted.
- Storage/retention grows over time.
- Administrator override and deletion policy require explicit governance.