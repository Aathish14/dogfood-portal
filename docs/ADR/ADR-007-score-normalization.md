# ADR-007 — Cross-Judge Normalization

## Status

Proposed / decision required

## Context

Cross-judge normalization is required, and opacity in existing platforms is a core problem. Fixtures include a constant-scoring judge.

## Problem

Judges may use different score levels/ranges. The source intentionally does not mandate an algorithm.

## Decision

No final normalization method. Any selected method must be documented, reproducible, handle zero variance, define missing/unequal review behavior, and expose raw versus normalized results. Judge-wise z-score normalization is only an advisory example.

## Alternatives Considered

- Raw averaging.
- Judge-wise z-scores.
- Robust centering/scaling.
- Rank/percentile transforms.
- Calibration through overlapping assignments/statistical models.
- Pairwise Bradley–Terry mode (bonus).

## Consequences

- Statistical assumptions and edge-case policies must be defended.
- Result provenance and worked examples are required for trustworthy operation.