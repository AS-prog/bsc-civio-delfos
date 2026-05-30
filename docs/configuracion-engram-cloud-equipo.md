# Conectarse a Engram Cloud del equipo

Esta guía explica cómo conectarse directamente al proyecto compartido `mi-proyecto`, importar el contexto del equipo y sincronizar nuevas memorias al terminar cada sesión.

## Ruta rápida

```bash
engram cloud config --server http://91.134.240.217:18080
export ENGRAM_CLOUD_TOKEN="<token-entregado-por-canal-seguro>"
engram cloud enroll mi-proyecto
engram sync --cloud --import --project mi-proyecto
engram sync --cloud --status --project mi-proyecto
```

El resultado esperado del último comando es `Pending import: 0`.

## Estado validado

La conexión fue probada con `mi-proyecto` y funciona de punta a punta.

- `engram cloud enroll mi-proyecto`: correcto.
- `engram cloud status`: Cloud configurado y autenticación lista.
- `engram sync --cloud --import --project mi-proyecto`: importación correcta, sin chunks pendientes después de sincronizar.
- `engram sync --cloud --project mi-proyecto`: exportación correcta; en la prueba creó el chunk `2d93d9de`.
- `engram sync --cloud --status --project mi-proyecto`: `Pending import: 0`.
- `engram search "TEST CLOUD OVH" --project mi-proyecto`: encontró memorias compartidas.
- Estado posterior a la unificación: `mi-proyecto` contiene 46 observaciones, 19 sesiones y 74 prompts.

Conclusión: `mi-proyecto` es el proyecto operativo y canónico actual para el equipo.

## Datos de conexión

| Variable | Valor |
|---|---|
| `ENGRAM_CLOUD_SERVER` | `http://91.134.240.217:18080` |
| `ENGRAM_PROJECT` | `mi-proyecto` |
| `ENGRAM_CLOUD_TOKEN` | Solicitar por canal seguro |

> [!warning]
> No pegues el token en Markdown, commits, issues ni chats. Configuralo como variable de entorno o desde el gestor de secretos del equipo.

## Instalación paso a paso

1. Verificar que Engram está instalado:

```bash
engram version
```

2. Configurar el servidor Cloud:

```bash
engram cloud config --server http://91.134.240.217:18080
```

3. Configurar el token en la terminal.

macOS/Linux:

```bash
export ENGRAM_CLOUD_TOKEN="<token-entregado-por-canal-seguro>"
```

PowerShell:

```powershell
$env:ENGRAM_CLOUD_TOKEN="<token-entregado-por-canal-seguro>"
```

4. Enrolar el proyecto:

```bash
engram cloud enroll mi-proyecto
```

5. Importar memorias compartidas:

```bash
engram sync --cloud --import --project mi-proyecto
```

6. Verificar estado:

```bash
engram sync --cloud --status --project mi-proyecto
```

Estado actual: `mi-proyecto` es el proyecto canónico. Usar este nombre en todas las máquinas para evitar fragmentar memorias entre proyectos.

## Configurar el agente

Engram puede configurar automáticamente integraciones para agentes soportados.

OpenCode:

```bash
engram setup opencode
```

Claude Code:

```bash
engram setup claude-code
```

Gemini CLI:

```bash
engram setup gemini-cli
```

Codex:

```bash
engram setup codex
```

Configuración MCP manual, si el agente no tiene setup automático:

```json
{
  "mcp": {
    "engram": {
      "type": "stdio",
      "command": "engram",
      "args": ["mcp", "--tools=agent"]
    }
  }
}
```

## Flujo de trabajo diario

Este es el flujo recomendado para que el equipo comparta contexto entre máquinas y agentes.

### Cómo funciona la sincronización

| Acción | Cuándo usarla | Qué hace |
|---|---|---|
| `engram sync --cloud --import --project mi-proyecto` | Antes de empezar | Descarga memorias nuevas creadas por otras personas |
| `engram context mi-proyecto` | Al abrir una sesión | Muestra contexto reciente del proyecto |
| `engram search "<tema>" --project mi-proyecto` | Cuando necesitás recuperar algo concreto | Busca decisiones, bugs, comandos o descubrimientos previos |
| `engram sync --cloud --project mi-proyecto` | Al terminar | Sube las memorias nuevas de tu máquina a Cloud |
| `engram sync --cloud --status --project mi-proyecto` | Para verificar | Muestra chunks locales, remotos y pendientes de importar |

Regla simple: importar al empezar, exportar al terminar.

### Primera vez en una máquina

1. Instalar o verificar Engram.
2. Configurar servidor y token.
3. Enrolar `mi-proyecto`.
4. Importar memorias existentes.
5. Configurar el agente que use cada persona.

Comando para importar memorias existentes:

```bash
engram sync --cloud --import --project mi-proyecto
```

Comando de verificación final:

```bash
engram sync --cloud --status --project mi-proyecto
```

El resultado esperado es que `Pending import` quede en `0` después de importar.

### Al empezar una sesión de trabajo

Traer primero el contexto compartido:

```bash
engram sync --cloud --import --project mi-proyecto
engram context mi-proyecto
```

Después de eso, abrir el agente normalmente. La idea es que el agente arranque con lo que el equipo ya aprendió en sesiones anteriores.

### Durante el trabajo

Guardar memorias cuando aparezca algo que deba sobrevivir a la sesión:

- Decisiones técnicas o de arquitectura.
- Bugs resueltos y su causa raíz.
- Configuración nueva o cambios de entorno.
- Convenciones del equipo.
- Gotchas, errores raros o comportamiento inesperado.

Ejemplo manual, si hace falta guardar algo desde CLI:

```bash
engram save "Decisión sobre scraper" "**What**: Se decidió mantener el scraper en Ruby. **Why**: Es el stack dominante en los scrapers Civio existentes. **Where**: vault-context/delfos-context/referencias/repos-civio/" --type decision --project mi-proyecto
```

Si el agente tiene Engram configurado por MCP, normalmente puede guardar memorias por sí mismo cuando detecta decisiones o descubrimientos relevantes.

### Al terminar una sesión

Publicar lo aprendido en Cloud:


```bash
engram sync --cloud --project mi-proyecto
```

Luego comprobar que no queda nada pendiente de importar:

```bash
engram sync --cloud --status --project mi-proyecto
```

### Cuando otra persona quiere continuar

La siguiente persona debe importar antes de trabajar:

```bash
engram sync --cloud --import --project mi-proyecto
engram search "<tema>" --project mi-proyecto
```

Usá búsquedas concretas: nombre de feature, repo, error, decisión o herramienta. Evitá búsquedas demasiado genéricas.

## Verificación

Comprobar estado de Cloud:

```bash
engram cloud status
```

Buscar memorias compartidas:

```bash
engram search "mi-proyecto"
```

Comprobar sincronización:

```bash
engram sync --cloud --status --project mi-proyecto
```

## Troubleshooting

| Problema | Causa probable | Acción |
|---|---|---|
| `ENGRAM_CLOUD_TOKEN` no está configurado | La variable solo vive en la terminal actual | Volver a exportar el token o configurarlo en el gestor de secretos local |
| Proyecto no permitido | El servidor no tiene el proyecto en `ENGRAM_CLOUD_ALLOWED_PROJECTS` | Usar `mi-proyecto`, que es el proyecto canónico actual |
| El servidor no responde | VPS caída, puerto bloqueado o URL incorrecta | Verificar conectividad con el administrador |
| El agente no encuentra herramientas Engram | Falta setup MCP del agente | Ejecutar `engram setup <agente>` o añadir la configuración MCP manual |

## Reglas de seguridad

- No versionar tokens ni secretos.
- No compartir capturas con valores de `ENGRAM_CLOUD_TOKEN`.
- Rotar el token si se pegó en un archivo, issue, chat o commit.
- Usar siempre el mismo nombre de proyecto para evitar memorias fragmentadas.
