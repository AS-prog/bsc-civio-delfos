---
tags:
  - repo-civio
  - archivado
  - contratos
  - transparencia
  - ruby
repo: quiencobralaobra
url: https://github.com/civio/quiencobralaobra
language: HTML
stars: 7
forks: 0
estado: archivado
ultimo-push: 2021-01-07
---

# quiencobralaobra

"¿Quién cobra la obra?" — Investigación sobre contratos públicos y adjudicaciones.

## README

### Stack

- Ruby 2.5.1
- Rails 4.2.10
- PostgreSQL 9.3+

### Instalación

```bash
bundle install
npm install
rake db:create
rake db:seed
rake data:import_awards[db/awards.csv]
rake data:import_utes
```

### Funcionalidad

- Carga de datos de contratos públicos
- Mapeo de UTE (Uniones Temporales de Empresas)
- Visualización de adjudicatarios

## Contexto

- Proyecto archivado de investigación sobre contratación pública
- Precedente de [[quienmanda]] pero enfocado en contratos
- Datos de adjudicaciones y empresas
