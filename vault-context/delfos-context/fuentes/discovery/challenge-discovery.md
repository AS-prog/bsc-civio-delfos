**Este documento es un material de trabajo preparado específicamente para los equipos participantes en el hackathon. Recoge contexto interno del equipo de Civio para facilitar el trabajo durante la jornada.**

> **Fuentes:** Transcripción de reunión de discovery con equipo Civio · Política de uso de IA de Civio (civio.es/nosotros/uso-IA, marzo 2026) · ["La larga travesía de más de un año para saber quiénes son los asesores en los ministerios"](https://civio.es/poder/2025/05/20/la-larga-travesia-de-mas-de-un-ano-para-saber-quienes-son-los-asesores-de-los-ministros/) (Civio, mayo 2025) · ["Las excusas de la mayoría de ministerios para ocultar a sus asesores"](https://civio.es/poder/2025/06/11/las-excusas-de-la-mayoria-de-ministerios-para-ocultar-a-sus-asesores/) (Civio, junio 2025)

---

# ⚠️ Restricciones organizativas — Política de IA de Civio

Estas restricciones son públicas, deliberadas y no negociables. Los equipos de la hackathon deben leerlas antes de proponer cualquier solución.

**Vetado:** generación de texto periodístico, alegaciones, recursos, enmiendas o cualquier documento legal; fuente de información en investigaciones; creación de imágenes/ilustraciones; comunicación directa con lectores o socios.

**Permitido:** conversión de formatos y limpieza de datos (PDF → CSV, normalización), transcripción de entrevistas en local, asistencia a programación, tareas internas de gestión y automatización, consultas exploratorias sobre bases de datos propias.

---

# Desired Outcome

**Mejorar significativamente la capacidad de Civio para acceder, monitorizar y gestionar información pública, reduciendo el esfuerzo manual en tareas administrativas y aumentando la cobertura y profundidad de sus investigaciones periodísticas.**

# BLOQUE 1 — Publicidad Activa y el Portal de Transparencia

## Resumen

Cuando alguien quiere encontrar información pública en España, la respuesta oficial es: "ve al portal de transparencia". El problema es que ese portal no contiene mucha de la información — en gran parte, es un directorio de enlaces a otros portales. Las mayoría de las administraciones no vuelcan sus datos ahí; simplemente ponen un link a su propio sistema. El resultado es lo que el equipo de Civio describe como "un paso intermedio tonto": un portal que en teoría centraliza el acceso a lo público pero que en la práctica te deriva a una docena de lugares distintos, sin consistencia ni curación en muchos de los casos. 

Civio lleva años trabajando con esto y ha desarrollado una forma de manejarse: se saltan el portal de transparencia directamente y van a las fuentes primarias. Para contratos, van al Portal de Contratación del Sector Público. Para subvenciones, a la Plataforma de Subvenciones Generales. Para declaraciones de bienes de altos cargos, van directamente al BOE, porque el portal de transparencia ni siquiera aloja esa información — solo linkea al BOE, que es donde está publicada de verdad. Hay un caso excepcional en el que sí merece la pena ir al portal: las retribuciones de altos cargos, que sí están recogidas directamente ahí

Este conocimiento no está escrito en ningún sitio. Vive en la experiencia acumulada del equipo. Cuando Civio va a dar charlas a asociaciones de vecinos, comprueba de primera mano que la gente no sabe ni que existe el portal de contratación, y mucho menos cómo usarlo. El ejemplo que surgió en la reunión lo ilustra bien: un vecino metido en el seguimiento de las obras de un colegio en Barcelona descubrió por casualidad que los contratos de esa obra estaban publicados, con siete PDFs detallando fases, adjudicaciones y plazos. "Está todo ahí", decía — pero sin saber que existía ese portal, nunca lo habría encontrado.

Incluso para quien sabe que existe el portal de contratación, usarlo requiere conocimiento técnico específico. La búsqueda funciona por varios criterios como el CPV (código de clasificación normalizado), número de expediente o administración que licita, entre otros.. Sin saber estos datos de forma exacta, el usuario no puede explorar los contratos o encontrar uno concreto de forma ágil y rápida. Es una barrera invisible que hace el portal prácticamente inaccesible para cualquier persona no especializada. 

El ecosistema lo completa el Consejo de Transparencia y Buen Gobierno, el organismo encargado de vigilar que las administraciones cumplan con la publicidad activa y encargada de las reclamaciones en materia de transparencia, entre otras funciones. Hace su trabajo: revisa la publicidada activa de ciertas entidades como comunidades autónomas, empresas públicas, partidos políticos; produce informes anuales de quién cumple y quién no. El problema es que la Ley de Transparencia no es punitiva. No existe capacidad sancionadora. Los organismos que incumplen reciben el informe con las recomendaciones y poco más . No pasa nada. Esto significa que la fragmentación y la falta de calidad de los portales no tienen perspectiva de mejora orgánica a corto plazo.

| Tipo de información en publicidad activa | Ejemplo concreto              | Dónde está realmente                   |
| ---------------------------------------- | ----------------------------- | -------------------------------------- |
| Alojada directamente en el portal        | Retribuciones de altos cargos | Portal de transparencia                |
| Linkeada desde otro sitio                | Declaraciones de bienes       | BOE (el portal solo linkea)            |
| En portales sectoriales propios          | Contratos, subvenciones       | Portales específicos de cada organismo |

---

## Oportunidades y Análisis. 🔴 OPP-1a. Acceder y descubrir información pública requiere un conocimiento técnico tácito que el sistema no provee

> _"Nosotros sabemos dónde buscar, pero quizás no tiene por qué saberlo nadie que no tenga este nivel de detalle de cómo funciona la administración pública."_ _"El portal de transparencia es un agregador de enlaces externos… Si estuviese mejor estructurado sería más fácil para el ciudadano común."_

### Sub-oportunidades

- **OPP-1a.1 — Falta de estructura y consistencia en la exposición de datos.** Cada organismo presenta la información de forma diferente. Lo que debería ser un portal de transparencia funciona como un directorio de enlaces externos sin curación.
- **OPP-1a.2 — No es posible saber qué información existe antes de buscarla.** No hay mapa o inventario previo. El periodista investiga portal por portal para descubrir qué hay.
- **OPP-1a.3 — El conocimiento de dónde buscar es tácito y frágil.** Civio sabe navegar el caos porque tiene años de experiencia acumulada, pero ese conocimiento vive en personas concretas, no en sistemas.
- **OPP-1a.4 — Los portales usan vocabulario técnico desconocido para los no especialistas.** Buscar contratos en el Portal de Contratación requiere conocer ciertos datos como el CPV (clasificación europea de productos y servicios), la empresa licitadora o la administración contratante. Sin saber distinguir "servicio", "suministro" o "contrato menor", por ejemplo, los filtros son inútiles. Esta barrera existe incluso para quien ya sabe que el portal existe y que tiene que ir ahí.

> _Nota contextual: el hecho de que solo se publique lo mínimo obligatorio no es una oportunidad en sí — es una restricción regulatoria que ninguna solución puede cambiar. Se mantiene como contexto en el análisis de factores externos._

### Análisis cualitativo

**Dimensionamiento.** Es la oportunidad de mayor frecuencia: cada investigación que comienza con búsqueda de información pública pasa por este cuello de botella. Civio ya ha desarrollado estrategias de navegación efectivas, pero ese conocimiento no existe escrito, lo que lo hace frágil ante rotación de equipo y no escalable hacia ciudadanos.

**Factores externos.** El entorno regulatorio establece obligaciones de publicidad activa con amplio margen interpretativo y sin poder sancionador real — incluyendo que solo se exige publicar los mínimos legales, con los vacíos que eso genera. Esto mantiene la fragmentación sin perspectiva de mejora orgánica a corto plazo: cualquier solución tiene que construirse sobre la fragmentación existente, no esperar a que desaparezca. La tendencia europea hacia más datos abiertos y estándares de interoperabilidad crea ventanas de oportunidad a medio plazo.

**Factores de la organización.** Esta oportunidad está perfectamente alineada con la misión central de Civio: traducir la complejidad de lo público para ciudadanos y periodistas. El activo diferencial de Civio es exactamente ese conocimiento tácito de fuentes — sistematizarlo es una forma de hacer más robusto el capital organizativo sin añadir personal. La restricción de IA aplica de forma favorable: la extracción y normalización de datos de portales públicos está permitida.

**Factores del beneficiario.** Los periodistas de Civio tienen satisfacción relativa en esta área — han aprendido a navegar el caos — pero con una carga invisible que se acumula diariamente. Los ciudadanos son los beneficiarios de mayor impacto potencial y menor satisfacción actual: no saben ni que existe el portal de contratación, y cuando llegan a él no pueden usarlo sin conocimiento técnico previo.

---

## Oportunidades y Análisis. 🔴 OPP-1b. Los cambios en la información pública no se detectan hasta que alguien tropieza con ellos

> _"Ahora para encontrar información nueva o cambiada lo hacemos a mano, investigando en las fuentes que ya conocemos o investigando si hay nuevos enlaces. Si como periodista quieres tener seguimiento de un tema, es complejo."_

### Sub-oportunidades

- **OPP-1b.1 — No hay sistema de detección de cambios en portales conocidos.** Los periodistas revisan manualmente las fuentes que ya conocen. Es inconsistente y fácil de olvidar.
- **OPP-1b.2 — No hay seguimiento de nuevas fuentes o enlaces.** Nuevos portales, secciones o documentos no se detectan hasta que alguien tropieza con ellos casualmente.
- **OPP-1b.3 — El seguimiento temático a largo plazo es costoso.** Mantener vigilancia sobre un tema específico durante meses requiere disciplina y herramientas que hoy no existen.

### Análisis cualitativo

**Dimensionamiento.** La fricción es diaria pero con intensidad baja y distribuida: los periodistas revisan fuentes conocidas manualmente, de forma inconsistente. Con una carga de trabajo interno muy variable, pero que puede suponer fácilmente 1-2h de gestión a la semana entre varias personas. En momentos de pico, más. Es la oportunidad con mejor ratio coste beneficio potencial de todo el documento. 

**Factores externos.** El mercado de herramientas de monitorización web es ya muy maduro: existen opciones open source (changedetection.io) y comerciales (Visualping, Distill.io) que resuelven el 80% del problema sin desarrollo propio, con cero riesgo técnico. Esto significa que buena parte de esta oportunidad tiene solución inmediata con herramientas existentes. La estrategia de publicar qué organismos cumplen y cuáles no es un mecanismo de presión que Civio ya usa en otras áreas y que podría aplicarse a un índice de completitud de transparencia.

**Factores de la organización.** La restricción de IA aplica de forma favorable: scraping y extracción de datos están permitidos. El principal riesgo organizativo es el mantenimiento: si se configuran muchos monitores sin disciplina de gestión, el ruido puede volverse un problema mayor que el que resuelven.

**Factores del beneficiario.** Saber que no se les escapa información nueva reduce la ansiedad de seguimiento — tiene un valor emocional real más allá del operativo. Para los ciudadanos, esta oportunidad es secundaria respecto a OPP-1a: primero necesitan poder encontrar la información; el seguimiento de cambios es un paso posterior.

---

# BLOQUE 2 — Derecho de Acceso: el sistema interno en detalle

## Resumen

El derecho de acceso a la información pública es el mecanismo legal que permite a cualquier persona (o a Civio) pedir información a la administración cuando esa información no está publicada. La Ley de Transparencia de 2013 establece las reglas: la administración tiene un mes para responder desde que comienza a tramitar la solicitud —no desde que la recibe—, y puede prorrogar otro mes más si lo justifica y lo notifica. Esto ya introduce la primera complejidad: el reloj no empieza con el envío, sino cuando el organismo decide empezar a tramitar, un momento que puede llegar días o semanas después y que Civio tiene que monitorizar.

Aproximadamente en el 60% de los casos, la respuesta que llega es incompleta. Entonces comienza la segunda fase: la reclamación ante el Consejo de Transparencia. El proceso se prolonga: el Consejo abre un período de alegaciones, el organismo presenta
sus argumentos, y el Consejo delibera durante meses. Si la resolución es favorable a Civio, el organismo "debería" dar la información — pero sin mecanismo de sanción real, puede simplemente no darla. En ese caso, lo único que puede hacer Civio es contabilizar los días de incumplimiento. Nada más. 

Para gestionar todo esto, Civio usa una **tabla tipo Airtable** que calcula automáticamente las fechas clave a partir de la fecha de inicio de tramitación: cuándo vence el plazo ordinario, cuándo vence si hubo prórroga, cuándo hay que reclamar. Cada mañana, el sistema les manda un email con tres listas: solicitudes a reclamar por silencio administrativo, solicitudes a reclamar por respuesta incompleta, y reclamaciones ya resueltas a su favor pero sin información recibida (con contador de días). Es una automatización parcial útil, pero que depende de que la tabla esté bien alimentada con datos introducidos a mano.

El punto más doloroso del sistema es lo que ocurre con las notificaciones del portal. Cada vez que hay una novedad en una solicitud, el portal de transparencia envía un email a Civio con el número de referencia del expediente y el nombre del organismo. Solo eso. No dice qué tipo de notificación es. Para saberlo, hay que entrar en el portal con certificado digital, localizar la notificación, y descargar el PDF antes de que caduque —si no lo haces en plazo, el documento expira y llega incluso un segundo email de aviso de caducidad. Solo al abrir el PDF descubres si es un inicio de tramitación, una prórroga, una resolución parcial o una resolución completa. Este proceso se repite para cada notificación, de cada solicitud, de cada organismo — y hay muchas en paralelo simultáneamente.

El caso de la investigación sobre asesores en los ministerios ilustra hasta dónde puede escalar esto. Civio solicitó al Ministerio de Función Pública datos de los nombres de personal eventual de cada ministerio. Función Pública respondió que no iba a dar esa información, aunque ya lo había hecho en el pasado. Civio reclamó al Consejo de Transparencia, que les dio la razón. La respuesta del ministerio fue abrir, en nombre de Civio, 22 solicitudes de transparencia individuales —una por cada ministerio del gobierno— para que cada uno respondiera directamente. De golpe, una sola solicitud se convirtió en 22 ciclos paralelos, cada uno con sus propias notificaciones, plazos, posibles alegaciones y posibles reclamaciones. El equipo de Civio confirma que esta táctica de redistribución se está repitiendo: no es un caso aislado, es un patrón emergente. 

---

## Oportunidades y Análisis. 🔴 OPP-2. El proceso de solicitud y seguimiento de información (derecho de acceso) es costoso, fragmentado y difícil de mantener

> _"Para cada caso tiene que ir a portales diferentes… Es complejo seguir el estado de las solicitudes, son procesos largos y mucho back and forth. Es un seguimiento al que tienes que estar pendiente."_

### Sub-oportunidades

- **OPP-2.1 — Fragmentación de portales de solicitud.** Cada organismo (nacional, autonómico, local) tiene su propio portal y proceso. Un periodista gestionando varios temas simultáneamente puede estar en 10+ portales diferentes con credenciales distintas.
- **OPP-2.2 — El seguimiento de solicitudes es manual, acumulativo y propenso a errores con consecuencias irreversibles.** El sistema interno (tabla tipo Airtable con cálculo de plazos) es un buen punto de partida pero deja sin resolver lo más costoso: las notificaciones del portal llegan como emails opacos que solo revelan su contenido tras entrar con certificado digital y descargar el PDF antes de que caduque.
- **OPP-2.3 — El conocimiento sobre cómo solicitar eficazmente es especializado y no está formalizado.** Saber qué pedir, a quién, con qué formulación y cómo recurrir requiere experiencia y conocimiento del sistema que vive en las cabezas de los periodistas de Civio.
- **OPP-2.4 — El alcance se limita al nivel nacional por complejidad operativa.** Mucha información relevante está en organismos autonómicos y locales, pero extender la cobertura multiplica la complejidad de gestión.
- **OPP-2.5 — Cuando la administración redistribuye un expediente, el equipo no tiene forma de detectarlo ni gestionarlo diferente a una solicitud normal.** Una solicitud legítima puede convertirse de golpe en 22 ciclos paralelos sin que el sistema de seguimiento lo distinga. Cada subexpediente genera sus propias notificaciones, plazos y posibles alegaciones — y el equipo lo descubre solo cuando ya está desbordado. El equipo confirma que esta táctica de redistribución se está repitiendo.
- **OPP-2.6 — Los períodos de alegaciones no tienen seguimiento compartido en el sistema.** Cuando el Consejo de Transparencia abre un período de alegaciones , ese plazo no se registra en la tabla — vive en la cabeza de la periodista responsable. Si se pierde ese plazo, la reclamación puede quedar invalidada después de meses de proceso.

### Análisis cualitativo

**Dimensionamiento.** Esta oportunidad afecta directamente a los periodistas de Civio que llevan investigaciones activas — un grupo pequeño pero que trabaja con alta intensidad y durante períodos largos. Cada solicitud individual puede durar meses o incluso más de un año con trabajo activo en múltiples puntos del proceso: el caso de los asesores duró más de catorce meses desde la solicitud inicial hasta el recurso judicial, generando en el camino notificaciones, burofaxes, más notificaciones, expedientes derivados y decenas de plazos que seguir. Comparada con OPP-1, esta oportunidad afecta a menos personas pero cada episodio es mucho más costoso e impacta en el trabajo de toda la organización.

**Factores externos.** La Ley de Transparencia de 2013 establece plazos claros pero sin capacidad sancionadora: el Consejo de Transparencia puede emitir resoluciones favorables que la administración simplemente ignora, como demostró el caso de los asesores. La táctica de redistribución de expedientes es una innovación táctica reciente de la administración, no prevista en la ley y documentada por primera vez de forma sistemática en la investigación de Civio; su proliferación puede convertirse en el principal vector de sobrecarga en los próximos años.

**Factores de la organización.** Civio tiene una ventaja diferencial crítica: conocen el sistema desde dentro, saben qué funciona y qué no, y ya han construido una infraestructura parcial de seguimiento que está en uso activo. Esto significa que las soluciones no parten de cero — hay una tabla real, hay un email diario real, hay un equipo que ya ha pensado en estos problemas. El riesgo organizativo más real es el de la sostenibilidad del sistema si el equipo sigue creciendo en número de solicitudes activas sin mejoras en la infraestructura.

**Factores del beneficiario.** Los periodistas de Civio expresaron frustración muy específica y operativa: no saben qué dice una notificación hasta que la descargan con certificado digital; los documentos caducan si no se descarga en plazo y llegan avisos de caducidad que añaden más ruido; y la gestión de 22 expedientes paralelos generados por la táctica de redistribución es operativamente insostenible con el sistema actual. Hay un riesgo de consecuencias irreversibles que no existe en las otras oportunidades: perder el plazo de recurso por no haber visto una notificación puede invalidar meses de trabajo de investigación. La satisfacción actual con el proceso es baja y el nivel de ansiedad generada es alto.

---

# Resumen de oportunidades

## OST — Oportunidades

```
DESIRED OUTCOME
─────────────────────────────────────────────────────────
Mejorar la capacidad de Civio para acceder, monitorizar y
gestionar información pública, reduciendo esfuerzo manual
y aumentando cobertura y profundidad de investigaciones
─────────────────────────────────────────────────────────
│
├─── PRIORIDAD ALTA 🔴 OPP-2: Seguimiento derecho de acceso
│         (costoso, fragmentado, consecuencias irreversibles si se pierde un plazo)
│    │
│    ├─── OPP-2.1 Fragmentación de portales de solicitud
│    ├─── OPP-2.2 Seguimiento manual con notificaciones opacas
│    ├─── OPP-2.3 Conocimiento de cómo solicitar no formalizado
│    ├─── OPP-2.4 Cobertura limitada al nivel nacional
│    ├─── OPP-2.5 Redistribución de expedientes desborda el sistema sin aviso
│    └─── OPP-2.6 Períodos de alegaciones sin seguimiento compartido
│
├─── PRIORIDAD MEDIA 🔴 OPP-1a: Acceso y descubrimiento de información pública
│         (conocimiento tácito, portales innavegables, vocabulario técnico opaco)
│    │
│    ├─── OPP-1a.1 Falta de estructura y consistencia entre portales
│    ├─── OPP-1a.2 No se puede saber qué información existe antes de buscarla
│    ├─── OPP-1a.3 Conocimiento de dónde buscar es tácito y frágil
│    └─── OPP-1a.4 Vocabulario técnico (CPV, tipos de contrato) inaccesible para no especialistas
│
└─── PRIORIDAD MEDIA 🔴 OPP-1b: Monitorización y detección de cambios
          (sin alertas, revisión manual e inconsistente)
     │
     ├─── OPP-1b.1 Sin sistema de detección de cambios en portales conocidos
     ├─── OPP-1b.2 Sin seguimiento de nuevas fuentes o secciones
     └─── OPP-1b.3 Seguimiento temático a largo plazo costoso
```