---
name: 4geeks-progress
description: "Resumen de solo lectura del avance del usuario en 4Geeks: total de tareas, conteo y porcentaje por estado, y desglose por tipo con total y cuántas están DONE. Úsala cuando el usuario pregunte cuánto ha avanzado en el curso. Requiere BREATHECODE_TOKEN protegido y el proxy de salida de secretos de OpenClaw activo."
---

# Resumir mi avance en 4Geeks

1. Ejecuta `scripts/progress.py` mediante `exec` en el host `gateway` (no sandbox ni nodo remoto). Consulta solo `GET /v1/assignment/user/me/task` sin filtro de estado; sigue `next` hasta el final y solo si permanece en HTTPS, host `breathecode.herokuapp.com` y ruta exacta del endpoint. No pases el token en argumentos, variables explícitas, comandos, archivos ni texto: se usa el sentinel protegido y la cabecera se entrega por stdin a curl.
2. Devuelve literalmente el resumen breve del helper: total; conteo y porcentaje para cada valor de `task_status` observado; y por cada `task_type`, total y cuántas están completadas (`DONE`). No listes tareas individuales ni muestres IDs, URLs, JSON u otros campos. Los estados/tipos no reconocidos se cuentan dinámicamente.
3. Si hay HTTP 401, responde exactamente `El token no es válido.` y nada más. Para otros errores, comunica solo el mensaje genérico del helper.
