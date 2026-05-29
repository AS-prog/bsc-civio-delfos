# Recomendaciones de ergonomía para portales de contratación pública

> **Documento de referencia.** Síntesis (parafraseada) de las propuestas publicadas en la fuente citada abajo. No reproduce el texto original; resume cada propuesta con sus ideas clave para uso interno del equipo Delfos.

## Fuente

- **Sitio:** [contractacio.cat](https://contractacio.cat/) — "Propuestas a los portales de contratación"
- **Autor:** Jaime Gómez-Obregón ([@JaimeObregon](https://twitter.com/JaimeObregon))
- **Alcance:** propuestas de mejora a la ergonomía de los portales de transparencia de la contratación pública en **Cataluña** (Plataforma de Contratación de Cataluña y Registro Público de Contratos).
- **Licencia del original:** CC BY-SA.
- **Consultado:** 2026-05-29.

## Por qué es relevante para Civio / Delfos

Conecta directamente con **OPP-1a** (acceso y descubrimiento de información pública: portales innavegables, vocabulario técnico opaco) y con la presentación de datos de contratación. Es un catálogo concreto y accionable de mejoras de UX/UI sobre datos públicos reales — justo el tipo de trabajo que cae en lo **permitido** por la política de IA de Civio (limpieza, normalización y presentación de datos).

---

## Las 16 propuestas

### 1. Retitular las columnas con nombres legibles

**Problema:** las cabeceras de la tabla de licitaciones muestran identificadores técnicos crudos (`CODI_EXPEDIENT`, `TIPUS_CONTRACTE`, `VALOR_ESTIMAT_CONTRACTE`…).

**Recomendación:** mostrar títulos pensados para personas ("Tipo" en vez de `TIPUS_CONTRACTE`).

### 2. Precargar los resultados en el cliente

**Problema:** algunas tablas paginan/ordenan al instante (datos precargados) y otras tardan segundos porque consultan al servidor en cada operación.

**Recomendación:** descargar el conjunto una sola vez y hacer ordenación, paginación y filtrado en el navegador. El JSON comprime ~85 % con Brotli/gzip; además conviene podar campos del JSON que no se muestran. (Salvedad: no aplica si el volumen de datos es enorme.)

### 3. Ocultar las secuencias de control

**Problema:** las descripciones muestran literalmente `\n`, `\r`, `\t` provenientes de los datos.

**Recomendación:** reemplazar esas secuencias por espacios antes de renderizar.

### 4. No mostrar URLs crudas al usuario

**Problema:** se exhiben direcciones URL largas y crípticas como dato, lo que intimida o genera desconfianza.

**Recomendación:** sustituir la URL visible por un texto descriptivo del recurso, manteniendo el enlace activo.

### 5. Hacer enlazables los contratos

**Problema:** el detalle de cada contrato se abre en un modal sin URL propia; no se puede enlazar, compartir ni guardar en marcadores.

**Recomendación:** asignar a cada contrato una URL única (idealmente corta) que abra su detalle directamente. Ejemplo citado: [contratosdecantabria.es](https://contratosdecantabria.es).

### 6. Mostrar los estados como un proceso

**Problema:** la contratación es un ciclo (se anuncia → se adjudica → se formaliza) pero los portales solo informan de la fase aislada.

**Recomendación:** situar el estado actual dentro del proceso completo, para que el ciudadano entienda qué pasó y qué falta.

### 7. Evitar el patrón "etiqueta: dato"

**Problema:** la presentación columnar tipo `Tipo: servicios` es artificiosa; muchas etiquetas son innecesarias porque el dato ya revela su naturaleza.

**Recomendación:** construir frases naturales con conectores ("Contrato menor de servicios, adjudicado a … por …"), atendiendo al carácter multilingüe de los portales.

### 8. No tabular datos no tabulares

**Problema:** los contratos se fuerzan en tablas (19 columnas) que no caben, obligando a scroll horizontal y desperdiciando espacio.

**Recomendación:** usar listas o tarjetas en vez de tablas, mostrando solo los datos más relevantes y dejando el resto para la vista de detalle.

### 9. Omitir decimales y divisa en las celdas de resultados

**Problema:** los céntimos y el símbolo € repetido en cada celda añaden ruido y restan espacio.

**Recomendación:** redondear al euro en las tablas y mover el símbolo € a la cabecera de columna. Los céntimos sí se muestran en la página de detalle del contrato.

### 10. Elidir correctamente el objeto del contrato

**Problema:** el texto largo se corta de forma brusca en el carácter 150, generando alturas de celda desiguales y cortes arbitrarios.

**Recomendación:** usar la propiedad CSS `line-clamp` (ejemplo en [CodePen](https://codepen.io/gareth53/pen/AwbQyO)).

### 11. Usar formatos vectoriales para marcas y logos

**Problema:** emblemas institucionales servidos como mapas de bits borrosos, agravado por pantallas de alta densidad.

**Recomendación:** usar siempre SVG para marcas, logos y pictogramas.

### 12. Mostrar primero los contratos más recientes

**Problema:** por defecto las tablas listan los contratos más antiguos, obligando a navegar hasta la última página para ver lo actual.

**Recomendación:** ordenar por defecto en cronología inversa (lo más reciente publicado, adjudicado, formalizado o modificado primero).

### 13. Usar las tablas de forma coherente

**Problema:** controles de descarga, paginación y filtrado aparecen duplicados o en posiciones inconsistentes entre dos tablas de la misma página (caso del portal de Manresa).

**Recomendación:** aplicar el [principio de mínima sorpresa](https://es.wikipedia.org/wiki/Principio_de_la_m%C3%ADnima_sorpresa): que elementos análogos se comporten de forma análoga.

### 14. Corregir el enlace roto de descarga de datos

**Problema:** el botón "Accede a todos los datos" lleva a un 404 en varios portales municipales (producto de AOC).

**Recomendación:** corregir el enlace e integrar monitorización de excepciones (ej. [Sentry](https://sentry.io/)) para detectar estos fallos al instante.

### 15. Eliminar el aviso de cookies de la Plataforma

**Problema:** un modal de cookies bloquea la primera interacción; instala cookies de Google Analytics y YouTube (estas últimas ni siquiera declaradas en la política).

**Recomendación:** prescindir de Google Analytics (o usar la variante sin cookies) y servir vídeos desde `youtube-nocookie.com`. Sin cookies reguladas, desaparece el modal, baja el mantenimiento y el riesgo legal.

### 16. Unificar la Plataforma y el Registro

**Problema:** la contratación pública catalana está repartida entre dos servicios (Plataforma de Contratación y Registro de Contratos); el usuario no sabe que existen ambos y obtiene una visión parcial, lo que alimenta percepción de opacidad.

**Recomendación:** unificar ambos en un punto de acceso único. Salvedad del autor: el desacople de modelos de datos (*impedance mismatch*) hace inviable una mera agregación; la unificación real es costosa y probablemente a medio plazo.

---

## Principios transversales que se desprenden

- **Reducir la carga cognitiva**: lenguaje humano, menos ruido visual, jerarquía clara.
- **Cada recurso, una URL** (enlazable, compartible, marcable).
- **Presentación ≠ modelo de datos**: no calcar la estructura de la base de datos en la UI.
- **Coherencia y mínima sorpresa** entre componentes análogos.
- **Privacidad por defecto** y menos dependencias de terceros.
- **Punto de acceso único** frente a la fragmentación de portales.
