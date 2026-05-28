# Design: Docker + PostgreSQL Environment for Data Work

## Technical Approach

Minimal data runtime scaffold under `packages/data/` using Docker Compose with two services (`postgres` + `data`). The design follows the "Minimal data app scaffold" approach from the exploration, keeping the repo docs-first while providing a verifiable execution path. All decisions align with `entorno-dockerizado.md` blueprint and the `docker-runtime-env` spec.

## Architecture Decisions

### Decision: Service placement

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `docker-compose.yml` in root | Root keeps repo clean; matches blueprint structure | **Root** — aligns with `entorno-dockerizado.md` and monorepo blueprint |
| `docker-compose.yml` under `packages/data/` | Closer to code, but harder to discover | Rejected — blueprint uses root |

### Decision: Python base image

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `python:3.12-slim` | Smaller image, official, matches blueprint | **slim** — weight matters in docs-first repo where few will build |
| `python:3.12` (full) | Includes build tools, ~2x larger | Rejected — not needed for runtime-only |
| `python:3.13-slim` | Newer, but less tested in Civio ecosystem | Rejected — 3.12 is the documented standard |

### Decision: PostgreSQL version and persistence

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `postgres:16` named volume | Matches DVMI pattern, mature, documented | **postgres:16 + named volume** |
| `postgres:17` latest | Newer features, less battle-tested | Rejected — blueprint explicitly uses 16 |
| Bind mount `./data/pg/` | Easier to inspect, but OS-dependent permissions | Rejected — named volume is cleaner for team portability |

### Decision: packaging approach

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `pyproject.toml` with `pip install .` | Modern standard, no extra tooling required | **pyproject.toml** — future-compatible with uv/pix if team adopts them |
| `requirements.txt` | Simpler, but legacy | Rejected — `pyproject.toml` is the current Python standard |
| `uv.lock` | Faster installs, but adds `uv` dependency | Rejected — extra tooling门槛 for a scaffold-first repo |

### Decision: Smoke test location

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `packages/data/tests/smoke/test_connection.py` | pytest structure, discoverable | **Inside container** via `docker compose exec` — no host pytest needed |
| External test runner | More automation, but requires CI setup | Rejected — out of scope |

### Decision: docs-first identity preservation

| Option | Tradeoff | Decision |
|--------|----------|----------|
| README explains boundary explicitly | One extra doc, clear signal | **README at root** — states this is scaffold-only, vault is primary |
| No explanation | Saves lines, but risks confusion | Rejected — exploration flagged this as the #1 risk |

## Data Flow

```
Contributor
    │
    │ docker compose up -d
    ▼
┌─────────────────────────────────┐
│  docker-compose.yml (root)      │
│  ├── postgres:16 ──┐            │
│  │                 │ 5432/tcp   │
│  ├── data (build)  │            │
│  │   python:3.12   │           │
│  └── civic-net     │           │
└─────────────────────────────────┘
         │                    │
         │  DNS resolve       │  Named volume
         ▼                    ▼
    ┌─────────┐        ┌──────────────┐
    │ postgres│◄──────►│ postgres_data│
    │ :5432   │  SQL   │ (persistent) │
    └─────────┘        └──────────────┘
         ▲
         │ psycopg connect
         │ (env vars from .env)
    ┌─────────┐
    │  data   │
    │  :8000  │  (placeholder)
    └─────────┘
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `docker-compose.yml` | Create | Root Compose file: `postgres` + `data` services, `civic-net` network, `postgres_data` volume |
| `.env.example` | Create | Template with `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` placeholders |
| `.gitignore` | Modify | Add `.env`, `data/raw/`, `data/warehouse/`, `__pycache__/`, `.pytest_cache/`, `*.egg-info/` |
| `README.md` | Create | Startup instructions, docs-first boundary explanation, smoke test command |
| `packages/data/Dockerfile` | Create | python:3.12-slim, copy pyproject.toml + install deps, copy app, smoke test CMD |
| `packages/data/pyproject.toml` | Create | `psycopg[binary]`, `polars`, `duckdb` — minimal data stack |
| `packages/data/tests/smoke/test_connection.py` | Create | Verifies `psycopg` connects to Postgres using env vars |

## Interfaces / Contracts

### Environment Variables (`.env` / Compose `env_file`)

```yaml
# docker-compose.yml references
POSTGRES_USER=civio
POSTGRES_PASSWORD=change-me-locally
POSTGRES_DB=civio
```

Python service reads these via `os.environ["POSTGRES_USER"]`, etc. No hardcoded values.

### Docker Compose Service Contract

```yaml
services:
  postgres:
    image: postgres:16
    env_file: .env
    volumes: [postgres_data:/var/lib/postgresql/data]
    ports: ["5432:5432"]
    healthcheck: ...

  data:
    build: ./packages/data
    env_file: .env
    depends_on: [postgres]
    ports: ["8000:8000"]  # placeholder
    volumes: [./packages/data:/app]
```

### Smoke Test Contract

```python
# packages/data/tests/smoke/test_connection.py
import os
import psycopg

def test_postgres_connection():
    """Verify data service can reach PostgreSQL."""
    conn = psycopg.connect(
        host="postgres",          # Docker DNS name
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    assert conn.is_closed is False
    conn.close()
```

Key contract: `host="postgres"` (Docker DNS), credentials from env only, exits non-zero on failure.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Smoke | Python → Postgres connectivity | `docker compose exec data python -m pytest tests/smoke/` |
| Smoke | Missing env vars cause clear error | Omit `.env`, run same command, expect `KeyError` or `OperationalError` |
| Integration | Volume persistence | Write data, `down`/`up`, query again |
| Integration | `.env` not in git status | `git status` after `cp .env.example .env` |

No unit or E2E framework required — smoke test is the verification gate per spec.

## Migration / Rollout

No migration required. This is additive scaffolding in a docs-only repo.

Rollout sequence:
1. Clone repo → `cp .env.example .env` (edit placeholders)
2. `docker compose up -d`
3. `docker compose exec data python -m pytest tests/smoke/`

## Security / Secrets Handling

- `.env` is in `.gitignore` — never committed
- `.env.example` contains only placeholder strings (`change-me-locally`, `civio`, `5432`)
- No real credentials exist in the repo
- PostgreSQL uses default `postgres` superuser — acceptable for local-only dev
- Port `5432` exposed to host for debugging but only accessible via Docker network in practice
- Port `8000` is a placeholder with no active listener

## Rollback Strategy

1. `git revert` the change commit (single commit expected)
2. Or manually: delete `docker-compose.yml`, `.env.example`, `README.md`, `packages/data/`
3. Restore `.gitignore` to original 4-line state (OS + Obsidian + agent caches)
4. Vault content (`vault-context/`) is untouched — zero risk to documentation

## Preserving Docs-First Identity

| Signal | Mechanism |
|--------|-----------|
| README header | States "vault-first, scaffold-secondary" explicitly |
| `packages/data/` scope | Only data stack (no frontend, no API, no Jupyter) |
| Blueprint reference | README links to `entorno-dockerizado.md` for full vision |
| Git structure | `vault-context/` remains the primary directory; `packages/data/` is supplementary |
| Commit message | Follows Conventional Commits in Spanish, scope-tagged |

## Open Questions

- [ ] Should `pyproject.toml` include a `build-system` section pointing to `setuptools` or `hatchling`? (Both work; `hatchling` is lighter for a smoke-test-only project.)
- [ ] Is port `8000` the right placeholder, or should we leave it unexposed until a real service binds it?
- [ ] Should we add a `docker compose config` verification step to the README?

## Next Step

Ready for tasks (sdd-tasks).
