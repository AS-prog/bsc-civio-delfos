---
title: Flujo SDD Ejecutado — docker-python-postgres-env
eyebrow: SPEC-DRIVEN DEVELOPMENT · RETROSPECTIVA
---

# Flujo SDD Ejecutado

Branch :chip[feat/docker-python-postgres-env] · Fecha :chip[2026-05-27] · Estado :pill[PASS WITH WARNINGS]{.olive}

:::tldr
Recorrido paso a paso del cambio `docker-python-postgres-env`: por qué cada fase se delega a su agente especializado, qué produce y cómo encajan los artefactos OpenSpec en el ciclo completo. Veredicto final **PASS WITH WARNINGS** — 4 bugs reales detectados y corregidos antes de archivar.
:::

:::summary-band
:::stat-card num="10" label="FASES SDD" delta="init → archive"
:::
:::stat-card num="7" label="ARCHIVOS CREADOS"
:::
:::stat-card num="13" label="COMMITS" delta="work units"
:::
:::stat-card ok num="PASS" label="VEREDICTO" delta="with warnings"
:::
:::

## Pipeline del ciclo

Siete fases principales en secuencia; bajo `sdd-new` se ramifican cinco sub-fases, cada una con su agente dedicado y su artefacto.

:::timeline
:::timeline-entry time="00" title="Session Preflight" mitigated
El orchestrator fija los guardrails de toda la sesión: ritmo, artefactos, política de PRs y umbral de revisión.
:::
:::timeline-entry time="01" title="sdd-init" mitigated
Detecta el stack real, las convenciones y el backend de persistencia. Decide `strict_tdd` una sola vez.
:::
:::timeline-entry time="02" title="sdd-new" impact
Cinco sub-fases encadenadas: **explore → propose → spec → design → tasks**. Cada una produce su artefacto (`exploration.md`, `proposal.md`, `spec.md`, `design.md`, `tasks.md`).
:::
:::timeline-entry time="03" title="Git — rama y commits" mitigated
Estado de git, inline en el orchestrator: `git switch`, `add`, `commit` por work unit.
:::
:::timeline-entry time="04" title="sdd-apply" mitigated
Implementa los 7 archivos a partir de tasks + proposal + spec + design.
:::
:::timeline-entry time="05" title="sdd-verify" mitigated
Puerta de calidad: ejecuta pruebas reales contra el runtime. Encuentra y corrige 4 bugs.
:::
:::timeline-entry time="06" title="sdd-archive" mitigated
Promueve el spec a fuente de verdad y mueve el cambio al archivo. Cierra el ciclo.
:::
:::

## 0 · Session Preflight

:::card accent head="¿POR QUÉ EL ORCHESTRATOR HACE ESTO?"
Toda la sesión SDD necesita guardrails consistentes. El orchestrator pregunta estas 4 opciones al inicio para que cada sub-agente herede las mismas reglas sin repetir la configuración. Si no se fijan antes de arrancar, cada fase podría operar con supuestos distintos.
:::

| Opción | Elección |
|--------|----------|
| Ritmo | Interactivo :chip[A1] |
| Artefactos | OpenSpec :chip[B1] |
| PRs | Preguntar siempre :chip[C1] |
| Revisión | 400 líneas :chip[D1] |

## 1 · sdd-init

:::card accent head="¿POR QUÉ ESTE AGENTE?"
Antes de cualquier cambio necesitamos saber qué estamos pisando. `sdd-init` está especializado en detectar el stack real del proyecto, las convenciones, las herramientas de testing y en configurar el backend de persistencia (OpenSpec). El orchestrator delega porque leer 4+ archivos de configuración inflaría su contexto sin necesidad. El skill registry y `strict_tdd` se deciden una vez y quedan para toda la sesión.
:::

- Detectó el proyecto como vault de documentación Obsidian
- Stack: Markdown, JSON Canvas, sin código de aplicación
- `strict_tdd: false`
- Creó `openspec/config.yaml` y `.atl/skill-registry.md`

## 2 · sdd-new docker-python-postgres-env

Cinco sub-fases encadenadas: exploración, propuesta, especificación, diseño y desglose en tareas.

### 2a · sdd-explore

:::card accent head="¿POR QUÉ ESTE AGENTE?"
Proponer un cambio sin entender lo que existe es ciego. `sdd-explore` investiga codebases sin modificarlos: busca archivos, lee estructuras, detecta patrones y documentación existente. El orchestrator **no** lo hace inline porque leer 4+ archivos para entender el contexto lo inflaría innecesariamente. Produce `exploration.md`, que consumen las fases siguientes.
:::

- Investigó qué existe en el repo (Docker, Python, apps)
- Descubrió `entorno-dockerizado.md` existente
- Recomendó scope mínimo en `packages/data/`
- Forecast: ~120–220 líneas · Artefacto: `exploration.md`

### 2b · sdd-propose

:::card accent head="¿POR QUÉ ESTE AGENTE?"
Una vez que sabemos qué existe, necesitamos un artefacto formal que defina QUÉ se va a hacer y QUÉ NO. `sdd-propose` crea propuestas con alcance, enfoque, riesgos y plan de rollback. Hacerlo inline mezclaría la coordinación con la definición del cambio.
:::

- Alcance exacto: 7 archivos, Python + PostgreSQL
- Excluyó: frontend, Jupyter, API, CI/CD, Makefile
- Imágenes: `python:3.12-slim` + `postgres:16`
- Forecast: ~128–197 líneas · riesgo :pill[Low]{.olive} · Artefacto: `proposal.md`

### 2c · sdd-spec

:::card accent head="¿POR QUÉ ESTE AGENTE?"
Antes de diseñar o implementar, necesitamos requisitos precisos y escenarios testables. `sdd-spec` escribe delta specs con formato Given/When/Then y palabras clave RFC 2119 (MUST, SHOULD, MAY). Mezclarlo con otras fases dejaría escenarios pobres o incompletos.
:::

- 6 requisitos funcionales con 11 escenarios Given/When/Then
- Artefacto: `specs/docker-runtime-env/spec.md`

### 2d · sdd-design

:::card accent head="¿POR QUÉ ESTE AGENTE?"
Con los requisitos claros, alguien tiene que decidir cómo se construye la solución: qué imágenes, cómo se conectan los servicios, cómo se manejan los secretos, cómo se persisten los datos. `sdd-design` documenta decisiones con tablas de alternativas y diagramas de secuencia.
:::

- 7 decisiones de arquitectura documentadas en tablas
- Diseño de red, volúmenes, env vars
- Artefacto: `design.md`

### 2e · sdd-tasks

:::card accent head="¿POR QUÉ ESTE AGENTE?"
Antes de implementar necesitamos un plan de batalla: tareas concretas, ordenadas por dependencia, con estimación de líneas y decisión sobre PRs encadenados. `sdd-tasks` desglosa propuesta + spec + design en un plan cohesivo.
:::

- 4 fases, 12 tareas
- 3 work units (Foundation → Core → Docs)
- Forecast: ~130–200 líneas · riesgo :pill[Low]{.olive}
- Chained PRs: no recomendado · Artefacto: `tasks.md`

## 3 · Git — rama y commits

:::card accent head="¿POR QUÉ INLINE?"
La creación de ramas y commits es estado de git, no trabajo de análisis. El orchestrator ejecuta `git switch`, `git add` y `git commit` sin inflar su contexto porque son comandos mecánicos y acotados. La skill `work-unit-commits` se cargó para guiar cómo dividir los cambios.
:::

- Rama: `feat/docker-python-postgres-env`
- Commits independientes por work unit (7 commits)
- `PLAN-CONFIG-AGENTES.md` excluido del cambio por ser ajeno

## 4 · sdd-apply

:::card accent head="¿POR QUÉ ESTE AGENTE?"
Escribir código en múltiples archivos con lógica nueva es el caso arquetípico de delegación. `sdd-apply` lee tasks, proposal, spec y design, y produce los archivos reales. El orchestrator **nunca** implementa inline porque escribir código nuevo en 7 archivos inflaría su contexto y perdería la visión de coordinación.
:::

| Archivo | Descripción |
|---------|-------------|
| `.gitignore` | Ignora `.env`, `data/`, caches Python |
| `.env.example` | Template con placeholders |
| `docker-compose.yml` | 2 servicios (postgres + data) |
| `packages/data/Dockerfile` | Multi-stage con `python:3.12-slim` |
| `packages/data/pyproject.toml` | hatchling, psycopg, polars, duckdb |
| `packages/data/tests/smoke/test_connection.py` | Smoke test básico |
| `README.md` | Quick-start y scope boundary |

:::callout warning title="Verificación parcial"
`docker compose config` ✅ — Docker no estaba disponible en ese momento; la validación completa quedó para `sdd-verify`.
:::

## 5 · sdd-verify

:::card accent head="¿POR QUÉ ESTE AGENTE?"
Implementar y verificar son dos preocupaciones distintas. `sdd-verify` es la puerta de calidad: lee proposal, spec, design y tasks, y ejecuta pruebas reales contra el código implementado. Si el orchestrator verificara inline, mezclaría coordinación con validación, y errores como los 4 bugs descubiertos podrían pasarse por alto.
:::

- Docker disponible ✅
- Comandos ejecutados: `config`, `up -d`, smoke test, `git check-ignore`
- Postgres healthy, `data` corre smoke test y sale

**Bugs reales encontrados y corregidos durante verify:**

| Bug | Estado | Fix |
|-----|--------|-----|
| `^3.12` no es PEP 508 válido | :badge[Corregido]{.success} | → `>=3.12` |
| pytest no instalado en contenedor | :badge[Corregido]{.success} | → `[project.optional-dependencies] test` + `".[test]"` |
| `conn.is_closed` no existe en psycopg v3 | :badge[Corregido]{.success} | → `cursor.execute("SELECT 1")` |
| hatchling no encuentra directorios | :badge[Corregido]{.success} | → `[tool.hatch.build.targets.wheel] packages = ["."]` |

:::callout info title="Veredicto: PASS WITH WARNINGS"
Implementación validada contra spec, con bugs reales detectados y corregidos antes de archivar.
:::

## 6 · sdd-archive

:::card accent head="¿POR QUÉ ESTE AGENTE?"
Cerrar un ciclo requiere cuidado: hay que sincronizar los delta specs con la fuente de verdad, mover la carpeta del cambio al archivo y verificar que nada se pierda. `sdd-archive` finaliza cambios SDD sin destruir artefactos de auditoría.
:::

- Spec promovido a source of truth: `openspec/specs/docker-runtime-env/spec.md`
- Cambio movido a: `openspec/changes/archive/2026-05-27-docker-python-postgres-env/`
- Ciclo SDD cerrado

## Configuración de modelos

Asignación en `~/.config/opencode/opencode.json`.

### Modelos base

| Variable | Modelo |
|----------|--------|
| `model` (default) | `opencode-go/deepseek-v4-flash` |
| `small_model` | `nan/gemma4` |

### Asignación por agente

| Agente | Rol | Modelo | reasoning_effort |
|---|---|---|---|
| `gentle-orchestrator` | Coordina todo el flujo SDD | `openai/gpt-5.5` | :pill[high]{.clay} |
| `sdd-init` | Bootstrap SDD | `openai/gpt-5.5` | medium |
| `sdd-explore` | Investiga codebase | `openai/gpt-5.5` | medium |
| `sdd-propose` | Crea propuestas | `nan/qwen3.6` | — |
| `sdd-spec` | Escribe specs | `bailian-coding-plan/glm-5` | thinking nativo |
| `sdd-design` | Diseño técnico | `nan/qwen3.6` | — |
| `sdd-tasks` | Desglose en tareas | `nan/qwen3.6` | — |
| `sdd-apply` | Implementa código | `nan/qwen3.6` | — |
| `sdd-verify` | Valida contra specs | `nan/qwen3.6` | — |
| `sdd-archive` | Archiva cambios | `small_model` (`nan/gemma4`) | — |
| `sdd-onboard` | Guía al usuario | `nan/qwen3.6` | — |
| `general` (built-in) | Chat por defecto | usa `model` global | — |

## Resumen de commits

```
9ed431b docs: archivar cambio Docker Python PostgreSQL
e108b57 fix: corregir verificación Docker Python PostgreSQL
d911e08 docs: actualizar progreso de tareas Docker
58ab322 docs: agregar README con quick-start y límite de alcance
e72ba5a feat: crear scaffold packages/data con pyproject, Dockerfile y smoke test
c172edf feat: agregar docker-compose.yml con servicios postgres y data
5dad6ae feat: agregar plantilla .env.example para PostgreSQL local
00a585f chore: agregar entradas de .gitignore para env local y caches
d386270 docs: planificar tareas del entorno Docker
3009722 docs: diseñar entorno Docker Python PostgreSQL
d8883bc docs: proponer entorno Docker Python PostgreSQL
eb6a1ed docs: inicializar contexto SDD del proyecto
17eb283 chore: ignorar cachés y secretos locales
```

## Artefactos OpenSpec generados

```
openspec/
├── config.yaml
├── specs/
│   └── docker-runtime-env/
│       └── spec.md
└── changes/
    └── archive/
        └── 2026-05-27-docker-python-postgres-env/
            ├── archive-report.md
            ├── design.md
            ├── exploration.md
            ├── proposal.md
            ├── specs/
            │   └── docker-runtime-env/
            │       └── spec.md
            ├── tasks.md
            └── verify-report.md
```

## Roles en el flujo

Resumen consolidado: por qué cada agente recibe su tarea.

| Agente | ¿Por qué se le asigna esta tarea? |
|--------|----------------------------------|
| `gentle-orchestrator` | Coordina fases y delega toda ejecución. Nunca hace análisis o implementación inline. Solo opera directamente sobre comandos mecánicos (git, state) o lecturas de 1-3 archivos para decidir. |
| `sdd-init` | Detecta stack, convenciones y herramientas. Se delega porque leer 4+ archivos de configuración infla el contexto del orchestrator innecesariamente. |
| `sdd-explore` | Investiga el codebase sin modificarlo. Entender un ecosistema requiere leer múltiples archivos. |
| `sdd-propose` | Define alcance, enfoque y riesgos. Escribir una propuesta con análisis es trabajo complejo que necesita su propio contexto. |
| `sdd-spec` | Escribe requisitos y escenarios Given/When/Then. La especificación requiere atención exclusiva. |
| `sdd-design` | Diseña arquitectura y documenta decisiones técnicas. Preocupación separada que se beneficia de su propio contexto. |
| `sdd-tasks` | Desglosa propuesta + spec + design en tareas. Requiere leer todos los artefactos anteriores y producir un plan cohesivo. |
| `sdd-apply` | Implementa el código a partir de las tareas. Escribir código nuevo en múltiples archivos es el caso arquetípico de delegación. |
| `sdd-verify` | Ejecuta pruebas reales contra spec y runtime. Ejecutar herramientas externas y analizar resultados requiere un contexto limpio. |
| `sdd-archive` | Sincroniza specs con la fuente de verdad y mueve el cambio al archivo. Operaciones mecánicas que requieren cuidado para no perder artefactos. |
