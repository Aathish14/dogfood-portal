# ADR-002 — Persistence Technology

## Status

Proposed

## Context

The portal needs event-scoped roles, teams, projects, assignments, criterion scores, results, and exports, and must run locally/offline.

## Problem

No database technology, schema, migration tool, or persistence layout is specified.

## Decision

Proposed: select a locally runnable relational database because the advisory source recommends one and the domain is strongly relational. The specific product remains TBD.

## Alternatives Considered

- Embedded relational database.
- Containerized client/server relational database.
- Document/key-value persistence.
- Files-only persistence.

## Consequences

- Relational constraints may support ownership and judging integrity.
- Compose/offline packaging and backup procedures must be documented.
- Product/version selection, migration tooling, concurrency, and operational complexity remain open.