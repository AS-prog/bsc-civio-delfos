# 00 · Por qué — el problema y la decisión

> Contexto destilado del discovery del reto (29 may 2026), la presentación en vivo de Civio
> y el modelo operativo de la organización. Detalle ampliado en [fuentes/](fuentes/) y
> [archivo/](archivo/).

## El cliente y su misión

**Civio** es una fundación independiente sin ánimo de lucro que combate la opacidad
institucional combinando **periodismo de datos, ingeniería de software y litigio legal**.
Equipo pequeño (~10 personas: periodistas, desarrollo, codirección). Todo su código es open
source y sus datos se publican con licencia abierta. Principio rector que condiciona todo:
**human-in-the-loop** — la IA asiste, el humano decide y verifica; nada se publica sin
auditoría humana.

Su trabajo se apoya en dos patas de la **Ley 19/2013 de transparencia**:
- **Publicidad activa**: lo que la administración debe publicar de oficio (contratos,
  subvenciones, retribuciones de altos cargos, organigramas, presupuestos…).
- **Derecho de acceso**: lo que cualquiera puede solicitar cuando no está publicado.

## La restricción innegociable: la política de IA de Civio

Esto **condiciona toda la propuesta**. Es pública, deliberada y no negociable.

| ❌ VETADO | ✅ PERMITIDO |
|-----------|-------------|
| Generar texto periodístico | Conversión y limpieza de datos (PDF → CSV, normalización) |
| Generar alegaciones, recursos o documentos legales | Transcripción de entrevistas en local |
| IA como **fuente de información** en investigaciones | Asistencia a programación |
| Crear imágenes / ilustraciones | Tareas internas de gestión y automatización |
| Comunicación directa con lectores o socios | Consultas exploratorias sobre bases de datos propias |

**Implicación de diseño**: cualquier solución que construyamos tiene que caer del lado
permitido — extracción, limpieza, estructuración y consulta de datos públicos. El momento en
que la IA "redacta" o "decide" cruza la línea.

## Las oportunidades detectadas (discovery)

### 🔴 OPP-2 — Seguimiento del derecho de acceso · prioridad alta
Proceso costoso, fragmentado y con consecuencias irreversibles si se pierde un plazo.
- Portales fragmentados (10+), credenciales distintas.
- **Notificaciones opacas**: el email solo trae nº de expediente; para saber qué es hay que
  entrar con **certificado digital** a la sede y abrir un PDF **antes de que caduque**.
- **Redistribución de expedientes**: una solicitud puede estallar en ~22 ciclos paralelos
  (caso real: personal eventual → 22 expedientes, ~1 año de tramitación).
- Plazos legales calculados a mano; hoy viven en un Airtable + email diario.

### 🟠 OPP-1a / OPP-1b — Acceso, descubrimiento y monitorización · prioridad media
- El **Portal de Transparencia es un agregador de enlaces**: "de cada 5 links, 4 te mandan a
  otra página". No se puede saber qué información existe antes de buscarla.
- Vocabulario técnico (CPV, tipos de contrato) inaccesible para el ciudadano común.
- Sin sistema de detección de cambios en portales conocidos (el propio portal cambió en
  mayo 2026 sin aviso; solo cambió la capa de presentación, los problemas de fondo siguen).

> El **"doble combo"** que pide Civio: que la solución sirva a la vez a sus periodistas **y**
> al ciudadano común que ni sabe que el portal existe.

## La decisión del equipo Delfos

Atacamos el **lado de datos de OPP-1a**: hacer **explotable y consultable** el corpus de
**Publicidad Activa** de `transparencia.gob.es`, que hoy es un laberinto de enlaces.

**Por qué esta y no OPP-2** (el dolor más agudo):
- OPP-2 toca certificados digitales, sedes electrónicas y plazos legales — inviable de
  demostrar de verdad en un hackathon sin acceso a credenciales reales.
- El corpus de Publicidad Activa es **público, scrapeable y de solo lectura**: cae limpio
  dentro de la política de IA (extracción + limpieza + consulta, cero generación).
- Deja un **activo reutilizable** (base de datos + MCP) sobre el que Civio puede construir.

**El qué construido vive en [01-que.md](01-que.md). El cómo, en [02-como.md](02-como.md).**
