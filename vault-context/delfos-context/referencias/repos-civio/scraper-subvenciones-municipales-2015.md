---
tags:
  - repo-civio
  - activo
  - scraper
  - elecciones
  - subvenciones
  - ruby
repo: scraper-subvenciones-municipales-2015
url: https://github.com/civio/scraper-subvenciones-municipales-2015
language: Ruby
stars: 6
forks: 2
estado: activo
ultimo-push: 2015-06-02
---

# scraper-subvenciones-municipales-2015

Cálculo de subvenciones recibidas por partidos políticos en las [[Elecciones Municipales 2015]].

## README

> **AVISO:** El código está un poco manga por hombro, se hizo contrareloj y tomando bastantes atajos. Pero los datos de los CSV son correctos.

Artículo relacionado: [[El PP pierde cinco millones de subvención pública para sufragar la campaña electoral]]

### Scripts

- `fetch.rb` — descarga páginas del portal oficial de resultados electorales
- `parse.rb` — extrae datos de municipios y votos por candidatura
- `calculate.rb` — calcula subvención asignada a un partido

### Uso

```bash
ruby calculate.rb 4253  # Para calcular subvención del PP
```

## Contexto

- Scraper + calculadora de subvenciones electorales
- Periodismo de datos: datos oficiales → investigación
- Aviso: código legacy pero datos correctos
