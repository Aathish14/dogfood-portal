# ADR-006 — Judge Assignment Strategy

## Status

Proposed / decision required

## Context

T2 requires judge invitation/assignment and multiple judges per project. Fixtures include unfinished batches.

## Problem

No coverage target, workload rule, expertise model, conflict policy, overlap requirement, or reassignment algorithm is specified.

## Decision

No final strategy. The implementation must document desired judges per project, workload balancing, expertise/conflicts, normalization overlap, incomplete-batch reassignment, and assignment mutability.

## Alternatives Considered

- Manual assignment.
- Round-robin/balanced assignment.
- Track/expertise-aware assignment.
- Optimization-based assignment.

## Consequences

- Progress and normalization quality depend on the eventual choice.
- The decision must be testable against incomplete batches and conflict scenarios.