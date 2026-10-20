# Programación diaria (08:30 Santiago)

El resumen debe llegar cada día a las **08:30 hora de Santiago** (`America/Santiago`). Es después de las horas de silencio de `AGENTS.md` (23:00–08:00), así que no necesita excepción.

## Antes de crear la automatización
1. Revisa los comandos disponibles en el VPS: `openclaw automations --help` (y `openclaw automations list --all` para ver lo que ya existe; **no dupliques ni pises** una automatización existente).
2. El VPS corre en UTC. Indica la zona `America/Santiago` explícitamente al programar; si el comando solo acepta una expresión cron en UTC, recuerda que el huso de Chile cambia entre UTC−3 y UTC−4 según la época del año.
3. Haz primero una prueba manual a la hora que quieras y compara con lo que debería salir.

## Texto sugerido para la automatización
> A las 08:30 (hora de Santiago), usa el skill `resumen-noticias-chile`: ejecuta `armar_resumen.py`, revisa `ok_para_enviar`, pule el borrador y envíalo por Telegram a mi chat. Si no se puede armar un resumen completo, avísame en una línea qué falló y no mandes uno a medias. Tras enviarlo, ejecuta el script con `--guardar`.

## Después
- Comprueba la primera semana: que llegue a la hora, que los enlaces abran y que `memory/noticias/` nunca conserve más de 7 días.
- Ajustes de la lista de prioridad de medios: `scripts/fuentes.json`.
