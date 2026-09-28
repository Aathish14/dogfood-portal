# ADR-010 — Offline-First Local Deployment

## Status

Accepted at requirements level; implementation pending

## Context

The portal must be adoptable and run on a laptop with networking disabled using `docker compose up`.

## Problem

Hosted databases, identity providers, CDNs, and mandatory SaaS integrations would violate the adoption/evaluation model.

## Decision

Package all core application services, assets, persistence, migrations, and fixture loading for local Docker Compose operation. Core T1/T2 behavior must not require an external account or network service.

## Alternatives Considered

- Cloud-hosted database/authentication (rejected).
- SaaS-only deployment (rejected).
- Local deployment with remotely loaded assets (insufficient for network-off operation).

## Consequences

- Images/dependencies must be available under the evaluator's setup assumptions.
- Local persistence, backup, and upgrades become operator responsibilities.
- Optional external integrations must fail without breaking core operation.