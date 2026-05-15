---
tags:
  - repo-civio
  - archivado
  - covid
  - datos
  - ruby
  - scraper
repo: covid-vaccination-spain
url: https://github.com/civio/covid-vaccination-spain
language: Ruby
stars: 24
forks: 3
estado: archivado
ultimo-push: 2023-04-11
---

# covid-vaccination-spain

Seguimiento de la vacunación contra la [[COVID-19]] en España. Extraía datos de los informes PDF diarios del [[Ministerio de Sanidad]].

## README

```bash
./fetch.sh          # Descargar informe PDF del día y convertir a texto
ruby parse.rb > data.csv  # Extraer datos estructurados
```

Los datos extraídos están disponibles en `data.csv` del repositorio.

## Contexto

- Proyecto de respuesta rápida durante la pandemia
- Pipeline simple: fetch → parse → CSV
- Datos ya extraídos disponibles como dataset
- Archivado tras finalizar la pandemia
