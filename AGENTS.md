# AGENTS.md — bsc-civio-delfos

## Descripción del proyecto

Este repositorio contiene un análisis completo del ecosistema de repositorios de la organización [Civio](https://civio.es) en GitHub, con el objetivo de preparar una hackathon alineada con su stack tecnológico actual.

Cubre:
- Inventario y análisis de los **60 repositorios públicos** de Civio
- **Stack tecnológico activo en 2026**: Svelte 5 + Vite 7 + D3.js, Vue.js + Express + ElasticSearch, Ruby scrapers
- **Mapa visual de dominios**: transparencia presupuestaria, visualizaciones periodísticas, scraping/datos
- **Blueprint de monorepo** con migración gradual por capas

## Estructura del vault

```
vault-context/delfos-context/
├── .obsidian/                          ← Configuración del vault de Obsidian
├── referencias/
│   ├── informe-repos-civio.md          ← Informe general con stack 2026
│   ├── analisis-monorepo-civio.md      ← Blueprint de monorepo por temas
│   ├── mapa-dominios-civio.canvas      ← Mapa visual (JSON Canvas)
│   └── repos-civio/                    ← Una nota por cada repositorio de Civio
│       ├── presupuesto.md              ← DVMI core (Django + jQuery + D3)
│       ├── civio-graphs-public.md      ← Nuevo estándar (Svelte 5 + Vite 7 + D3)
│       ├── verba.md                    ← Buscador RTVE (Vue + Express + ES)
│       ├── pi-mono.md                  ← Outlier IA
│       ├── scraper-pge.md              ← Scraper Ruby
│       ├── presupuesto-navarra.md      ← Adaptación territorial
│       └── ...                         ← 54 notas adicionales
```

## Documentos clave

| Archivo | Propósito |
|---|---|
| `referencias/informe-repos-civio.md` | Visión general del ecosistema y stack recomendado |
| `referencias/analisis-monorepo-civio.md` | Arquitectura interna de cada dominio y blueprint de monorepo |
| `referencias/mapa-dominios-civio.canvas` | Mapa visual de dominios (abrir en Obsidian) |
| `referencias/repos-civio/*.md` | Nota individual por repositorio con README, stack y contexto |

## Stack Civio 2026 (prioridad para hackathon)

| Propósito | Stack | Referencia |
|---|---|---|
| Visualización interactiva | **Svelte 5 + Vite 7 + D3.js** | `civio-graphs-public` |
| API / backend ligero | **Node.js / Express** | `verba` |
| Búsqueda textual | **ElasticSearch 7** | `verba` |
| Scrapers | **Ruby** (fetch → parse → CSV) | `scraper-*` |
| Mapas España | **TopoJSON + d3-composite-projections** | `es-atlas` |

## Convenciones

- **Idioma**: Español
- **Commits**: Conventional Commits en español (`feat:`, `fix:`, `refactor:`, `chore:`)
- **Formato notas**: Obsidian Flavored Markdown con frontmatter (tags, estado, lenguaje, repo)
- **Canvas**: JSON Canvas spec 1.0
- **Tags en notas repos-civio**: `repo-civio`, estado (`activo`/`archivado`), tema, lenguaje

## Comandos útiles

```bash
# Actualizar listado de repos de Civio
gh repo list civio --limit 100 --json name,description,url,primaryLanguage,stargazerCount,forkCount,isArchived,isPrivate,pushedAt,homepageUrl

# Leer README de un repo
gh api -H 'Accept: application/vnd.github.raw' repos/civio/<repo>/readme
```
