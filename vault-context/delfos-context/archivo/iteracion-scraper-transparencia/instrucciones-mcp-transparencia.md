---
tags:
  - civio
  - hackathon
  - mcp
  - python
  - plan
title: "Instrucciones — MCP del Corpus de Transparencia"
aliases:
  - MCP Transparencia
  - Instrucciones scraper transparencia
  - División de tareas MCP
---

# Instrucciones — MCP del Corpus de Transparencia

> [!abstract] Origen
> Iteración del 30 de mayo 2026 — raw en `30 May at 11-49.txt`.
> Objetivo: convertir el modelo de datos del scraper en un **MCP (Model Context Protocol) en Python** consumible por cualquier agente.

---

## 1. Objetivo

Construir un **MCP en Python** que exponga el corpus de Publicidad Activa (`transparencia.gob.es`) extraído por el scraper. El MCP debe tener dos capas bien diferenciadas:

| Capa | Responsabilidad |
|---|---|
| **SQL** | Consultas directas a la base de datos (`civio`) donde está persistido el corpus |
| **Marts** | Reglas de negocio, transformaciones y vistas analíticas (equivalente a `dbt marts`) |

El MCP debe ser **agnóstico al agente cliente** — cualquier agente (Claude Code, OpenCode, Cursor, etc.) debe poder conectarse y consultar.

---

## 2. Modelo de datos

Partimos del JSON existente (`models.py` del scraper: `PageData`, `PageSection`, `AccordionItem`, `ExternalLink`).

### Tareas de limpieza

1. Revisar el JSON/modelo actual y **normalizar nombres** (snake_case consistente, sin ambigüedades).
2. Agregar **comentarios descriptivos en cada columna y tabla** (qué representa, tipo de dato, ejemplo, fuente).
3. Documentar **relaciones** entre tablas (FK lógicas aunque no haya constraints en SQLite/Postgres).
4. Definir **tipos estrictos** para cada campo (text, integer, timestamp, array, etc.).

El modelo limpio será la **fuente de verdad** que consumirá el MCP.

---

## 3. Arquitectura del MCP

```
mcp-transparencia/
├── mcp_server.py              ← Entry point del servidor MCP
├── sql/
│   ├── __init__.py
│   ├── connection.py          ← Conexión a DB (`civio`)
│   ├── queries.py             ← Consultas SQL parametrizadas
│   └── models.py              ← Tipos/esquemas derivados del modelo limpio
├── marts/
│   ├── __init__.py
│   ├── rules.py               ← Reglas de negocio (clasificaciones, filtros)
│   ├── aggregations.py        ← Vistas agregadas por organismo, año, etc.
│   └── enrichments.py         ← Enriquecimiento (links a BOE, cruces con otros datos)
├── pyproject.toml
└── README.md
```

### Capa SQL (`sql/`)

- `connection.py`: maneja la conexión a la base de datos `civio` (configurable por variable de entorno).
- `queries.py`: consultas SQL crudas pero parametrizadas. Cada función devuelve datos listos para consumir.
- `models.py`: dataclasses `pydantic` o `dataclass` que reflejan el esquema limpio.

### Capa de negocio (`marts/`)

- `rules.py`: lógica de dominio — ej. "esta subvención pertenece a este organismo", "este enlace es BOE vs contenido".
- `aggregations.py`: consultas que agrupan y resumen — ej. "subvenciones por ministerio en 2025".
- `enrichments.py`: cruce con fuentes externas o transformaciones que no son SQL puras.

### Servidor MCP (`mcp_server.py`)

Expone **tools** (herramientas) que los agentes pueden invocar:

| Tool | Capa | Descripción |
|---|---|---|
| `execute_sql(query, limit=100)` | SQL | Ejecuta una consulta read-only (`SELECT`, `WITH`, `EXPLAIN`) contra Postgres |
| `get_page(url)` | SQL | Devuelve el `PageData` completo de una URL |
| `search_pages(query)` | SQL | Búsqueda textual en títulos y secciones |
| `list_organisms()` | Mart | Lista organismos con su volumen de datos |
| `get_links_by_category(category, materia_slug=None)` | Mart | Lista enlaces por categoría curada (`subvenciones`, `normativa`, `documento`, etc.) |
| `get_external_links(domain)` | SQL | Enlaces externos filtrados por dominio |

---

## 4. División de tareas (paralelo vía Engram)

Dividimos en **2 tareas independientes** para trabajar en paralelo en distintas máquinas.

### Tarea A: Limpieza del modelo + capa SQL

**Responsable**: — (asignar)

| Paso | Descripción |
|---|---|
| A1 | Tomar el JSON actual de `models.py` y limpiarlo: comentarios, tipos, relaciones |
| A2 | Crear conexión configurable a `civio` |
| A3 | Crear `sql/models.py` con las dataclasses limpias |
| A4 | Crear `sql/queries.py` con las consultas fundamentales |
| A5 | Testear contra la base de datos real |
| A6 | Pushear a Engram |

### Tarea B: Capa de negocio (marts) + servidor MCP

**Responsable**: — (asignar)

| Paso | Descripción |
|---|---|
| B1 | Crear `marts/rules.py` con reglas de negocio iniciales |
| B2 | Crear `marts/aggregations.py` con agregados por organismo/año |
| B3 | Crear `marts/enrichments.py` con cruce BOE |
| B4 | Crear `mcp_server.py` con las tools conectando a SQL + Marts |
| B5 | Testear el servidor MCP contra un agente (Claude Code, etc.) |
| B6 | Pushear a Engram |

---

## 5. Flujo de trabajo con Engram

```
[Plan] → Push Tarea A → Push Tarea B → [Máquina 1 hace A, Máquina 2 hace B]
                                             ↓
                                  Cada una importa desde Engram
                                             ↓
                                  Implementan su parte en paralelo
                                             ↓
                                  Push de cada pieza a Engram
                                             ↓
                                     Conectar ambas partes
                                             ↓
                                  Pull final + merge → MCP completo
```

### Comandos de referencia

```bash
# Pushear avance a Engram
engram push "mcp-transparencia/task-a"

# Importar en otra máquina
engram import "mcp-transparencia/task-a"

# Sincronizar cambios
engram pull
```

---

## 6. Conexión final

Una vez ambas tareas están implementadas:

1. Hacer `engram pull` en la máquina que integra.
2. Verificar que `mcp_server.py` importa correctamente `sql/` y `marts/`.
3. Probar todas las tools contra la base de datos `civio`.
4. Conectar desde un agente y ejecutar consultas de extremo a extremo.

### Criterio de éxito

> Un agente externo (Claude Code, OpenCode) puede conectarse al MCP, ejecutar `get_page(url)` y recibir el `PageData` completo, y ejecutar `list_organisms()` para ver el resumen por organismo.

### Estado actual

El MCP queda habilitado en `opencode.json` como servidor local `transparencia`:

```json
{
  "mcp": {
    "transparencia": {
      "type": "local",
      "command": ["uv", "run", "--project", "packages/mcp-transparencia", "python", "packages/mcp-transparencia/mcp_server.py"]
    }
  }
}
```

La base restaurada desde `data/warehouse/transparencia-transparencia-schema.dump` contiene:

- `transparencia.pages`: 1167 filas
- `transparencia.sections`: 1402 filas
- `transparencia.accordion`: 320 filas
- `transparencia.links`: 13267 filas

---

## Referencias

- [[scraper-transparencia]] — implementación del scraper y modelos originales
- [[pendientes-scraper-transparencia]] — backlog de fixes (P1-P6)
- `packages/data/scrapers/transparencia/models.py` — fuente del modelo de datos
- `https://modelcontextprotocol.io/` — especificación MCP
