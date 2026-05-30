# MCP Transparencia

Corpus de Publicidad Activa: schema Postgres, ETL desde Parquet y servidor MCP
read-only para consultar la base desde agentes.

## Servidor MCP

El servidor vive en `mcp_server.py` y se registra para OpenCode en el
`opencode.json` del proyecto con el nombre `transparencia`.

Tools disponibles:

- `execute_sql(query, limit=100)`: ejecuta una unica consulta `SELECT`, `WITH` o
  `EXPLAIN` en una transaccion read-only.
- `get_page(url)`: devuelve pagina, secciones, acordeones y enlaces
  clasificados.
- `search_pages(query, limit=20)`: busqueda full-text en castellano.
- `list_organisms()`: resumen por materia; el nombre se conserva por
  compatibilidad, no son organismos emisores.
- `get_external_links(domain, limit=100)`: enlaces salientes filtrados por host.
- `get_links_by_category(category, materia_slug=None, limit=100)`: enlaces por
  categoria curada.

Ejecucion directa para smoke test:

```bash
uv run --project packages/mcp-transparencia python mcp_server.py
```

OpenCode carga MCP al arrancar. Despues de modificar `opencode.json` o
`mcp_server.py`, reiniciar OpenCode para que el servidor aparezca en la sesion.

El ETL lee por defecto el warehouse del repositorio:

```text
data/warehouse
```

## Carga

```bash
python packages/mcp-transparencia/etl/load_parquet.py --verify
```

Variables de conexion:

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=civio
POSTGRES_USER=civio
POSTGRES_PASSWORD=...
```

El schema se crea en `transparencia` y carga:

- `transparencia.pages`
- `transparencia.sections`
- `transparencia.accordion`
- `transparencia.links`
- `transparencia.resource_types`
- `transparencia.link_patterns`

El dump versionado `data/warehouse/transparencia-transparencia-schema.dump`
incluye `transparencia.accordion` con los acordeones extraidos desde cache HTML.

## Validacion

Con Postgres levantado y datos cargados:

```bash
docker compose exec -T postgres psql -U civio -d civio -f /workspace/packages/mcp-transparencia/sql/validate.sql
```

Si se ejecuta desde Windows sin montar el repo dentro del contenedor `postgres`, usar redireccion desde el host:

```powershell
Get-Content -Raw "packages/mcp-transparencia/sql/validate.sql" | docker compose exec -T postgres psql -U civio -d civio
```

Las validaciones comprueban conteos, nulos criticos, integridad referencial, orden por pagina, materias, clasificacion de enlaces, busqueda textual, consistencia de vistas y muestras por categoria.
