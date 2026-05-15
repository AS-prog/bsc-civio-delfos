---
tags:
  - repo-civio
  - activo
  - periodismo
  - rtvе
  - busqueda
repo: verba
url: https://github.com/civio/verba
language: HTML
stars: 37
forks: 5
estado: activo
ultimo-push: 2025-07-26
homepage: https://verba.civio.es
---

# verba

Explorador y buscador de Telediarios de [[RTVE]] desde 2014. Permite consultar el contenido de los informativos de TVE mediante búsqueda por texto.

## README

### Stack técnico

- **Backend**: [[ElasticSearch]] 7 + API en [[Node.js]]/[[Express]]
- **Frontend**: [[Vue.js]]
- **Corpus**: Subtítulos originales (VTT) con metadatos de RTVE (JSON). Descargable desde verba.civio.es

### Despliegue

- Servidor: `midas` en `/var/www/verba.civio.es/`
- Frontend servido por Apache, API como servicio systemd
- API: `verba.civio.es/api`

### Datos

El corpus completo está disponible para descarga:
- `corpus_raw.tar.gz` - Subtítulos originales VTT + metadatos
- `corpus_cooked.tar.gz` - Subtítulos segmentados en frases con `syntok`

## Contexto para hackathon

Proyecto de periodismo de datos con gran potencial para:
- Análisis de narrativas y sesgos en medios
- Detección de temas y evolución de cobertura
- Procesamiento de NLP sobre corpus de noticias
