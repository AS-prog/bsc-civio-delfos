# Proposal: Docker + PostgreSQL Environment for Data Work

## Intent

El repositorio `bsc-civio-delfos` es un vault de documentación sin código ejecutable. El blueprint `entorno-dockerizado.md` describe un entorno Docker completo para la hackathon de Civio, pero nunca se implementó.

Este cambio introduce un **scaffold mínimo ejecutable** bajo `packages/data/` con Docker Compose (Python + PostgreSQL) que permite a cualquier miembro del equipo clonar y arrancar con `docker compose up` — sin dependencias locales — validando la infraestructura base antes de añadir frontend, Jupyter o APIs.

## Scope

### In Scope
- `docker-compose.yml` con servicios `postgres` y `data` (Python 3.12-slim)
- `packages/data/Dockerfile` mínimo (shell + psycopg smoke test)
- `packages/data/pyproject.toml` con dependencias de conexión a Postgres (psycopg, polars, duckdb)
- `.env.example` con credenciales locales de PostgreSQL
- `.gitignore` actualizado (`.env`, `data/raw/`, `data/warehouse/`, caches Python)
- `README.md` con instrucciones de arranque y explicación del límite docs-first vs. runtime
- Reconciliación con `entorno-dockerizado.md` (referencia, no duplicación)

### Out of Scope
- Frontend Svelte / Node
- JupyterLab (contenedor o puerto)
- FastAPI o cualquier API
- Scrapers reales (solo estructura de carpetas si existe)
- Makefile de atajos
- CI/CD o despliegue
- Migración al monorepo completo

## Capabilities

### New Capabilities
- `docker-runtime-env`: Docker Compose environment providing Python 3.12 + PostgreSQL 16 services with local data persistence.

### Modified Capabilities
- None (no existing spec-level capabilities to modify; this is a docs-only vault).

## Approach

**Minimal data app scaffold** (enfoque recomendado por exploración):

1. **`docker-compose.yml`** en raíz con dos servicios:
   - `postgres` → `postgres:16` con volumen nombrado `postgres_data`, expuesto en `5432`
   - `data` → build de `packages/data/Dockerfile` (python:3.12-slim), mount de `./packages/data:/app`, depende de `postgres`, expuesto en `8000` (placeholder para futuro endpoint)
   - Red `civio-net` para resolución DNS entre servicios

2. **`packages/data/`** con:
   - `Dockerfile` multi-stage mínimo (slim + copiado de pyproject.toml + deps)
   - `pyproject.toml` con `psycopg[binary]`, `polars`, `duckdb`
   - `tests/smoke/test_connection.py` — script que verifica conexión a Postgres

3. **`.env.example`** — variables `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` (sin valores reales)

4. **`.gitignore`** — extender con `data/`, `.env`, `__pycache__/`, `.pytest_cache/`, `*.egg-info/`

5. **`README.md`** — explicar que el repo es docs-first, el scaffold es base técnica para experimentos, y dar comandos de arranque

**Base images**: `python:3.12-slim` (coherente con blueprint, peso reducido, imagen oficial estable) y `postgres:16` (coherencia con DVMI de Civio, versión madura documentada en `entorno-dockerizado.md`).

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `docker-compose.yml` | New | Compose file with postgres + data services |
| `.env.example` | New | Non-sensitive credential template |
| `.gitignore` | Modified | Add data/, .env, Python cache patterns |
| `README.md` | New | Startup instructions + docs-first boundary explanation |
| `packages/data/Dockerfile` | New | Python 3.12-slim build for data service |
| `packages/data/pyproject.toml` | New | Minimal dependency declaration |
| `packages/data/tests/smoke/test_connection.py` | New | Smoke test verifying Postgres connectivity |
| `vault-context/delfos-context/referencias/entorno-dockerizado.md` | Referenced | Blueprint to reconcile with (no changes) |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Cambio de identidad del repo (docs-only → ejecutable) | Medium | README explica explícitamente el límite; scaffold mínimo no desvía el propósito del vault |
| Duplicación con `entorno-dockerizado.md` | Medium | README y Dockerfile referencian el blueprint; no reimplementar frontend/Jupyter |
| Secrets expuestos por error | Low | `.env` en `.gitignore`, solo `.env.example` versionado con placeholders |
| Confusión sobre volumen `postgres_data` | Low | README indica que es estado desechable/local |

## Rollback Plan

1. Eliminar `docker-compose.yml`, `.env.example`, `README.md`, `packages/data/`
2. Revertir cambios en `.gitignore` al estado anterior (3 líneas de Obsidian + OS)
3. El vault de Obsidian queda intacto — no se toca contenido de `vault-context/`

## Dependencies

- Docker Desktop o Docker Engine con Compose plugin (requisito del blueprint)
- No requiere dependencias externas de red (Postgres corre en contenedor)

## Review Workload Forecast

| File | Est. líneas | Tipo |
|------|-------------|------|
| `docker-compose.yml` | 35–45 | New |
| `.env.example` | 5–8 | New |
| `.gitignore` (modificado) | +6 / -0 | Modified |
| `README.md` | 40–55 | New |
| `packages/data/Dockerfile` | 12–18 | New |
| `packages/data/pyproject.toml` | 15–20 | New |
| `packages/data/tests/smoke/test_connection.py` | 15–25 | New |
| **Total** | **~128–197** | |

Riesgo frente al presupuesto de 400 líneas: **Low**. Chained PRs no necesarios a menos que se amplíe el scope (Jupyter, frontend, Makefile).

## Success Criteria

- [ ] `docker compose up -d` levanta postgres y data sin errores
- [ ] `docker compose exec data python -c "..."` verifica conexión a Postgres
- [ ] `.env` no aparece en `git status` (correctamente ignorado)
- [ ] `postgres_data` sobrevive a `docker compose down` / `up`
- [ ] README ejecutable: un contributor nuevo puede arrancar el entorno sin consultar vault

## Next Recommended Phase

**specs + design** (en paralelo o secuencial):
- `sdd-spec`: definir requisitos funcionales (Given/When/Then) para el arranque del entorno, persistencia de datos, y smoke test
- `sdd-design`: diagrama de secuencia del arranque Compose, decisiones de red/volumen, y arquitectura de contenedores alineada con `entorno-dockerizado.md`
