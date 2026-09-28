# ADR-003 — Authentication Mechanism

## Status

Proposed

## Context

The checker requires four working authentication headers but does not perform login. The product itself requires authentication beyond a login-page demo and must work offline.

## Problem

No credential, password, session, token, or authentication library is selected.

## Decision

Proposed: use an offline-capable mechanism that produces revocable server-recognized credentials and can print/provide fixture headers at startup. Cookie sessions and locally verifiable tokens remain alternatives; no final choice is made.

## Alternatives Considered

- Server-side cookie sessions.
- Locally signed bearer tokens.
- Another offline-capable header mechanism.
- Hosted identity provider (rejected by source constraint).

## Consequences

- Session/token storage, expiration, revocation, CSRF, password handling, and secret management require follow-up decisions.
- `.dogfood.toml` can remain independent of the login UI.