---
name: resumen-noticias-chile
description: "Arma y envía por Telegram el resumen diario de noticias de Chile, tipo diario: titular principal (el tema que más medios cubren), noticias secundarias, economía y finanzas, internacional, deportes y 'otros' si algo lo merece. Lee feeds oficiales de varios medios chilenos, cuenta cuántos medios cubren cada noticia y enlaza solo notas que se pueden leer sin muro de pago. Úsalo cuando la automatización diaria de las 08:30 (hora de Santiago) lo dispare, o cuando el usuario pida 'las noticias de hoy', 'el resumen del día' o 'qué pasó hoy en Chile'. No lo uses para buscar una noticia puntual ni para noticias fuera de Chile."
---
# Resumen diario de noticias de Chile

Cada mañana lee los titulares de varios medios chilenos, detecta qué temas cubren más medios y manda un resumen corto con un enlace libre por noticia. La lectura, la agrupación, la verificación de enlaces y el primer borrador los hacen scripts; el agente solo revisa y pule el mensaje.

## Cuándo usar este skill

Úsalo cuando:
- La automatización diaria (08:30 `America/Santiago`) lo dispara.
- El usuario pide "las noticias de hoy", "el resumen del día", "qué pasó hoy en Chile".

No lo uses cuando:
- Pregunta por una noticia concreta o quiere ampliar una nota (búscala aparte).
- Pide noticias de otros países, o análisis y opinión sobre un hecho.

## Estilo

Tranquilo y directo, como en `IDENTITY.md` y `SOUL.md`. El resumen se lee en un par de minutos: sin relleno, sin opinión propia sobre los hechos, sin alarmismo. El único saludo es una frase breve al inicio del mensaje, si encaja. Texto propio y breve; nunca copies párrafos de las notas.

## Scripts (úsalos en vez de abrir páginas)

Hacen todo el trabajo pesado y entregan un resultado compacto. Detalles en [references/scripts.md](references/scripts.md).

- Resumen completo, borrador listo para Telegram:
  `python3 -I skills/resumen-noticias-chile/scripts/armar_resumen.py --formato borrador`
- Mismo resumen en JSON (secciones, recuentos, descripciones, estado de fuentes):
  `python3 -I skills/resumen-noticias-chile/scripts/armar_resumen.py`
- Después de enviar, guardar en el historial: añade `--guardar`.

Fuentes, prioridad de medios y estado de acceso: [references/fuentes.md](references/fuentes.md).

## Flujo

1. **Ejecuta** `armar_resumen.py` (el JSON si quieres afinar texto; `--formato borrador` si basta con el borrador).
2. **Comprueba `ok_para_enviar`.** Si es falso (pocas fuentes, pocas notas, sin titular), **no envíes un resumen a medias**: avisa en una línea qué falló, por ejemplo "hoy no pude armar el resumen: solo respondieron 3 fuentes".
3. **Pule el borrador:** mantén la estructura, los recuentos de medios y los enlaces tal cual. Puedes mejorar la redacción del titular principal con 2 o 3 líneas propias (usa `descripcion` y `otros_titulos`) y acortar títulos largos. No inventes datos que no estén en el resultado.
4. **Envía por Telegram** en formato HTML ([references/formato.md](references/formato.md)): un solo mensaje, menos de 4000 caracteres.
5. **Guarda en el historial** con `--guardar` solo si el envío salió bien.

## Reglas de contenido

- **Importancia = cuántos medios distintos cubren el tema.** No cambies el orden por criterio propio.
- **Un solo enlace por noticia**, el del medio de mayor prioridad cuya nota se lee completa sin suscripción. Si el resultado no trae enlace, deja "sin enlace libre"; no busques otro por tu cuenta ni enlaces medios de pago.
- **Secciones diarias:** titular principal (con secundarias), economía y finanzas, internacional y deportes. "Otros" solo si el script lo trae. Cultura no es sección fija.
- **↻** marca los temas que ya salieron en días anteriores y siguen vivos; ya vienen ordenados con ese descuento.
- Si dos noticias de una sección tratan del mismo hecho (los temas grandes a veces quedan divididos), puedes unirlas en una línea con sus recuentos.

## Casos especiales

- **Fuente caída:** el script la omite; si el resumen igual cumple el mínimo, envíalo sin mencionarlo.
- **Día con poca noticia:** manda lo que haya; no rellenes secciones vacías.
- **Pedido manual a otra hora:** ejecuta el mismo flujo; no repitas el `--guardar` si ya se guardó hoy.
- **El usuario pide más detalle de una noticia:** usa el enlace del resumen y tu herramienta de lectura; no es parte de este skill.

## Límites

- No leas ni cites medios que prohíben el uso por agentes de IA (por ejemplo Emol); no están en la lista de fuentes y no deben añadirse.
- No uses el texto completo de las notas, aunque algún feed lo incluya.
- Las horas de silencio de `AGENTS.md` (23:00–08:00) siguen vigentes: no envíes antes de las 08:00 salvo petición expresa.
- Programación de la automatización: [references/programacion.md](references/programacion.md).
