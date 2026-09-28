# ADR-009 — API and Webhook Versioning

## Status

Proposed / planned T4

## Context

T4 requires REST API and webhooks; the API First bonus requires all UI actions and OpenAPI documentation.

## Problem

No API version, compatibility, error, webhook payload, retry, or deprecation contract exists.

## Decision

No final versioning scheme. Before T4 is claimed, select an explicit API and webhook payload version strategy, document it in OpenAPI, and define compatibility/deprecation. Webhook delivery IDs and versioned payloads are recommended.

## Alternatives Considered

- URI versioning.
- Header/media-type versioning.
- Unversioned API with compatibility discipline.

## Consequences

- Client stability depends on the choice.
- OpenAPI, idempotency, webhook signing/replay, and deprecation tests must align.