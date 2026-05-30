# 02 · Cómo — arquitectura y decisiones técnicas

> Cómo está hecho y por qué se decidió así. El qué y el alcance están en
> [01-que.md](01-que.md). Detalle exhaustivo (diagramas, métricas de corrida, backlog) en
> [archivo/iteracion-scraper-transparencia/](archivo/iteracion-scraper-transparencia/).

## Visión de conjunto

Monorepo con dos paquetes Python hermanos, sobre un entorno Docker (Postgres + contenedor
`data`):

```
packages/
├── data/                       # scraper + warehouse Parquet
│   └── scrapers/transparencia/ # fetch / parse / crawl / storage / models / cli
└── mcp-transparencia/          # schema SQL + ETL + servidor MCP
    ├── sql/{schema.sql, validate.sql}
    ├── etl/load_parquet.py
    └── mcp_server.py
```

## Capa 1 — Scraper

Pipeline `discover (BFS) → fetch (cache) → parse → store`. Componentes:

| Módulo | Responsabilidad |
|--------|-----------------|
| `fetch.py` | Cliente HTTP `httpx`, 1 req/s, retry con `tenacity`, cache `SHA256[:16].html` + `.json` |
| `parse.py` | Parseo con `selectolax` (selectores CSS) — título, breadcrumb, secciones, acordeones, enlaces |
| `crawl.py` | BFS desde semillas; descubre URLs internas que el sitemap no lista |
| `storage.py` | Persistencia dual: JSONL (raw, append) + Parquet (analítico, Polars) |
| `cli.py` | `discover` / `crawl` / `export` (Typer) |

### Decisiones clave y su porqué

| Decisión | Por qué |
|----------|---------|
| **Sin navegador headless** (`httpx` + `selectolax`) | El portal entrega navegación y contenido en HTML estático; JS solo controla UI. Playwright sería sobreingeniería. |
| **Rate limit 1 req/s** | `robots.txt` no define Crawl-delay. Cortesía mínima con un servidor público. |
| **Cache local SHA256** | Permite reprocesar (reparse) sin volver a la red — clave para iterar el parser. |
| **Output dual JSONL + Parquet** | JSONL para depurar y append; Parquet para análisis con Polars/DuckDB. |
| **BFS sobre sitemap** | El sitemap es semilla; el crawl descubre URLs no listadas y evita stale links. |

## Capa 2 — Base de datos

Decisión de modelado documentada: **arreglar el dato en origen** (parser + storage), no solo
normalizar aguas abajo. El ETL re-exporta desde la cache HTML (`reparse_cache.py`, cero red) y
carga a Postgres.

- **Schema** (`sql/schema.sql`): esquema `transparencia`, tipos estrictos, `COMMENT ON` por
  tabla/columna, `search_tsv tsvector` poblado con `to_tsvector('spanish', ...)`, vistas que
  clasifican enlaces (subvenciones=`pap.hacienda` / normativa=`boe.es` / documento=`dam` / otro).
- **ETL** (`etl/load_parquet.py`): patrón `psycopg` reutilizado del smoke test de `data`;
  `TRUNCATE ... RESTART IDENTITY CASCADE` + `COPY FROM STDIN` en una transacción → idempotente.
  Flag `--verify` imprime counts. Validación independiente en `sql/validate.sql`.
- **Riesgo conocido**: si el usuario `civio` no puede `CREATE EXTENSION` (`unaccent`/`pg_trgm`),
  la búsqueda cae a solo `tsvector` (sin fuzzy ni insensibilidad a acentos).

## Capa 3 — Servidor MCP

- SDK oficial **`mcp` (FastMCP)**, transporte **stdio**. Conexión a Postgres por `psycopg`,
  configurable por env (`POSTGRES_HOST/PORT/DB/USER/PASSWORD`).
- Arquitectura en dos capas conceptuales: **SQL** (consultas parametrizadas, nunca f-string) y
  **marts** (reglas de negocio / clasificaciones). Las tools combinan ambas.
- **Build vs. buy resuelto como híbrido**: se evaluó `postgres-mcp` (MCP genérico de Postgres,
  read-only restringido). Decisión: usarlo como herramienta de **exploración/QA** durante el
  desarrollo, y mantener `mcp-transparencia` como **superficie curada de cara al agente** en
  producción. No se re-implementa tuning de índices: para eso, `postgres-mcp` directo.

## Limitaciones técnicas vivas (heredadas del diagnóstico)

| Tema | Estado |
|------|--------|
| **Sesgo de cobertura** | 89% del corpus es `organizacion-empleo`; el resto de materias apenas tocadas. |
| **Texto de secciones** | El extractor de secciones se reescribió para el markup AEM real, pero la frescura/cobertura textual sigue siendo el flanco débil para NLP. |
| **`updated_at` escaso** | Solo ~5% de páginas exponen fecha en HTML; la real está en `Last-Modified` (HTTP). |
| **P1 — JSONL append** | El storage abría JSONL en modo append (duplicación entre corridas). El ETL hace `TRUNCATE+load`, así que la **base no hereda duplicados**, pero el flanco existe en el scraper. |

## Stack

Python 3.12/3.13 · `httpx` · `selectolax` · `tenacity` · `typer` · `polars` · `duckdb` ·
`psycopg[binary]` · `mcp` (FastMCP) · Postgres · Docker Compose · `uv` (gestión de deps).
