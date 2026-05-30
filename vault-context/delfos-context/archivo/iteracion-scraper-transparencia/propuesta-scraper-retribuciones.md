# Propuesta: Scraper de Retribuciones del Buscador de Transparencia

## Problema

El scraper actual solo captura páginas HTML del sitio `transparencia.gob.es/publicidad-activa/`. Las retribuciones de altos cargos viven en una aplicación Java/J2EE separada — el **Buscador de Publicidad Activa** (`/servicios-buscador/`) — que renderiza tablas con paginación y ordenación. Los datos no están embebidos en el HTML de las páginas del portal, sino que se obtienen mediante peticiones al buscador con parámetros de filtro.

Ejemplo de URL con datos:
```
https://transparencia.gob.es/servicios-buscador/buscar.htm?
  categoria=retribuciones&
  categoriasPadre=altcar&
  lang=es&
  orderBy=retribucion&
  or=DESC
```

---

## Arquitectura actual

```
crawl.py (BFS sobre HTML del portal)
  ↓
parse.py (selectolax → PageData)
  ↓
storage.py (Parquet + JSONL)
  ↓
  ──→ Postgres (ETL externo)
```

El `TransparenciaFetcher` usa `httpx` con `base_url=https://transparencia.gob.es`, cacheo por SHA256 y rate limiting. Eso mismo sirve para el buscador.

---

## Propuesta de implementación

### 1. Nuevo modelo: `RetribucionesRow`

```python
# scrapers/transparencia/models.py

@dataclass
class RetribucionesRow:
    alto_cargo: str
    organismo: str
    ministerio: str
    retribucion: float        # en euros
    anyo: int
    page_url: str             # URL del buscador con los filtros aplicados
    crawled_at: Optional[str] = None
```

### 2. Nuevo parser: `BuscadorParser`

Extrae filas del HTML server-side renderizado del buscador usando selectolax (mismo approach que `TransparenciaParser`).

```python
# scrapers/transparencia/buscador.py

class BuscadorParser:
    """Parsea las tablas HTML del Buscador de Publicidad Activa."""

    def parse_retribuciones(self, html: str) -> list[RetribucionesRow]:
        """Extrae filas de la tabla de retribuciones."""
        tree = HTMLParser(html)
        rows = []
        for tr in tree.css("table#resultados tbody tr"):
            cells = tr.css("td")
            if len(cells) >= 5:
                rows.append(RetribucionesRow(
                    alto_cargo=self._cell_text(cells[0]),
                    organismo=self._cell_text(cells[1]),
                    ministerio=self._cell_text(cells[2]),
                    retribucion=self._parse_salary(cells[3]),
                    anyo=int(self._cell_text(cells[4])),
                ))
        return rows
```

### 3. Scraper con paginación

El buscador devuelve 10 resultados por página. La paginación está en los parámetros de la URL (`pag=1`, `pag=2`, ...). También se puede filtrar por año (`anyo=2025`) para acotar.

```python
# Misma URL base, mismo fetcher

def scrape_retribuciones(
    fetcher: TransparenciaFetcher,
    anyo: Optional[int] = None,
    max_pages: int = 10,
) -> list[RetribucionesRow]:
    parser = BuscadorParser()
    todas: list[RetribucionesRow] = []

    params = {
        "categoria": "retribuciones",
        "categoriasPadre": "altcar",
        "lang": "es",
        "orderBy": "retribucion",
        "or": "DESC",
    }
    if anyo:
        params["anyo"] = str(anyo)

    for pag in range(1, max_pages + 1):
        params["pag"] = str(pag)
        # Construir query string y llamar al fetcher
        path = f"/servicios-buscador/buscar.htm?{urlencode(params)}"
        html = fetcher.fetch(path)
        if not html:
            break
        rows = parser.parse_retribuciones(html)
        if not rows:
            break
        todas.extend(rows)

    return todas
```

### 4. Nueva tabla en Postgres

```sql
CREATE TABLE transparencia.retribuciones (
    id              BIGSERIAL PRIMARY KEY,
    alto_cargo      TEXT NOT NULL,
    organismo       TEXT,
    ministerio      TEXT,
    retribucion     NUMERIC(12,2) NOT NULL,
    anyo            INTEGER NOT NULL,
    page_url        TEXT NOT NULL,
    crawled_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- metadatos
    UNIQUE (alto_cargo, organismo, anyo)
);

COMMENT ON TABLE transparencia.retribuciones IS
    'Retribuciones anuales de altos cargos extraidas del Buscador de Publicidad Activa.';

COMMENT ON COLUMN transparencia.retribuciones.alto_cargo IS
    'Nombre y cargo de la persona (ej. "Presidenta SEPI", "PRESIDENTE DEL GOBIERNO").';

COMMENT ON COLUMN transparencia.retribuciones.organismo IS
    'Organismo pagador (ej. "Sociedad Estatal de Participaciones Industriales").';

COMMENT ON COLUMN transparencia.retribuciones.ministerio IS
    'Ministerio de adscripcion del organismo.';

COMMENT ON COLUMN transparencia.retribuciones.retribucion IS
    'Retribucion integra anual en euros.';
```

### 5. Comando CLI nuevo

```python
# En cli.py

@app.command()
def retribuciones(
    anyo: Optional[int] = typer.Option(None, "--anyo", help="Filtrar por año"),
    export: bool = typer.Option(False, "--export", help="Exportar a Parquet"),
):
    """Scrapea retribuciones de altos cargos desde el Buscador."""
    fetcher = TransparenciaFetcher(rate_limit=1.0)
    rows = scrape_retribuciones(fetcher, anyo=anyo)
    logger.info("scraped %d retribuciones rows", len(rows))
    if export:
        df = pl.DataFrame([asdict(r) for r in rows])
        df.write_parquet(WAREHOUSE_DIR / "retribuciones.parquet")
    # flush a postgres via ETL
```

### 6. Pipeline ETL

El ETL existente (scripts/load_postgres.py o similar) se extiende para insertar desde el Parquet de retribuciones:

```python
# Ejemplo conceptual
df = pl.read_parquet("/data/warehouse/retribuciones.parquet")
with psycopg.connect(DSN) as conn:
    with conn.cursor() as cur:
        for row in df.iter_rows(named=True):
            cur.execute("""
                INSERT INTO transparencia.retribuciones
                    (alto_cargo, organismo, ministerio, retribucion, anyo, page_url)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (alto_cargo, organismo, anyo)
                DO UPDATE SET retribucion = EXCLUDED.retribucion
            """, (row["alto_cargo"], row["organismo"], row["ministerio"],
                  row["retribucion"], row["anyo"], row["page_url"]))
```

---

## Cobertura del buscador

Además de retribuciones, el Buscador de Publicidad Activa expone otras categorías que podrían scrapearse con el mismo patrón:

| Categoría | Parámetro | Filas |
|---|---|---|
| Retribuciones | `categoria=retribuciones` | 9.237 |
| Indemnizaciones | `categoria=indemnizaciones` | (no estimado) |
| Declaraciones de bienes | `categoria=bienesinmuebles` | (no estimado) |
| RPT | `categoria=rpt` | (no estimado) |
| Currículums | `categoria=curriculums` | (no estimado) |

Todas comparten la misma estructura de tabla con filtros por año, ministerio, organismo.

---

## Alternativa considerada: XLS export

El buscador ofrece un enlace "Descargar" que llama a:
```
/servicios-buscador/buscar/expTab.htm?categoria=retribuciones&...&nResultados=9237
```

Devuelve un `.xls`. Limitación: máximo 2.000 registros por exportación. Ventaja: no requiere parsear HTML. Pero requiere filtros para bajar por debajo del límite (ej. `anyo=2025` da ~200-400 filas).

**Recomendación**: usar la descarga XLS por año como plan A. Si falla, fallback al parseo del HTML.

---

## Resumen de cambios necesarios

| Archivo | Acción |
|---|---|
| `scrapers/transparencia/models.py` | Agregar `RetribucionesRow` |
| `scrapers/transparencia/buscador.py` | **Nuevo**: `BuscadorParser` con `parse_retribuciones()` |
| `scrapers/transparencia/fetch.py` | Sin cambios (el `TransparenciaFetcher` ya sirve) |
| `scrapers/transparencia/buscador_scraper.py` | **Nuevo**: lógica de paginación + filtros |
| `scrapers/transparencia/cli.py` | Agregar comando `retribuciones` |
| `scrapers/transparencia/storage.py` | Opcional: método `save_retribuciones_parquet()` |
| `scripts/` | ETL para volcar a `transparencia.retribuciones` |
| Postgres | Migración: `CREATE TABLE transparencia.retribuciones` |
