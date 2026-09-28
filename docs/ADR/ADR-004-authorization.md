# ADR-004 — Backend and Object-Level Authorization

## Status

Accepted at requirements level; implementation pending

## Context

The critical acceptance rule requires a judge to be unable to read a peer judge's scores. Frontend hiding is explicitly insufficient.

## Problem

Role checks alone may not prevent access to another judge's object when an identifier is supplied in a path/query.

## Decision

Enforce authorization in the backend on every protected request. At minimum, evaluate authenticated identity, event role, and judge-score ownership/assignment. `judge_b` targeting `judge_a` scores must receive `401` or `403`.

## Alternatives Considered

- Frontend-only visibility controls (rejected).
- Trusting a requested judge/team identifier (rejected).
- Role-only checks without object ownership (insufficient for peer isolation).

## Consequences

- Authorization policy becomes a central reusable component.
- Direct HTTP negative tests are mandatory.
- Organizer visibility into judge scores and event-scoping details still require decisions.