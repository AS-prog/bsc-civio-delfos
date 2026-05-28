# Configuración de Agentes y Modelos en opencode

Asignación de modelos a cada agente SDD en `~/.config/opencode/opencode.json`.

## Modelos base

| Variable | Modelo |
|----------|--------|
| `model` (default) | `opencode-go/deepseek-v4-flash` |
| `small_model` | `nan/gemma4` |

## Asignación por agente

| Agente | Rol | Modelo | reasoning_effort |
|---|---|---|---|
| `gentle-orchestrator` | Coordina todo el flujo SDD | `openai/gpt-5.5` | **high** |
| `sdd-init` | Bootstrap SDD | `openai/gpt-5.5` | medium |
| `sdd-explore` | Investiga codebase | `openai/gpt-5.5` | medium |
| `sdd-propose` | Crea propuestas | `nan/qwen3.6` | — |
| `sdd-spec` | Escribe specs | `bailian-coding-plan/glm-5` | thinking nativo |
| `sdd-design` | Diseño técnico | `nan/qwen3.6` | — |
| `sdd-tasks` | Desglose en tareas | `nan/qwen3.6` | — |
| `sdd-apply` | Implementa código | `nan/qwen3.6` | — |
| `sdd-verify` | Valida contra specs | `nan/qwen3.6` | — |
| `sdd-archive` | Archiva cambios | `small_model` (`nan/gemma4`) | — |
| `sdd-onboard` | Guía al usuario | `nan/qwen3.6` | — |
| `general` (built-in) | Chat por defecto | usa `model` global | — |
