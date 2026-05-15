---
tags:
  - repo-civio
  - archivado
  - visualizacion
  - redes
  - ruby
  - d3js
repo: onodo
url: https://github.com/civio/onodo
language: SCSS
stars: 25
forks: 13
estado: archivado
ultimo-push: 2024-10-30
homepage: http://onodo.org
---

# onodo

Plataforma de análisis y visualización de redes. Proyecto cerrado oficialmente en julio 2024.

> Onodo development is discontinued! The project is now closed.

## README

### Stack

- [[Ruby]] 2.4.3
- [[Rails]] 4.2.x
- [[Backbone.js]] 1.2.2
- [[D3.js]] 4.x
- [[Handsontable]]
- [[Webpack]] 2.x
- [[PostgreSQL]] 9.x
- [[Imagemagick]] 6.x
- [[Docker]] para desarrollo

### Análisis de redes

Módulo separado en [[Python]] usando [[igraph]]:

```bash
pip install python-igraph
```

### Desarrollo

```bash
bundle install
npm install
bundle exec rake db:create db:migrate db:seed
bundle exec foreman start -f Procfile.dev
```

Con Docker:

```bash
docker compose build
docker compose run --rm onodo bundle exec rake db:create db:migrate db:seed
docker compose up
```

## Contexto

- Proyecto cerrado pero con legado técnico importante
- Anuncio de cierre: [[Adiós a Onodo]]
- Precedente de herramientas de visualización de redes de Civio
