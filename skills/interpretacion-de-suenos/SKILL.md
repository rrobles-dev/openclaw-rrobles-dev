---
name: interpretacion-de-suenos
description: "Interpreta sueños que el usuario relata (propios o de un tercero) consultando diccionarios de sueños en la web (Dream Bible por defecto) y mantiene un registro privado para detectar patrones. Úsalo cuando el usuario cuente un sueño o pesadilla ('soñé que…', 'tuve un sueño'), pregunte qué significa soñar con algo, o pida ver tendencias de sus sueños. No lo uses para consejos médicos sobre insomnio o para la función interna de 'dreaming' (DREAMS.md, memory/dreaming/) de OpenClaw."
---
# Interpretación de sueños

Interpreta el relato de un sueño con apoyo de diccionarios web, hace preguntas que ayuden a afinar la lectura y registra los sueños para detectar patrones con el tiempo.

## Cuándo usar este skill

Úsalo cuando:
- El usuario relata un sueño o pesadilla ("soñé que…", "anoche tuve un sueño…").
- Pregunta qué significa soñar con algo concreto ("¿qué significa soñar con una serpiente?").
- Pide ver patrones, símbolos recurrentes o un resumen de sus sueños.

No lo uses cuando:
- Habla de insomnio, calidad del sueño o salud sin relatar un sueño.
- Se refiere al "dreaming" interno de OpenClaw (`DREAMS.md`, `memory/dreaming/`): es otra función y no se toca desde aquí.

## Recursos web

| Recurso | Consulta de un símbolo | Notas |
|---|---|---|
| Dream Bible | `https://www.dreambible.com/search.php?q=TERM` | Gratis, solo inglés. Una palabra por búsqueda. Automatizado en el script |
| AuntyFlo | `https://www.auntyflo.com/dream-dictionary/TERM` | Gratis, solo inglés. URL directa, 404 si no existe la entrada. Automatizado en el script |
| Dream Dictionary | Sin URL de búsqueda: su `robots.txt` prohíbe el buscador interno (`?s=`). Encuentra la entrada con búsqueda web (`site:dreamdictionary.org snake dreams`) y léela con `--url` | Gratis, solo inglés. Solo manual |
| Dream Moods | No usar | Su buscador devuelve 404 y no hay entradas legibles de forma automática |

**Por defecto se consultan Dream Bible y AuntyFlo a la vez y se comparan.** Si el usuario prefiere uno solo, guarda la preferencia y usa `--portales`.

Si el usuario nombra otro portal, úsalo. Ningún diccionario tiene validez científica: las lecturas son simbólicas y subjetivas.

## Scripts (úsalos en vez de leer páginas completas)

Ahorran tokens y tiempo: el script descarga, limpia el HTML, quita menús y anuncios, trunca y guarda caché 7 días; el agente solo recibe JSON compacto. Detalles en [references/scripts.md](references/scripts.md).

- Consultar símbolos (varios en una llamada):
  `python3 -I skills/interpretacion-de-suenos/scripts/buscar_simbolos.py snake water --comparar --max-entradas 3 --max-chars 600`
  (consulta ambos portales; `--portales dreambible` o `--portales auntyflo` para uno solo)
- Una entrada concreta de otro portal: `... buscar_simbolos.py --url <url>`
- Registrar: `python3 -I skills/interpretacion-de-suenos/scripts/registro.py agregar --titulo ... --simbolos "snake,house" ...`
- Tendencias: `python3 -I skills/interpretacion-de-suenos/scripts/registro.py tendencias`

Si el script falla (red, cambio de formato del portal), recurre a WebFetch con la misma URL y avisa al usuario.

## Flujo

1. **Recibe el relato.** Si el usuario ya lo contó, no preguntes si tiene un sueño: pasa al paso 2. Si solo preguntó por un símbolo suelto, salta al paso 4 sin registrar nada.
2. **Elige el recurso.** Usa la preferencia guardada en `memory/suenos/preferencias.md`; si no existe, consulta Dream Bible y AuntyFlo y menciónalo en una línea ("Lo contrasto en Dream Bible y AuntyFlo; dime si prefieres otro"). Pregunta solo si el usuario ya expresó una preferencia ambigua.
3. **Extrae los elementos del relato:** personajes, lugares, acciones, objetos, emociones durante el sueño y al despertar. Elige de 3 a 5 símbolos clave: los más cargados emocionalmente o repetidos, no todas las palabras.
4. **Consulta el recurso** con `buscar_simbolos.py` (todos los símbolos en una sola llamada) para cada símbolo clave:
   - Traduce el símbolo al inglés antes de buscar, con una sola palabra por consulta.
   - Los resultados de Dream Bible no siempre incluyen la entrada exacta (por ejemplo, "house" puede devolver "Beach House" primero). Si el título no corresponde al símbolo, repite con `--max-entradas 5`, o sigue un enlace de `ver_tambien` (como "Snakes") y vuelve a consultar con ese término.
   - Si la búsqueda falla o no hay entrada, prueba un sinónimo y luego el recurso de siguiente prioridad. Dile al usuario qué símbolos no encontraste.
   - Parafrasea, no copies texto textual, y cita siempre el enlace consultado.
5. **Contrasta las fuentes.** Con `--comparar`, `temas_en_comun` es solo una pista (palabras compartidas). Lee los extractos y decide tú si los portales coinciden en el sentido. Dilo así: *coinciden* (misma idea en ambos), *se complementan* (enfoques distintos que no se contradicen) o *difieren* (lecturas opuestas; preséntalas ambas, sin forzar una). Si solo un portal tiene la entrada, indícalo y baja la confianza de esa lectura.
6. **Interpreta.** Integra los significados con el contexto y las emociones del usuario, no como lista suelta de símbolos. Presenta varias lecturas posibles cuando el diccionario las da.
7. **Pregunta para afinar:** máximo 2 o 3 preguntas por turno, abiertas y sin sugerir la respuesta. Prioriza las emociones y qué ocurre en la vida real del usuario relacionado con el sueño. Ejemplo: "¿Cómo te sentías en ese momento?".
8. **Registra** el sueño con `registro.py agregar` (ver "Registro"), después de interpretar, e indica al usuario que quedó guardado.
9. **Tendencias:** ejecuta `registro.py tendencias`; si `umbral_cumplido` es verdadero (ver "Tendencias"), añade el reporte; si no, no lo menciones.

## Formato de la respuesta

1. **Resumen:** el sueño en una línea.
2. **Símbolos clave:** cada uno con su significado parafraseado y el enlace de la fuente.
3. **Acuerdo entre fuentes:** una línea (coinciden / se complementan / difieren).
4. **Lectura integrada:** qué podría significar en conjunto, conectado con las emociones reportadas.
5. **Preguntas** de seguimiento (máximo 3).
6. **Tendencias:** solo si hay datos suficientes.

Cierra con una sola línea, solo en la primera interpretación de la conversación: "Es una lectura simbólica orientativa, no un diagnóstico."

## Registro

- **Ubicación:** `memory/suenos/` (el repo ya usa `memory/` como almacén; la subcarpeta evita mezclarlo con `memory/dreaming/`, que pertenece a OpenClaw).
  - `registro.md`: un bloque por sueño, el más reciente al final.
  - `preferencias.md`: recurso web preferido y otras preferencias del usuario para este skill.
- **Escritura:** usa `registro.py agregar`, que añade al final sin sobrescribir lo existente (cumple la regla de AGENTS.md de no pisar memoria). No leas el archivo completo; para tendencias usa `registro.py tendencias`.
- **Formato de cada entrada** (lo genera el script; úsalo como referencia si editas a mano):

```md
## YYYY-MM-DD — título corto
- Fuente del relato: propio | tercero (quién, de forma genérica)
- Personajes:
- Lugares:
- Acciones:
- Emociones (durante / al despertar):
- Símbolos clave:
- Recurso consultado:
- Estado: completo | parcial
- Recurrente: no | sí (ver YYYY-MM-DD)
- Notas del usuario / aclaraciones posteriores:
```

- **Privacidad:** los sueños son datos sensibles.
  - Lee o menciona el registro solo en la sesión principal con el usuario, nunca en grupos ni sesiones compartidas.
  - No incluyas nombres completos de terceros; usa "mi hermano", "una compañera".
  - `memory/suenos/` está en `.gitignore` y no se sube al repo.

## Tendencias

- Genera el reporte cuando haya al menos 5 sueños registrados, o cuando un símbolo, personaje o emoción aparezca 3 o más veces.
- Incluye: símbolos y personajes repetidos, emociones predominantes, evolución en el tiempo (ejemplo: "la persecución aparece en 4 de los últimos 6 sueños") y fechas de referencia.
- Describe lo observado sin diagnosticar. Pregunta al usuario si lo relaciona con algo de su vida.
- Si el usuario pide el reporte con menos datos, entrégalo y aclara que la muestra es pequeña.

## Casos especiales

- **Sueño de un tercero:** interpreta igual, pero marca "tercero" en el registro y no lo mezcles en las tendencias del usuario. Pregunta si prefiere no registrarlo.
- **Sueño incompleto o poco recordado:** interpreta lo que hay y señala que la lectura es parcial; registra con estado "parcial". Ofrece volver a preguntar más tarde ("¿quieres que mañana te pregunte si recuerdas más?"). Solo crea una automatización o recordatorio si el usuario acepta, y cuando lo recuerde, actualiza la misma entrada.
- **Varios sueños en un mensaje:** trátalos por separado y registra cada uno.
- **Sueño recurrente:** enlázalo con las entradas previas y destaca qué cambió entre una y otra.
- **Portal no disponible:** informa, pasa al siguiente recurso; si ninguno responde, ofrece una lectura basada en simbolismo general y dilo claramente.

## Límites y seguridad

- No presentes la interpretación como hecho, predicción o diagnóstico.
- Si el usuario describe pesadillas recurrentes con angustia fuerte, miedo a dormir, trauma o ideas de hacerse daño, deja de centrarte en el símbolo: responde con empatía y sugiere con tacto hablar con un profesional de salud mental. Si hay riesgo inmediato, indica servicios de emergencia o líneas de ayuda locales.
- No publiques ni envíes el contenido de los sueños a servicios externos sin que el usuario lo pida.
