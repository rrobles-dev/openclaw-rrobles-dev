# SKILL_LOG — Mi Asistente 4Geeks

Registro de las skills que OpenClaw construyó conmigo para conectarse a la API de estudiantes de 4Geeks (BreatheCode). Cada skill nació de una conversación con el agente; yo no escribí el código. Las skills viven en [`skills/`](skills/) y se versionan en este repo.

- **Agente:** OpenClaw 2026.9.8, modelo `litellm/online/openrouter/openai/gpt-6-luna`.
- **API:** `https://breathecode.herokuapp.com` (autenticación `Authorization: Token <token>`).
- **Idioma:** español.
- **Fechas:** sesión de trabajo del 21 al 22 de octubre de 2026 (noche en Santiago, UTC−3). Las horas están en UTC; entre paréntesis, la hora de Santiago. Donde no quedó un registro exacto lo indico.

## Estado

| # | Skill | Endpoint | Estado |
|---|---|---|---|
| 1 | Autenticar y mostrar perfil (`4geeks-profile`) | `GET /v1/admissions/user/me` | Hecha y probada |
| 2 | Obtener mis proyectos (`4geeks-projects`) | `GET /v1/assignment/user/me/task?task_type=PROJECT` | Hecha y probada |
| 3 | Obtener trabajo pendiente (`4geeks-pending`) | `GET /v1/assignment/user/me/task?task_status=PENDING` | Hecha y probada |
| 4 | Obtener resumen de progreso (`4geeks-progress`) | `GET /v1/assignment/user/me/task` (conteo por estado y tipo) | Hecha y probada |
| Extra A | Próximos eventos (`4geeks-events`) | `GET /v1/events/all?upcoming=true` | Hecha y probada |
| Extra B | Estado de revisión de entregas (`4geeks-reviews`) | `GET /v1/assignment/user/me/task` (`revision_status`) | Hecha y probada |

Las skills 2, 3, 4 y las adicionales solo leen datos. Dejé fuera a propósito los endpoints que escriben (`PUT /v1/assignment/task/{id}` y `POST .../deliver`) para que el agente no pueda entregar tareas por error.

## Configuración inicial: token y conexión segura

El token de estudiante no está en ninguna skill, archivo ni repo. Se guarda como secreto protegido de OpenClaw y solo se sustituye al llamar al host permitido.

1. **Guardado del secreto.** `openclaw secrets store set BREATHECODE_TOKEN --kind secret --allow-host breathecode.herokuapp.com --value-file -`, con el valor leído por stdin (`read -rs`), de modo que no queda en el historial ni en los argumentos del proceso. Antes se validó con `--dry-run`.
2. **Descubrimiento del mecanismo.** Según la conversación con OpenClaw (ver más abajo), un secreto protegido solo llega a una skill si el proxy de salida está activo (`secrets.egressProxy.enabled`). Está desactivado por defecto.
3. **Activación del proxy.** El 22 de octubre de 2026 a las ~02:27 UTC (23:27 del 21 en Santiago) OpenClaw hizo una copia de `openclaw.json` (`openclaw.json.before-egress-proxy.20261022T022738Z.bak`, permisos 0600), activó el proxy y reinició el Gateway. Comprobé después con `openclaw config get secrets.egressProxy` que quedó `{"enabled": true}`.
4. **Efecto lateral esperado.** El reinicio interrumpió una ejecución de la tarea automática de heartbeat (`cron: job interrupted by gateway restart`, ~02:40 UTC). Era un fallo puntual y no del cambio.

## Conversación de descubrimiento

**Mi solicitud** (22 oct 2026, hora no registrada, antes de las 02:27 UTC):

> Quiero darte la habilidad de conectarte a mi cuenta de 4Geeks usando mi token de estudiante, sin que yo desarrolle código. El token ya está guardado como secreto protegido `BREATHECODE_TOKEN`, con el host permitido `breathecode.herokuapp.com`. ¿Qué debemos hacer para que una skill pueda usarlo en una llamada a `https://breathecode.herokuapp.com/v1/admissions/user/me` con la cabecera `Authorization: Token ...`? ¿Qué necesitas de mí?

**Qué sugirió OpenClaw:**
- Confirmó que `BREATHECODE_TOKEN` es de tipo protegido y que tiene permitido exactamente `breathecode.herokuapp.com`.
- Indicó que `secrets.egressProxy` no estaba configurado y que hay que activarlo y reiniciar el Gateway.
- Propuso crear la skill como instrucciones que hagan la petición desde un proceso `exec` administrado por el Gateway, usando la variable del secreto en `Authorization: Token ...`. El proxy sustituye el valor protegido solo al enviar al host permitido.
- Advirtió que no sirve hacer la llamada desde `web_fetch`, un sandbox ni un nodo remoto, porque esos caminos no reciben el secreto.
- Recomendó probar el `GET` y vigilar que ni el token ni datos personales innecesarios aparezcan en la salida.

**Qué información me pidió:** solo mi confirmación para activar el proxy y reiniciar el Gateway, y qué datos del perfil quería recibir. Dijo expresamente que no necesitaba que compartiera el token.

**Mi respuesta:**

> Sí, activa el proxy de salida de secretos y reinicia el Gateway. Hazme una copia de la configuración antes, y después confirma que el Gateway quedó arriba. Quiero una skill de solo lectura sobre `/v1/admissions/user/me`. Debe devolver únicamente: si el token es válido, mi nombre, el nombre de mi academia y mi cohorte activa (`educational_status` ACTIVE). Nada de email, teléfono ni el token en la salida. Si la respuesta es 401, dime solo que el token no es válido.

## Skill 1 — `4geeks-profile` (Autenticar)

- **Archivos:** [`SKILL.md`](skills/4geeks-profile/SKILL.md), [`scripts/profile.py`](skills/4geeks-profile/scripts/profile.py).
- **Commit:** `f5660f7`, 22 oct 2026 03:36 UTC (00:36 en Santiago).
- **Prompt inicial:** el de la respuesta anterior. Una segunda iteración lo corrigió con la estructura real de la API (ver más abajo).
- **Qué hace:** llama a `GET /v1/admissions/user/me` con el secreto protegido y devuelve únicamente estado del token, nombre, academia (`roles[0].academy.name`) y una línea por cada cohorte con `educational_status == "ACTIVE"` (`cohorts[].cohort.name`). Si no hay cohortes activas dice `Cohorte activa: ninguna`; con un 401 responde solo `El token no es válido.`
- **Seguridad:** el helper exige que `BREATHECODE_TOKEN` llegue como sentinel del Gateway (`oc-sent-v2.…`), nunca el valor real; no sigue redirecciones (`--max-redirs 0`); descarta `stderr`; usa mensajes de error genéricos; y construye la salida solo a partir de una lista de campos permitidos, de modo que no hay camino que imprima email, ids, permisos o el JSON.

**Prueba exitosa** (22 oct 2026, entre ~02:40 y 03:36 UTC; el token válido se guardó y se recargó con `openclaw secrets reload` antes de esta prueba). Salida exacta, con el nombre abreviado y la lista de cohortes recortada:

```
Token: válido
Nombre: R… R… M…
Academia: 4Geeks Latam
Cohorte activa: Secure AI Applications
Cohorte activa: Ai Engineering Project Delivery
Cohorte activa: Real-Time Communication
… (32 cohortes activas en total)
Cohorte activa: Advanced personal assitants with Openclaw
… 
Cohorte activa: Application telemetry
```

Es una skill de una sola responsabilidad (consultar el perfil) sobre un solo endpoint.

### Iteraciones y lecciones

1. **Primer intento: `El token no es válido.`** El token que copié de la cookie al principio era incorrecto. La solución fue copiar el valor correcto y **comprobarlo antes de guardarlo**, con una llamada directa a la API (`200` esperado).
2. **Segundo intento: error genérico.** El token ya era válido y la API respondió `200`, pero el helper asumió mal la estructura. Esperaba la cohorte con `name` en el elemento, y está anidada en `cohort.name`; esperaba la academia en un campo superior, y está en `roles[0].academy.name`; y exigía exactamente una cohorte activa, cuando hay varias. Para no volver a adivinar, listé **solo los nombres de las claves y sus tipos** de la respuesta real, sin valores, y se lo pasé a OpenClaw.

   Prompt de corrección:

   > El helper de `4geeks-profile` falla con el error genérico porque asumió una estructura equivocada. La respuesta real de `/v1/admissions/user/me` es: nombre en `first_name` y `last_name`; academia en `roles[0].academy.name`; cohortes en `cohorts[]`, cada una con `educational_status` y el nombre anidado en `cohort.name`. Corrige el helper para: (1) mostrar el nombre completo; (2) mostrar la academia desde `roles[0].academy.name`; (3) mostrar una línea `Cohorte activa: <nombre>` por cada cohorte con `educational_status == "ACTIVE"`, usando `cohort.name`. Si hay varias activas, lista todas, y si no hay ninguna, imprime `Cohorte activa: ninguna` en lugar de dar error. No imprimas email, ids, permisos, datos de GitHub o Google, ni el JSON. Después pruébalo y muéstrame la salida exacta.
3. **Tercer intento: otra vez `El token no es válido.`** con el secreto ya corregido. La API directa dio un error de autenticación puntual con el valor que pegué en ese momento y `200` con el siguiente; no pude determinar si fue un valor mal pegado o un fallo transitorio del token. Lo que resolvió el problema fue **guardar de nuevo el token, ejecutar `openclaw secrets reload` y probar enseguida**. Sin la recarga, el Gateway puede seguir con el valor anterior.
4. **Lección de método:** para cada skill nueva, primero conocer la forma real de la respuesta (claves, no valores) y solo después escribir el helper.

## Skill 2 — `4geeks-projects` (Obtener mis proyectos)

- **Archivos:** [`SKILL.md`](skills/4geeks-projects/SKILL.md), [`scripts/projects.py`](skills/4geeks-projects/scripts/projects.py).
- **Commit:** `a9c770a`, 22 oct 2026 03:54 UTC (00:54 en Santiago).
- **Prompt inicial:**

  > Quiero otra skill de solo lectura, separada de `4geeks-profile`, que me muestre mis proyectos de 4Geeks. Debe llamar a `GET /v1/assignment/user/me/task?task_type=PROJECT` con el mismo secreto protegido `BREATHECODE_TOKEN` y el mismo método (helper vía `exec` en el host `gateway`, sin token en archivos ni argumentos). Pagina con `limit` y `offset` hasta traer todos, y muestra una línea por proyecto con título y estado (`task_status`), más un conteo por estado al final. No imprimas ids, URLs de repositorio ni el JSON. Si hay 401, responde solo que el token no es válido. Antes de crearla, dime qué campos tiene la respuesta real, usando solo nombres de claves y no valores, para no asumir la estructura. Después pruébala y muéstrame la salida exacta.
- **Qué sugirió OpenClaw:** inspeccionó una respuesta real antes de escribir el helper. Informó de que viene paginada (`count`, `first`, `last`, `next`, `previous`, `results`) y de que cada elemento de `results` trae `title` y `task_status`, además de otros campos que la skill no muestra. Con eso creó una skill independiente. Esta vez la estructura no tuvo que corregirse.
- **Qué hace:** pide los proyectos con `limit=100` y `offset`, comprueba que el `count` no cambie entre páginas y que el total recibido coincida con él, y devuelve una línea `título — estado` por proyecto y un conteo por estado. Un 401 produce `El token no es válido.`
- **Seguridad:** la cabecera `Authorization` se entrega a `curl` por stdin (`--config -`), de modo que ni el sentinel va en los argumentos del proceso; sin redirecciones; salida solo con título y estado.

**Prueba exitosa** (22 oct 2026, antes de las 03:54 UTC). Salida exacta, recortada:

```
Milestone — AI-driven Engineering — DONE
My 4Geeks Assistant — Teaching OpenClaw to Track Your Progress — PENDING
Is This Snack Healthy? — A Nutrition-Check Automation — DONE
… (22 proyectos en total)
Milestone 1 — Your Company's Public Website — DONE
Conteo por estado:
DONE: 12
PENDING: 10
```

## Skill 3 — `4geeks-pending` (Obtener trabajo pendiente)

- **Archivos:** [`SKILL.md`](skills/4geeks-pending/SKILL.md), [`scripts/pending.py`](skills/4geeks-pending/scripts/pending.py).
- **Commit:** `ac92963`, 22 oct 2026 03:59 UTC (00:59 en Santiago).
- **Prompt inicial:**

  > Quiero otra skill de solo lectura, separada de `4geeks-profile` y `4geeks-projects`, que me diga qué trabajo tengo pendiente. Debe llamar a `GET /v1/assignment/user/me/task?task_status=PENDING` con el mismo secreto protegido y el mismo método. Pagina con `limit` y `offset` siguiendo `next`. Quiero una línea por tarea con título y tipo (`task_type`), agrupadas por tipo (proyecto, ejercicio, lección, cuestionario) y con un conteo por grupo y un total al final. No imprimas ids, URLs ni el JSON. Si hay 401, responde solo que el token no es válido. Reutiliza la estructura de respuesta que ya inspeccionaste (`results[].title`, `task_status`) y comprueba solo si existe `task_type`, diciéndome antes si el nombre del campo es otro. Pruébala y muéstrame la salida exacta.
- **Qué sugirió OpenClaw:** confirmó con una respuesta real (HTTP 200) que `results[]` contiene `task_type` y `task_status`, y dijo que seguiría el enlace `next` solo si permanece en el host y el endpoint esperados.
- **Qué hace:** pagina siguiendo `next`, valida cada enlace de continuación (HTTPS, host `breathecode.herokuapp.com`, ruta del endpoint, `task_status=PENDING`, `limit` y `offset` válidos), agrupa por Proyecto, Ejercicio, Lección y Cuestionario (con un grupo "Otros" para tipos desconocidos) y muestra título y tipo, conteo por grupo y total.
- **Seguridad:** mismo método que la skill 2 (cabecera por stdin al `curl`, sin redirecciones, salida acotada).

**Prueba exitosa** (22 oct 2026, antes de las 03:59 UTC). Salida exacta, recortada:

```
Proyecto:
My 4Geeks Assistant — Teaching OpenClaw to Track Your Progress — Proyecto
… (10 proyectos)
Conteo proyecto: 10
Ejercicio:
Connecting OpenClaw with 4Geeks Academy — Ejercicio
… (68 ejercicios)
Conteo ejercicio: 68
Lección:
What is The Internet? — Lección
… (15 lecciones)
Conteo lección: 15
Total: 93
```

**Verificación cruzada:** las skills 2 y 3 son independientes y devuelven datos coherentes. Los 10 proyectos `PENDING` de la skill 2 son los mismos 10 del grupo "Proyecto" de la skill 3, y 10 + 68 + 15 = 93, el total reportado. Los ejercicios repetidos en la salida son el mismo contenido asignado en cohortes distintas.

## Skill 4 — `4geeks-progress` (Obtener resumen de progreso)

- **Archivos:** [`SKILL.md`](skills/4geeks-progress/SKILL.md), [`scripts/progress.py`](skills/4geeks-progress/scripts/progress.py).
- **Commit:** `e5bf2ea`, 22 oct 2026 04:16 UTC (01:16 en Santiago).
- **Prompt inicial:**

  > Quiero otra skill de solo lectura, separada de las otras, que me dé un resumen de cuánto he avanzado en el curso. Debe llamar a `GET /v1/assignment/user/me/task` (sin filtro de estado) con el mismo secreto protegido y el mismo método, paginando con `next` solo dentro del host y endpoint esperados. Quiero una salida corta, de pocas líneas: el total de tareas, el conteo y el porcentaje por estado (`task_status`), y el mismo desglose por tipo (`task_type`) con cuántas están completadas. No listes tareas individuales. Verifica antes en una respuesta real los valores que existen de `task_status`, sin asumir que solo hay `DONE` y `PENDING`, y dime cuáles son. No imprimas ids, URLs ni el JSON, y si hay 401, responde solo que el token no es válido. Pruébala y muéstrame la salida exacta.
- **Qué sugirió OpenClaw:** recorrió todas las páginas de una respuesta real (128 tareas) y confirmó que los únicos valores de `task_status` son `DONE` y `PENDING`. Aun así, el helper cuenta cualquier estado nuevo que aparezca en lugar de descartarlo. Durante la prueba corrigió la URL inicial para incluir `limit` y `offset`.
- **Qué hace:** agrega todas las tareas del usuario y devuelve el total, el conteo y el porcentaje por estado, y por tipo cuántas tareas hay y cuántas están `DONE`. No lista tareas individuales.
- **Seguridad:** mismo método que las skills 2 y 3 (cabecera por stdin, sin redirecciones, enlaces `next` validados contra el host y la ruta esperados, salida acotada).

**Prueba exitosa** (22 oct 2026, antes de las 04:16 UTC). Salida exacta:

```
Total de tareas: 128
Por estado:
DONE: 35 (27.3%)
PENDING: 93 (72.7%)
Por tipo:
EXERCISE: 89 tareas, 21 completadas
LESSON: 17 tareas, 2 completadas
PROJECT: 22 tareas, 12 completadas
```

**Verificación cruzada con las skills 2 y 3:** 35 + 93 = 128 = 89 + 17 + 22. Los 93 pendientes coinciden con el total de la skill 3; los 22 proyectos con 12 completadas coinciden con los 12 `DONE` y 10 `PENDING` de la skill 2; y los ejercicios y lecciones pendientes (89 − 21 = 68 y 17 − 2 = 15) coinciden con los conteos de la skill 3.

## Skill adicional A — `4geeks-events` (Próximos eventos)

- **Archivos:** [`SKILL.md`](skills/4geeks-events/SKILL.md), [`scripts/events.py`](skills/4geeks-events/scripts/events.py).
- **Commit:** `8dd590c`, 22 oct 2026 04:44 UTC (01:44 en Santiago).
- **Necesidad que cubre:** saber cuáles son los próximos eventos de la academia sin salir del agente.
- **Prompt inicial:**

  > Quiero otra skill de solo lectura, separada de las otras, que me diga cuáles son los próximos eventos de 4Geeks. Debe llamar a `GET /v1/events/all?upcoming=true` con el mismo secreto protegido y el mismo método (helper vía `exec` en el host `gateway`, cabecera por stdin al `curl`). Antes de crearla, dime qué campos tiene la respuesta real, solo nombres de claves, y si el endpoint necesita algún parámetro más, por ejemplo `academy`. Muestra una línea por evento con título, fecha y hora, limitado a los 10 más próximos. No imprimas ids, URLs de reunión ni el JSON. Si hay 401, responde solo que el token no es válido. Pruébala y muéstrame la salida exacta.
- **Qué sugirió OpenClaw:** inspeccionó una respuesta real (HTTP 200 sin parámetro `academy`, una lista de 4 eventos) y listó los campos del evento. Decidió usar solo `title` y `starting_at`.
- **Qué hace:** pide los eventos futuros y devuelve hasta los 10 más próximos, ordenados por fecha de inicio, con título y fecha y hora (en UTC, con el desfase explícito). Tolera eventos sin fecha y devuelve un mensaje claro si no hay ninguno. Un 401 produce `El token no es válido.` No muestra ids, enlaces ni URLs de reunión ni otros campos.

**Incidencia durante la creación:** la primera ejecución del agente falló dos veces con `Agent run failed` y dejó la skill incompleta, con `SKILL.md` pero sin `scripts/events.py`. El log del Gateway mostró dos causas: límites de tasa (HTTP 429) del proveedor por peticiones de unos 198 000 tokens, y desbordamiento del contexto de la sesión (entrada estimada de 128 316 tokens frente a una ventana de 128 000, sin espacio para la respuesta). Tras abrir una sesión nueva y darle un mensaje autocontenido que pedía solo el helper que faltaba, el agente lo escribió sin tocar el `SKILL.md`.

**Prueba exitosa** (22 oct 2026, antes de las 04:44 UTC). Salida exacta:

```
Real Projects. Real AI. Built by Our AI Engineers. — 2026-10-23 14:00 +00:00
Your Way Into the AI Jobs That Pay 62% More — 2026-11-03 23:00 +00:00
Your Way Into the AI Jobs That Pay 62% More (DAY 2) — 2026-11-04 23:00 +00:00
Your Way Into the AI Jobs That Pay 62% More (DAY 3) — 2026-11-05 23:00 +00:00
```

## Skills adicionales exploradas y descartadas

Antes de llegar a la segunda skill adicional se exploraron dos ideas que no se pudieron construir. Se documentan porque forman parte del proceso de convertir una necesidad en una capacidad del agente, y porque el agente respetó los límites de acceso.

- **Actividad reciente (`GET /v1/activity/me`).** Prompt: pedirle al agente que inspeccionara una respuesta real y propusiera un resumen de los últimos 7 días, sin crear nada. Resultado: **HTTP 403**. El cuerpo decía `Missing academy_id parameter expected for the endpoint url or 'Academy' header`. Se autorizó probar una única variante, la cabecera `Academy` con el id de mi academia (obtenido de `roles[0].academy.id` en `/v1/admissions/user/me`), con las mismas credenciales y sin otro método de autenticación. Seguía en 403, así que el agente se detuvo y no se insistió: el endpoint no está abierto a mi rol de estudiante.
- **Próximas entregas (`4geeks-deadlines`).** Prompt: inspeccionar las claves de las 128 tareas y comprobar si existe una fecha límite. Resultado: no existe (`associated_slug`, `cohort`, `created_at`, `delivered_at`, `description`, `github_url`, `id`, `live_url`, `opened_at`, `read_at`, `reviewed_at`, `revision_status`, `task_status`, `task_type`, `title`, `updated_at`). `delivered_at` indica cuándo se entregó, no cuándo vence. El agente se detuvo en lugar de ordenar por un campo que no sirve.

## Skill adicional B — `4geeks-reviews` (Estado de revisión de entregas)

- **Archivos:** [`SKILL.md`](skills/4geeks-reviews/SKILL.md), [`scripts/reviews.py`](skills/4geeks-reviews/scripts/reviews.py).
- **Commit:** `c84652e`, 22 oct 2026 05:34 UTC (02:34 en Santiago).
- **Necesidad que cubre:** saber cómo van las revisiones de mis entregas. Ninguna otra skill lo responde, porque la skill de progreso cuenta el estado de mi lado (`task_status`) y no el de la revisión (`revision_status`).
- **Prompts:** primero una inspección, y después una segunda fase con un ajuste.

  Inspección:

  > Descartamos las skills de actividad y de fechas límite. Quiero otra skill de solo lectura, `4geeks-reviews`, sobre `GET /v1/assignment/user/me/task`, que me diga cómo van las revisiones de mis entregas. Antes de crear nada, inspecciona una respuesta real y dime qué valores distintos tiene `revision_status` y cuántas tareas hay de cada uno (solo conteos, sin títulos ni datos personales), y cuántas tareas tienen `delivered_at` y `reviewed_at` no nulos. Con eso propón una salida corta (por ejemplo, entregas por estado de revisión y cuántas llevan más de 7 días sin revisar) y espera mi confirmación antes de escribir nada.

  El agente respondió: 128 tareas, `APPROVED: 23` y `PENDING: 105`, y 23 con `delivered_at` y `reviewed_at` no nulos. Propuso contar las entregas pendientes con más de 7 días sin revisar, y con la cifra resultante, 0, no se distinguía entre "ninguna espera" y "la métrica no mide lo que creemos": `revision_status: PENDING` incluye tareas que nunca se entregaron. Se ajustó la definición.

  Ajuste:

  > Sí, escribe `4geeks-reviews`, con este ajuste. Define "entrega esperando revisión" como `task_status = DONE` y `revision_status = PENDING`. Muestra: (1) el total de tareas aprobadas, por tipo; (2) las entregas esperando revisión, por tipo, con un total; (3) los días que lleva esperando la más antigua, calculados desde `delivered_at`. No listes tareas individuales ni imprimas ids, URLs, ni el JSON. Mismo secreto protegido, mismo método, mismo patrón que `4geeks-progress`. Si hay 401, responde solo que el token no es válido. Pruébala y muéstrame la salida exacta.
- **Qué hace:** cuenta las tareas aprobadas por tipo y las entregas esperando revisión (`task_status = DONE` y `revision_status = PENDING`) por tipo, con un total y los días que lleva esperando la más antigua con fecha de entrega. Indica aparte cuántas de las que esperan no tienen `delivered_at`. No lista tareas individuales.
- **Seguridad:** mismo método que las skills anteriores (cabecera por stdin, sin redirecciones, enlaces `next` validados, salida acotada).

**Prueba exitosa** (22 oct 2026, antes de las 05:34 UTC). Salida exacta:

```
Tareas aprobadas por tipo:
EXERCISE: 14
PROJECT: 9
Entregas esperando revisión por tipo:
EXERCISE: 7
LESSON: 2
PROJECT: 3
Total esperando revisión: 12
Antigüedad de la más antigua con fecha disponible: 1 días
Entregas esperando revisión sin delivered_at: 9
```

**Verificación cruzada con las skills 2 y 4:** 14 + 9 = 23 aprobadas, y 35 `DONE` − 23 aprobadas = 12 esperando revisión. Por tipo también encaja: 21 ejercicios `DONE` = 14 + 7, 2 lecciones = 0 + 2, y 12 proyectos `DONE` = 9 + 3. Una hipótesis previa, que los 12 eran todos proyectos, resultó falsa: son 7 ejercicios, 2 lecciones y 3 proyectos. Los 9 sin `delivered_at` corresponden a ejercicios y lecciones marcados como hechos sin una entrega que revisar, y el helper lo indica en lugar de inventar una antigüedad. Los 3 proyectos que sí esperan revisión llevan 1 día.

## Lecciones generales

- **Inspeccionar antes de escribir.** Para cada skill se pidió a OpenClaw que primero describiera la respuesta real de la API (solo nombres de claves, sin valores), en lugar de suponer su forma. La única skill en la que se supuso mal la estructura fue la primera.
- **Un secreto recién guardado necesita recarga.** Tras `secrets store set`, ejecutar `openclaw secrets reload` y probar enseguida.
- **Las sesiones largas se desbordan.** Una conversación con muchas salidas largas llegó a superar la ventana de contexto del modelo y provocó fallos que parecían de autenticación o del proveedor. Abrir una sesión nueva con un mensaje autocontenido lo resolvió.
- **Verificar la coherencia entre skills.** Los totales de las skills 2, 3 y 4 se cruzaron entre sí (por ejemplo, 93 pendientes en la skill 3 y en la 4), lo que da confianza en que los datos no se están inventando ni truncando.
