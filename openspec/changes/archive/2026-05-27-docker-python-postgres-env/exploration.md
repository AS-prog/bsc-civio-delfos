## Exploration: docker-python-postgres-env

### Current State
El repositorio sigue siendo docs-first: `openspec/config.yaml` declara un vault de documentación/análisis sin aplicación, tests, linter ni build. No existen archivos reales de Docker, Python, PostgreSQL ni dependencias (`Dockerfile`, `docker-compose.yml`, `pyproject.toml`, `requirements.txt`, `*.py`, `package.json`, `Gemfile`). Sí existe un blueprint muy relevante en `vault-context/delfos-context/referencias/entorno-dockerizado.md`, que propone un entorno para hackathon con `postgres:16`, `python:3.12-slim`, datos locales gitignored y, en una fase más amplia, frontend Svelte.

La documentación del vault ya justifica el contexto técnico: Civio combina visualización Svelte/Vite/D3, APIs ligeras Node/Express, scrapers Ruby `fetch → parse → CSV`, Python para análisis de datos y PostgreSQL en el ecosistema DVMI/presupuestos. `analisis-monorepo-civio.md` también anticipa `docker-compose.yml` y `packages/` como dirección futura, pero no hay implementación en este repo.

### Affected Areas
- `openspec/changes/docker-python-postgres-env/exploration.md` — artifact de exploración de esta fase.
- `.gitignore` — debería ampliarse si se crean `data/`, `.env`, caches Python y artefactos locales.
- `docker-compose.yml` — probable raíz del entorno Compose mínimo.
- `.env.example` — contrato no sensible para credenciales locales de PostgreSQL.
- `README.md` — no existe; sería necesario para mantener el repo usable si se introduce runtime.
- `app/` o `packages/data/` — posible scaffold Python; hoy no existe y cambiaría el carácter docs-only.
- `vault-context/delfos-context/referencias/entorno-dockerizado.md` — blueprint existente que debería referenciarse o reconciliarse para evitar documentación duplicada.

### Approaches
1. **Compose infra-only** — Crear solo Compose, `.env.example`, `.gitignore` y README con un contenedor Python de shell/smoke y PostgreSQL.
   - Pros: menor diff, mantiene el repo docs-first, permite validar Docker/Postgres sin comprometer arquitectura de app.
   - Cons: no deja una estructura clara para código futuro más allá de comandos manuales.
   - Effort: Low

2. **Minimal data app scaffold** — Crear Compose más `app/` o `packages/data/` con `pyproject.toml`, Dockerfile y smoke script de conexión.
   - Pros: base ejecutable para futuros scrapers/API; más útil para hackathon.
   - Cons: introduce código de aplicación en un repo que hoy es de documentación; requiere decisiones de estructura y tooling.
   - Effort: Medium

3. **Full hackathon scaffold** — Implementar lo que describe `entorno-dockerizado.md`: Python, PostgreSQL, Jupyter, Makefile, datos, y preparar compatibilidad futura con frontend.
   - Pros: maximiza utilidad inmediata para equipo data-heavy.
   - Cons: probablemente supera el cambio mínimo, aumenta carga de revisión y mezcla decisiones de infra, data y frontend.
   - Effort: High

### Recommendation
Recomiendo **Minimal data app scaffold**, pero acotado: Docker Compose con `postgres` y un servicio Python basado en `python:3.12-slim`, `packages/data/` como ubicación compatible con el blueprint de monorepo, `pyproject.toml` mínimo, `.env.example`, `.gitignore` actualizado y README de arranque. No introducir frontend todavía.

Python 3.12 es coherente con el blueprint existente y el análisis de monorepo; `python:3.12-slim` reduce peso sin abandonar una imagen oficial estable. PostgreSQL debería usar `postgres:16` por coherencia con `entorno-dockerizado.md` y por ser una versión madura alineada con el uso relacional tipo DVMI; si el objetivo fuera máxima vida útil futura, la propuesta puede evaluar `postgres:17`, pero el repo ya documenta 16.

El repo debería seguir **docs-first con un scaffold runtime pequeño**, no convertirse todavía en aplicación completa. Para evitar confusión, el README debe explicar que `packages/data/` es base técnica para experimentos Civio-aligned y que el vault sigue siendo la fuente principal de análisis.

### Risks
- Cambio de identidad del repo: pasar de vault/documentación a entorno ejecutable sin explicar el límite puede confundir a revisores.
- Duplicación o contradicción con `entorno-dockerizado.md` si la implementación mínima no queda vinculada al blueprint.
- Secretos: `.env` debe quedar ignorado y solo versionarse `.env.example`.
- Persistencia local: `data/` y volumen `postgres_data` deben tratarse como estado desechable/local, no como contenido del vault.
- Alcance: incluir Jupyter, FastAPI o frontend en el primer cambio puede disparar líneas y decisiones no necesarias.

### Review Workload Forecast
Estimación alta de revisión para la opción recomendada: **120–220 líneas cambiadas** si incluye `docker-compose.yml`, `.env.example`, `.gitignore`, `README.md`, `packages/data/Dockerfile`, `packages/data/pyproject.toml` y un smoke script pequeño. Riesgo frente al presupuesto de 400 líneas: **Low–Medium**. Chained PRs no parecen necesarios si se mantiene el alcance mínimo; sí conviene pedir confirmación si se incluye Jupyter/FastAPI/frontend.

### Ready for Proposal
Yes — el siguiente paso debería ser `sdd-propose`, dejando explícito que la propuesta debe elegir entre infra-only y scaffold mínimo, y mantener fuera de alcance frontend, Jupyter avanzado y API hasta cambios posteriores.
