# MCP Transparencia

Fase 1 del corpus de Publicidad Activa: schema Postgres y ETL desde Parquet.

El ETL lee por defecto el warehouse externo:

```text
C:\Users\marin\Documents\hackathon\data 2\data\warehouse
```

Los Parquet no se copian al repositorio.

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
- `transparencia.links`
- `transparencia.resource_types`
- `transparencia.link_patterns`

`accordion` no es obligatorio en esta fase. Se conserva `accordion_count` en `pages` y el texto indexable sale de `sections.text` y `sections.content`.

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
