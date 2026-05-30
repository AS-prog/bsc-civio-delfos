ººœ@# Plan de enfoque — Buscador ciudadano de contratación pública (Equipo Delfos · OPP-1a)

> Plan de **estrategia/abordaje**, no de implementación. Sin código todavía: define QUÉ construimos, CÓMO lo afrontamos en un día y en qué orden.

## Contexto

Hackathon Ship for Good (Civio), entrega **sábado 30 may 19:00**, branch `team-delfos`, demo funcional obligatoria. Tras leer el discovery y la presentación en vivo, elegimos atacar **OPP-1a — acceso y descubrimiento de información pública para el ciudadano**.

El porqué: María (Civio) insistió en el **"doble combo"** — que la solución sirva al ciudadano común Y a Civio. Su mayor dolor declarado es que el portal de transparencia es un agregador de enlaces inservible para quien no es periodista, y que el vocabulario técnico (CPV, tipos de contrato) es una barrera invisible (OPP-1a.4). OPP-2 (gestión interna del derecho de acceso) es prioridad alta en el discovery pero depende de la sede con **certificado digital**, que no tenemos → mala demo. OPP-1a usa **datos públicos abiertos** y produce una demo visual de alto impacto.

**Resultado buscado:** un buscador donde una persona sin jerga pueda encontrar contratos públicos por tema o municipio, leerlos en lenguaje claro, y que cada contrato tenga URL propia compartible.

## Principios rectores (innegociables)

1. **Política de IA de Civio.** Permitido: limpieza, normalización y presentación de datos. **Vetado**: generar texto/descripciones con IA, IA como fuente. → La "traducción" de CPV a lenguaje llano usa la **nomenclatura oficial CPV** (tiene descripciones en español), NO texto inventado por un LLM.
2. **Las 16 recomendaciones de [[contractacio-cat-recomendaciones]]** son nuestra checklist de UX, no decoración. Las que aplican directo al MVP: listas/tarjetas en vez de tablas (#8), lenguaje humano sin "etiqueta: dato" (#1, #7), URL única por contrato (#5), orden cronológico inverso (#12), importes redondeados sin céntimos (#9), estado como proceso (#6).
3. **Demo sobre datos REALES**, no mockup (regla del hackathon).

## Concepto del producto (MVP)

Un buscador ciudadano de contratación pública con tres capas:

- **Búsqueda sin jerga**: caja de texto libre + filtros legibles (categoría en lenguaje llano derivada de CPV, ubicación, importe, año, estado). El gancho para el jurado: *"buscá contratos de tu pueblo sin saber qué es un CPV"*.
- **Resultados legibles**: lista de tarjetas (no tabla), cada una en frase natural ("Contrato menor de servicios, adjudicado a … por 123.456 €"), orden por fecha descendente.
- **Detalle compartible**: cada contrato con URL propia, estado mostrado como proceso (anuncio → adjudicación → formalización), enlace al expediente oficial.

## Arquitectura de alto nivel (sobre lo que YA existe)

El equipo ya dejó un scaffold en la rama `feat/docker-python-postgres-env` que reutilizamos:
- `docker-compose.yml` — Postgres 16 + servicio `data` (Python 3.12), puerto 8000 expuesto, healthchecks, red `civic-net`.
- `packages/data/pyproject.toml` — deps `psycopg[binary]`, `polars`, `duckdb`; extra `test` con pytest; smoke tests en `tests/smoke/`.

Flujo propuesto (4 piezas):

```
[1 Ingesta]  dataset Parquet → DuckDB/polars → tabla normalizada en Postgres
[2 Modelo]   tabla `contratos` + tabla/dicc CPV→categoría legible + índices
[3 API]      FastAPI en el servicio `data` (puerto 8000): /search, /contrato/{id}
[4 Frontend] UI ciudadana que consume la API
```

## Decisión de datos (primer paso, BLOQUEANTE)

Fuente candidata de **menor fricción** (a validar antes de comprometer): datasets en **Parquet** ya limpios, p. ej. `github.com/BquantFinance/licitaciones-espana` (Releases con ZIPs; `ted.zip` ~217 MB para MVP rápido, `nacional.zip` ~1,34 GB para cobertura). Parquet carga directo en DuckDB sin parsear el XML CODICE de PLACSP.

- **Camino A (recomendado):** subconjunto Parquet (un año o el ZIP TED) → DuckDB → Postgres.
- **Plan B si el dataset falla:** API de Cataluña (Socrata, libre) o BDNS subvenciones (`bdns-fetch`) filtrado a un organismo.
- **Evitar:** parsear XML CODICE de PLACSP directo (consume el día).

> ⚠️ Estas fuentes vienen de investigación web sin verificar descarga. **Tarea 0 del día = spike de 45 min**: descargar, abrir el Parquet, confirmar columnas (CPV, importe, adjudicatario, órgano, fechas, estado). Si no carga limpio en 45 min → Plan B. No se construye nada encima hasta pasar este gate.

## Cómo lo afrontamos — fases del día (sáb 30, ~10:00–17:00 + margen)

1. **Gate de datos (45 min, todo el equipo).** Spike de la fuente. Confirmar columnas reales. Decidir A o B. Sin esto no se sigue.
2. **Arranque en paralelo** una vez pasado el gate, en tracks:
   - *Datos/Backend*: ingesta del subconjunto → Postgres, modelo `contratos` + diccionario CPV→categoría, índices (cpv, órgano, adjudicatario, fecha). Smoke test de carga.
   - *API*: FastAPI sobre el servicio `data` — endpoint de búsqueda (texto + filtros) y de detalle. Contrato de API acordado temprano para desbloquear al front.
   - *Frontend/UX*: UI ciudadana aplicando la checklist de contractacio.cat. Empieza con datos mock contra el contrato de API, luego enchufa el real.
3. **Integración** (media tarde): front contra API real, datos reales.
4. **Pulido + guion de demo** (última hora): un flujo end-to-end impecable > muchas features a medias. README de entrega (requisito) y guion de 3 min.

## Alcance

| Entra en el MVP | Queda fuera (decir en demo si se pregunta) |
|---|---|
| Una fuente de datos (contratos; subvenciones solo si sobra tiempo) | Cobertura nacional + autonómica + local completa |
| Búsqueda texto + filtros legibles | Cruce contratos × subvenciones por adjudicatario |
| Traducción CPV→categoría con nomenclatura oficial | Monitorización de cambios (OPP-1b) |
| Tarjetas + detalle con URL propia | Cuentas de usuario, alertas, export |
| Estado como proceso | Multi-idioma |

## Riesgos y mitigación

- **Datos no cargan/formato engorroso** → gate bloqueante + Plan B definido.
- **Volumen (1,34 GB)** → empezar con subconjunto (TED 217 MB o filtrar un año).
- **Sobre-scope** → un solo flujo pulido; la tabla de "queda fuera" es explícita.
- **Cruzar la línea de la política de IA** → CPV se traduce con tabla oficial, no con LLM.
- **Frontend desacoplado consume tiempo** → contrato de API temprano; el front arranca con mock.

## Verificación / criterio de demo (3 min)

Flujo único end-to-end, sobre datos reales: *abrir la web → buscar por un término ciudadano (p. ej. un municipio o "comida escolar") → ver resultados legibles ordenados por fecha → abrir un contrato → copiar su URL y reabrirla*. Si ese camino corre sin romperse, la demo está lista. README permite arrancar el proyecto siguiendo sus pasos (`docker compose up` + ingesta + front).

## Decisiones abiertas (a cerrar al inicio del día, no bloquean este plan)

1. **Stack de frontend**: opciones — (a) FastAPI + plantillas server-side (menos piezas, todo Python), (b) front React generado con **Lovable** (tienen tokens del evento, acelera UI bonita) consumiendo la API, (c) Datasette (UI instantánea pero poco "ciudadana"). Recomendación inicial: (b) si priorizamos impacto visual, (a) si priorizamos simplicidad e integración.
2. **Eje de datos**: contratos (recomendado, más visual) vs subvenciones vs ambos.
