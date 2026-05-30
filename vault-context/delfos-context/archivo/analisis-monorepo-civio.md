---
tags:
  - civio
  - monorepo
  - arquitectura
  - hackathon
  - analisis
title: "Análisis de monorepo Civio por temas"
aliases:
  - Monorepo Civio
  - Blueprint monorepo
---

# Análisis de monorepo Civio por temas

Este documento analiza la arquitectura real de los repositorios de [[Civio]] agrupados por los tres dominios de la organización, con el objetivo de diseñar un **monorepo preconfigurado** que unifique patrones, stacks y herramientas.

> [!warning] Estado actual
> Civio **no tiene un monorepo**. Cada proyecto vive en su propio repo con su propio stack, build system y configuración. Esto es lo que analizamos para entender cómo podría estructurarse uno.

---

## Tema 1: Transparencia presupuestaria (DVMI)

### Qué es

El ecosistema `presupuesto-*` es el núcleo histórico de Civio. Una aplicación Django con un sistema de **themes** que permite adaptar visualmente la misma aplicación a distintas administraciones.

### Cómo está hoy

```
presupuesto/                      ← Aplicación base (Django 3.2)
├── budget_app/                   ← App Django principal
│   ├── models/                   ← 18 modelos (budget, entity, categories, etc.)
│   ├── views/                    ← 22 vistas (policies, entities, budgets, search, etc.)
│   ├── loaders/                  ← 10 scripts ETL (CSV → BD)
│   └── management/commands/      ← 11 comandos Django manage.py
├── templates/                    ← Jinja2 templates
├── requirements/                 ← Python deps (Django + psycopg2 + jinja + etc.)
├── package.json                  ← Rollup para bundle D3.js
└── project/                      ← Django settings, urls, wsgi

presupuesto-pge/                  ← Tema específico (plugin Django)
├── settings.py                   ← Config del tema
├── loaders/pge_budget_loader.py  ← Loader custom para formato PGE
├── templates/                    ← Templates que sobreescriben a base
├── static/data/                  ← CSVs de presupuesto y población
└── static/javascripts/ccaa.js    ← D3 v3 para mapa CCAA
```

### Stack actual

| Componente | Tecnología |
|---|---|
| Backend | Django 3.2 + PostgreSQL |
| Frontend | Jinja2 + jQuery 2 + SCSS |
| Visualización | D3.js v5 (bundled con Rollup) |
| Themes | Directorios con templates override |
| ETL | Scripts Python + comandos manage.py |
| Node | v16 |

### Patrón de datos

```
CSV fuente → manage.py load_budget → PostgreSQL → Django views → Jinja2 templates + D3.js
```

Los CSVs provienen de los scrapers Ruby (Tema 3). La aplicación base ofrece:
- ~70 rutas REST
- 30 formatos de descarga (CSV/XLS)
- 5 idiomas
- Sistema de caché agresivo (middleware que limpia tracking params)

### Para monorepo

```
packages/
  presupuesto-core/          ← La app Django base
  presupuesto-theme-pge/     ← Tema PGE (depende de core)
  presupuesto-theme-navarra/ ← Tema Navarra
  presupuesto-loader-ccaa/   ← Loader para scraper CCAA
```

> [!tip] Clave técnica
> El sistema de themes de DVMI es el precedente más cercano a una arquitectura de paquetes. Cada theme es un plugin Django que sobreescribe templates y configuración.

---

## Tema 2: Visualizaciones e investigación periodística

### Qué es

La capa editorial de Civio. Visualizaciones interactivas modernas y aplicaciones de datos para investigaciones periodísticas.

### Cómo está hoy

**civio-graphs-public** (nuevo estándar — Svelte 5):

```
civio-graphs-public/
└── justicia/
    └── aislamiento-prisiones/
        ├── motivos-sanciones/         ← Visualización independiente
        │   ├── package.json
        │   ├── vite.config.js
        │   ├── svelte.config.js
        │   ├── src/
        │   │   ├── main.js            ← Entry point (mount Svelte)
        │   │   ├── App.svelte         ← Root component
        │   │   ├── states/            ← Clases reactivas ($state, $derived)
        │   │   ├── lib/               ← Componentes Svelte
        │   │   └── utils/             ← Utilidades JS puras
        │   └── public/
        ├── sanciones-administracion/  ← Mismo patrón
        └── tiempos-limbo/             ← Mismo patrón
```

Cada visualización es **completamente independiente**: su propio `package.json`, `vite.config.js`, build system y ciclo de despliegue. Se publican via `sync.sh` (rsync + cron).

**Stack moderno:**

| Componente | Tecnología | Versión |
|---|---|---|
| Framework | Svelte | 5 (runes: $state, $derived, $effect) |
| Bundler | Vite | 7 |
| Visualización | D3.js | 7.9 (uso mínimo: csv, rollup, scaleLinear) |
| Linter | Oxlint | 1.43 |
| Formateo | Prettier | 3.8 |
| Dead deps | Knip | 5.82 |
| Test / iframes | Playwright | 1.57 |
| Node | 24.13 |

**Patrón de componente Svelte 5 (Runes):**

```js
// main.js — entry point
import { mount } from 'svelte';
import App from './App.svelte';
const app = mount(App, {
  target: document.getElementById(__APP_ID__),
  props: { lang, chartID, a11y, alt }
});

// Estado reactivo: $state / $derived
class Data {
  value = $state(undefined);
  selectedAdm = $state('AGE');
  rows = $derived.by(() => compute(this.value, this.selectedAdm));
}

// Efectos: $effect
$effect(() => { /* reacciona a cambios */ });
```

**verba** (Vue 2 + Express + ElasticSearch 7) — aplicación web completa:

```
verba/
├── api/                  ← Express 4 + elasticsearch.js
│   └── src/
│       ├── index.js      ← 6 endpoints REST
│       └── captions.js   ← Cliente ElasticSearch
├── web/                  ← Vue 2 + Vuex + Vue Router
│   └── src/
│       ├── Search.vue, Programme.vue, etc.
│       └── components/   ← SearchBox, Results, AreaChart, etc.
└── docker-compose.yml    ← elasticsearch + web + api
```

**Stack verba:**

| Componente | Tecnología |
|---|---|
| Frontend | Vue 2 + Vuex + Vue Router + D3 v6 |
| Backend | Express 4 + elasticsearch.js |
| Búsqueda | ElasticSearch 7.4 |
| Docker | 3 servicios orquestados |

### Para monorepo

```
packages/
  graph-templates/        ← Scafolding para nuevas visualizaciones
    svelte-vite-d3/       ← Template base (Svelte 5 + Vite 7 + D3)
  graph-motivos/          ← Visualización individual
  graph-sanciones/        ← Visualización individual
  graph-tiempos-limbo/    ← Visualización individual
  graph-components/       ← Componentes Svelte compartidos (Tooltip, Footer, etc.)
  graph-utils/            ← Utilidades compartidas (colors, locale, D3 helpers)
  verba-api/              ← Express backend
  verba-web/              ← Vue frontend
```

> [!tip] Clave técnica
> El patrón de `civio-graphs-public` (cada visualización independiente) sugiere que un monorepo para visualizaciones debería ser **multi-paquete** (turborepo/nx) donde cada chart es un workspace independiente que comparte utilidades pero tiene su propio build y despliegue.

> [!tip] Patrón D3 en Svelte
> D3 se usa exclusivamente para **cálculos y escalas** (`d3.csv`, `d3.rollup`, `d3.scaleLinear`). El renderizado es **Svelte SVG**, no manipulación directa del DOM. Esto es clave para el rendimiento y la reactividad.

---

## Tema 3: Scraping y pipelines de datos

### Qué es

La infraestructura de datos de Civio. Todos siguen el mismo patrón: fetch → parse → CSV.

### Cómo está hoy

**scraper-pge** (Presupuestos Generales del Estado):

```
Gemfile: nokogiri, mustache, unicode_utils
Pipeline: parse_budget.rb → output/{año}/*.csv
Estructura interna: breakdown por entidad, programa, ingresos, genérico
```

**scraper-ccaa-budget-summaries** (Presupuestos autonómicos):

```
Gemfile: mechanize, optimist
Pipeline: fetch.rb → staging/ → parse.rb → budget.sorted.csv
Output: CSV con columnas year, region, policy, + capítulos 1-9 + total
```

**scraper-subvenciones-municipales-2015** (Subvenciones electorales):

```
Pipeline: fetch.rb → parse.rb → town_data.csv + party_data.csv → calculate.rb → subvención
Lógica de negocio: fórmula (votos × 0.54€ + concejales × 270.90€)
```

**scraper-party-register** (Registro de partidos):

```
Pipeline: fetch.rb (descarga) → parse.rb → partidos.csv
```

**scraper-alcaldes** (Lista de alcaldes):

```
Shell script para descargar provincia a provincia
```

### Stack común

| Componente | Tecnología |
|---|---|
| Lenguaje | Ruby 2.6+ |
| HTTP | mechanize |
| Parseo HTML | nokogiri |
| CLI | optimist (argumentos) |
| Patrón | fetch.rb → parse.rb → CSV |
| Output | CSV siempre |

### Ausencias notables

- Sin base de datos (todo termina en CSV)
- Sin tests
- Sin CI/CD
- Sin Docker
- Sin código compartido entre scrapers

### Para monorepo

```
packages/
  scraper-pge/               ← Scraper PGE (Ruby)
  scraper-ccaa/              ← Scraper CCAA (Ruby)
  scraper-electoral/         ← Subvenciones (Ruby)
  scraper-party-register/    ← Registro de partidos (Ruby)
  scraper-alcaldes/          ← Alcaldes (Shell)
  scraper-core/              ← Gemas compartidas (formato CSV, mapeo regiones, etc.)
  scraper-templates/         ← Scaffold para nuevo scraper (fetch.rb + parse.rb base)
```

> [!tip] Clave técnica
> El patrón `fetch.rb → parse.rb → CSV` es increíblemente consistente. Un monorepo podría ofrecer un **scaffold** que genere la estructura base para un nuevo scraper en segundos.

---

## Tema 4: Mapas y datos geoespaciales

### es-atlas

```
package.json: d3-dsv, d3-geo-projection, ndjson-cli, shapefile, topojson
Pipeline (prepublish — bash script de 132 líneas):
  1. Descarga shapefiles del CNIG (líneas límite municipales/provinciales)
  2. Descarga padrones INE
  3. shp2json → ndjson-map → toposimplify → topomerge → topoquantize
  4. Output: es/municipalities.json + es/provinces.json
```

### Para monorepo

```
packages/
  es-atlas/                  ← Generador TopoJSON España
  world-atlas/               ← Generador TopoJSON mundial
  map-utils/                 ← Utilidades de proyección compartidas
```

---

## Blueprint de monorepo integrado

### Estructura propuesta

```
civio-monorepo/
├── package.json              ← Workspaces raíz (npm/pnpm workspaces)
├── turbo.json                ← Turborepo config (build, lint, test)
├── pnpm-workspace.yaml       ← Definición de workspaces
├── .github/workflows/        ← CI/CD centralizado
│   ├── ci.yml                ← Tests + lint para todos los paquetes
│   └── deploy.yml            ← Despliegue condicional por paquete
├── docker-compose.yml        ← Entorno de desarrollo completo
│
├── packages/
│   │
│   ├── presupuesto-core/          ← Django app base (Tema 1)
│   ├── presupuesto-theme-pge/     ← Tema PGE
│   ├── presupuesto-theme-navarra/ ← Tema Navarra
│   ├── presupuesto-loader-ccaa/   ← ETL presupuestos CCAA
│   │
│   ├── graph-templates/           ← Scaffold de visualizaciones (Tema 2)
│   ├── graph-components/          ← Componentes Svelte compartidos
│   ├── graph-utils/               ← Utilidades D3 + colores Civio
│   ├── graph-motivos/             ← Visualización específica
│   │
│   ├── verba-api/                 ← Express + ElasticSearch
│   ├── verba-web/                 ← Vue 2 frontend
│   │
│   ├── scraper-core/              ← Gemas Ruby compartidas (Tema 3)
│   ├── scraper-pge/               ← Scraper PGE
│   ├── scraper-ccaa/              ← Scraper CCAA
│   ├── scraper-electoral/         ← Subvenciones municipales
│   ├── scraper-party-register/    ← Registro partidos
│   │
│   └── es-atlas/                  ← Mapas España
│
├── tools/
│   ├── sync-graphs.sh        ← Script de publicación (hereda de sync.sh)
│   ├── scaffold-scraper.sh   ← Genera nuevo scraper Ruby
│   └── scaffold-graph.sh     ← Genera nueva visualización Svelte
│
└── docs/
    ├── ARCHITECTURE.md        ← Visión general
    └── CONTRIBUTING.md        ← Guía para empezar
```

### Patrones técnicos a estandarizar

| Aspecto | Elección para monorepo | Por qué |
|---|---|---|
| Package manager | **pnpm** | Espacio en disco, strictness, workspaces nativos |
| Task orchestrator | **Turborepo** | Build paralelo, caché, dependencias entre paquetes |
| Node version | **>=22** | Svelte 5 + Vite 7 requieren Node moderno |
| Python version | **3.12** | Django 5+ (actualizar desde 3.2) |
| Ruby version | **3.3** | Actualizar desde 2.6 |
| Linting unificado | **oxlint** (JS/TS/Svelte) + **ruff** (Python) | Ya usado en civio-graphs-public |
| Formateo | **Prettier** (JS/TS/Svelte) | Ya usado |
| Testing JS | **Playwright** + **vitest** | Playwright ya usado para iframes |
| Testing Python | **pytest** | No existe hoy, hay que añadirlo |
| CI/CD | **GitHub Actions** | Ya ecosistema GitHub |
| Docker | **Compose** con perfiles por paquete | Ya usado en verba |

### Lo que NO entra en el monorepo

- [[repos-civio/pi-mono|pi-mono]] — proyecto independiente de IA, sin relación con la misión Civio
- [[repos-civio/datawrapper|datawrapper]] — fork de proyecto externo
- [[repos-civio/lita-slack|lita-slack]] — gema externa mantenida
- [[repos-civio/gulp-boilerplate|gulp-boilerplate]] — obsoleto (Gulp)

### Migración gradual

> [!example] Fases de migración
> 1. **Fase 0** — Setup del monorepo vacío con Turborepo + pnpm + CI
> 2. **Fase 1** — Migrar `civio-graphs-public` (es el stack moderno, más fácil)
> 3. **Fase 2** — Migrar scrapers Ruby a `packages/scraper-*` (patrón consistente)
> 4. **Fase 3** — Migrar `verba` (ya es casi un monorepo con api/ + web/)
> 5. **Fase 4** — Migrar `presupuesto` y themes (el más complejo, requiere refactor Django)

---

## Referencias

- [[repos-civio/presupuesto]] — análisis detallado del repo base
- [[repos-civio/civio-graphs-public]] — análisis del stack Svelte 5
- [[repos-civio/verba]] — análisis del stack Vue + Express + ES
- [[repos-civio/scraper-pge]] — análisis del scraper Ruby
- [[repos-civio/es-atlas]] — análisis del generador de mapas
- [[informe-repos-civio]] — visión general del ecosistema
