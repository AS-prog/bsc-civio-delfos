---
tags:
  - repo-civio
  - activo
  - scraper
  - presupuestos
  - ruby
repo: scraper-pge
url: https://github.com/civio/scraper-pge
language: Ruby
stars: 25
forks: 4
estado: activo
ultimo-push: 2023-04-12
---

# scraper-pge

Parser de los [[Presupuestos Generales del Estado]]. Extrae y estructura los datos presupuestarios desde la web del [[Ministerio de Hacienda]].

## README

### Funcionamiento

1. **Descarga**: Obtiene los presupuestos desde la web del Ministerio en formato HTML
2. **Parseo**: Extrae toda la información de gastos usando la estructura de tomos y artículos
3. **Resumen**: Genera cifras clave y verifica validez contra cifras oficiales

### Uso

```bash
rake "budget:parse[2014]"   # Extraer datos de gastos
rake "budget:summary[2014]" # Generar resumen con cifras clave
```

### Estructura de ficheros

Los presupuestos descargados consisten en ficheros .HTM con nombres crípticos. La lógica de parsing está en `lib/budget.rb`.

## Contexto

- Pieza clave de la cadena de datos de [[Civio]]
- Los datos extraídos alimentan [[presupuesto]] y sus adaptaciones territoriales
- Ruby con tareas Rake
