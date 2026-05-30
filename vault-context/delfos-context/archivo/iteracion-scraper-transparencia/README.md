# Iteración — Scraper Portal de Transparencia

Centraliza toda la información de la iteración del scraper de **Publicidad Activa**
de `transparencia.gob.es` (rama `feat/scraper-transparencia`, commit base `640377a`).

## Contexto

Scraper en `packages/data/scrapers/transparencia/` que descubre (BFS) y extrae
páginas de Publicidad Activa, persistiendo a JSONL + Parquet. Esta carpeta agrupa
el plan, el resultado de las corridas y el diagnóstico posterior del corpus.

## Documentos (orden de lectura sugerido)

| # | Documento | Qué contiene | Estado |
|---|---|---|---|
| 1 | [scraper-transparencia.md](scraper-transparencia.md) | Plan + implementación + diagramas Mermaid (arquitectura y secuencia) | Referencia |
| 2 | [informe-ejecucion-scraper-transparencia.md](informe-ejecucion-scraper-transparencia.md) | Resultado de las corridas y descripción de los artefactos generados | Referencia |
| 3 | [pendientes-scraper-transparencia.md](pendientes-scraper-transparencia.md) | Backlog de fixes priorizados (P1–P6) detectados en la revisión | Diagnóstico |
| 4 | [oportunidades-explotacion-corpus-transparencia.md](oportunidades-explotacion-corpus-transparencia.md) | Análisis del corpus y oportunidades de explotación (O1–O4) | Diagnóstico |
| 5 | [instrucciones-mcp-transparencia.md](instrucciones-mcp-transparencia.md) | Especificación funcional del MCP (corpus → servidor consumible) | Especificación |

## Plan de ejecución (corpus → MCP)

El plan original [frolicking-riding-pascal.md](frolicking-riding-pascal.md) se dividió en dos
planes encadenados por dependencia (la base debe estar lista antes del MCP):

| Orden | Documento | Qué entrega |
|---|---|---|
| 1 | [plan-base-datos-transparencia.md](plan-base-datos-transparencia.md) | Limpieza del corpus + ETL Parquet → Postgres. Salida: base `civio` poblada y consultable (Fases 0–1) |
| 2 | [plan-mcp-transparencia.md](plan-mcp-transparencia.md) | Capa SQL + marts + servidor MCP + integración con agente (Fases 2–4) |

## Estado de la iteración

- **Código**: implementado y commiteado (`640377a`), 18 tests sobre `parse`.
- **Datos**: corpus de 1167 páginas únicas (en `data.zip`, no versionado en git).
- **Diagnóstico**: completo. 2 problemas de alta prioridad y 4 oportunidades de uso.

## Próximos pasos (resumen)

1. **P1** (backlog): JSONL duplica en append → corrupción silenciosa de datos.
2. **O1** (oportunidades): grafo de enlaces subvenciones+BOE → explotable HOY.
3. Arreglar extractor de secciones (99% texto vacío) → desbloquea corpus textual.

> Detalle completo de prioridades y dependencias en los documentos 3 y 4.
