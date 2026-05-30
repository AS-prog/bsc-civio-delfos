---
title: Delfos — Transparencia pública, consultable
eyebrow: CIVIO · SHIP FOR GOOD 2026
---

# Transparencia pública, consultable

Equipo :chip[Delfos] · Reto :chip[Civio] · 42 Barcelona :chip[29–30 may 2026] · Licencia :pill[MIT]{.slate}

:::tldr
El Portal de Transparencia estatal es un laberinto de enlaces: opaco para el periodista y para el ciudadano. Delfos lo convierte en un **corpus estructurado y consultable por agentes de IA** — del HTML público a una base de datos honesta, vía scraper → Postgres → servidor MCP. Cero generación de texto: solo extracción, limpieza y consulta. Cae limpio dentro de la política de IA de Civio.
:::

:::summary-band
:::stat-card num="1.167" label="PÁGINAS DEL CORPUS"
:::
:::stat-card num="13.267" label="ENLACES EXTERNOS"
:::
:::stat-card num="6" label="TOOLS MCP" delta="read-only"
:::
:::stat-card ok num="1" label="BASE CONSULTABLE" delta="Postgres · civio"
:::
:::

## Por qué — el problema

Civio es una fundación independiente que combate la opacidad institucional con **periodismo de datos, ingeniería y litigio**. La Ley 19/2013 obliga a la administración a publicar contratos, subvenciones, retribuciones y organigramas. El problema no es que falten: es que **están, pero inaccesibles**.

:::card accent head="LA CRÍTICA CENTRAL"
El Portal de Transparencia es un **agregador de enlaces**: "de cada 5 links, 4 te mandan a otra página". No se puede saber qué información existe antes de buscarla, y el vocabulario técnico deja fuera al ciudadano común. El **doble combo** que pide Civio: que la solución sirva a la vez a sus periodistas y a quien ni sabe que el portal existe.
:::

### La restricción innegociable: la política de IA de Civio

Condiciona todo. Es pública y no negociable. Cualquier solución tiene que caer del lado permitido.

:::split-2
:::card title="❌ Vetado"
- Generar texto periodístico
- Redactar alegaciones o recursos
- IA como **fuente** de información
- Crear imágenes o ilustraciones
:::
:::card title="✅ Permitido"
- Conversión y limpieza de datos
- Transcripción en local
- Asistencia a programación
- Consultas sobre bases de datos propias
:::
:::

:::callout info title="Nuestra decisión"
Atacamos el lado de datos de **OPP-1a**: hacer explotable el corpus de Publicidad Activa. Es público, scrapeable y de solo lectura — extracción + limpieza + consulta, **cero generación**. Y deja un activo reutilizable sobre el que Civio puede construir.
:::

## Qué construimos

Un pipeline de datos que va del HTML público a una base consultable por agentes: **scraper → base de datos → servidor MCP.**

@@FIG:pipeline@@

:::grid
:::card head="CAPA 1" title="Scraper"
Recorre por BFS la Publicidad Activa **sin navegador headless** (HTTP + parser CSS). Respetuoso: 1 req/s, cache local para reprocesar sin volver a la red. Exporta a Parquet + JSONL.
:::
:::card head="CAPA 2" title="Base de datos"
Schema Postgres en el esquema `transparencia`, tipos estrictos, búsqueda full-text en castellano y vistas que clasifican enlaces. ETL idempotente (`TRUNCATE` + `COPY`).
:::
:::card head="CAPA 3" title="Servidor MCP"
Superficie **curada y read-only** consumible por cualquier agente (Claude Code, OpenCode). Docstrings que encuadran el dato y evitan que el agente alucine.
:::
:::

### Las 6 tools del MCP

| Tool | Devuelve |
|------|----------|
| `execute_sql(query, limit)` | SQL read-only (`SELECT`/`WITH`/`EXPLAIN`) en transacción restringida |
| `get_page(url)` | Página completa: metadata, breadcrumb, secciones, acordeones, enlaces |
| `search_pages(query, limit)` | Búsqueda full-text en castellano por relevancia |
| `list_organisms()` | Resumen por materia |
| `get_external_links(domain, limit)` | Enlaces salientes filtrados por host |
| `get_links_by_category(category, materia_slug, limit)` | Enlaces por categoría curada |

### El valor diferencial: honestidad del dato

:::callout warning title="Dos verdades que el MCP hace explícitas"
**"Organismo" ≠ entidad emisora.** En este corpus es la *materia* (categoría temática del path). El **89% es `organizacion-empleo`** — hay un sesgo de cobertura fuerte, y el MCP no lo esconde.

**"Subvención" ≠ monto.** Aquí es un *enlace* a `pap.hacienda`. No hay importes ni años en los datos; el MCP no los inventa.
:::

**Sesgo de cobertura del corpus** — `organizacion-empleo` domina:

`organizacion-empleo` · 1.043 de 1.167 páginas
:::progress value="89"
:::

El resto de materias apenas tocadas (económico-presupuestaria 40, altos cargos 26, trámites 25, normativa 19, planificación 11).

### A dónde apuntan los 13.267 enlaces

El activo con mayor valor periodístico es el **grafo de enlaces**: órgano público → subvenciones (`pap.hacienda`) y normativa (`boe.es`). Está completo y limpio, explotable **hoy**.

@@FIG:enlaces@@

## Cómo está hecho

Monorepo con dos paquetes Python hermanos sobre Docker (Postgres + contenedor `data`).

:::grid
:::card title="Scraper — packages/data"
Pipeline `discover (BFS) → fetch (cache) → parse → store`. `httpx` + `selectolax`, retry con `tenacity`, persistencia dual JSONL + Parquet (Polars).
:::
:::card title="BD + ETL — packages/mcp-transparencia"
`schema.sql` (esquema `transparencia`, `tsvector` español, vistas de clasificación) + `load_parquet.py` (psycopg, `COPY` idempotente). Re-parse desde cache HTML, cero red.
:::
:::card title="Servidor MCP"
`mcp_server.py` con FastMCP, transporte stdio. Dos capas: SQL parametrizado + marts (reglas de negocio).
:::
:::

### Decisiones técnicas y su porqué

| Decisión | Por qué |
|----------|---------|
| Sin navegador headless | El portal sirve navegación y contenido en HTML estático; Playwright sería sobreingeniería |
| Rate limit 1 req/s | `robots.txt` sin Crawl-delay; cortesía con un servidor público |
| Cache local SHA256 | Permite reprocesar el parser sin volver a la red |
| Output dual JSONL + Parquet | JSONL para depurar; Parquet para análisis con Polars/DuckDB |
| MCP curado vs SQL genérico | Híbrido: `postgres-mcp` para exploración/QA, MCP propio como superficie honesta en producción |

**Stack:** :tag[Python 3.12] :tag[httpx] :tag[selectolax] :tag[tenacity] :tag[typer] :tag[polars] :tag[duckdb] :tag[psycopg] :tag[mcp / FastMCP] :tag[Postgres] :tag[Docker] :tag[uv]

## Estado y próximo paso

:::split-2
:::card title="Hecho"
Scraper + corpus completo · schema + ETL a Postgres · MCP con 6 tools read-only · registrado en `opencode.json` y `.mcp.json`.
:::
:::card accent title="Oportunidad inmediata"
Construir el **grafo de enlaces** subvenciones + normativa. Máximo valor periodístico, cero deuda previa: el ángulo anti-opacidad de Civio servido en bandeja.
:::
:::
