# DOGFOOD Portal — Developer and Operator Runbook

## Current status

As of September 27, 2026, the repository contains documentation sources but no portal implementation, Docker Compose file, database configuration, fixture JSON, or checker. Therefore the required application startup procedure cannot currently be executed or verified.

The event hacking window is open on this date and the code freeze is September 29, 2026 at 18:00 UTC, as recorded by the source materials.

## Prerequisites

### Portal runtime

Source-defined prerequisite:

- Docker with Docker Compose capability sufficient to run `docker compose up`.

Unknown/TBD:

- supported operating systems and architecture;
- Docker/Compose versions;
- CPU, memory, and disk;
- ports;
- browser support;
- application language/runtime;
- database technology.

### Documentation build

The current repository uses LaTeX. A working TeX installation with the packages imported by `main.tex` is required. The local `longtable-finite-glue.sty` must be resolvable from the project directory.

## Installation

### Portal

Blocked: no source code, image definitions, Dockerfile, or Compose file is present.

### Documentation

From the project root, the established build command used in this workspace is:

```sh
latexmk -pdf main.tex
```

This builds documentation only, not the hackathon portal.

## Configuration

The required future portal must provide root `.dogfood.toml`. See [CONFIGURATION.md](CONFIGURATION.md). Environment variables and database settings are TBD.

## Startup

### Required final portal startup

```sh
docker compose up
```

Expected source-defined outcome: a seeded, working portal available locally and usable without network access.

Current outcome: cannot execute because no Compose file exists.

## Shutdown

No verified shutdown command is documented because no Compose configuration exists. Standard Compose operations may be selected by the future implementation but must be tested and documented before being presented as project procedure.

## Restart

Recommended final behavior:

1. stop and restart the Compose project;
2. preserve existing event data;
3. avoid duplicating fixture records;
4. restore application readiness without external network access.

No restart procedure is currently executable.

## Database initialization

Database technology and initialization are TBD. The final startup path must initialize required schema and seed fixtures or clearly document a local command executed before checker use. Hosted database dependency is prohibited.

## Database migration

No migration tooling exists. The future implementation must document apply, status, failure, rollback/forward-fix, and compatibility with persisted fixture/event data.

## Fixture loading

Required behavior:

- load the provided `fixtures.json`;
- preserve exact `submissions_close`;
- expose fixture projects publicly;
- make four checker identities usable;
- retain intentional edge cases.

Current blocker: fixture file and loader are absent.

## Health checks

No health endpoint or Compose health check exists. Advisory guidance recommends distinguishing application liveness from database/readiness. Path, schema, and thresholds are TBD.

## Logs

No logging implementation exists. Future logs should make migration, seed, authentication, assignment, normalization, export, and webhook failures diagnosable while redacting credentials and unnecessary personal data.

## Debugging checklist

When implementation exists:

1. Confirm Compose services/health.
2. Confirm local port/base URL matches `.dogfood.toml`.
3. Confirm fixture load counts and exact close timestamp.
4. Confirm printed/configured auth headers.
5. Call gallery anonymously.
6. Call own/peer/participant judge routes directly.
7. Parse CSV with a standard reader.
8. Check logs without exposing auth headers.
9. Re-run the official checker.

## Backup

No persistence technology or backup command exists. The future runbook must identify all persistent volumes/files (database and uploads), consistency requirements, and a tested backup command.

## Restore

No restore procedure exists. Before adoption, test restoring into a clean local environment and verify users/roles, submissions, assignments, scores, results, audit/provenance, and assets.

## Data persistence

The source implies persistent event operation but does not specify volumes or retention. Ordinary restart should preserve data (recommended). Fixture reset must be separate from ordinary startup and destructive behavior must be opt-in (recommended).

## Offline operation verification

1. Obtain all permitted images/dependencies in advance.
2. Disable outbound networking.
3. Run final documented startup.
4. Load all T1/T2 pages/assets.
5. Authenticate the four identities.
6. Exercise submission, judging, normalization, and CSV.
7. Run `run.py .dogfood.toml`.
8. Restart and confirm persistence.

This procedure is currently blocked by absent implementation and checker artifacts.

## Failure recovery

Policies/commands are TBD for:

- failed migration;
- malformed/missing fixture file;
- unavailable local database;
- corrupted persistence;
- invalid auth configuration;
- failed normalization;
- export failure;
- webhook failure (T4);
- accidental destructive reset.

## Upgrade procedure

No application versioning or upgrade mechanism exists. A future procedure must cover image/build version, schema migrations, backups, compatibility, downtime, and fixture/config changes.

## Rollback

No rollback strategy exists. Decide whether rollback means restoring prior containers plus compatible schema, forward-fixing, or restoring a backup. Record the decision in ADRs and test it.

## Operational security

- Treat `.dogfood.toml` auth headers as secrets.
- Keep runtime offline-capable.
- Do not log credentials.
- Restrict local data/backup access.
- Verify backend authorization with direct HTTP requests.
- Separate fixture/test credentials from real operation.
- Document organizer privilege and audit access.

## Release/submission runbook

1. Confirm OSI license.
2. Build from a clean checkout.
3. Start with `docker compose up`.
4. Verify offline behavior.
5. Validate fixtures and auth headers.
6. Populate `.dogfood.toml` honestly.
7. Run tests and acceptance checker.
8. Commit actual `acceptance-report.txt`.
9. Verify README, architecture, data model, and judging docs match code.
10. Record known limitations and freeze code by the event deadline.

## Current operational blockers

Portal source, Dockerfile/Compose, database/schema, migrations, fixtures, checker, `.dogfood.toml`, acceptance report, license, and application configuration are all absent.