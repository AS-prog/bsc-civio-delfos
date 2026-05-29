# Resumen — Presentación en vivo del reto (Civio)

> **Documento de referencia.** Síntesis (parafraseada) de la charla de apertura del hackathon. No reproduce la transcripción literal; resume las ideas clave para el equipo Delfos.
> Relacionado: [[documento-trabajo]] · [[contractacio-cat-recomendaciones]]

## Fuente

- **Origen:** transcripción de la presentación del reto — `referencias/29 May at 18-34.txt`
- **Fecha:** 29 de mayo de 2026, ~18:34 (apertura del hackathon Ship for Good).
- **Ponentes:** **María** (periodista de Civio, conectada desde Madrid; es quien más pelea con el portal de transparencia) y **Carmen** (equipo técnico de Civio, presente en sala; soporte técnico durante el evento).
- **Nota:** el archivo es una auto-transcripción con muchos errores de reconocimiento de voz; nombres y términos se han corregido en este resumen.

---

## 1. Quién es Civio y el marco legal

- **Civio**: fundación independiente que combate la opacidad institucional vía periodismo, tecnología y datos. Equipo muy pequeño (~4 periodistas + ~3 desarrollo + codirección); todos tocan un poco de todo. Además de periodismo hacen **incidencia/lobby**: reuniones con la administración, recomendaciones, intentos de cambiar leyes.
- **Ley 19/2013** (de transparencia, en vigor desde 2014): reconoce el derecho de toda la ciudadanía a conocer información sobre el funcionamiento de la administración pública. Tiene dos patas que son el foco del reto:
  - **Publicidad activa**: lo que la administración debe publicar de forma proactiva, sin que nadie lo pida (e idealmente en formato reutilizable).
  - **Derecho de acceso**: lo que cualquiera puede solicitar cuando no está publicado.

---

## 2. Publicidad activa y el portal de transparencia

- **Obligados a publicar**: todos los organismos públicos (ministerios, CCAA, ayuntamientos, universidades, Casa Real, Congreso, Senado, Tribunal de Cuentas…). Parcialmente también partidos, sindicatos y entidades privadas que reciban >40 % de ayudas públicas.
- **Qué debe publicarse**: contratos, subvenciones, retribuciones de altos cargos, convenios, cuentas anuales, organigrama, presupuestos, ejecución presupuestaria, declaraciones de bienes… La ley se conforma con "lo mínimo".
- **El portal del reto**: [transparencia.gob.es](https://transparencia.gob.es) — el de la **Administración General del Estado** (ministerios y presidencia). **No hay nada unificado**: cada CCAA, ayuntamiento grande, Congreso, etc. tiene su propio portal.
- **Cambio reciente**: cambiaron el portal "la semana pasada" (~mediados de mayo 2026). El lenguaje es ahora más claro y orientado al ciudadano, pero **los problemas de fondo persisten** — solo cambió la capa de presentación.
- **Crítica central — es un agregador de enlaces**: "de cada 5 links, 4 te mandan a otra página". Solo algunas cosas viven realmente en el portal (ej. **retribuciones de altos cargos**, en una tabla descargable). El resto deriva a portales externos:
  - Subvenciones → Plataforma de subvenciones (la describe como completa pero "una web horrible" para el ciudadano).
  - Contratos → Portal de Contratación (donde están los pliegos, "la chicha"); el portal solo muestra un listado básico.
  - Declaraciones de bienes de altos cargos → otro enlace externo.
- **Doble visión que pide María**: que la mejora sirva tanto a Civio (periodistas) **como al ciudadano común** que ni sabe que el portal existe.

---

## 3. Derecho de acceso: el proceso y sus dolores

### Barrera de entrada
- **No se permiten solicitudes anónimas.** En el portal estatal hay que identificarse con **certificado electrónico o Cl@ve** — la barrera principal, deja fuera a muchísima gente. Algunas autonomías/ayuntamientos (ej. ciudad de Madrid) permiten sin certificado.
- La solicitud exige identidad y un medio de contacto (email o dirección física). **La motivación NO es obligatoria** (preguntas por derecho, no hace falta justificar).
- **Excepción**: la información medioambiental tiene una ley propia que permite solicitar por **email** (Civio la usa en el proyecto *España en Llamas*).
- Hacer la solicitud requiere **muchísimos clics** a través de los formularios web de cada organismo.

### Plazos
- La administración tiene **1 mes** para responder… pero **el reloj empieza cuando el organismo decide tramitar**, no cuando recibe la solicitud. Ese inicio puede demorarse.
- Prórroga de **+1 mes** si alega volumen/complejidad (art. 20.1 / referido como art. 21).
- **Silencio administrativo negativo**: muchísimas veces simplemente no contestan.

### Reclamación ante el Consejo de Transparencia y Buen Gobierno (CTBG)
- Es **otra web y otra sede** distinta del portal de transparencia.
- Plazo de **3 meses** para resolver, pero están atascados (se va a 4-5 meses).
- **Sin poder sancionador**: si el Consejo da la razón a Civio y la administración ignora la resolución, queda en un **limbo**; la única vía sería el contencioso-administrativo. La administración ha aprendido que "no le pasa nada".
- El CTBG **solo cubre la AGE y 4-5 CCAA**; el resto tienen sus propios consejos. Lo gestionan ~30 personas para las reclamaciones; acaba de entrar nueva dirección.

### Caso de los 22 expedientes (patrón de redistribución)
- Solicitud iniciada en **2023** sobre personal eventual / denuncias de acoso sexual en la administración. Función Pública dijo no tener los datos y remitió a pedirlos ministerio por ministerio. Civio reclamó al CTBG y **ganó**. La respuesta: Función Pública abrió **~21-22 expedientes** (uno por ministerio). Resultado: **~1 año** hasta conseguir las respuestas, con notificaciones, plazos y reclamaciones multiplicados.

### Fragmentación territorial
- Materias como **educación y sanidad** las gestionan las CCAA → para un dato nacional hay que hacer **17 solicitudes** (una por comunidad), cada una en su portal. La "gincana".

---

## 4. El sistema interno de Civio (Airtable)

- Una base tipo **Airtable** ("nada fancy, pero funciona"). Campos manuales (nº de expediente, fecha de inicio de tramitación, si aplica el +1 mes…) y **fechas límite calculadas automáticamente**.
- **Email diario (~8:00)** con avisos: solicitudes a reclamar por silencio, a reclamar por respuesta incompleta, **alegaciones** a presentar (incorporación reciente), y reclamaciones ganadas sin información recibida (con un **contador** de días, "ya de cachondeo porque no sirve de nada").
- Dos pestañas conectadas: **solicitudes** y **reclamaciones** (numeraciones distintas, vinculadas para el seguimiento completo).
- Estados: respondida / en reclamación / etc. Las que no interesan se dejan sin seguimiento. La clasificación de la administración ("acceso total/parcial/denegado") **no coincide** con la valoración real de Civio.

### El dolor de las notificaciones opacas
- Cada novedad llega como un **email que solo trae el nº de expediente**, sin decir el tipo. Para saber qué es (inicio de trámite, ampliación de plazo, resolución parcial/total) hay que **entrar con certificado a la sede electrónica** y abrir el documento.
- **Los documentos caducan**: si no entras a tiempo, la notificación expira.
- Todo el seguimiento depende de **un único certificado** → cuello de botella enorme.

### Otros problemas de la sede
- **Buscador inútil**: no busca por palabras clave, solo por número de expediente exacto.
- **"Carpeta ciudadana" vs "Preguntas"**: tras el último cambio de la sede, el histórico de resoluciones de Civio quedó en "carpeta ciudadana" y lo nuevo en "preguntas", sin explicación clara.
- **Formato de respuesta**: piden formato reutilizable, pero a veces reciben **PDF escaneado**; otras veces un CSV limpio.
- **Sin comunicación directa**: si la respuesta llega incompleta no puedes replicar; toca reclamar. A veces han resuelto contactando informalmente con la **OIT** (unidades de transparencia de cada ministerio).

---

## 5. Qué pediría Civio / cómo se vería el éxito

- **El "doble combo"** (prioridad declarada): que la solución **sirva a la vez a Civio y al ciudadano común**.
- Que el portal de transparencia sea **útil de verdad y no un mero agregador de enlaces**.
- Los dos dolores que más le pesan a María:
  1. **No es accesible para la ciudadanía general** (quien no es periodista ni encuentra ni entiende la información).
  2. **La fragmentación** (las 17 solicitudes; portales dispersos). Su deseo ideal: un punto único donde buscar por municipio y ver contratos, presupuestos, ejecución, etc.
- **Carmen** afinará el enfoque del hackathon con el equipo al día siguiente.

---

## 6. Datos y recursos mencionados

- **Airtable anonimizado**: Civio comparte una versión anonimizada de su base (las cabeceras/columnas) como modelo de datos para jugar → corresponde a `discovery/Solicitudes_anonimizado.csv`.
- **Datos públicos abiertos**: el CTBG publica un **listado de reclamaciones resueltas**; el portal publica un **Excel de solicitudes denegadas y límites aplicados**. Civio sacó de ahí un tema: el límite más usado para denegar es el de **intereses económicos** (ej. RENFE y su algoritmo de precios de billetes).
- **Sin límite** de solicitudes por persona o CIF (salvo inadmisión por solicitudes repetitivas/abusivas).
- **Proyectos/recursos de Civio**:
  - *España en Llamas* (datos vía email con la ley medioambiental).
  - **Curso gratuito por email** (5-7 entregas) sobre cómo solicitar información y reclamar — todo su conocimiento volcado, en la web de Civio.
  - **tuderechoasaber.es**: portal que permitía hacer solicitudes en nombre de terceros; **murió el 10 de diciembre de 2015** justo cuando se impuso el certificado digital obligatorio.
- **Referencias externas citadas**: **superbore.es** (mencionado como "superboy"); **Eva Belmonte** (codirectora de Civio) hace cobertura diaria del **BOE**.

---

## 7. Relación con las oportunidades del discovery

- **OPP-2** (derecho de acceso): confirmada y muy detallada — notificaciones opacas, certificado como cuello de botella, caducidad de documentos, caso de los 22 expedientes, alegaciones, Airtable + email diario.
- **OPP-1a** (acceso/descubrimiento): el portal como agregador de enlaces; barrera del vocabulario; ciudadano que no sabe ni que existe. Conecta con [[contractacio-cat-recomendaciones]].
- **OPP-1b** (monitorización de cambios): el propio cambio reciente del portal (sin aviso) y el seguimiento manual ilustran la necesidad.
