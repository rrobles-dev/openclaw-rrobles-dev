# Programación diaria (08:30 Santiago)

El resumen debe llegar cada día a las **08:30 hora de Santiago** (`America/Santiago`). Es después de las horas de silencio de `AGENTS.md` (23:00–08:00), así que no necesita excepción.

## Antes de crear la automatización
1. En el VPS (OpenClaw 2026.9.8) el comando es `openclaw automations` (alias `openclaw cron`) con los subcomandos `add`, `list`, `show`, `edit`, `enable`, `disable`, `rm`, `run`, `runs`, `status` y `scratch`. Revisa primero `openclaw automations list --all` (**no dupliques ni pises** una automatización existente) y las opciones de `openclaw automations add --help`.
2. El VPS corre en UTC. Indica la zona `America/Santiago` explícitamente al programar; si el comando solo acepta una expresión cron en UTC, recuerda que el huso de Chile cambia entre UTC−3 y UTC−4 según la época del año.
3. Tras crearla, pruébala una vez con `openclaw automations run <id>` y revisa lo que llegó con `openclaw automations runs`. Comprueba la hora programada con `openclaw automations show <id>`.

## Texto sugerido para la automatización
> A las 08:30 (hora de Santiago), usa el skill `resumen-noticias-chile`: ejecuta `armar_resumen.py`, revisa `ok_para_enviar`, pule el borrador y envíalo por Telegram a mi chat. Si no se puede armar un resumen completo, avísame en una línea qué falló y no mandes uno a medias. Tras enviarlo, ejecuta el script con `--guardar`.

## Después
- Comprueba la primera semana: que llegue a la hora, que los enlaces abran y que `memory/noticias/` nunca conserve más de 7 días.
- Ajustes de la lista de prioridad de medios: `scripts/fuentes.json`.
