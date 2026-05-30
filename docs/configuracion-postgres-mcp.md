# Configuración MCP — PostgreSQL (Civio)

Este documento explica cómo conectar opencode a la base de datos PostgreSQL `civio` usando el protocolo MCP, con **guardrails** de seguridad y documentos de contexto para que las consultas sean precisas.

## Arquitectura

```
opencode
  └── MCP servidor "civio-postgres" (Docker)
        └── @ahmetkca/mcp-server-postgres (read-only)
              └── PostgreSQL 16 (Docker, usuario civio_readonly)
```

### Base de datos: `civio` (Portal de Transparencia)

Contiene el schema `transparencia` con 5 tablas extraídas del Portal de Transparencia (Publicidad Activa):

| Tabla                          | Filas  | Descripción                                                  |
| ------------------------------ | ------ | ------------------------------------------------------------ |
| `transparencia.link_patterns`  | 12     | Reglas editables de clasificación de enlaces por host y path |
| `transparencia.resource_types` | 8      | Tipos de recurso enlazado para UI y marts                    |
| `transparencia.pages`          | 1.167  | Páginas rastreadas del Portal de Transparencia               |
| `transparencia.sections`       | 1.402  | Bloques de contenido textual extraídos de cada página        |
| `transparencia.links`          | 13.267 | Hipervínculos normalizados encontrados en las páginas        |

Tres capas de protección:

1. **Base de datos** — usuario `civio_readonly` con solo `SELECT`
2. **MCP server** — `@ahmetkca/mcp-server-postgres` ejecuta todas las queries en transacciones read-only
3. **SQL parsing** — el servidor rechaza `COMMIT`, `ROLLBACK`, `DROP`, `ALTER`, etc.

## Prerrequisitos

- Docker corriendo
- PostgreSQL 16 levantado (`docker compose up -d postgres`)
- opencode instalado

## Restaurar dump de la base de datos

El dataset del Portal de Transparencia está empaquetado como un dump custom de PostgreSQL (`pg_dump -Fc`) en la raíz del repo.

```bash
# Copiar el dump al contenedor
docker cp transparencia-transparencia-schema.dump bsc-civio-delfos-postgres-1:/tmp/transparencia.dump

# Restaurar (ignorar error si la DB ya existe — los objetos se crean igual)
docker exec bsc-civio-delfos-postgres-1 pg_restore --create -U civio -d postgres /tmp/transparencia.dump 2>&1 | grep -v "already exists"

# Conceder permisos al usuario read-only sobre el nuevo schema
docker exec bsc-civio-delfos-postgres-1 psql -U civio -d civio -c "
GRANT USAGE ON SCHEMA transparencia TO civio_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA transparencia TO civio_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA transparencia GRANT SELECT ON TABLES TO civio_readonly;
"
```

## Configurar el MCP server

Editar `~/.config/opencode/opencode.jsonc`:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "civio-postgres": {
      "type": "local",
      "command": [
        "docker",
        "run",
        "-i",
        "--rm",
        "--network",
        "bsc-civio-delfos_civic-net",
        "node:20-alpine",
        "npx",
        "-y",
        "@ahmetkca/mcp-server-postgres",
        "postgresql://civio_readonly:TU_PASSWORD@postgres:5432/civio",
      ],
      "enabled": true,
    },
  },
}
```

Después de guardar, **reiniciar opencode**.

## Usuario read-only

El usuario `civio_readonly` se crea con permisos mínimos sobre **todos los schemas**:

```sql
CREATE ROLE civio_readonly WITH LOGIN PASSWORD 'TU_PASSWORD' NOSUPERUSER NOCREATEDB NOCREATEROLE;
GRANT CONNECT ON DATABASE civio TO civio_readonly;

-- Schema public
GRANT USAGE ON SCHEMA public TO civio_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO civio_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO civio_readonly;

-- Schema transparencia
GRANT USAGE ON SCHEMA transparencia TO civio_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA transparencia TO civio_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA transparencia GRANT SELECT ON TABLES TO civio_readonly;
```

No puede hacer `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE` ni `TRUNCATE`.

## Verificar que funciona

```bash
# Listar tablas del schema transparencia
docker exec bsc-civio-delfos-postgres-1 psql -U civio -d civio -c "\dt transparencia.*"

# Probar conexión read-only
docker exec bsc-civio-delfos-postgres-1 psql -U civio_readonly -d civio -c "SELECT 1"

# Consulta de prueba contra el schema transparencia
docker exec bsc-civio-delfos-postgres-1 psql -U civio_readonly -d civio -c "
SELECT t.table_name, pg_size_pretty(pg_total_relation_size(quote_ident(t.table_schema) || '.' || quote_ident(t.table_name))) as size
FROM information_schema.tables t
WHERE t.table_schema = 'transparencia'
ORDER BY pg_total_relation_size(quote_ident(t.table_schema) || '.' || quote_ident(t.table_name)) DESC;
"
```

## Documentos de contexto

Para que el agente entienda el esquema de la base de datos, se pueden crear notas en Obsidian con el DDL de cada tabla y referenciarlas.

### Ubicación

```
vault-context/delfos-context/referencias/esquemas/
├── _template.md              ← Plantilla para documentar una tabla
├── link_patterns.md          ← transparencia.link_patterns
├── links.md                  ← transparencia.links
├── pages.md                  ← transparencia.pages
├── resource_types.md         ← transparencia.resource_types
└── sections.md               ← transparencia.sections
```

### Template de esquema

Crear `vault-context/delfos-context/referencias/esquemas/_template.md`:

````markdown
---
tags:
  - esquema
  - db-civio
  - tabla
tabla: '<nombre_tabla>'
schema: 'transparencia'
---

# Esquema: `<nombre_tabla>`

```sql
<COPY DDL AQUÍ>
```
````

### Columnas

| Columna | Tipo    | Nulable | Default      | Descripción        |
| ------- | ------- | ------- | ------------ | ------------------ |
| id      | integer | NO      | nextval(...) | PK autoincremental |
| ...     | ...     | ...     | ...          | ...                |

### Relaciones

- **FK → `<otra_tabla>`** por `columna`

### Uso típico

```sql
SELECT * FROM <tabla> LIMIT 10;
```

````

### Cómo obtener el DDL de una tabla

```bash
docker exec bsc-civio-delfos-postgres-1 pg_dump -U civio -d civio --schema-only -t transparencia.<tabla>
````

### Cargar contexto en opencode

Editar `~/.config/opencode/opencode.jsonc` para incluir los esquemas como instrucciones:

```jsonc
{
  "instructions": [
    "AGENTS.md",
    "vault-context/delfos-context/referencias/esquemas/_template.md",
  ],
}
```

O bien, mencionar la nota relevante durante la conversación:

```
/usar vault-context/delfos-context/referencias/esquemas/<tabla>.md
```

## Conexión desde otros clientes MCP

La conexión vía Docker con `--network bsc-civio-delfos_civic-net` usa el hostname interno `postgres`. Si el cliente no puede ejecutar Docker, se puede exponer el puerto 5432 del host y conectar por `localhost` o `host.docker.internal`.

Claves según topología:

| Escenario                                    | Host en connection string |
| -------------------------------------------- | ------------------------- |
| El MCP corre en Docker (misma red)           | `postgres`                |
| El MCP corre en Docker (macOS, host network) | `host.docker.internal`    |
| El MCP corre nativo en la máquina host       | `localhost`               |

### Claude Desktop

Editar `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "civio-postgres": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network",
        "bsc-civio-delfos_civic-net",
        "node:20-alpine",
        "npx",
        "-y",
        "@ahmetkca/mcp-server-postgres",
        "postgresql://civio_readonly:TU_PASSWORD@postgres:5432/civio"
      ]
    }
  }
}
```

### Cursor

Editar `.cursor/mcp.json` en la raíz del proyecto:

```json
{
  "mcpServers": {
    "civio-postgres": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network",
        "bsc-civio-delfos_civic-net",
        "node:20-alpine",
        "npx",
        "-y",
        "@ahmetkca/mcp-server-postgres",
        "postgresql://civio_readonly:TU_PASSWORD@postgres:5432/civio"
      ]
    }
  }
}
```

### Windsurf

Editar `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "civio-postgres": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network",
        "bsc-civio-delfos_civic-net",
        "node:20-alpine",
        "npx",
        "-y",
        "@ahmetkca/mcp-server-postgres",
        "postgresql://civio_readonly:TU_PASSWORD@postgres:5432/civio"
      ]
    }
  }
}
```

### VS Code (GitHub Copilot)

Editar `.vscode/mcp.json` en la raíz del proyecto:

```json
{
  "servers": {
    "civio-postgres": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network",
        "bsc-civio-delfos_civic-net",
        "node:20-alpine",
        "npx",
        "-y",
        "@ahmetkca/mcp-server-postgres",
        "postgresql://civio_readonly:TU_PASSWORD@postgres:5432/civio"
      ]
    }
  }
}
```

### Cline (VS Code extension)

Editar `~/.config/cline/cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "civio-postgres": {
      "type": "docker",
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network",
        "bsc-civio-delfos_civic-net",
        "node:20-alpine",
        "npx",
        "-y",
        "@ahmetkca/mcp-server-postgres",
        "postgresql://civio_readonly:TU_PASSWORD@postgres:5432/civio"
      ]
    }
  }
}
```

### Claude Code

Editar `~/.claude.jsonc`:

```jsonc
{
  "mcpServers": {
    "civio-postgres": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network",
        "bsc-civio-delfos_civic-net",
        "node:20-alpine",
        "npx",
        "-y",
        "@ahmetkca/mcp-server-postgres",
        "postgresql://civio_readonly:TU_PASSWORD@postgres:5432/civio",
      ],
    },
  },
}
```

### Variante: conexión directa por localhost (sin red Docker)

Si el cliente no puede unirse a la red `bsc-civio-delfos_civic-net` pero PostgreSQL está expuesto en `localhost:5432`, usar `host.docker.internal` (o `localhost` si el MCP corre nativo):

```json
{
  "command": "docker",
  "args": [
    "run",
    "-i",
    "--rm",
    "node:20-alpine",
    "npx",
    "-y",
    "@ahmetkca/mcp-server-postgres",
    "postgresql://civio_readonly:TU_PASSWORD@host.docker.internal:5432/civio"
  ]
}
```

## Notas importantes

- **`node:20-alpine`** se descarga la primera vez (~40 MB). Después queda cacheados.
- La **red Docker `bsc-civio-delfos_civic-net`** es creada por `docker compose up` — si no existe, iniciar PostgreSQL con `docker compose up -d postgres`.
- El `--rm` elimina el contenedor al terminar. No deja residuos.
- Todos los clientes apuntan al mismo servidor y usuario read-only — los guardrails son idénticos en todos.
- El schema activo es `transparencia` — el MCP server lista tablas de todos los schemas automáticamente.
- Para recargar el dump desde cero: `docker compose down -v` borra los datos, luego `docker compose up -d postgres` y restaurar de nuevo.

## Troubleshooting

| Problema                                     | Causa                             | Solución                                                 |
| -------------------------------------------- | --------------------------------- | -------------------------------------------------------- |
| `ECONNREFUSED postgres:5432`                 | PostgreSQL no está corriendo      | `docker compose up -d postgres`                          |
| `role "civio_readonly" does not exist`       | No se ejecutó el CREATE ROLE      | Ejecutar los GRANTs de arriba                            |
| `relation "transparencia.X" does not exist`  | El dump no se restauró            | Repetir `pg_restore` y grants                            |
| `permission denied for schema transparencia` | Faltan grants para civio_readonly | `GRANT USAGE ON SCHEMA transparencia TO civio_readonly;` |
| MCP server no aparece en opencode            | opencode no se reinició           | Salir y abrir opencode de nuevo                          |
| `ERATE 429` de npm                           | Muchas descargas de npx           | Esperar un minuto y reintentar                           |
