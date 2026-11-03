# Programación diaria (08:30 Santiago)

El resumen debe llegar cada día a las **08:30 hora de Santiago** (`America/Santiago`). Es después de las horas de silencio de `AGENTS.md` (23:00–08:00), así que no necesita excepción.

## Antes de crear la automatización
1. En el VPS (OpenClaw 2026.9.8) el comando es `openclaw automations` (alias `openclaw cron`) con los subcomandos `add`, `list`, `show`, `edit`, `enable`, `disable`, `rm`, `run`, `runs`, `status` y `scratch`. Revisa primero `openclaw automations list --all` (**no dupliques ni pises** una automatización existente) y las opciones de `openclaw automations add --help`.
2. El VPS corre en UTC. Indica la zona `America/Santiago` explícitamente al programar; si el comando solo acepta una expresión cron en UTC, recuerda que el huso de Chile cambia entre UTC−3 y UTC−4 según la época del año.
3. Tras crearla, pruébala una vez con `openclaw automations run <id>` y revisa lo que llegó con `openclaw automations runs`. Comprueba la hora programada con `openclaw automations show <id>`.

## Comando sugerido (OpenClaw 2026.9.8)

Revisado contra `openclaw automations add --help`. Sustituye `<CHAT_ID>` por el id del chat de Telegram del usuario:

```
openclaw automations add \
  --name "Resumen de noticias Chile" \
  --cron "30 8 * * *" --tz America/Santiago --exact \
  --session isolated \
  --timeout-seconds 300 \
  --announce --channel telegram --to <CHAT_ID> \
  --message "Usa el skill resumen-noticias-chile: ejecuta armar_resumen.py con --formato texto, revisa ok_para_enviar y pule el borrador sin tocar ni quitar ninguna URL. Tu respuesta final debe ser solo el mensaje del resumen en texto plano, listo para Telegram, con cada URL entera en su propia línea. Si no se puede armar un resumen completo, responde en una línea qué falló y no mandes uno a medias. Antes de terminar, ejecuta el script con --guardar."
```

- `--cron "30 8 * * *" --tz America/Santiago` fija las 08:30 hora de Santiago (el VPS corre en UTC; la zona evita el desfase por el cambio de horario). `--exact` quita el desplazamiento aleatorio que el programador añade por defecto.
- `--session isolated` ejecuta cada día en una sesión nueva, sin arrastrar contexto de otras conversaciones.
- `--timeout-seconds 300` porque el valor por defecto es de 30 s y armar el resumen más redactarlo puede tardar más.
- `--announce --channel telegram --to <CHAT_ID>` entrega la respuesta final al chat. No uses `--best-effort-deliver`: si falla la entrega, queremos verlo.
- Sin `--to`, `--channel last` enviaría al último chat usado; es más frágil.

**Entrega y enlaces (observado):** con el mensaje original (borrador HTML) las noticias llegaban a Telegram sin enlaces: la entrega por `--announce` no respeta el HTML. Por eso la automatización usa `--formato texto`, con la URL visible en su propia línea, que Telegram convierte en enlace. Para actualizar una automatización ya creada, revisa su mensaje con `openclaw automations show <id>` y cámbialo con `openclaw automations edit <id> --message "..."` (comprueba las opciones con `--help`). Si prefieres negritas y enlaces con nombre, el agente puede enviar el mensaje él mismo con `parse_mode` HTML y la automatización terminar con una respuesta corta.

## Después
- Comprueba la primera semana: que llegue a la hora, que los enlaces abran y que `memory/noticias/` nunca conserve más de 7 días.
- Ajustes de la lista de prioridad de medios: `scripts/fuentes.json`.
- Ver el historial de ejecuciones con `openclaw automations runs`; pausar con `openclaw automations disable <id>`.
