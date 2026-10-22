---
name: 4geeks-pending
description: Consulta de solo lectura el trabajo pendiente propio en 4Geeks mediante GET /v1/assignment/user/me/task?task_status=PENDING. Úsala cuando el usuario pregunte por sus tareas pendientes. Requiere el secreto protegido BREATHECODE_TOKEN y el proxy de salida de secretos de OpenClaw activo.
---

# Consultar trabajo pendiente de 4Geeks

1. Ejecuta `scripts/pending.py` mediante `exec` en el host `gateway` (nunca sandbox ni nodo remoto). El helper consulta solo el endpoint de tareas filtrado por `task_status=PENDING`, pagina siguiendo el campo `next` hasta que sea nulo y acepta enlaces de continuación solo para el mismo host y endpoint. No pases el token en argumentos, variables explícitas, comandos, archivos ni texto; el helper usa el sentinel protegido y entrega la cabecera a curl por stdin.
2. Devuelve literalmente solo la salida del helper. Agrupa por Proyecto, Ejercicio, Lección y Cuestionario; imprime título y tipo por tarea, conteo por grupo y total. Tipos no reconocidos se colocan en Otros con el tipo devuelto. No muestres IDs, URLs, JSON ni otros campos.
3. Si el servidor devuelve HTTP 401, responde exactamente `El token no es válido.` y nada más. Para otros errores, muestra solo el mensaje genérico que da el helper.
