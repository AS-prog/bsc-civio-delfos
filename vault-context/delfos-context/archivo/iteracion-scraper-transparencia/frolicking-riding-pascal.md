# Plan: MCP del Corpus de Transparencia (Publicidad Activa)

> **Documento dividido.** Este plan se separó en dos planes encadenados por dependencia.
> Usá esos como fuente de verdad; este queda como referencia histórica:
> 1. [plan-base-datos-transparencia.md](plan-base-datos-transparencia.md) — base `civio`
>    lista para consumo (Fases 0–1: limpieza del corpus + ETL Parquet → Postgres).
> 2. [plan-mcp-transparencia.md](plan-mcp-transparencia.md) — servidor MCP (Fases 2–4:
>    capa SQL + marts + server + integración con agente).

## Context

El scraper de `transparencia.gob.es` ya extrajo un corpus de **1167 páginas** de Publicidad
Activa, persistido en Parquet (`data/warehouse/*.parquet`) + JSONL. El documento
`instrucciones-mcp-transparencia.md` pide convertir ese corpus en un **servidor MCP en
Python** consumible por cualquier agente (Claude Code, OpenCode, Cursor), con dos capas:
**SQL** (consultas directas) y **marts** (reglas de negocio / vistas analíticas).

Decisiones del usuario que dirigen este plan:
1. **Fuente de datos**: cargar Parquet → **Postgres** (DB `civio`, ya provisionada) vía ETL;
   el MCP consulta Postgres con `psycopg`.
2. **Modelo limpio**: arreglar también el **scraper** (storage + parser), no solo normalizar
   en el MCP. Re-exportar desde caché con `reparse_cache.py` (cero red).
3. **Tools realistas**: solo lo que el corpus tiene. "Subvenciones" = *enlaces a pap.hacienda*,
   NO montos ni años (no existen en los datos).

Correcciones de hechos respecto al documento original:
- La DB se llama **`civio`**, no `podcast`.
- El corpus **no está en SQL**: hoy vive en Parquet; Postgres está vacío.
- "Organismo" en este corpus es en realidad **materia** (categoría temática del path
  `/por-materias/<slug>/`), no la entidad emisora. 89% es `organizacion-empleo`.

## Approach

Construir un paquete nuevo `packages/mcp-transparencia/` (hermano de `packages/data/`),
precedido por una limpieza del corpus en el scraper existente. Flujo:
`scraper limpio → re-export parquet → ETL a Postgres → capa SQL → marts → servidor MCP`.

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

### Fase 2 — Capa SQL del MCP
Archivos: `packages/mcp-transparencia/sql/{connection.py, models.py, queries.py}`.

- `connection.py`: `get_connection()` por env (`POSTGRES_HOST` default `localhost`, etc.).
- `queries.py`: funciones puras, **siempre parametrizadas** (`%s`, nunca f-string):
  `fetch_page`, `search_pages` (`search_tsv @@ plainto_tsquery('spanish', %s)`),
  `links_by_domain`, `links_by_category`, `list_organisms`.
- `models.py`: dataclasses del esquema limpio (`PageDetail`, `Section`, `AccordionItem`, `Link`).
- **Verificación**: `tests/test_queries.py` contra Postgres real (fetch_page devuelve
  secciones; search_pages("empleo")>0; links_by_domain("boe.es")>0).

### Fase 3 — Marts + servidor MCP
Archivos: `packages/mcp-transparencia/marts/{rules,aggregations,enrichments}.py`,
`packages/mcp-transparencia/mcp_server.py`, `pyproject.toml` (añade dep `mcp>=1.2`).

- SDK oficial **`mcp` (FastMCP)**; transporte **stdio** primario. Tools (docstrings
  explican honestamente qué son los datos):

| Tool | Capa | Devuelve |
|---|---|---|
| `get_page(url)` | sql→mart | página completa: metadata, breadcrumb, sections, accordion, links clasificados |
| `search_pages(query, limit=20)` | sql | `{url, title, materia_label, rank}` por relevancia |
| `list_organisms()` | mart | resumen por materia (page_count, external_links, accordion) |
| `get_external_links(domain, limit=100)` | sql | enlaces salientes filtrados por dominio |
| `get_links_by_category(category, materia=None)` | mart | enlaces ∈ {subvenciones, normativa, documento, otro} |
| `get_links_by_organism(category=None)` | mart | conteo enlaces por materia×categoría (sin montos/años) |

- `list_organisms` conserva el nombre del doc por compatibilidad, pero el docstring aclara
  que devuelve **materias** (categorías temáticas), no entidades emisoras.
- **Verificación**: `mcp dev mcp_server.py` (MCP Inspector) o `tests/test_tools.py`.

### Fase 4 — Integración con agente
Archivos: `packages/mcp-transparencia/.mcp.json.example`, README.

- Registrar en Claude Code (`.mcp.json`) con `command: python`,
  `args: [packages/mcp-transparencia/mcp_server.py]`, env de Postgres.
- **Criterio de éxito (del doc)**: un agente externo ejecuta `get_page(url)` y recibe el
  PageData completo, y `list_organisms()` devuelve el resumen.
- HTTP en :8000 (puerto ya expuesto): opcional, vía **servicio `mcp` nuevo en compose**
  (no reusar `data` para no romper su smoke test). Diferido a v2.

## Archivos críticos
- A modificar: `packages/data/scrapers/transparencia/{parse.py, storage.py, models.py}`,
  re-correr `packages/data/scripts/reparse_cache.py`.
- A reutilizar: `packages/data/tests/smoke/test_connection.py` (patrón psycopg).
- A crear: todo `packages/mcp-transparencia/` (server, sql/, marts/, etl/, schema.sql,
  pyproject.toml, .mcp.json.example).

## Riesgos / decisiones abiertas
- **"Organismo" ≠ entidad emisora** y el corpus es 89% una sola materia: framing honesto
  en docstrings. (Confirmar si preferís renombrar la tool a `list_materias()`.)
- Extensiones Postgres (`unaccent`/`pg_trgm`) requieren `CREATE EXTENSION`: si el user
  `civio` no puede, `search_pages` usa solo `tsvector` (sin fuzzy/acento-insensible).
- `accordion.content`: verificar en Fase 0 que el HTML cacheado trae los paneles
  server-rendered (no por JS).
- P1 (JSONL append/duplicación) sigue vivo en el scraper; el ETL hace `TRUNCATE+load`, así
  que el MCP no hereda duplicados, pero conviene cerrar P1 igual.

## Verification (end-to-end)
1. Fase 0: re-parse en contenedor → `transparencia_accordion.parquet` existe, breadcrumb limpio.
2. Fase 1: `python etl/load_parquet.py --verify` → counts esperados; vistas correctas.
3. Fase 2-3: `pytest packages/mcp-transparencia/tests/` verde.
4. Fase 4: agente conectado ejecuta `get_page(url)` y `list_organisms()` con datos reales.
