---
tags:
  - repo-civio
  - activo
  - scraper
  - presupuestos
  - ccaa
  - ruby
repo: scraper-ccaa-budget-summaries
url: https://github.com/civio/scraper-ccaa-budget-summaries
language: Ruby
stars: 2
forks: 0
estado: activo
ultimo-push: 2025-12-05
---

# scraper-ccaa-budget-summaries

Scraper para descargar y preparar resúmenes presupuestarios de todas las [[Comunidades Autónomas]] desde la web del [[Ministerio de Hacienda]].

## README

### Datos presupuestarios

Descarga desde la web del Ministerio de Hacienda, usando el scraper:

```bash
ruby fetch.rb 2010 2021
ruby parse.rb staging_budget | sort > budget.sorted.csv
```

### Datos de ejecución

Para datos de ejecución presupuestaria (liquidaciones):

```bash
ruby fetch.rb --actual 2010 2019
ruby parse.rb staging_actual | sort > actual.sorted.csv
```

### Datos de población

Obtenidos del [[INE]]. Necesarios para normalizar los datos per cápita.

### Actualización de DVMI

Para integrar nuevos datos en [[Dónde van mis impuestos]]:
1. Añadir datos de población a `static/data/population_YYYY.csv`
2. Actualizar archivo de datos presupuestarios `static/data/budget_data_YYYY.csv`
3. Modificar `availableYears` en `static/javascripts/ccaa.js`
4. Actualizar texto y configuración en `templates/ccaa/index.html`

## Contexto

- Alimenta la capa autonómica de [[presupuesto]]
- Ruby con scraper secuencial (fetch → parse)
- Incluye datos de presupuesto, ejecución y población
