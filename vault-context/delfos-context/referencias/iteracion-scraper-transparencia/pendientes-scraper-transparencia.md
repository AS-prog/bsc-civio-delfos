# Pendientes — Scraper Portal de Transparencia

> Estado: **diagnóstico**. Documento de backlog. Ningún cambio aplicado todavía.
> Origen: revisión del commit `640377a` (feat: implementar scraper de publicidad activa).
> Fecha: 2026-05-30.

## Resumen

El paquete `packages/data/scrapers/transparencia/` tiene una arquitectura limpia
(fetch / parse / crawl / storage / models) y un fetcher respetuoso. El diagnóstico
identifica 2 problemas que afectan la integridad/eficiencia de los datos y varios
puntos de mejora menores. Este documento prioriza la corrección, no la implementa.

## Prioridad alta

### P1 — El JSONL duplica filas en cada re-ejecución
- **Dónde**: `storage.py:44` — `self._jsonl_path.open("a", ...)`
- **Síntoma**: el archivo `pages.jsonl` se abre en modo append y nunca se trunca.
  Cada corrida de `crawl` agrega de nuevo todas las filas. El parquet sí se
  sobrescribe (`write_parquet`), generando inconsistencia entre ambos artefactos.
- **Impacto**: corrupción silenciosa de datos; a la N-ésima corrida hay N copias.
- **Opciones a evaluar** (no decididas):
  - Truncar el JSONL al iniciar la corrida (modo `"w"` la primera escritura).
  - Deduplicar por `url` / `canonical` antes de persistir.
  - Versionar las salidas por run (carpeta con timestamp).
- **Pendiente**: tests de `storage` que cubran re-ejecución.

### P2 — `--limit` no acota el barrido de red en `discover`
- **Dónde**: `cli.py:93-94` y `crawl.py:40-60`
- **Síntoma**: `discover` hace BFS sin límite de profundidad ni de páginas. El
  `--limit` solo recorta DESPUÉS de descubrir todas las URLs por red.
- **Impacto**: `--limit 10` igual dispara el barrido completo (~1111 URLs, ~20 min).
- **Opciones a evaluar**: pasar `limit`/`max_depth` a `discover`; cortar el BFS
  al alcanzar el tope.

## Prioridad media

### P3 — Seeds inconsistentes entre comandos
- **Dónde**: `crawl.py:12` (`SEEDS`) vs `cli.py:89-92` (seeds hardcodeados).
- **Síntoma**: el comando `discover` usa unas seeds y `crawl` usa otras distintas.
- **Impacto**: dos fuentes de verdad que se van a desincronizar.
- **Pendiente**: unificar en una sola constante/configuración.

### P4 — Cobertura de tests parcial
- **Dónde**: `tests/scrapers/transparencia/` — solo `test_parse.py` (18 tests).
- **Síntoma**: `fetch`, `crawl` y `storage` sin tests, justo donde están P1 y P2.
- **Pendiente**: tests de fetcher (cache/404/retry), crawler (BFS/límites) y
  storage (append/dedup/parquet).

## Prioridad baja

### P5 — Detección de breadcrumb frágil
- **Dónde**: `parse.py:89` — `if t and t != li.text().strip()`.
- **Síntoma**: la comparación para descartar el crumb activo es frágil; `_text`
  y `.text()` casi siempre coinciden. Funciona de casualidad.

### P6 — Paths hardcodeados
- **Dónde**: `cli.py:25-26` — `/data/raw`, `/data/warehouse`.
- **Síntoma**: válidos para Docker, pero no configurables por variable de entorno.

## Orden sugerido de ataque
1. P1 (integridad de datos — bloquea próxima corrida limpia).
2. P2 (eficiencia — habilita iterar rápido con `--limit`).
3. P4 (tests que blinden P1 y P2).
4. P3, P5, P6 (limpieza).
