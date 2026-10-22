---
name: 4geeks-events
description: Consulta de solo lectura los próximos eventos de 4Geeks mediante GET /v1/events/all?upcoming=true. Úsala cuando el usuario pregunte por próximos eventos. Requiere el secreto protegido BREATHECODE_TOKEN y el proxy de salida de secretos de OpenClaw activo.
---

# Consultar próximos eventos de 4Geeks

1. Ejecuta `scripts/events.py` mediante `exec` en el host `gateway`, nunca sandbox ni nodo remoto. Consulta solo `https://breathecode.herokuapp.com/v1/events/all?upcoming=true`; no añadas un parámetro academy, porque la consulta global se verificó sin él. El helper usa el sentinel protegido y entrega Authorization por stdin a curl; no pongas el token en argumentos, archivos ni texto.
2. Muestra literalmente solo la salida del helper: hasta los 10 eventos futuros más próximos, una línea por evento con título y fecha/hora de inicio. Solo se leen `title` y `starting_at`; no imprimas IDs, enlaces, URLs de reunión, ni JSON. La respuesta no se persiste.
3. Si la respuesta HTTP es 401, responde exactamente `El token no es válido.` y nada más. Para cualquier otro error, comunica solo el mensaje genérico del helper.
