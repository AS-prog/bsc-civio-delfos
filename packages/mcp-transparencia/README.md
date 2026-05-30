# MCP Transparencia

Fase 1 del corpus de Publicidad Activa: schema Postgres y ETL desde Parquet.

El ETL lee por defecto el warehouse externo:

```text
C:\Users\marin\Documents\hackathon\data 3\data\warehouse
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
- `transparencia.accordion`
- `transparencia.links`
- `transparencia.resource_types`
- `transparencia.link_patterns`

`accordion` se carga desde `transparencia_accordion.parquet` cuando existe. Si falta, el ETL mantiene compatibilidad y carga 0 acordeones. `search_tsv` combina pagina, secciones y acordeones.

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
