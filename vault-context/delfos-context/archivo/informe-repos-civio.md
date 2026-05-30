---
tags:
  - civio
  - informe
  - repositorios
  - hackathon
  - stack
title: "Informe de repositorios de Civio"
aliases:
  - Informe Civio
  - Stack Civio 2026
---

# Informe de repositorios de Civio

## Resumen ejecutivo

La organización `civio` gira alrededor de tres bloques claros: visualización de presupuestos públicos, periodismo de datos interactivo y scrapers/ETL para capturar datos oficiales. En el listado público actual hay **61 repositorios**, de los cuales **35 están archivados** y **26 siguen activos**.

El patrón dominante es la familia `presupuesto-*`: representa la mayor parte del ecosistema y agrupa la aplicación base, adaptaciones territoriales y piezas auxiliares. En paralelo, Civio mantiene una línea fuerte de visualizaciones editoriales y proyectos de investigación como `verba`, `quienmanda` y `civio-graphs-public`.

> [!info] Notas detalladas por repositorio
> Cada repositorio de Civio tiene su propia nota con README completo en [[repos-civio/]].

## Metodología

Este informe se basa en:

1. El inventario público de repositorios de la organización (60 repos total).
2. Metadatos de GitHub: nombre, descripción, lenguaje principal, estrellas, estado archivado y fecha de actividad.
3. Lectura completa de los README de **todos los repositorios** para confirmar el foco funcional y tecnologías empleadas.
4. Análisis de actividad reciente: los repos con push en 2025-2026 definen el *stack* moderno de Civio.

## Foto general del ecosistema

### Distribución por estado

- Repositorios totales: **61**
- Activos: **26**
- Archivados: **35**

### Distribución por lenguaje principal

- Python: **21**
- HTML: **19**
- Ruby: **7**
- JavaScript: **5**
- Shell: **3**
- SCSS: **2**
- Otros: TypeScript, Svelte, CSS y PHP en menor medida

### Concentración por nombre

El prefijo `presupuesto` domina claramente el catálogo: **38 repositorios** empiezan por ese nombre. Esto sugiere un producto base reutilizable que se ha ido adaptando a diferentes administraciones y momentos políticos.

## Stack tecnológico activo en 2026

El ecosistema de Civio convive con tecnologías de varias épocas. Analizando los repos con actividad reciente (*push* en 2025-2026) se distinguen claramente tres capas.

### Capa moderna: el nuevo estándar de visualización

El repo [[repos-civio/civio-graphs-public]] marca la dirección tecnológica actual de Civio para nuevas visualizaciones:

| Tecnología | Versión | Uso |
|---|---|---|
| **Svelte** | 5 | *Framework* frontend reactivo |
| **Vite** | 7 | *Bundler* y *dev server* |
| **D3.js** | — | Visualización de datos y SVG |

Este *stack* permite crear visualizaciones interactivas modulares con alto rendimiento. Las tres piezas publicadas en 2026 (aislamiento en prisiones) demuestran que es el formato preferido para nuevas investigaciones.

### Capa de aplicaciones web

| Proyecto | Stack | Estado |
|---|---|---|
| [[repos-civio/presupuesto|presupuesto]] (DVMI) | JavaScript + Django (*legacy*) | Activo, base histórica |
| [[repos-civio/verba|verba]] | Vue.js + Express/Node.js + ElasticSearch 7 | Activo, mantenimiento |
| Adaptaciones `presupuesto-*` | HTML/Python con DVMI base | Mixto activo/archivado |

El núcleo [[repos-civio/presupuesto|presupuesto]] usa un *stack* Django clásico. [[repos-civio/verba|verba]] representa una evolución moderna con Vue.js en *frontend* y Express en *backend*, con ElasticSearch como motor de búsqueda.

### Capa de datos: *scrapers* y *pipelines*

Todos los *scrapers* activos están escritos en **Ruby**, siguiendo un patrón secuencial uniforme:

```mermaid
graph LR
    A[fetch.rb] --> B[parse.rb]
    B --> C[CSV estructurado]
```

Este patrón se repite en `scraper-pge`, `scraper-ccaa-budget-summaries`, `scraper-subvenciones-municipales-2015` y `scraper-party-register`. La simplicidad del *pipeline* favorece la auditabilidad y reproducción de los datos.

### Capa auxiliar: mapas y datos geoespaciales

- [[repos-civio/es-atlas|es-atlas]] y [[repos-civio/world-atlas|world-atlas]] generan archivos **TopoJSON** desde fuentes oficiales (IGN, Natural Earth).
- Compatibles con **D3.js** y **d3-composite-projections** para mapas de España.

### *Outlier*: pi-mono

[[repos-civio/pi-mono|pi-mono]] (TypeScript, activo en mayo 2026) es un monorepo de herramientas para agentes de IA con OpenAI/Anthropic/Google, agente de codificación CLI, y despliegue vLLM. No pertenece al ADN Civio pero muestra exploración en IA.

### Resumen del *stack* recomendado para 2026

| Propósito | Stack recomendado | Referencia Civio |
|---|---|---|
| Visualización interactiva | **Svelte 5 + Vite + D3** | [[repos-civio/civio-graphs-public]] |
| API / *backend* ligero | **Node.js / Express** | [[repos-civio/verba]] |
| Búsqueda textual | **ElasticSearch** | [[repos-civio/verba]] |
| *Scrapers* | **Ruby** (patrón fetch→parse) | `scraper-*` |
| Mapas | **TopoJSON + D3** | [[repos-civio/es-atlas]] |
| Datos geoespaciales España | **d3-composite-projections** | [[repos-civio/es-atlas]] |

## Qué hace Civio, por temas

### 1. Transparencia presupuestaria

Es la línea más fuerte y reconocible de la organización.

Repositorios relevantes:

- [[repos-civio/presupuesto|presupuesto]]: aplicación principal de visualización de presupuestos, con foco en ingresos, gastos, clasificaciones presupuestarias y evolución temporal.
- [[repos-civio/presupuesto-navarra|presupuesto-navarra]], [[repos-civio/presupuesto-vitoriagasteiz|presupuesto-vitoriagasteiz]], [[repos-civio/presupuesto-castillalamancha|presupuesto-castillalamancha]], [[repos-civio/presupuesto-elprat|presupuesto-elprat]], [[repos-civio/presupuesto-bilbao|presupuesto-bilbao]], [[repos-civio/presupuesto-madrid|presupuesto-madrid]], [[repos-civio/presupuesto-menorca|presupuesto-menorca]], [[repos-civio/presupuesto-barcelona|presupuesto-barcelona]], [[repos-civio/presupuesto-pge|presupuesto-pge]], etc.: adaptaciones de la misma idea a distintas administraciones.
- [[repos-civio/scraper-pge|scraper-pge]]: *parser* de Presupuestos Generales del Estado.
- [[repos-civio/scraper-ccaa-budget-summaries|scraper-ccaa-budget-summaries]]: descarga y preparación de resúmenes presupuestarios autonómicos.

> [!quote] Lectura de fondo
> Civio no solo publica visualizaciones, sino que construye una cadena completa de captura, normalización y presentación de datos presupuestarios.

### 2. Visualizaciones e investigación periodística

Aquí aparece la capa más editorial y narrativa.

Repositorios relevantes:

- [[repos-civio/civio-graphs-public|civio-graphs-public]]: repertorio moderno de visualizaciones abiertas para investigaciones periodísticas. *Charts* interactivos recientes sobre aislamiento en prisiones.
- [[repos-civio/verba|verba]]: explora los Telediarios de RTVE desde 2014.
- [[repos-civio/quienmanda|quienmanda]]: mapa de relaciones de poder en España.
- [[repos-civio/civio-graphs-lib|civio-graphs-lib]] y [[repos-civio/civio-graphs-boilerplate|civio-graphs-boilerplate]]: reutilización técnica para producir gráfos y visualizaciones.
- [[repos-civio/civio-informe-2016|civio-informe-2016]]: memoria o informe de gestión.

> [!quote] Lectura de fondo
> La organización usa visualización interactiva como herramienta periodística, no como soporte secundario.

### 3. *Scraping* y *pipelines* de datos

La infraestructura de datos es una parte estructural del proyecto.

Repositorios relevantes:

- [[repos-civio/scraper-pge|scraper-pge]]
- [[repos-civio/scraper-subvenciones-municipales-2015|scraper-subvenciones-municipales-2015]]
- [[repos-civio/scraper-party-register|scraper-party-register]]
- [[repos-civio/scraper-alcaldes|scraper-alcaldes]]

> [!quote] Lectura de fondo
> Civio convierte fuentes públicas dispersas en *datasets* explotables para investigación y visualización.

### 4. Proyectos históricos, experimentales o de soporte

Varios repositorios reflejan etapas anteriores, prototipos o dependencias de apoyo:

- [[repos-civio/onodo|onodo]]: red social/visual de relaciones; hoy aparece archivado y cerrado.
- [[repos-civio/medicamentalia|medicamentalia]]: investigación periodística sobre acceso a medicamentos.
- [[repos-civio/covid-vaccination-spain|covid-vaccination-spain]]: seguimiento de vacunación.
- [[repos-civio/lita-slack|lita-slack]]: adaptador de Slack para Lita.
- [[repos-civio/datawrapper|datawrapper]], [[repos-civio/gulp-boilerplate|gulp-boilerplate]], [[repos-civio/es-atlas|es-atlas]], [[repos-civio/world-atlas|world-atlas]], [[repos-civio/pi-mono|pi-mono]]: piezas de soporte, experimentación o reutilización externa. `pi-mono` es un *outlier* moderno dentro del ecosistema.

> [!quote] Lectura de fondo
> La organización ha acumulado una base técnica heterogénea a lo largo del tiempo, con varios proyectos cerrados pero valiosos para entender su evolución.

## Repositorios activos en 2026 (ordenados por actividad reciente)

| Repositorio | Último *push* | Lenguaje | *Stack* real | Qué aporta |
|---|---|---|---|---|
| [[repos-civio/pi-mono\|pi-mono]] | May 2026 | TypeScript | TypeScript monorepo | Herramientas IA (*outlier*) |
| [[repos-civio/presupuesto-navarra\|presupuesto-navarra]] | May 2026 | HTML | DVMI | Adaptación territorial presupuestaria |
| [[repos-civio/presupuesto-vitoriagasteiz\|presupuesto-vitoriagasteiz]] | Abr 2026 | HTML | DVMI | Adaptación municipal |
| [[repos-civio/presupuesto\|presupuesto]] | Abr 2026 | JavaScript | Django + JS clásico | Aplicación principal de visualización presupuestaria |
| [[repos-civio/presupuesto-castillalamancha\|presupuesto-castillalamancha]] | Mar 2026 | HTML | DVMI | Adaptación autonómica |
| **[[repos-civio/civio-graphs-public\|civio-graphs-public]]** | **Mar 2026** | **Svelte** | **Svelte 5 + Vite 7 + D3** | **Nuevo estándar de visualización** |
| [[repos-civio/presupuesto-pge\|presupuesto-pge]] | Ene 2026 | HTML | DVMI | Adaptación PGE |
| [[repos-civio/scraper-ccaa-budget-summaries\|scraper-ccaa-budget-summaries]] | Dic 2025 | Ruby | Ruby + CSV *pipeline* | Resúmenes presupuestarios autonómicos |
| [[repos-civio/presupuesto-elprat\|presupuesto-elprat]] | Nov 2025 | HTML | DVMI | Adaptación municipal |
| [[repos-civio/presupuesto-polinya\|presupuesto-polinya]] | Oct 2025 | HTML | DVMI | Adaptación municipal |
| [[repos-civio/presupuesto-eibar\|presupuesto-eibar]] | Sep 2025 | Python | DVMI | Adaptación municipal |
| [[repos-civio/presupuesto-madrid\|presupuesto-madrid]] | Ago 2025 | JavaScript | DVMI | Adaptación municipal |
| [[repos-civio/verba\|verba]] | Jul 2025 | HTML | Vue.js + Express + ES7 | Buscador/visor de telediarios RTVE |
| [[repos-civio/presupuesto-menorca\|presupuesto-menorca]] | Abr 2025 | HTML | DVMI | Adaptación insular |
| [[repos-civio/presupuesto-larioja\|presupuesto-larioja]] | Abr 2025 | Python | DVMI | Adaptación autonómica |

### Repositorios archivados de referencia

| Repositorio | Lenguaje | Qué aporta |
|---|---|---|
| [[repos-civio/quienmanda\|quienmanda]] | HTML | Mapa de poder y relaciones (40 estrellas, el más popular) |
| [[repos-civio/onodo\|onodo]] | SCSS | Visualización de redes; proyecto cerrado oficialmente |
| [[repos-civio/medicamentalia\|medicamentalia]] | HTML | Investigación periodística internacional |
| [[repos-civio/covid-vaccination-spain\|covid-vaccination-spain]] | Ruby | Seguimiento de vacunación COVID |
| [[repos-civio/scraper-party-register\|scraper-party-register]] | Ruby | *Scraping* de registro de partidos |

## Lectura estratégica para *hackathon*: por qué *stack* apostar

Si el objetivo es preparar ideas aprovechables para una *hackathon*, el *stack* de Civio en 2026 sugiere prioridades claras:

### *Stack* prioritario (lo que Civio usa ahora)

| Tecnología | Cuándo usarla | Referencia |
|---|---|---|
| **Svelte 5 + Vite** | Visualizaciones interactivas nuevas | [[repos-civio/civio-graphs-public\|civio-graphs-public]] |
| **D3.js** | Gráficos de datos a medida | [[repos-civio/civio-graphs-public\|civio-graphs-public]] |
| **Node.js / Express** | APIs ligeras para servir datos | [[repos-civio/verba\|verba]] |
| **ElasticSearch** | Búsqueda sobre corpus textuales | [[repos-civio/verba\|verba]] |
| **Ruby** | *Scrapers* y *pipelines* ETL | `scraper-*` |
| **Python** | Análisis de datos, NLP, ML | Ecosistema general |

### *Stack* tolerable (convive pero no es el futuro)

- **Django** → el presupuesto base lo usa, pero no hay nuevas piezas en Django
- **Vue.js 2** → verba lo usa, pero `civio-graphs-public` migró a Svelte
- **Webpack** → reemplazado por Vite en el *stack* moderno

### *Stack* a evitar (archivado o muerto)

- **Ruby on Rails** → onodo, quienmanda (archivados)
- **Backbone.js** → onodo (archivado)
- **SCSS** → onodo (archivado)
- **Gulp** → gulp-boilerplate (sin actividad desde 2019)

### Direcciones con ventaja para *hackathon*

> [!tip] Idea 1 — Visualización cívica con Svelte 5 + D3
> Replica el patrón de [[repos-civio/civio-graphs-public]] pero con *datasets* diferentes (presupuestos locales, indicadores sociales, series históricas). Es el *stack* donde Civio está invirtiendo ahora.

> [!tip] Idea 2 — *Scraping* Ruby → API Express
> Tomar el *pipeline* clásico de Civio (fetch → parse → CSV) y envolverlo en una API Express para servir los datos a visualizaciones modernas. Combinarías la capa de datos probada con la capa de presentación nueva.

> [!tip] Idea 3 — ElasticSearch + visualización
> Como [[repos-civio/verba|verba]] pero sobre otros corpus (boletines oficiales, datos judiciales, contratación pública). El *stack* ya está validado por Civio.

> [!tip] Idea 4 — Extensión de presupuesto con Svelte
> El núcleo [[repos-civio/presupuesto|presupuesto]] sigue en Django clásico; una interfaz Svelte moderna sobre los mismos datos sería una mejora clara.

## Conclusiones

Civio es una organización de periodismo de datos y tecnología cívica con una especialización muy marcada en transparencia presupuestaria. Su *repo* principal y sus derivaciones muestran un modelo repetido: capturar datos públicos, limpiarlos, estructurarlos y publicarlos como experiencias comprensibles para no expertos.

> [!important] Para la *hackathon* de 2026
> El *stack* que maximiza la alineación con Civio es **Svelte 5 + Vite + D3** para visualizaciones, con **Ruby o Python** para la capa de datos. El movimiento tecnológico más claro de Civio en el último año es la adopción de Svelte 5 en `civio-graphs-public`, abandonando progresivamente herramientas *legacy* como Webpack, Gulp y Backbone.js.

## Referencia de comandos utilizados

```bash
# Listar repositorios
gh repo list civio --limit 100 \
  --json name,description,url,primaryLanguage,stargazerCount,forkCount,isArchived,isPrivate,pushedAt,homepageUrl

# Leer README de un repositorio
gh api -H 'Accept: application/vnd.github.raw' repos/civio/<repo>/readme
```
