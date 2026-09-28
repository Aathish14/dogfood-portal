# DOGFOOD Portal — Configuration Reference

## Status

Only the `.dogfood.toml` format is described by the source. No actual configuration file, environment-variable loader, Compose file, or implementation defaults are present.

## `.dogfood.toml`

The file belongs at the repository root and tells the acceptance checker where the implementation placed required behavior. The checker does not log in; it uses supplied headers.

### Source sample

```toml
[portal]
base_url = "http://localhost:8080"

[tiers]
claimed = ["T1", "T2"]

[auth]
organizer   = "Cookie: session=org_7f2a"
judge_a     = "Cookie: session=jdg_a_91bc"
judge_b     = "Cookie: session=jdg_b_44de"
participant = "Cookie: session=prt_2e88"

[routes]
gallery      = "/projects"
submit       = "/projects/new"
judge_scores = "/api/judge/scores"
peer_scores  = "/api/judge/scores?judge=judge_a"
csv_export   = "/api/export.csv"
```

The values are examples, not required defaults.

## Configuration keys

| Variable/key | Required | Default | Purpose | Sensitive |
|---|---:|---|---|---:|
| `portal.base_url` | Yes | None; sample `http://localhost:8080` | Portal origin used by checker | No, unless environment-specific policy says otherwise |
| `tiers.claimed` | Yes | None; sample `T1`, `T2` | Honest list of tiers the checker/evaluator should assess | No |
| `auth.organizer` | Yes | None | Complete HTTP auth header for organizer identity | **Yes** |
| `auth.judge_a` | Yes for T2 checks | None | Complete HTTP auth header for first judge | **Yes** |
| `auth.judge_b` | Yes for peer check | None | Complete HTTP auth header for second judge | **Yes** |
| `auth.participant` | Yes | None | Complete HTTP auth header for participant | **Yes** |
| `routes.gallery` | Yes for T1 | None | Public gallery route | No |
| `routes.submit` | Yes for T1 | None | Submission route used for closed-event check | No |
| `routes.judge_scores` | Yes for T2 | None | Authenticated judge's score route | No |
| `routes.peer_scores` | Yes for T2 | None | Route/query that targets a peer judge's scores | May contain identifiers, not normally secret |
| `routes.csv_export` | Yes for T2 | None | CSV export route | No |

Exact conditional requirements based on `tiers.claimed` come from `run.py`, which is absent.

## Secrets

Auth values are working credentials and must be treated as sensitive local test configuration. Do not copy sample-like fixture credentials into production. The actual secret-generation/storage mechanism is TBD.

## Ports and URLs

Port `8080` is a sample only. The implementation may choose another local port and declare it in `base_url`. Bind address, TLS, proxy, and multi-host behavior are not specified.

## Environment variables

No environment variables are defined by the supplied files.

| Category | Status |
|---|---|
| Database URL/path | TBD |
| Session/token secret | TBD |
| Application port | TBD |
| Log level | TBD |
| Fixture path/reset mode | TBD |
| Result/normalization settings | TBD |
| Feature flags | TBD |
| Webhook/API credentials | TBD |

Future variables must be documented here with requiredness, defaults, sensitivity, and offline-safe behavior.

## Database configuration

No database technology or configuration is selected. Hosted databases are prohibited as mandatory dependencies; any database must run locally/offline under the selected architecture.

## Feature flags

No feature-flag system exists. Tier claims are declarations to the checker, not necessarily runtime feature flags. If feature flags are added, claims must remain honest and checker routes must match active behavior.

## Acceptance configuration

The authoritative acceptance configuration is `.dogfood.toml` plus `run.py`. No other acceptance configuration is specified.

## Fixture configuration

No fixture path/key is specified. The application must use the provided fixture event's own `submissions_close`. Loader invocation, reset mode, and seed idempotency are implementation decisions.

## Validation recommendations

On checker startup, validate missing sections/keys, malformed header values, non-HTTP base URL, unsupported tier names, and relative route shape. Exact checker behavior cannot be claimed without `run.py`.

## Open decisions

Environment-variable naming, database settings, secret injection, production vs fixture configuration, feature flags, log level, health route, fixture reset, normalization parameters, webhook settings, and API client configuration.