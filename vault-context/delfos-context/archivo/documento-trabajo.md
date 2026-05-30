# Documento de trabajo — Equipo Delfos · Ship for Good 2026

> Documento vivo. Síntesis del discovery + espacio para decisiones del equipo.
> Iteramos sobre él. Las secciones marcadas con 🟡 están abiertas y se completan a medida que decidimos.

---

## 1. Contexto del evento

| Campo | Valor |
|-------|-------|
| Hackathon | Ship for Good · 1.ª edición |
| Fechas | 29–30 de mayo de 2026 |
| Sede | 42 Barcelona |
| Cliente / challenge owner | [Civio](https://civio.es/) — fundación independiente contra la opacidad institucional |
| Equipo | Delfos |
| Branch de trabajo | `team-delfos` (no tocar `main` ni branches de otros equipos) |
| Licencia | MIT |

### Entrega

- **Deadline: sábado 30 de mayo, 19:00.** Todo pusheado a la branch del equipo.
- README obligatorio: nombre del proyecto/equipo, problema que resuelve, prerequisitos, instalación/setup, nombres de variables de entorno (sin valores), tecnologías.
- **Demo funcionando de verdad** (deployado o local, pero ejecutándose). Mockups o prototipos no funcionales NO valen.
- Formato showcase: 3 min de demo + 3 min de feedback del jurado. Mostrar el flujo principal.
- Commits: Conventional Commits recomendado (no obligatorio).

---

## 2. Restricción innegociable: Política de IA de Civio

Esto condiciona TODA la propuesta. Es pública, deliberada y no negociable.

| ❌ VETADO | ✅ PERMITIDO |
|-----------|-------------|
| Generar texto periodístico | Conversión y limpieza de datos (PDF → CSV, normalización) |
| Generar alegaciones, recursos, enmiendas o documentos legales | Transcripción de entrevistas en local |
| IA como **fuente de información** en investigaciones | Asistencia a programación |
| Crear imágenes / ilustraciones | Tareas internas de gestión y automatización |
| Comunicación directa con lectores o socios | Consultas exploratorias sobre bases de datos propias |

> Implicación clave: la oportunidad de mayor impacto (OPP-2) cae de lleno en lo permitido (gestión/automatización interna). El riesgo está en cruzar el límite hacia "que la IA redacte la reclamación".

---

## 3. Objetivo deseado (Desired Outcome)

> Mejorar significativamente la capacidad de Civio para **acceder, monitorizar y gestionar** información pública, reduciendo el esfuerzo manual en tareas administrativas y aumentando la cobertura y profundidad de sus investigaciones periodísticas.

---

## 4. Oportunidades detectadas

### 🔴 OPP-2 — Seguimiento del derecho de acceso · PRIORIDAD ALTA

Proceso costoso, fragmentado y con consecuencias irreversibles si se pierde un plazo.

- **OPP-2.1** Fragmentación de portales de solicitud (10+ portales, credenciales distintas).
- **OPP-2.2** Seguimiento manual con **notificaciones opacas**: el email solo trae nº de expediente + organismo; hay que entrar con **certificado digital** y descargar el PDF **antes de que caduque** para saber qué tipo de notificación es.
- **OPP-2.3** Conocimiento de cómo solicitar eficazmente no formalizado.
- **OPP-2.4** Cobertura limitada al nivel nacional.
- **OPP-2.5** **Redistribución de expedientes**: una solicitud puede convertirse en 22 ciclos paralelos sin que el sistema lo distinga. Patrón emergente y creciente.
- **OPP-2.6** Períodos de alegaciones sin seguimiento compartido (viven en la cabeza de la periodista).

**Infraestructura actual de Civio:** tabla tipo Airtable que calcula automáticamente fechas clave desde la fecha de inicio de tramitación, + email diario con 3 listas (reclamar por silencio, reclamar por respuesta incompleta, resueltas a favor sin info recibida con contador de días).

### 🟠 OPP-1a — Acceso y descubrimiento de información pública · PRIORIDAD MEDIA

- **OPP-1a.1** Falta de estructura/consistencia entre portales (el portal de transparencia es un directorio de enlaces).
- **OPP-1a.2** No se puede saber qué información existe antes de buscarla.
- **OPP-1a.3** Conocimiento de dónde buscar es tácito y frágil.
- **OPP-1a.4** Vocabulario técnico (CPV, tipos de contrato) inaccesible para no especialistas.

> 📎 **Referencia de diseño:** [referencias/contractacio-cat-recomendaciones.md](./referencias/contractacio-cat-recomendaciones.md) — 16 propuestas de ergonomía para portales de contratación pública (J. Gómez-Obregón, [contractacio.cat](https://contractacio.cat/)). Checklist de UX ya validada sobre datos de contratación reales; muy aplicable si atacamos OPP-1a.

> Civio se salta el portal de transparencia y va a fuentes primarias: Portal de Contratación del Sector Público (contratos), Plataforma de Subvenciones Generales (subvenciones), BOE (declaraciones de bienes). Excepción: retribuciones de altos cargos sí están en el portal.

### 🟠 OPP-1b — Monitorización y detección de cambios · PRIORIDAD MEDIA

- **OPP-1b.1** Sin sistema de detección de cambios en portales conocidos.
- **OPP-1b.2** Sin seguimiento de nuevas fuentes o secciones.
- **OPP-1b.3** Seguimiento temático a largo plazo costoso.

> Mercado maduro: open source (changedetection.io) y comercial (Visualping, Distill.io) resuelven ~80% sin desarrollo propio. Mejor ratio coste/beneficio del documento, pero menor diferenciación.

---

## 5. Datos disponibles

**`Solicitudes_anonimizado.csv`** (muestra de 22 filas) — modelo de datos real de la tabla que Civio ya usa en producción.

Esquema de columnas:

```
Id · Ámbito · Fecha · Estado · Asunto · Ministerio · Inicio tramitación ·
Art 20.1 (volumen) · Vencimiento normal · Vencimiento 20.1 · Vencimiento ·
Resolución · Notificación · Días para respuesta ·
Días para reclamar por silencio administrativo · Días para reclamar resolución ·
Notas · Autor · Reclamación
```

---

## 6. 🟡 Decisión: oportunidad elegida

_(pendiente — a completar)_

---

## 7. 🟡 Propuesta de solución

_(pendiente — a completar)_

---

## 8. 🟡 Stack técnico

_(pendiente — a completar)_

---

## 9. 🟡 Alcance para el hackathon (qué entra y qué no)

_(pendiente — a completar)_

---

## 10. 🟡 Tareas / plan

_(pendiente — a completar)_

---

## 11. Referencias externas

- **[referencias/presentacion-reto-civio-resumen.md](./referencias/presentacion-reto-civio-resumen.md)** — resumen de la presentación en vivo del reto (María + Carmen, Civio, 29 may 2026).
  _Relevancia:_ fuente primaria del challenge · confirma y detalla OPP-2 y OPP-1a (notificaciones opacas, 22 expedientes, fragmentación, "doble combo").
- **[referencias/contractacio-cat-recomendaciones.md](./referencias/contractacio-cat-recomendaciones.md)** — 16 propuestas de ergonomía para portales de contratación pública (J. Gómez-Obregón, [contractacio.cat](https://contractacio.cat/), CC BY-SA).
  _Relevancia:_ OPP-1a · checklist de UX/UI ya validada sobre datos de contratación reales.
