# 01 · Qué — la solución construida

> Qué hicimos, con qué alcance y en qué estado. La arquitectura y el porqué técnico están en
> [02-como.md](02-como.md).

## En una frase

Un **pipeline de datos del Portal de Transparencia** que va del HTML público a una base de
datos consultable por agentes de IA: **scraper → base de datos Postgres → servidor MCP**.
Convierte un agregador de enlaces opaco en un corpus estructurado y honestamente etiquetado.

## Las tres piezas

```
transparencia.gob.es  ──scraper──▶  Parquet/JSONL  ──ETL──▶  Postgres (civio)  ──MCP──▶  Agente
   (publicidad activa)              (data/warehouse)        (esquema transparencia)    (Claude/OpenCode)
```

### 1. Scraper de Publicidad Activa
`packages/data/scrapers/transparencia/`. Recorre por BFS todos los niveles de Publicidad
Activa, extrae contenido estructurado **sin navegador headless** (HTTP + parser CSS) y exporta
a Parquet + JSONL. Respetuoso: 1 req/s, cache local para reprocesar sin volver a la red.

**Resultado real de la corrida:** corpus de **1167 páginas únicas**, **13.267 enlaces
externos**, 1402 secciones, 320 acordeones. Cache HTML de ~410 MB (no versionado).

### 2. Base de datos + ETL
`packages/mcp-transparencia/sql/` + `etl/load_parquet.py`. Schema Postgres en el esquema
`transparencia` con tipos estrictos, comentarios por tabla/columna, FK lógicas, búsqueda
full-text en castellano (`tsvector`) y vistas que clasifican enlaces. ETL idempotente
(`TRUNCATE` + `COPY`). Tablas: `pages`, `sections`, `accordion`, `links`, `resource_types`,
`link_patterns`. Dump versionado en `data/warehouse/transparencia-transparencia-schema.dump`.

### 3. Servidor MCP curado
`packages/mcp-transparencia/mcp_server.py`. Servidor MCP read-only (FastMCP) consumible por
cualquier agente. Expone **6 tools**:

| Tool | Devuelve |
|------|----------|
| `execute_sql(query, limit=100)` | SQL read-only (`SELECT`/`WITH`/`EXPLAIN`) en transacción restringida |
| `get_page(url)` | Página completa: metadata, breadcrumb, secciones, acordeones, enlaces clasificados |
| `search_pages(query, limit=20)` | Búsqueda full-text en castellano por relevancia |
| `list_organisms()` | Resumen por materia (no son organismos emisores — ver nota abajo) |
| `get_external_links(domain, limit=100)` | Enlaces salientes filtrados por host |
| `get_links_by_category(category, materia_slug=None, limit=100)` | Enlaces por categoría curada |

## El valor diferencial: honestidad del dato

La razón de ser del MCP curado (frente a un MCP genérico de Postgres) es que los docstrings
**encuadran el dato y evitan que el agente alucine**. Dos verdades incómodas del corpus que el
MCP hace explícitas:

- **"Organismo" ≠ entidad emisora.** En este corpus es la **materia** (categoría temática del
  path `/por-materias/<slug>/`). El **89% es `organizacion-empleo`** — hay un sesgo de
  cobertura fuerte.
- **"Subvención" ≠ monto.** Aquí es un **enlace** a `pap.hacienda`. No hay importes ni años en
  los datos; el MCP no los inventa.

> Esa curaduría honesta **es** el producto. Un servidor SQL genérico no la puede dar.

## Alcance: qué entra y qué no

**Entra (hecho):** scraper completo + corpus, schema + ETL a Postgres, MCP con 6 tools
read-only, registrado en `opencode.json` (OpenCode) y `.mcp.json` (Claude Code).

**No entra (diferido):** transporte HTTP/SSE del MCP (hoy stdio), resources MCP (soporte
desparejo entre clientes), reequilibrar el sesgo de cobertura del crawl, corpus textual para
NLP (bloqueado por la calidad de extracción de secciones, ver 02).

## Oportunidad de explotación recomendada

El dataset con mayor valor periodístico y explotable **hoy** es el **grafo de enlaces**:
"órgano público → subvenciones (`pap.hacienda`) / normativa (`boe.es`)". Está completo y
limpio en `links.parquet`, no depende de ningún fix pendiente. Es el ángulo anti-opacidad de
Civio servido en bandeja.
