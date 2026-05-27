# bsc-civio-delfos

Vault de documentación de Civio — **docs-first, scaffold-secondary**.

Este repositorio es un vault de Obsidian con análisis del ecosistema público de Civio (60+ repos). El scaffold Docker que incluye es una **base mínima ejecutable** para experimentos de datos, no desvía el propósito del vault.

## Quick start

```bash
# 1. Configurar variables locales
cp .env.example .env
# Editar .env si necesitás valores distintos

# 2. Arrancar servicios
docker compose up -d

# 3. Verificar conexión (smoke test)
docker compose exec data python -m pytest tests/smoke/ -v
```

## Servicios

| Servicio | Imagen | Puerto | Propósito |
|----------|--------|--------|-----------|
| `postgres` | `postgres:16` | 5432 | Base de datos local con persistencia en volumen nombrado |
| `data` | `python:3.12-slim` (build) | 8000 | Stack mínimo de datos (psycopg, polars, duckdb) |

## Alcance

| In scope | Out of scope |
|----------|-------------|
| PostgreSQL 16 con persistencia local | Frontend Svelte / Node |
| Python 3.12 con stack de datos | JupyterLab |
| Smoke test de conectividad | FastAPI / cualquier API |
| Scaffold Docker Compose | Scrapers reales |
| `.env` template | Makefile / CI/CD |

## Estado desechable

El volumen `postgres_data` sobrevive a `docker compose down` / `up`. Para reiniciar desde cero:

```bash
docker compose down -v
docker compose up -d
```

## Blueprint completo

Para la visión completa del entorno Dockerizado (frontend, Jupyter, scrapers), ver:
`vault-context/delfos-context/referencias/entorno-dockerizado.md`

## Rollback

```bash
# Eliminar scaffold
rm -rf docker-compose.yml .env.example README.md packages/data/
# Restaurar .gitignore (revertir commits)
```

El vault de Obsidian (`vault-context/`) queda intacto en cualquier caso.
