# Tasks: Docker + PostgreSQL Environment for Data Work

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~130–200 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Foundation: .gitignore, .env.example, docker-compose.yml | PR 1 | Base infra; no deps on other units |
| 2 | Core: packages/data/ scaffold + smoke test | PR 2 | Depends on PR 1 (compose service) |
| 3 | Docs: README.md | PR 3 | Independent; can merge anytime |

## Phase 1: Foundation / Infrastructure

- [x] 1.1 Create `packages/data/` directory structure (`packages/data/tests/smoke/`)
- [x] 1.2 Update `.gitignore` — append `.env`, `data/raw/`, `data/warehouse/`, `__pycache__/`, `.pytest_cache/`, `*.egg-info/`
- [x] 1.3 Create `.env.example` with `POSTGRES_USER=civio`, `POSTGRES_PASSWORD=change-me-locally`, `POSTGRES_DB=civio`, `POSTGRES_PORT=5432`
- [x] 1.4 Create root `docker-compose.yml` — services `postgres` (postgres:16, named volume `postgres_data`, port 5432, healthcheck) and `data` (build `./packages/data`, depends_on postgres, env_file `.env`, port 8000 placeholder, volume `./packages/data:/app`), network `civic-net`

## Phase 2: Core Implementation

- [x] 2.1 Create `packages/data/pyproject.toml` — build-system `hatchling`, deps `psycopg[binary]`, `polars`, `duckdb`, python `>=3.12`
- [x] 2.2 Create `packages/data/Dockerfile` — `python:3.12-slim` base, WORKDIR `/app`, copy `pyproject.toml` + `pip install .`, copy remaining files, CMD runs smoke test via `python -m pytest tests/smoke/`
- [x] 2.3 Create `packages/data/tests/smoke/test_connection.py` — `test_postgres_connection()` that reads `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT` from `os.environ`, connects to `host="postgres"` via `psycopg.connect()`, asserts `conn.is_closed is False`, closes connection

## Phase 3: Documentation

- [x] 3.1 Create root `README.md` — header stating vault-first/scaffold-secondary, quick-start section (cp .env.example .env, docker compose up -d, smoke test command), scope boundary table (in scope vs out of scope), link to `vault-context/delfos-context/referencias/entorno-dockerizado.md`

## Phase 4: Verification

- [x] 4.1 Run `docker compose config` to validate compose file syntax
- [x] 4.2 Run `docker compose up -d` and verify both services start clean
- [x] 4.3 Run `docker compose exec data python -m pytest tests/smoke/` and confirm smoke test passes
- [x] 4.4 Run `git status` after `cp .env.example .env` and confirm `.env` is not tracked

## Work-Unit Commit Plan

| Commit | Scope | Files |
|--------|-------|-------|
| `chore: add .gitignore entries for data env and caches` | .gitignore | `.gitignore` |
| `feat: add .env.example template for local Postgres` | Config | `.env.example` |
| `feat: add docker-compose.yml with postgres and data services` | Infra | `docker-compose.yml` |
| `feat: scaffold packages/data with pyproject, Dockerfile, and smoke test` | Core | `packages/data/pyproject.toml`, `packages/data/Dockerfile`, `packages/data/tests/smoke/test_connection.py` |
| `docs: add README with quick-start and scope boundary` | Docs | `README.md` |

Tests and docs stay with their user-visible change per work-unit-commits skill.
