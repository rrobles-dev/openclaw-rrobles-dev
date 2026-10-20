# SKILLS_DESIGN.md — Diseño de skills

Antes de escribir un `SKILL.md`, cada skill responde tres preguntas. Sirven para no construir a ciegas y para saber, al final, si el skill funcionó.

1. **¿Qué hace?** Una frase.
2. **¿Qué input necesita el agente?** Qué se le da y en qué formato, y qué ya sabe por los archivos de configuración del workspace.
3. **¿Cómo es un buen output?** Formato, destino y cómo sabremos que funcionó.

## Qué ya sabe el agente (archivos de configuración)

Son los cinco `.md` de la raíz del workspace. Los skills **no deben repetir** lo que ya está aquí; solo agregan lo específico de la tarea.

| Archivo | Qué aporta al agente | Estado actual |
|---|---|---|
| `IDENTITY.md` | Nombre («Mi pana»), saludo, vibe (tranquilo, auténtico, curioso, directo, humor natural) y emoji 😎. | Completo. |
| `SOUL.md` | Carácter y límites: ser útil sin florituras, tener opinión, resolver antes de preguntar, **no enviar respuestas a medias a canales de mensajería**, no filtrar datos privados a espacios compartidos. El saludo de `IDENTITY.md` se usa al abrir un chat nuevo. | Completo. |
| `AGENTS.md` | Convenciones del workspace: memoria (`memory/`, `USER.md`, `MEMORY.md`), líneas rojas (confirmar lo irreversible, preferir `trash` a `rm`), revisar soluciones existentes antes de construir a medida, automatizaciones (`openclaw automations`), formato por plataforma (Discord y WhatsApp; Telegram no se menciona). | Completo. |
| `USER.md` | Preferencias estables del usuario, como directrices con fecha. | **Vacío: sigue siendo la plantilla.** El agente no sabe nada del usuario por este archivo. |
| `DREAMS.md` | Diario del «dreaming» interno de OpenClaw (consolidación de memoria). No es configuración del usuario ni tiene relación con los sueños del skill. | Generado por OpenClaw; no se edita. |

Consecuencia práctica: la personalidad, el saludo y las reglas generales de memoria y privacidad **no se escriben en los skills**. Lo que cada skill debe aportar es el procedimiento, las fuentes y el formato de salida. Y como `USER.md` está vacío, conviene registrar ahí las preferencias estables que vayan apareciendo (idioma, nivel de detalle, horarios), en lugar de repetirlas en cada skill.

---

# Skill 1: `interpretacion-de-suenos`

Ubicación: `skills/interpretacion-de-suenos/` · Estado: **implementado y probado en el VPS**.

## 1. ¿Qué hace?

Convierte el relato de un sueño en una lectura imaginativa y lúdica, inspirada en tres diccionarios de sueños en la web, y lo guarda en un diario privado para descubrir hilos recurrentes con el tiempo.

## 2. ¿Qué input necesita el agente?

**Lo que se le da**
- Un mensaje de texto libre por Telegram con el relato del sueño («Anoche soñé que…»), propio o de un tercero. Puede ser incompleto o llegar varios sueños en un mensaje.
- También vale una pregunta suelta sobre un símbolo («¿qué significa soñar con agua?»), que no se registra.
- No hay formato obligatorio: el agente extrae solo personajes, lugares, acciones, objetos y emociones.

**Lo que ya sabe (de los archivos de configuración)**
- Cómo hablar: tono tranquilo, directo y con humor natural (`IDENTITY.md`, `SOUL.md`).
- Que no debe mandar respuestas a medias a Telegram y que los datos privados no salen a espacios compartidos (`SOUL.md`, `AGENTS.md`).
- Cómo escribir memoria sin pisarla y que el contexto sensible solo se carga en la sesión principal (`AGENTS.md`).
- **Lo que no sabe:** nada del usuario (`USER.md` vacío), ni los portales, ni el formato del registro, ni el estilo de lectura artística. Eso lo aporta el `SKILL.md` y sus `references/`.

**Lo que debe consultar o generar él mismo**
- Los portales, a través de `scripts/buscar_simbolos.py` (Dream Bible, AuntyFlo, Dream Book).
- El historial, a través de `scripts/registro.py` (no la búsqueda semántica de memoria, que en esta instalación falla sin clave de OpenAI).

## 3. ¿Cómo es un buen output?

**Formato:** mensaje de Telegram en español, que empieza directamente con el título (sin disclaimers ni explicación de fuentes antes de la lectura):
1. Título con gancho.
2. Lectura artística de 1 a 3 párrafos.
3. Ingredientes: cada símbolo con su idea tradicional parafraseada y su fuente.
4. Hasta 3 preguntas para seguir jugando.
5. Hilos recurrentes, solo si hay datos suficientes.
6. Nota final de una línea (fantasía y diversión, fuentes), solo la primera vez en la conversación.

**Destino:**
- Telegram: la respuesta al usuario.
- Disco: una entrada nueva en `memory/suenos/registro.md` (ignorado por git, privado).

**Cómo sabremos que funcionó** (se revisa leyendo la respuesta y el VPS):

| Criterio | Cómo se comprueba |
|---|---|
| Usó el skill y no respondió de memoria | Hay archivos en `skills/interpretacion-de-suenos/.cache/` y la respuesta cita Dream Bible, AuntyFlo y Dream Book. |
| Estructura correcta | Título + lectura + ingredientes + preguntas; nada de aviso al inicio. |
| Tono lúdico, no clínico | Lenguaje condicional («quizá», «como si»), sin predicciones ni diagnósticos. |
| Registró el sueño | `cat memory/suenos/registro.md` muestra la entrada con símbolos, personajes y emociones. |
| Respeta la privacidad | El registro no aparece en `git status` y no se menciona fuera de la sesión principal. |
| Hilos recurrentes en el momento justo | Aparecen con 5 sueños o un elemento repetido 3 veces; no antes. |
| Seguridad | Ante angustia fuerte o trauma, deja el juego y sugiere apoyo profesional. |

**Resultado de la prueba real:** la primera respuesta (sin el skill cargado) fue genérica y no registró nada. Tras copiar el skill al VPS y reiniciar el gateway, la segunda cumplió título, lectura, ingredientes, preguntas y registro. Pendiente: confirmar con varios sueños que aparecen los hilos recurrentes y que la nota final solo se muestra la primera vez.

---

# Skill 2: `resumen-noticias-chile` (nombre provisional)

Ubicación prevista: `skills/resumen-noticias-chile/` · Estado: **implementado y probado en local** (falta probarlo en el VPS y programar la automatización) (decisiones de formato, hora e historial tomadas; hay verificación de fuentes y prueba de concepto del ranking).

## 1. ¿Qué hace?

Cada mañana lee los titulares de varios medios chilenos, elige la noticia más importante del día según cuántos portales la cubren, y manda por Telegram un resumen tipo diario (titular principal con noticias secundarias, economía y finanzas, internacional, deportes y, si hace falta, otros), indicando cuántos medios cubren cada noticia y con un solo enlace por noticia.

## 2. ¿Qué input necesita el agente?

**Lo que se le da**
- Nada por parte del usuario en el uso normal: se dispara solo, con una automatización diaria de OpenClaw (`openclaw automations`). Si el usuario escribe «noticias de hoy», se ejecuta el mismo flujo a pedido.
- Una lista de fuentes configurada en el skill (ver verificación de fuentes más abajo): cada una es un feed RSS o un *news sitemap* público, es decir, una lista oficial de las notas recientes con título, fecha y enlace.
- Preferencias estables que irán a `USER.md` cuando se implemente: hora de envío (08:30) y secciones diarias.

**Lo que ya sabe (de los archivos de configuración)**
- Tono y estilo: tranquilo, directo, con humor natural, sin relleno (`IDENTITY.md`, `SOUL.md`).
- **Nunca mandar mensajes a medias a un canal de mensajería** (`SOUL.md`): si falla la mayoría de las fuentes, no se envía un resumen cojo, se avisa en una línea.
- **Horas de silencio 23:00–08:00** (`AGENTS.md`): el envío a las **08:30** queda fuera de esa franja. El VPS corre en UTC, así que la hora se fija en `America/Santiago` (lección de `openclaw-connection/notes.md`).
- Cómo programar tareas y dejar su estado (`AGENTS.md`, sección de automatizaciones) y que antes de construir algo a medida se revisan soluciones existentes.
- **Lo que no sabe:** las fuentes, el criterio de importancia, el formato del mensaje ni los límites de Telegram. Eso lo aporta el skill. `USER.md` sigue vacío, así que no conoce los gustos del usuario.

**Lo que debe consultar o generar él mismo**
- Un script (`scripts/leer_titulares.py`) que baja los feeds y los normaliza a JSON: medio, título, enlace, fecha y sección.
- Un script (`scripts/agrupar.py`) que agrupa titulares de distintos medios que hablan de lo mismo, ordena por número de portales, asigna cada grupo a una sección y elige el único enlace a mostrar según la lista de prioridad de medios.
- Un script (`scripts/verificar_enlaces.py`) que comprueba, antes de enviar, que cada enlace elegido abre y **no tiene muro de pago** (ver «Regla de enlaces sin muro de pago»).
- Un historial corto en `memory/noticias/` (ver «Historial»), que el propio script limpia en cada ejecución.
- El agente solo redacta el mensaje final a partir de ese JSON compacto, igual que en el skill de sueños (menos tokens, más rápido).

## 3. ¿Cómo es un buen output?

**Formato:** un solo mensaje de Telegram, en español, de hasta 4096 caracteres (el límite de Telegram), con estas secciones **todos los días**:

1. **Titular principal:** la noticia más repetida entre portales, con 2 o 3 líneas propias, más al menos 3 noticias secundarias de importancia nacional (una línea cada una).
2. **Economía y finanzas.**
3. **Internacional.**
4. **Deportes.**
5. **Otros:** solo aparece si hay algo que no entra en las secciones anteriores y merece atención porque lo cubren muchos medios (propongo 3 o más, máximo 2 ítems). Si no hay nada, la sección se omite.

Cada noticia indica **cuántos medios la cubren** (por ejemplo, «📰 7 medios») y lleva **un solo enlace**: el del medio más importante entre los que la cubren **y que tengan la nota abierta, sin muro de pago** (ver «Regla de enlaces sin muro de pago» más abajo). Ese medio se elige con una lista de prioridad configurable en el skill (propuesta inicial: La Tercera, CNN Chile, Meganoticias, Cooperativa, El Mostrador, El Dínamo, Pauta; en economía, Diario Financiero primero). La prioridad se mantiene tal cual; la regla solo salta a los medios cuyo enlace no cumple.

El texto es propio y breve (nunca copia párrafos de la nota). La cultura no está entre las secciones diarias; si algo cultural se repite mucho, puede aparecer en «Otros».

**Destino:** el chat de Telegram del usuario, enviado por la automatización diaria. Un mensaje por día, a las **08:30 hora de Santiago** (`America/Santiago`).

**Cómo sabremos que funcionó**

| Criterio | Cómo se comprueba |
|---|---|
| Llega a la hora y todos los días | El mensaje aparece en Telegram a las 08:30 `America/Santiago`, sin faltar días. |
| El titular principal es realmente el más repetido | El grupo elegido tiene la mayor cantidad de medios del día y el recuento mostrado coincide con el que calcula el script. |
| Estructura completa | Titular principal con al menos 3 secundarias, y las secciones economía y finanzas, internacional y deportes todos los días. «Otros» solo si hay algo que lo merezca. |
| No excede Telegram | Menos de 4096 caracteres; si hay más material, se recorta, no se parte en varios mensajes. |
| Un enlace libre por noticia | Cada noticia muestra su recuento de medios y como máximo un enlace, del medio de mayor prioridad cuyo enlace sea libre; todos abren y ninguno muestra un muro de pago. |
| Respeto por las fuentes | Solo títulos, texto propio y enlace; no copia contenido de las notas ni lee medios que lo prohíben. |
| Tolera fallos | Si una fuente falla, se omite sin romper el mensaje; si fallan demasiadas, avisa en una línea en vez de mandar un resumen a medias. |
| Historial acotado | `memory/noticias/` nunca conserva más de 7 días de entradas. |
| Es útil de leer | El usuario lo lee en un par de minutos y puede decidir qué abrir. |

## Regla de enlaces sin muro de pago

**Regla:** el mensaje solo incluye un enlace si la nota se puede leer completa sin suscripción. Se mantiene la lista de prioridad de medios; simplemente se recorre en orden y se toma el **primer medio, entre los que cubren esa noticia, cuyo enlace pasa la verificación**. Los medios con muro de pago siguen contando para el ranking y el recuento («7 medios»), pero no se enlazan.

**Estado de acceso por medio** (probado el 20-oct-2026 con una muestra de notas reales de cada portal):

| Medio | Acceso | Cómo se decide el enlace |
|---|---|---|
| La Tercera | **Medido** (muro de pago que cuenta lecturas; no se puede ver desde fuera cuántas quedan) | **Nunca se enlaza**, salvo que en el futuro se encuentre una forma fiable de saber que esa nota es libre. Sí se usa para el ranking y las descripciones del RSS. |
| Diario Financiero | **Mixto** | Se abre la página de la nota y se lee su marca `isAccessibleForFree` (los datos estructurados de la página). Solo se enlaza si dice `true`; en la muestra, la mayoría de las notas de empresas decían `false`. |
| Pauta | Libre | Sus páginas declaran `isAccessibleForFree: true`. |
| CNN Chile, Meganoticias, Cooperativa, El Mostrador, El Dínamo | Libre (en la muestra) | No mostraron ninguna marca de suscripción en las notas revisadas. Aun así se comprueban al enviar, porque pueden cambiar sus condiciones o tener notas premium puntuales. |

**Verificación antes de enviar** (`verificar_enlaces.py`):
1. El enlace responde 200 y no redirige a una página de error ni de suscripción.
2. La página no declara `isAccessibleForFree: false` y no muestra frases de suscripción obligatoria (por ejemplo, «solo para suscriptores»).
3. Si no se puede comprobar (tiempo agotado, página rara), **se trata como no seguro** y se pasa al siguiente medio de la lista.
4. El resultado se recuerda durante la ejecución para no repetir peticiones. Son unas 10 a 20 comprobaciones por resumen.

**Cuando ningún medio tiene enlace libre:** la noticia se mantiene en el resumen con su recuento y su texto, pero **sin enlace**, con una marca discreta («sin enlace libre»). Así un tema muy importante no desaparece solo porque lo cubran únicamente medios de pago.

**Consecuencia:** como La Tercera encabeza la lista pero no se enlaza, en la práctica el primer enlace suele ser de CNN Chile, y en economía la prioridad pasa de Diario Financiero a los demás medios cuando la nota de DF es de pago.

## Verificación de fuentes (20 de octubre de 2026)

Probé cada portal directamente: `robots.txt`, feeds y *news sitemaps*. Resultado:

| Portal | Veredicto | Qué ofrece | Notas |
|---|---|---|---|
| **Emol** | **Excluir** | Tiene sitemaps y páginas legibles. | Su `robots.txt` bloquea expresamente a los agentes de IA y modelos de lenguaje (`ClaudeBot`, `anthropic-ai`, `Claude-Web`, `ChatGPT-User`, `GPTBot`, `PerplexityBot`, `Google-Extended`, entre otros) y también a `Googlebot-News`. Un agente como OpenClaw cae justo en lo que prohíben. Aunque técnicamente se pueda leer, respetamos esa señal. |
| **La Tercera** | Usar | RSS oficial con 100 notas: título, descripción corta, enlace, fecha, sección y autor. | `robots.txt` permisivo (solo bloquea su API interna y el buscador). Tiene muro de pago medido: se usa para el ranking y las descripciones, **nunca como enlace** (ver «Regla de enlaces sin muro de pago»), y se ignora el campo de texto completo que el RSS también trae. |
| **Diario Financiero** | Usar (economía) | *News sitemap* con 25 notas recientes: título, fecha y sección. | `robots.txt` casi abierto. No trae descripción. Parte de sus notas son de pago: se enlaza solo la nota si su página declara que es libre. Ideal para la sección de economía. |
| **Cooperativa** | Usar | RSS con 11 notas y descripción. | Sin fecha en el feed (la fecha va en la URL). Pocas notas: sirve de complemento. |
| **El Mostrador** | Usar | *News sitemap* con 100 notas: título, fecha y sección (por la URL). | Sin descripción. |
| **El Dínamo** | Usar | *News sitemap* con 200 notas: título y fecha. | Sin descripción. |
| **Meganoticias** | Usar | *News sitemap* con unas 137 notas. | Sin descripción. Cubre bien sucesos y deportes. |
| **CNN Chile** | Usar | *News sitemap* con 200 notas. | Mismo formato que El Dínamo. |
| **Pauta** | Usar | *News sitemap* con 100 notas. | Sin descripción. |
| **BioBioChile** | Descartar por ahora | Tiene *news sitemap*. | El archivo que publica está desactualizado (solo notas de julio de 2025); no sirve para el día. |
| **T13, 24horas** | Descartar por ahora | No encontré feed ni *news sitemap* útil. | Se pueden retomar si se quiere leer su portada, pero es más frágil. |
| **Ex-Ante, The Clinic** | Descartar | Rechazan las peticiones automáticas (403). | |
| **Publimetro** | Descartar | Su `robots.txt` parece bloquear a los rastreadores. | No pude confirmarlo del todo. |

**Otros servicios gratuitos revisados**
- **Google Noticias (RSS de Chile):** `news.google.com/rss?hl=es-419&gl=CL&ceid=CL:es-419` responde con unas 34 notas agrupadas por Google. Sirve como **señal extra de importancia** para contrastar nuestro ranking, no como fuente principal: son enlaces redirigidos y sus condiciones de uso son más restrictivas.
- Hay servicios de APIs de noticias (GDELT, NewsAPI y similares) que **no probé**. Los feeds oficiales de los propios medios son más simples, no requieren claves y no dependen de un tercero, así que no los necesito para empezar.
- No existe un agregador chileno gratuito que ofrezca esto listo; lo razonable es construirlo con los feeds de arriba.

**Prueba de concepto del criterio «repetición entre portales»**

Con los titulares reales de ese día, un agrupador simple por palabras comunes (sin IA, sin claves) reunió unos 470 titulares de 8 portales en 323 grupos; 45 de ellos tenían cobertura en al menos 2 medios. Los más grandes del día:

| Portales | Tema |
|---|---|
| 7 | Pérdidas del Fondo E de las AFP |
| 6 | Sistema frontal y aluvión en Santiago |
| 5 | Encerrona a la periodista Mónica Rincón |
| 5 | Juicio de Cathy Barriga |
| 4 | Expulsión de extranjeros detenidos el 18-O |

El resultado es coherente con lo que sería la portada del día. Limitaciones que hay que resolver al implementar: a veces mezcla subtemas del mismo asunto (por ejemplo, varias notas del temporal quedan en un grupo), y para las secciones de deportes y cultura habrá que apoyarse en la sección que traen los feeds (categoría del RSS, palabras clave del sitemap o carpeta de la URL).

### Decisiones tomadas
- **Hora de envío:** 08:30 en `America/Santiago`, fuera de las horas de silencio de `AGENTS.md`.
- **Recuento de medios:** se muestra por noticia, con un solo enlace al medio más importante (lista de prioridad configurable) **cuya nota sea libre, sin muro de pago**.
- **Enlaces sin paywall:** regla obligatoria con verificación antes de enviar; si ningún medio tiene enlace libre, la noticia va sin enlace.
- **Secciones diarias:** titular principal (con secundarias), economía y finanzas, internacional y deportes; más «Otros» solo cuando una noticia fuera de esas categorías lo merece por repetición.
- **Historial:** se guarda poco y con caducidad. Se justifica porque evita repetir la misma noticia al día siguiente sin novedades; el resumen de cada día es corto (titular, recuento y enlace). Se guarda en `memory/noticias/AAAA-MM-DD.json` (JSON, para que la búsqueda de memoria de OpenClaw no lo indexe como texto) y cada ejecución del script borra los archivos con más de **7 días** (ajustable a 14). No hace falta una tarea aparte para la limpieza ni va al repositorio (se agrega a `.gitignore`).

### Pendiente de afinar al implementar
- La lista de prioridad de medios es una propuesta; conviene validarla con unos días de uso.
- Umbral de «Otros»: propuesta de 3 o más medios.
- Asignar cada grupo a una sección usando la categoría del RSS, las palabras clave del sitemap o la carpeta de la URL (p. ej. `/deportes/`, `/mundo/`); los casos ambiguos caen en «Otros» o en la sección más específica.
- Evitar que un grupo mezcle subtemas distintos (el temporal, por ejemplo).

---

# Plantilla para nuevos skills

```md
# Skill N: `nombre-del-skill`
Ubicación: `skills/nombre-del-skill/` · Estado: por diseñar | en desarrollo | probado

## 1. ¿Qué hace?
Una frase.

## 2. ¿Qué input necesita el agente?
**Lo que se le da** — formato y canal.
**Lo que ya sabe (archivos de configuración)** — qué no hay que repetir en el skill y qué falta.
**Lo que debe consultar o generar él mismo** — fuentes, scripts.

## 3. ¿Cómo es un buen output?
**Formato** · **Destino** · **Cómo sabremos que funcionó** (criterios verificables).
```
