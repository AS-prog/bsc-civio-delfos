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

## Build vs. buy: `postgres-mcp` (Postgres MCP Pro)

Existe un MCP **genérico** para Postgres ya hecho —
[`postgres-mcp`](https://pypi.org/project/postgres-mcp/) (Postgres MCP Pro, de Crystal DBA,
licencia abierta)— que conviene evaluar antes de escribir tooling propio. Expone **9 tools**
genéricas sobre cualquier base Postgres:

| Tool | Para qué |
|---|---|
| `list_schemas` | enumera esquemas |
| `list_objects` | tablas, vistas, secuencias, extensiones de un esquema |
| `get_object_details` | columnas, constraints, índices de un objeto |
| `execute_sql` | ejecuta SQL (read-only en modo restringido) |
| `explain_query` | planes de ejecución, con índices hipotéticos vía `hypopg` |
| `get_top_queries` | consultas más lentas vía `pg_stat_statements` |
| `analyze_workload_indexes` | recomienda índices a partir del workload |
| `analyze_query_indexes` | recomienda índices para hasta 10 consultas dadas |
| `analyze_db_health` | chequeos de salud (índices, cache, vacuum, conexiones, replicación) |

Características relevantes para nosotros:
- **Modo de acceso** `--access-mode=restricted`: transacciones **read-only** parseando el SQL
  con `pglast` (rechaza `COMMIT`/`ROLLBACK` para que no se eluda). Encaja con que nuestro
  corpus es de **solo lectura**.
- **Transportes**: `stdio` (default) y `sse`/HTTP (`--transport=sse`, p.ej. `:8000`).
- **Instalación**: `pipx install postgres-mcp`, `uvx postgres-mcp`, o `docker pull
  crystaldba/postgres-mcp`. Conexión por `DATABASE_URI` (URI estándar de Postgres).
- **Extensiones**: para tuning/health pide `pg_stat_statements` y `hypopg` (superuser).
- **Probado** en Postgres 15–17; clientes Claude Desktop, Cursor, Windsurf, Goose.

**Decisión recomendada — híbrido, NO reemplazo.** `postgres-mcp` y nuestro MCP resuelven cosas
distintas y son complementarios:

- `postgres-mcp` da acceso **SQL crudo** sobre el esquema. Es excelente para **exploración
  durante el desarrollo**, validar el ETL, mirar planes y revisar salud de la base — sin
  escribir una línea. Pero expone tablas tal cual: un agente que llame `execute_sql` no sabe
  que `materia_slug` no es un organismo emisor, ni que "subvención" aquí es un enlace.
- Nuestro MCP existe **justo por eso**: tools **semánticas y honestas** (`get_page`,
  `list_organisms`, `get_links_by_category`) cuyos docstrings encuadran el dato y evitan que
  el agente alucine montos/años que el corpus no tiene. Esa curaduría es el valor del corpus,
  y un servidor SQL genérico no la puede dar.

Por tanto: usar `postgres-mcp` en **modo restringido** como herramienta de exploración/QA del
equipo (y opción de SQL ad-hoc para usuarios avanzados), y mantener `mcp-transparencia` como la
**superficie curada de cara al agente** en producción. Adoptar de su diseño dos ideas: (1)
ofrecer un `--access-mode` read-only por defecto, y (2) si más adelante hace falta, su tool
`explain_query`/health como inspiración para diagnósticos. No re-implementar index-tuning:
si se necesita, se usa `postgres-mcp` directo.

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

#### Resources (capa complementaria, opcional)

Las **tools** (arriba) son la superficie primaria — model-driven, soportada por todos los
clientes. Sobre ellas se puede sumar **resources** MCP: documentos *read-only* direccionables
por URI que el usuario/cliente adjunta al contexto (no los "ejecuta" el modelo). Para un corpus
de solo lectura encajan natural; son una **capa de presentación fina sobre `queries.py`** (Fase
2), sin duplicar lógica:

| Resource (URI) | Tipo | Devuelve |
|---|---|---|
| `transparencia://pages` | estático | catálogo `{url, title, materia}` de todas las páginas |
| `transparencia://page/{slug}` | plantilla | página completa renderizada (markdown) |
| `transparencia://materia/{slug}` | plantilla | páginas agrupadas por materia |

```python
@mcp.resource("transparencia://pages")
def pages_catalog() -> str:
    return render_catalog(queries.list_all_pages())          # reusa la capa SQL

@mcp.resource("transparencia://page/{slug}", mime_type="text/markdown")
def page_resource(slug: str) -> str:                          # {slug} de la URI → argumento
    return render_markdown(queries.fetch_page_by_slug(slug))
```

> **Caveat de soporte**: el soporte de resources es **desparejo entre clientes** (es justo la
> razón por la que `postgres-mcp` eligió tools en vez de resources). Tratarlos como **suma**,
> no como reemplazo: nunca mover funcionalidad de una tool a un resource. Diferible a v2 si el
> cliente objetivo (Claude Code) no los aprovecha.

- **Verificación**: `mcp dev mcp_server.py` (MCP Inspector) o `tests/test_tools.py`.

### Fase 4 — Integración con agente
Archivos: `packages/mcp-transparencia/.mcp.json.example`, README.

- Registrar en Claude Code (`.mcp.json`) con `command: python`,
  `args: [packages/mcp-transparencia/mcp_server.py]`, env de Postgres.
- **Criterio de éxito (del doc)**: un agente externo ejecuta `get_page(url)` y recibe el
  PageData completo, y `list_organisms()` devuelve el resumen.
- HTTP en :8000 (puerto ya expuesto): opcional, vía **servicio `mcp` nuevo en compose**
  (no reusar `data` para no romper su smoke test). Diferido a v2.
- **Opcional — registrar también `postgres-mcp` (exploración/QA, read-only).** Junto a
  nuestro server, en el mismo `.mcp.json`:

  ```json
  {
    "mcpServers": {
      "transparencia": {
        "command": "python",
        "args": ["packages/mcp-transparencia/mcp_server.py"],
        "env": { "POSTGRES_HOST": "localhost", "POSTGRES_DB": "civio" }
      },
      "postgres-civio": {
        "command": "uvx",
        "args": ["postgres-mcp", "--access-mode=restricted"],
        "env": { "DATABASE_URI": "postgresql://civio:***@localhost:5432/civio" }
      }
    }
  }
  ```

  `transparencia` = superficie curada de cara al agente; `postgres-civio` = SQL crudo
  read-only para exploración. Para SSE: `... --transport=sse` y el cliente apunta a
  `http://localhost:8000/sse`.

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
- Si se adopta `postgres-mcp` para tuning/health, requiere `pg_stat_statements` + `hypopg`
  (superuser). Para el caso read-only de exploración no hacen falta. Mismo riesgo de
  privilegios `CREATE EXTENSION` que ya marca el [plan de base de datos](plan-base-datos-transparencia.md).

## Verification (de este plan)
1. Fase 2-3: `pytest packages/mcp-transparencia/tests/` verde.
2. Fase 4: agente conectado ejecuta `get_page(url)` y `list_organisms()` con datos reales.

> Prerrequisito: base `civio` lista según
> [plan-base-datos-transparencia.md](plan-base-datos-transparencia.md).
