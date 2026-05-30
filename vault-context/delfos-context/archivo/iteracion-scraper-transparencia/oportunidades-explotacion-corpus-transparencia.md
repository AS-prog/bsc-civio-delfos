# Oportunidades de explotación — Corpus Portal de Transparencia

> Estado: **diagnóstico**. Análisis del corpus scrapeado, sin implementación.
> Fuente de datos: `data.zip` → `data/raw/transparencia/pages.jsonl` +
> `data/warehouse/transparencia_{pages,sections,links}.parquet`.
> Origen: análisis del commit `640377a`. Fecha: 2026-05-30.
> Relacionado: `pendientes-scraper-transparencia.md` (backlog de fixes).

## Qué es cada artefacto (no confundir)

| Artefacto | Contenido | Rol |
|---|---|---|
| `pages.jsonl` | Metadata + **conteos** por página (no el contenido) | Índice maestro / tabla de hechos |
| `transparencia_pages.parquet` | Mismo nivel: 1 fila por página, conteos | Catálogo |
| `transparencia_links.parquet` | 13.267 enlaces externos (origen → destino) | **Activo principal** |
| `transparencia_sections.parquet` | Headings + texto de secciones | Roto hoy (99% texto vacío) |
| `html/*.html` | 1167 HTML crudos | Respaldo para reprocesar |

**El JSONL NO es el corpus de contenido.** Es el índice. El contenido explotable
está en `links.parquet` (completo) y, tras arreglar el parser, en los HTML crudos.

## Estado del corpus (1167 páginas únicas)

- Registros vs únicos: **2283 / 1167** → duplicación del JSONL (ver P1 del backlog).
- Con título: 100%. Con enlaces externos: 100% (13.267 totales).
- Con secciones declaradas: 66%, pero **texto de sección no vacío: solo 1%**
  (4 de 2744) → el extractor de secciones pierde el cuerpo.
- Con `updated_at`: 4% → frescura casi inexistente.
- **Sesgo de cobertura**: 1043/1167 páginas son `organizacion-empleo`. El resto de
  materias apenas tocadas (económico-presupuestaria 40, altos-cargos 26,
  trámites 25, normativa 19, planificación-estadística 11).

## Destinos de los 13.267 enlaces externos

| Dominio destino | Enlaces | Qué es |
|---|---|---|
| transparencia.gob.es | 6197 | navegación interna/relacionados |
| pap.hacienda.gob.es + pap.minhafp + variantes | ~4271 | **Subvenciones** (Sist. Nac. Publicidad Subvenciones) |
| transparencia.sede.gob.es | 1167 | buscador de la sede (1 por página) |
| boe.es | 1107 | **Normativa** (BOE) |
| infosubvenciones.es | 47 | subvenciones |
| resto (hacienda, igae, seg-social, digital.gob…) | varios | fuentes institucionales |

## Oportunidades de explotación (priorizadas)

### O1 — Grafo de enlaces: subvenciones + normativa  ⭐ recomendado primero
- **Dato**: `links.parquet`, completo y limpio (no depende del parser roto).
- **Producto**: grafo "órgano público → subvenciones (pap.hacienda) / normativa (BOE)".
- **Por qué primero**: es el dataset con mayor valor periodístico (ángulo Civio
  anti-opacidad) y el único explotable HOY sin arreglar nada.
- **Esfuerzo**: bajo. Ya está en parquet; falta modelar nodos/aristas y enriquecer.

### O2 — Grafo de organización del Estado
- **Dato**: 1043 páginas `organizacion-empleo` (estructura orgánica + funciones).
- **Producto**: árbol navegable ministerio → órgano → unidad, con normativa asociada.
- **Limitación**: los headings están (Normativa, Funciones, Estructura orgánica),
  pero el cuerpo textual no (parser). Sirve para estructura, no para texto.

### O3 — Índice maestro / monitor de cambios
- **Dato**: `pages.jsonl` como tabla de hechos.
- **Producto**: dashboard de cobertura + detección de cambios entre corridas
  (diff por `crawled_at`), priorización de re-crawl, deduplicación.
- **Requisito**: resolver P1 (duplicación) para que el diff sea fiable.

### O4 — Corpus textual para NLP/búsqueda
- **Dato**: HTML crudos (`html/*.html`).
- **Bloqueado por**: el parser de secciones (99% texto vacío). Requiere arreglar
  `_sections` o reprocesar el HTML antes de cualquier indexación semántica.
- **Esfuerzo**: medio-alto. Posponer a 2ª iteración.

## Dependencias con el backlog de fixes

- O1 → sin bloqueos.
- O2 → parcial (estructura sí, texto no).
- O3 → requiere **P1** (duplicación JSONL).
- O4 → requiere arreglar el extractor de secciones (parser).

## Camino recomendado

1. **O1** (grafo subvenciones+BOE) — demostrable ya, máximo valor, cero deuda previa.
2. **P1** del backlog, en paralelo, para habilitar **O3**.
3. Arreglar parser de secciones → desbloquea **O4**.
4. Reequilibrar cobertura del crawl (sesgo organizacion-empleo) antes de escalar.
