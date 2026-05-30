# Plan: Servidor MCP del Corpus de Transparencia

> **Alcance de este documento**: construir la capa SQL, los marts y el servidor MCP que
> exponen el corpus de Publicidad Activa a cualquier agente (Claude Code, OpenCode, Cursor).
> **Prerrequisito**: la base `civio` poblada y verificada según
> [plan-base-datos-transparencia.md](plan-base-datos-transparencia.md).
>
> Origen: división de [frolicking-riding-pascal.md](frolicking-riding-pascal.md).
> Especificación funcional de referencia: [instrucciones-mcp-transparencia.md](instrucciones-mcp-transparencia.md).

## Context

Con el corpus ya cargado en Postgres (DB `civio`), este plan implementa el **servidor MCP en
Python** consumible por cualquier agente, con dos capas: **SQL** (consultas directas) y
**marts** (reglas de negocio / vistas analíticas). El MCP consulta Postgres con `psycopg`; no
vuelve a tocar el scraper ni el ETL.

Recordatorios de modelo de datos (heredados del plan de base de datos):
- "Organismo" en este corpus es en realidad **materia** (categoría temática del path
  `/por-materias/<slug>/`), no la entidad emisora. 89% es `organizacion-empleo`.
- "Subvenciones" = *enlaces a pap.hacienda*, NO montos ni años (no existen en los datos).

## Approach

Construir el paquete `packages/mcp-transparencia/` (hermano de `packages/data/`).
Flujo de este plan: `capa SQL → marts → servidor MCP → integración con agente`.

Reutilizar el patrón de conexión `psycopg` de
`packages/data/tests/smoke/test_connection.py` y las deps ya presentes
(`psycopg[binary]`, `typer`); añadir `mcp>=1.2`.

## Fases (incrementales, cada una con verificación)

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
- A reutilizar: `packages/data/tests/smoke/test_connection.py` (patrón psycopg).
- A crear: `packages/mcp-transparencia/` (server, sql/, marts/, etl/, pyproject.toml,
  .mcp.json.example). El `sql/schema.sql` y `etl/load_parquet.py` los crea el
  [plan de base de datos](plan-base-datos-transparencia.md).

## Riesgos / decisiones abiertas
- **"Organismo" ≠ entidad emisora** y el corpus es 89% una sola materia: framing honesto
  en docstrings. (Confirmar si preferís renombrar la tool a `list_materias()`.)
- Si la base no habilitó `unaccent`/`pg_trgm`, `search_pages` usa solo `tsvector`
  (sin fuzzy/acento-insensible).

## Verification (de este plan)
1. Fase 2-3: `pytest packages/mcp-transparencia/tests/` verde.
2. Fase 4: agente conectado ejecuta `get_page(url)` y `list_organisms()` con datos reales.

> Prerrequisito: base `civio` lista según
> [plan-base-datos-transparencia.md](plan-base-datos-transparencia.md).
