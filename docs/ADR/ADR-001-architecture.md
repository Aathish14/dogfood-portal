# ADR-001 — Application Architecture

## Status

Proposed

## Context

The portal must be completed rapidly, start through Docker Compose, work offline, and integrate registration, submissions, judging, results, and export.

## Problem

No application process topology or framework is selected.

## Decision

Proposed: implement a modular monolith with explicit domain modules and one deployable application boundary, unless implementation evidence demonstrates a lower-risk alternative.

## Alternatives Considered

- Multiple independently deployed services.
- Monolith without explicit module boundaries.
- Serverless/hosted architecture (incompatible with mandatory offline operation).

## Consequences

- Fewer deployment/runtime dependencies for a 72-hour build.
- Authorization and transactions can remain centralized.
- Module discipline is required to avoid a tightly coupled codebase.
- Scaling characteristics remain unproven and no scaling target exists.