# Flujo SDD Ejecutado — docker-python-postgres-env

Ciclo completo del cambio `docker-python-postgres-env`, paso a paso.

---

## 0. Session Preflight

**¿Por qué el gentle-orchestrator hace esto?** Porque toda la sesión SDD necesita guardrails consistentes. El orchestrator pregunta estas 4 opciones al inicio para que cada sub-agente herede las mismas reglas sin tener que repetir la configuración. Si no se fijan antes de arrancar, cada fase podría operar con supuestos distintos.

Se configuraron 4 opciones:

| Opción | Elección |
|--------|----------|
| Ritmo | Interactivo (A1) |
| Artefactos | OpenSpec (B1) |
| PRs | Preguntar siempre (C1) |
| Revisión | 400 líneas (D1) |

## 1. sdd-init

**¿Por qué `sdd-init` para esto?** Antes de cualquier cambio necesitamos saber qué estamos pisando. `sdd-init` está especializado en detectar el stack real del proyecto, las convenciones, herramientas de testing y configurar el backend de persistencia (OpenSpec). El orchestrator delega porque leer 4+ archivos de configuración y estructuras de directorio inflaría su contexto sin necesidad. Además, el skill registry y `strict_tdd` se deciden una vez y quedan para toda la sesión.

- Detectó el proyecto como vault de documentación Obsidian
- Stack: Markdown, JSON Canvas, sin código de aplicación
- `strict_tdd: false`
- Creó `openspec/config.yaml` y `.atl/skill-registry.md`

## 2. sdd-new docker-python-postgres-env

### 2a. sdd-explore

**¿Por qué `sdd-explore` para esto?** Porque proponer un cambio sin entender lo que existe es ciego. `sdd-explore` está especializado en investigar codebases sin modificarlos: busca archivos, lee estructuras, detecta patrones y documentación existente. El orchestrator **no** hace esto inline porque leer 4+ archivos para entender el contexto inflaría innecesariamente su contexto. La exploración produce un artefacto (`exploration.md`) que luego consumen las fases siguientes.

- Investigó qué existe en el repo (Docker, Python, apps)
- Descubrió `entorno-dockerizado.md` existente
- Recomendó scope mínimo en `packages/data/`
- Forecast: ~120–220 líneas
- Artefacto: `exploration.md`

### 2b. sdd-propose

**¿Por qué `sdd-propose` para esto?** Una vez que sabemos qué existe, necesitamos un artefacto formal que defina QUÉ se va a hacer y QUÉ NO. `sdd-propose` está especializado en crear propuestas de cambio con alcance, enfoque, riesgos y plan de rollback. El orchestrator delega porque escribir una propuesta con análisis es trabajo complejo que necesita su propio contexto; hacerlo inline mezclaría la coordinación con la definición del cambio.

- Definió alcance exacto: 7 archivos, Python + PostgreSQL
- Excluyó: frontend, Jupyter, API, CI/CD, Makefile
- Imágenes: `python:3.12-slim` + `postgres:16`
- Forecast: ~128–197 líneas, riesgo Low
- Artefacto: `proposal.md`

### 2c. sdd-spec

**¿Por qué `sdd-spec` para esto?** Antes de diseñar o implementar, necesitamos requisitos precisos y escenarios testables. `sdd-spec` está especializado en escribir delta specs con formato Given/When/Then y palabras clave RFC 2119 (MUST, SHOULD, MAY). El orchestrator delega porque la especificación es un artefacto de calidad que requiere atención exclusiva; si la mezclara con otras fases, los escenarios quedarían pobres o incompletos.

- 6 requisitos funcionales con 11 escenarios Given/When/Then
- Artefacto: `specs/docker-runtime-env/spec.md`

### 2d. sdd-design

**¿Por qué `sdd-design` para esto?** Con los requisitos claros, alguien tiene que decidir cómo se construye la solución: qué imágenes, cómo se conectan los servicios, cómo se manejan los secretos, cómo se persisten los datos. `sdd-design` está especializado en crear diseño técnico con decisiones documentadas, diagramas de secuencia y tablas de alternativas. El orchestrator delega porque el diseño arquitectónico es una preocupación separada que se beneficia de tener su propio contexto sin la presión de implementar.

- 7 decisiones de arquitectura documentadas en tablas
- Diseño de red, volúmenes, env vars
- Artefacto: `design.md`

### 2e. sdd-tasks

**¿Por qué `sdd-tasks` para esto?** Antes de implementar necesitamos un plan de batalla: tareas concretas, ordenadas por dependencia, con estimación de líneas y decisión sobre PRs encadenados. `sdd-tasks` está especializado en desglosar propuesta+spec+design en tareas accionables. El orchestrator delega porque crear un breakdown requiere leer todos los artefactos anteriores y producir un plan cohesivo; hacerlo inline fragmentaría la atención.

- 4 fases, 12 tareas
- 3 work units (Foundation → Core → Docs)
- Forecast: ~130–200 líneas, riesgo Low
- Chained PRs: no recomendado
- Artefacto: `tasks.md`

## 3. Git — Rama y Commits

**¿Por qué el gentle-orchestrator maneja esto directamente?** La creación de ramas y commits es estado de git, no trabajo de análisis. El orchestrator puede ejecutar `git switch`, `git add` y `git commit` sin inflar su contexto porque son comandos mecánicos y acotados. Además, el usuario pidió explícitamente "crea una rama y commitea en independientes". La skill `work-unit-commits` se cargó para guiar cómo dividir los cambios.

- Rama: `feat/docker-python-postgres-env`
- Commits independientes por work unit (7 commits total)
- `PLAN-CONFIG-AGENTES.md` excluido del cambio por ser ajeno

## 4. sdd-apply

**¿Por qué `sdd-apply` para esto?** Porque escribir código en múltiples archivos con lógica nueva es el caso arquetípico de delegación. `sdd-apply` está especializado en implementar cambios a partir de definiciones de tareas: lee tasks.md, proposal, spec y design, y produce los archivos reales. El orchestrator **nunca** implementa inline porque escribir código nuevo en 7 archivos inflaría su contexto y perdería la visión de coordinación. Además, `apply` consume los artefactos de planificación y produce los archivos de implementación, manteniendo la separación de responsabilidades.

**Creó:**

| Archivo | Descripción |
|---------|-------------|
| `.gitignore` | Ignora `.env`, `data/`, caches Python |
| `.env.example` | Template con placeholders |
| `docker-compose.yml` | 2 servicios (postgres + data) |
| `packages/data/Dockerfile` | Multi-stage con python:3.12-slim |
| `packages/data/pyproject.toml` | hatchling, psycopg, polars, duckdb |
| `packages/data/tests/smoke/test_connection.py` | Smoke test básico |
| `README.md` | Quick-start y scope boundary |

**Verificación parcial**: `docker compose config` ✅ (Docker no disponible en ese momento)

## 5. sdd-verify

**¿Por qué `sdd-verify` para esto?** Porque implementar y verificar son dos preocupaciones distintas. `sdd-verify` es la puerta de calidad: lee proposal, spec, design y tasks, y ejecuta pruebas reales contra el código implementado. El orchestrator delega porque ejecutar herramientas externas (Docker, pytest) y analizar resultados requiere un contexto limpio y enfocado. Si el orchestrator verificara inline, mezclaría la coordinación con la validación, y errores como los 4 bugs descubiertos podrían pasarse por alto.

- Docker disponible ✅
- Comandos ejecutados: config, up -d, smoke test, git check-ignore
- Postgres healthy, data corre smoke test y sale

**Bugs reales encontrados y corregidos durante verify:**

| Bug | Fix |
|-----|-----|
| `^3.12` no es PEP 508 válido | → `>=3.12` |
| pytest no instalado en contenedor | → `[project.optional-dependencies] test` + `".[test]"` |
| `conn.is_closed` no existe en psycopg v3 | → `cursor.execute("SELECT 1")` |
| hatchling no encuentra directorios | → `[tool.hatch.build.targets.wheel] packages = ["."]` |

**Veredicto**: `PASS WITH WARNINGS`

## 6. sdd-archive

**¿Por qué `sdd-archive` para esto?** Porque cerrar un ciclo requiere cuidado: hay que sincronizar los delta specs con la fuente de verdad, mover la carpeta del cambio al archivo y verificar que nada se pierda. `sdd-archive` está especializado en finalizar cambios SDD sin destruir artefactos de auditoría. El orchestrator delega porque las operaciones de archivo son mecánicas pero requieren atención a los detalles; si el orchestrator las hiciera inline, el riesgo de perder artefactos o dejar inconsistencias sería mayor.

- Spec promovido a source of truth: `openspec/specs/docker-runtime-env/spec.md`
- Cambio movido a: `openspec/changes/archive/2026-05-27-docker-python-postgres-env/`
- Ciclo SDD cerrado

---

## Configuración de modelos

Asignación de modelos a cada agente SDD en `~/.config/opencode/opencode.json`.

### Modelos base

| Variable | Modelo |
|----------|--------|
| `model` (default) | `opencode-go/deepseek-v4-flash` |
| `small_model` | `nan/gemma4` |

### Asignación por agente

| Agente | Rol | Modelo | reasoning_effort |
|---|---|---|---|
| `gentle-orchestrator` | Coordina todo el flujo SDD | `openai/gpt-5.5` | **high** |
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

---

## Resumen de Commits

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

---

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

---

## Roles en el flujo

| Agente | ¿Por qué se le asigna esta tarea? |
|--------|----------------------------------|
| **gentle-orchestrator** | Coordina fases y delega toda ejecución. Nunca hace trabajo de análisis o implementación inline porque inflaría su contexto. Solo opera directamente sobre comandos mecánicos (git, state) o lecturas de 1-3 archivos para decidir. |
| **sdd-init** | Detecta stack, convenciones y herramientas del proyecto. Se delega porque leer 4+ archivos de configuración infla el contexto del orchestrator innecesariamente. |
| **sdd-explore** | Investiga el codebase sin modificarlo. Se delega porque entender un ecosistema requiere leer múltiples archivos, y hacerlo inline fragmentaría la atención del orchestrator. |
| **sdd-propose** | Define alcance, enfoque y riesgos del cambio. Se delega porque escribir una propuesta con análisis es trabajo complejo que necesita su propio contexto. |
| **sdd-spec** | Escribe requisitos y escenarios Given/When/Then. Se delega porque la especificación es un artefacto de calidad que requiere atención exclusiva. |
| **sdd-design** | Diseña arquitectura y documenta decisiones técnicas. Se delega porque el diseño arquitectónico es una preocupación separada que se beneficia de tener su propio contexto. |
| **sdd-tasks** | Desglosa propuesta+spec+design en tareas concretas. Se delega porque el breakdown requiere leer todos los artefactos anteriores y producir un plan cohesivo. |
| **sdd-apply** | Implementa el código a partir de las tareas. Se delega porque escribir código en múltiples archivos con lógica nueva es el caso arquetípico de delegación. |
| **sdd-verify** | Ejecuta pruebas reales contra spec y runtime. Se delega porque ejecutar herramientas externas (Docker, pytest) y analizar resultados requiere un contexto limpio y enfocado. |
| **sdd-archive** | Sincroniza specs con la fuente de verdad y mueve el cambio al archivo. Se delega porque las operaciones de archivo son mecánicas pero requieren cuidado para no perder artefactos. |
