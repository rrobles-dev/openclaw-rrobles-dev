---
name: 4geeks-reviews
description: "Resumen de solo lectura del estado de las revisiones de entregas en 4Geeks: tareas aprobadas por tipo, entregas esperando revisión por tipo y antigüedad de la más antigua. Úsala cuando el usuario pregunte cómo van sus revisiones. Requiere BREATHECODE_TOKEN protegido y el proxy de salida de secretos de OpenClaw activo."
---

# Resumir mis revisiones de entregas en 4Geeks

1. Ejecuta `scripts/reviews.py` mediante `exec` en el host `gateway` (nunca sandbox ni nodo remoto). Consulta solo `GET https://breathecode.herokuapp.com/v1/assignment/user/me/task`, sin filtros, y pagina siguiendo `next` únicamente si conserva HTTPS, el host `breathecode.herokuapp.com` y la ruta exacta `/v1/assignment/user/me/task`. No pases el token en argumentos, variables explícitas, comandos, archivos ni texto; el helper usa el sentinel protegido y entrega la cabecera a curl por stdin.
2. Devuelve literalmente solo la salida del helper. Cuenta como aprobada una tarea con `revision_status=APPROVED`; agrupa por `task_type`. Cuenta como entrega esperando revisión una tarea que cumpla conjuntamente `task_status=DONE` y `revision_status=PENDING`; agrupa por `task_type`, indica el total y los días completos transcurridos desde `delivered_at` de la entrega pendiente más antigua. No listes tareas individuales ni muestres IDs, URLs, JSON u otros campos.
3. Si el servidor devuelve HTTP 401, responde exactamente `El token no es válido.` y nada más. Para otros errores, muestra solo el mensaje genérico del helper.
