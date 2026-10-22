---
name: 4geeks-profile
description: Consulta de solo lectura el perfil propio de 4Geeks en /v1/admissions/user/me. Úsala cuando el usuario pida su nombre, academia o cohorte activa. Requiere el secreto protegido BREATHECODE_TOKEN y el proxy de salida de secretos de OpenClaw activo.
---

# Consultar mi perfil de 4Geeks

1. Ejecuta el helper `scripts/profile.py` de esta skill mediante la herramienta `exec` en el host `gateway` (no sandbox, nodo remoto, `web_fetch` ni navegador). No añadas el token en argumentos, variables explícitas, comandos, archivos ni texto de conversación. El proceso recibe `BREATHECODE_TOKEN` como sentinel protegido del Gateway; el proxy autorizado lo sustituye solo al enviar HTTPS a `breathecode.herokuapp.com`.
2. Devuelve literalmente solo las líneas producidas por el helper. En éxito serán el estado del token, el nombre y la academia de `roles[0].academy.name`, seguidos de una línea `Cohorte activa: <nombre>` por cada elemento de `cohorts[]` cuyo `educational_status` sea `ACTIVE`; el nombre procede de `cohort.name`. Si no hay cohortes activas, mostrará `Cohorte activa: ninguna`. No muestres ni resumas otros campos. Nunca solicites o consultes endpoints distintos.
3. Si el helper informa `El token no es válido.`, responde exactamente eso y nada más. Ante cualquier otro error, comunica únicamente el mensaje genérico del helper, sin volcar respuesta HTTP, cuerpo, cabeceras, entorno ni diagnóstico que pueda incluir datos personales.

El helper rechaza redirecciones, no sigue enlaces y solo imprime campos permitidos. No persiste la respuesta ni imprime email, teléfono, IDs, permisos, datos de GitHub o Google, token ni JSON crudo.
