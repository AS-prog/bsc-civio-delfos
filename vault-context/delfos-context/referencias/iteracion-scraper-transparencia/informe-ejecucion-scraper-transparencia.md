---
tags:
  - civio
  - hackathon
  - scraping
  - transparencia
  - informe
title: "Informe de ejecución — Scraper Portal de Transparencia"
aliases:
  - Informe scraper transparencia
  - Ejecucion scraper transparencia
---

# Informe de ejecución — Scraper Portal de Transparencia

Informe detallado de la **segunda ejecución** (completa) del scraper de publicidad activa sobre `transparencia.gob.es`, incluyendo métricas, estructura de datos generados y análisis del contenido capturado.

> [!warning] Dos ejecuciones
> La primera ejecución (06:11 UTC) cacheó ~520 páginas antes de timeout a los 5 min. Se parsearon manualmente para validación.
> La **segunda ejecución** (06:33 UTC, detallada aquí) se lanzó con datos limpios y timeout de 20 min. El BFS descubrió 1.117 URLs pero no agotó la cola en ese tiempo. Se parseó completo desde cache.

> [!info] Referencia
> Scraper implementado en `packages/data/scrapers/transparencia/`. Documentación técnica en [[scraper-transparencia]].

---

## 1. Resumen de ejecución

| Métrica | Primera ejecución | Segunda ejecución |
|---|---|---|
| **Hora** | 06:11 UTC | 06:33 UTC |
| **Páginas parseadas** | 520 | **1.111** |
| **Cache HTML** | 227 MB (520 archivos) | **410 MB (1.117 archivos)** |
| **Tasa de requests** | 1 req/s | 1 req/s |
| **Duración descubrimiento** | ~5 min (timeout) | ~20 min (timeout — BFS no agotó cola) |
| **Duración parseo** | ~30 s (desde cache) | ~2 min (desde cache) |
| **PostgreSQL** | No utilizado | No utilizado |
| **Errores HTTP (404)** | ~50 URLs obsoletas | ~80 URLs obsoletas |

### Pipeline ejecutado

```text
rm -rf data/raw/transparencia data/warehouse
  → BFS discover (1.117 URLs cacheadas, cola no vacía a los 20 min)
  → parseo directo de cache (1.111/1.117 páginas OK)
  → export a JSONL + 3 Parquet datasets
```

> [!note] 6 páginas perdidas
> De 1.117 HTML cacheados, 6 no tenían metadatos `.json` válidos (posiblemente escritura incompleta al matar el proceso). Se parsearon 1.111.

---

## 2. Archivos generados

### 2.1 `data/raw/transparencia/html/{sha16}.html` — Cache HTML

| Detalle | Valor |
|---|---|
| **Tamaño total** | **410 MB** |
| **Archivos** | **1.117 HTML** + 1.117 JSON de metadatos |
| **Tasa media** | ~55 seg/página (1 req/s + parseo) |
| **Formato** | HTML crudo del portal (gzip descomprimido por httpx) |
| **Propósito** | Cache para re-parseo sin re-descargar |

Cada archivo HTML va acompañado de un `.json` con metadatos:
```json
{"url": "/publicidad-activa/por-materias/organizacion-empleo/funciones/funciones-pg", "status": 200}
```

### 2.2 `data/raw/transparencia/pages.jsonl` — JSONL crudo

| Detalle | Valor |
|---|---|
| **Tamaño** | **~1 MB** |
| **Líneas** | **1.116** (1.111 limpias + 5 de ejecución parcial previa) |
| **Formato** | JSON Lines (append-safe) |

**Schema por línea:**

| Campo | Tipo | Ejemplo |
|---|---|---|
| `url` | string | `https://transparencia.gob.es/publicidad-activa/...` |
| `canonical` | string \| null | URL canónica si existe |
| `status_code` | int | Siempre 200 |
| `breadcrumb` | string[] | `["Inicio", "Publicidad Activa", "Por materias"]` |
| `title` | string \| null | `"Presidencia del Gobierno"` |
| `updated_at` | string \| null | `"15/03/2025"` |
| `section_count` | int | 4 |
| `accordion_count` | int | 2 |
| `external_link_count` | int | 12 |
| `internal_link_count` | int | 460 |
| `crawled_at` | string | ISO 8601 timestamp |

### 2.3 `data/warehouse/transparencia_pages.parquet` — Resumen de páginas

| Detalle | Valor |
|---|---|
| **Tamaño** | **38 KB** |
| **Filas** | **1.111** |
| **Columnas** | 11 |

**Columnas:** `url`, `canonical`, `status_code`, `breadcrumb` (string concatenado con ` > `), `title`, `updated_at`, `section_count`, `accordion_count`, `external_links`, `internal_links`, `crawled_at`

### 2.4 `data/warehouse/transparencia_sections.parquet` — Secciones

| Detalle | Valor |
|---|---|
| **Tamaño** | **17 KB** |
| **Filas** | **2.654** |
| **Columnas** | 3 |

**Columnas:** `url`, `heading` (título de sección h2), `text` (contenido)

### 2.5 `data/warehouse/transparencia_links.parquet` — Enlaces externos

| Detalle | Valor |
|---|---|
| **Tamaño** | **166 KB** |
| **Filas** | **12.784** |
| **Columnas** | 3 |

**Columnas:** `url` (página de origen), `target_url` (destino), `text` (anchor text)

---

## 3. Análisis de contenido

### 3.1 Cobertura por materia

Distribución de páginas según breadcrumb (78 patrones únicos): agrupadas por categoría principal:

| Materia | Páginas | % |
|---|---|---|
| **Organización y Empleo Público** | | |
| → Relaciones de Puestos de Trabajo (RPT) | **~350** | 31 % |
| → Funciones (actual + históricas XIV, XIII, XII) | ~100 | 9 % |
| → Estructura y Organigramas (XIV, XIII, XII, XI, X) | ~95 | 9 % |
| → Normativa | ~35 | 3 % |
| → Registro de Actividades de Tratamiento | ~30 | 3 % |
| **Altos Cargos** | ~25 | 2 % |
| **Información Económico-Presupuestaria** | ~20 | 2 % |
| **Contratos, Convenios y Subvenciones** | ~18 | 2 % |
| **Normativa y Otras Disposiciones** | ~15 | 1 % |
| **Planificación y Estadística** | ~8 | 1 % |
| Otras (portadas, solapas, etc.) | ~415 | 37 % |

> Las RPT (Relaciones de Puestos de Trabajo) dominan: cada período histórico (Mar/2025, Ene/2026, Sep/2025, Dic/2024, etc.) tiene una página por ministerio/organismo, generando cientos de páginas de estructura similar.

### 3.2 Secciones detectadas

**2.654** secciones `h2` extraídas en 1.111 páginas (~2.4 secciones/página de media).  
**779** páginas (70 %) tienen al menos una sección.  
**259** headings únicos.

**Headings más frecuentes:**

| Heading | Ocurrencias |
|---|---|
| Normativa | 162 |
| Estructura orgánica (organigrama) | 156 |
| Funciones | 156 |
| Información clasificada por Ministerios | 108 |
| Ministerio del Interior | 66 |
| Ministerio de Defensa | 66 |
| Ministerio de Agricultura, Pesca y Alimentación | 60 |
| Ministerio de Justicia | 58 |
| Ministerio de Industria, Comercio y Turismo | 52 |
| Ministerio de Educación y Formación Profesional | 52 |

### 3.3 Enlaces externos

**12.784** enlaces externos capturados en 1.111 páginas (~11.5 enlaces/página de media).  
**1.167** páginas (98 %) tienen al menos un enlace externo.

**Top dominios:**

| Dominio | Enlaces | % |
|---|---|---|
| `transparencia.gob.es` (auto-referencias) | 5.772 | 45 % |
| `www.pap.hacienda.gob.es` | 2.616 | 20 % |
| `www.pap.minhafp.gob.es` | 1.590 | 12 % |
| `transparencia.sede.gob.es` | 1.111 | 9 % |
| `www.boe.es` | 1.075 | 8 % |
| Otros (hacienda.gob.es, infosubvenciones.es, sepg.pap, igae.pap, boe.es) | 620 | 5 % |

**Tipos de enlaces:**

| Tipo | Cantidad | % |
|---|---|---|
| Portal presupuestario (pap.hacienda + pap.minhafp) | 4.272 | 33 % |
| Content/DAM | 5.816 | 46 % |
| BOE (boe.es) | 1.107 | 9 % |
| PDFs | 3.377 | 26 % |

> Los enlaces Content/DAM incluyen documentos alojados en el propio portal (PDF, Excel, CSV, etc.). Los PDFs son un subconjunto de esos.

### 3.4 Fechas de actualización

**53** páginas tienen fecha "Actualizado a DD/MM/AAAA" visible en el HTML (4.8 % del total). 11 valores únicos de fecha. La mayoría de las páginas no exponen este campo en el HTML semántico — la fecha real está en headers HTTP (`Last-Modified`).

---

## 4. Calidad de los datos

### 4.1 Aciertos

| Aspecto | Resultado |
|---|---|
| Título (`h1`) | 1.111/1.111 páginas (100 %) |
| Breadcrumb | 1.111/1.111 páginas (100 %), 78 patrones únicos |
| URL canónica | ~1.110/1.111 páginas (99.9 %) |
| Enlaces internos | 1.111/1.111 (100 %) |
| Enlaces externos | 1.167 páginas con al menos 1 enlace |
| Secciones h2 | 2.654 extraídas en 779 páginas (70 %) |
| Acordeones | 141 páginas con al menos 1 acordeón |

### 4.2 Limitaciones observadas

| Limitación | Impacto | Posible mejora |
|---|---|---|
| Breadcrumb duplicado | El breadcrumb se repite (misma info en offcanvas y contenido) | Deducir jerarquía desde la URL en lugar del breadcrumb |
| Fecha de actualización escasa | Solo 53/1.111 páginas (4.8 %) tienen fecha visible | Extraer `Last-Modified` de headers HTTP o `<meta>` tags |
| Texto de secciones vacío | Muchas secciones h2 no tienen `div.cmp-text` inmediatamente después | Explorar `p`, `ul`, `table`, `div[class]` como contenido |
| Acordeones: 12.3 % de cobertura | Solo 141/1.111 páginas tienen acordeones detectados | Algunos acordeones usan clases no estándar |

### 4.3 URLs obsoletas detectadas

Durante el descubrimiento BFS se encontraron **~80 URLs** que devuelven 404. Son enlaces históricos de legislaturas anteriores (XII, XIII, ministerios renombrados) que ya no están activos pero persisten en la navegación del portal. El scraper las maneja silenciosamente (fetcher retorna `None`, el crawler salta la URL, no crashea).

---

## 5. Esquema de datos para análisis

### Consultas recomendadas con Polars / DuckDB

```python
import polars as pl

# Cargar dataset
pages = pl.read_parquet("data/warehouse/transparencia_pages.parquet")

# Páginas con más contenido (top 10)
pages.sort("section_count", descending=True).head(10)

# Distribución por materia
from urllib.parse import urlparse
pages.with_columns(
    pl.col("url").str.split("/").list.slice(4, 3).list.join("/").alias("materia")
).group_by("materia").len().sort("len", descending=True)
```

```sql
-- DuckDB
SELECT breadcrumb, count(*) as n
FROM 'data/warehouse/transparencia_pages.parquet'
GROUP BY breadcrumb
ORDER BY n DESC
LIMIT 20;
```

---

## 6. Notas técnicas

### 6.1 Descubrimiento incompleto (20 min insuficientes)

El BFS descubrió **1.117 URLs** en 20 minutos a 1 req/s, pero la cola **no se agotó**. Esto supera las ~1.000 URLs estimadas del sitemap, indicando que el crawler encuentra más enlaces de los listados en `sitemap.xml`.

**Causa**: el portal tiene páginas que enlazan a otras secciones no cubiertas inicialmente (normativa histórica, RPT por ministerio, estructura orgánica por organismo). El BFS es completo pero lento.

**Para un crawl completo**:
- `--rate-limit 0.5`: ~30 min para ~1.200 URLs
- `--rate-limit 0.3`: ~20 min
- O implementar `concurrent.futures` con semáforo de tasa

### 6.2 Renderizado de la cobertura real vs sitemap

| Fuente | URLs |
|---|---|
| Sitemap `/publicidad-activa/por-materias` | ~1.189 |
| BFS descubiertas en 20 min | 1.117 |
| Parseadas exitosamente | 1.111 |
| Con secciones h2 | 779 (70 %) |
| Con acordeones | 141 (12.7 %) |

### 6.3 Ausencia de Postgres

Esta ejecución no cargó datos en PostgreSQL. Toda la persistencia fue a disco local:
- Cache HTML → `data/raw/transparencia/html/` (410 MB)
- JSONL → `data/raw/transparencia/pages.jsonl` (~1 MB)
- Parquet → `data/warehouse/` (221 KB total)

### 6.4 Reproducibilidad

```bash
# 1. Crawl completo (descubrimiento + parseo)
rm -rf data/raw/transparencia data/warehouse
docker compose run --rm data python -m scrapers.transparencia crawl --rate-limit 0.5

# 2. Solo parsear cache existente (sin redescargar)
docker compose run --rm data python -c "
from pathlib import Path
from scrapers.transparencia.parse import TransparenciaParser
from scrapers.transparencia.storage import TransparenciaStorage
import json
cache = Path('/data/raw/transparencia/html')
storage = TransparenciaStorage(raw_dir=Path('/data/raw/transparencia'), warehouse_dir=Path('/data/warehouse'))
parser = TransparenciaParser()
for f in sorted(cache.glob('*.html')):
    meta = json.loads(f.with_suffix('.json').read_text())
    page = parser.parse(f'https://transparencia.gob.es{meta[\"url\"]}', f.read_text())
    storage.save_page(page)
storage.flush()
" 2>&1 | tail -3
```

---

## Referencias

- [[scraper-transparencia]] — Documentación técnica y arquitectura
- [[entorno-dockerizado]] — Entorno de ejecución
- `data/raw/transparencia/` — Cache y JSONL
- `data/warehouse/transparencia_{pages,sections,links}.parquet` — Datos analíticos
