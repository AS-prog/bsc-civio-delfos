---
tags:
  - repo-civio
  - activo
  - tooling
  - ruby
  - slack
  - bot
repo: lita-slack
url: https://github.com/civio/lita-slack
language: Ruby
stars: 0
forks: 0
estado: activo
ultimo-push: 2023-03-15
---

# lita-slack

Adapter de [[Slack]] para [[Lita]] (framework Ruby para chatbots).

## README

> **lita-slack** is an adapter for Lita that allows you to use the robot with Slack.

- Usa [[Real Time Messaging API]] de Slack
- Gema Ruby publicada

### Configuración

```ruby
Lita.configure do |config|
  config.robot.adapter = :slack
  config.adapters.slack.token = "abcd-1234567890-..."
end
```

## Contexto

- Repo auxiliar, no relacionado con la misión principal de Civio
- Fork/mantención de la gema oficial `lita-slack`
