---
tags:
  - repo-civio
  - activo
  - datos
  - mapas
  - espana
  - topojson
repo: es-atlas
url: https://github.com/civio/es-atlas
language: Shell
stars: 2
forks: 0
estado: activo
ultimo-push: 2016-12-27
---

# es-atlas

Generación de archivos [[TopoJSON]] de España desde datos del [[Instituto Geográfico Nacional]].

## README

> Generates TopoJSON files from the Spanish National Geographic Institute's National Reference Geographic Equipment vector data.

### Formatos

- `es/municipalities.json` — municipios, provincias, comunidades autónomas y nación
- `es/provinces.json` — mismo contenido sin municipios (menor tamaño)

Cada objeto geoespacial incluye su identificador del [[INE]].

### Proyección

Recomienda usar [[d3-composite-projections]] (ConicConformalSpain) para que Canarias aparezca cerca de la península.

## Contexto

- Datos geoespaciales de España listos para usar con [[D3.js]]
- Creado por [[Martín González]]
- Útil para visualizaciones geográficas de datos españoles
