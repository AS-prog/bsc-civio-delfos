# Plan: Base de Datos del Corpus de Transparencia (lista para consumo)

> **Alcance de este documento**: dejar el corpus de Publicidad Activa cargado en
> Postgres (`civio`) y listo para ser consultado. Cubre la limpieza del corpus en el
> scraper y el ETL Parquet → Postgres. **No** cubre el servidor MCP: eso vive en
> [plan-mcp-transparencia.md](plan-mcp-transparencia.md), que **depende** de este plan.
>
> Origen: división de [frolicking-riding-pascal.md](frolicking-riding-pascal.md).
> Especificación funcional de referencia: [instrucciones-mcp-transparencia.md](instrucciones-mcp-transparencia.md).

## Context

El scraper de `transparencia.gob.es` ya extrajo un corpus de **1167 páginas** de Publicidad
Activa, persistido en Parquet (`data/warehouse/*.parquet`) + JSONL. Antes de exponerlo vía
MCP hace falta un modelo de datos limpio y una base relacional poblada que cualquier capa de
consulta pueda usar.

Decisiones del usuario que dirigen este plan:
1. **Fuente de datos**: cargar Parquet → **Postgres** (DB `civio`, ya provisionada) vía ETL.
2. **Modelo limpio**: arreglar también el **scraper** (storage + parser), no solo normalizar
   aguas abajo. Re-exportar desde caché con `reparse_cache.py` (cero red).
3. **Datos realistas**: solo lo que el corpus tiene. "Subvenciones" = *enlaces a pap.hacienda*,
   NO montos ni años (no existen en los datos).

Correcciones de hechos respecto al documento original:
- La DB se llama **`civio`**, no `podcast`.
- El corpus **no está en SQL**: hoy vive en Parquet; Postgres está vacío.
- "Organismo" en este corpus es en realidad **materia** (categoría temática del path
  `/por-materias/<slug>/`), no la entidad emisora. 89% es `organizacion-empleo`.

## Approach

Flujo de este plan: `scraper limpio → re-export parquet → ETL a Postgres`. La salida es una
base `civio` poblada y consultable, que el plan del MCP consume sin volver a tocar el scraper.

Reutilizar lo existente: patrón de conexión `psycopg` de
`packages/data/tests/smoke/test_connection.py`, `reparse_cache.py` para regenerar parquet
sin red, y las deps ya presentes (`psycopg[binary]`, `polars`, `duckdb`, `typer`).

## Fases (incrementales, cada una con verificación)

### Fase 0 — Limpieza del corpus (toca el scraper)
Archivos: `packages/data/scrapers/transparencia/{parse.py, models.py, storage.py}`,
re-correr `packages/data/scripts/reparse_cache.py`.

- **parse.py**: deduplicar `_breadcrumb` (hoy emite espejo `['Inicio',...,'Inicio',...]`
  por usar dos selectores que matchean los mismos `li`).
- **storage.py**: nombres consistentes jsonl↔parquet (`external_link_count` en ambos),
  `breadcrumb` como **array nativo** (no string colapsado), columnas derivadas
  `materia_slug` (path idx 2) y `materia_label` (breadcrumb deduplicado), y **nueva tabla
  `transparencia_accordion.parquet`** (`url, ord, title, content`) — hoy el contenido de
  acordeones se pierde por completo. Añadir `ord` a sections y links para orden estable.
- Diferido a v2 (acotar blast radius): `internal_links` con anchor text.
- **Verificación**: re-correr reparse en el contenedor `data`; confirmar 1167 pages,
  `transparencia_accordion.parquet` con filas, breadcrumb sin duplicados.

### Fase 1 — Schema Postgres + ETL
Archivos nuevos: `packages/mcp-transparencia/sql/schema.sql`,
`packages/mcp-transparencia/etl/load_parquet.py` (CLI `typer`).

- **schema.sql**: DDL con tipos estrictos, `COMMENT ON` por tabla/columna, FK lógicas e
  índices. Tablas: `transparencia_pages` (PK url, breadcrumb `text[]`, `materia_slug`,
  `search_tsv tsvector`), `transparencia_sections`, `transparencia_accordion`,
  `transparencia_links` (con `scope` y `target_domain` derivado). Vistas:
  `v_link_categories` (clasifica subvenciones=pap.hacienda / normativa=boe.es /
  documento=dam / otro) y `v_organisms` (resumen por materia).
- **ETL**: psycopg reusando patrón del smoke test; `TRUNCATE ... RESTART IDENTITY CASCADE`
  + carga con `COPY FROM STDIN` (idempotente, una transacción); deriva `target_domain`,
  `updated_at`→`date` (tolerar NULL), pobla `search_tsv` con
  `to_tsvector('spanish', title+headings+accordion)`. Flag `--verify` imprime counts.
- **Verificación**: `count(*)` por tabla (pages≈1167, links≈13k, accordion>0);
  `SELECT * FROM v_organisms` lista las 6 materias; `v_link_categories` clasifica bien.

## Archivos críticos
- A modificar: `packages/data/scrapers/transparencia/{parse.py, storage.py, models.py}`,
  re-correr `packages/data/scripts/reparse_cache.py`.
- A reutilizar: `packages/data/tests/smoke/test_connection.py` (patrón psycopg).
- A crear: `packages/mcp-transparencia/sql/schema.sql`,
  `packages/mcp-transparencia/etl/load_parquet.py`.

## Riesgos / decisiones abiertas
- Extensiones Postgres (`unaccent`/`pg_trgm`) requieren `CREATE EXTENSION`: si el user
  `civio` no puede, la búsqueda aguas abajo usa solo `tsvector` (sin fuzzy/acento-insensible).
- `accordion.content`: verificar en Fase 0 que el HTML cacheado trae los paneles
  server-rendered (no por JS).
- P1 (JSONL append/duplicación) sigue vivo en el scraper; el ETL hace `TRUNCATE+load`, así
  que la base no hereda duplicados, pero conviene cerrar P1 igual (ver
  [pendientes-scraper-transparencia.md](pendientes-scraper-transparencia.md)).

## Verification (de este plan)
1. Fase 0: re-parse en contenedor → `transparencia_accordion.parquet` existe, breadcrumb limpio.
2. Fase 1: `python etl/load_parquet.py --verify` → counts esperados; vistas correctas.

Con la base `civio` poblada y verificada, continuar en
[plan-mcp-transparencia.md](plan-mcp-transparencia.md).
