---
name: 4geeks-projects
description: Consulta de solo lectura los proyectos propios de 4Geeks con GET /v1/assignment/user/me/task?task_type=PROJECT. Úsala cuando el usuario pida ver sus proyectos. Requiere el secreto protegido BREATHECODE_TOKEN y el proxy de salida de secretos de OpenClaw activo.
---

# Consultar mis proyectos de 4Geeks

1. Ejecuta `scripts/projects.py` mediante `exec` en el host `gateway`, nunca en sandbox o nodo remoto. El helper consulta únicamente el endpoint de proyectos con `limit` y `offset` hasta recopilar todas las páginas. No pases el token en argumentos, variables explícitas, comandos, archivos ni texto: lo obtiene como sentinel protegido y entrega la cabecera a curl por stdin.
2. Muestra literalmente solo la salida del helper: una línea por proyecto con su título y `task_status`, seguida del conteo por estado. No muestres ids, URLs, descripciones, otros campos ni JSON. El helper no guarda la respuesta.
3. Si responde HTTP 401, el helper imprime exactamente `El token no es válido.`; responde solo con esa línea. Para cualquier otro fallo, comunica solo el mensaje genérico producido por el helper, sin volcar cuerpo, cabeceras, entorno ni detalles de transporte.
