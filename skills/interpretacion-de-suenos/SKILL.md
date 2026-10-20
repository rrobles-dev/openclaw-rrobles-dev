---
name: interpretacion-de-suenos
description: "Interpreta sueños con una lectura imaginativa y artística, por diversión: toma el relato del usuario (propio o de un tercero), consulta diccionarios de sueños en la web como fuente de inspiración y teje una interpretación creativa. Mantiene un registro privado para descubrir hilos recurrentes. Úsalo cuando el usuario cuente un sueño o pesadilla ('soñé que…', 'tuve un sueño'), pregunte qué significa soñar con algo, o pida ver los hilos recurrentes de sus sueños. No lo uses para consejos médicos sobre insomnio ni para la función interna de 'dreaming' (DREAMS.md, memory/dreaming/) de OpenClaw."
---
# Interpretación de sueños

Interpreta sueños **por diversión y como juego creativo**, no como ciencia. Los diccionarios web aportan los ingredientes (símbolos y significados tradicionales); el agente los mezcla con el relato y las emociones del usuario para escribir una lectura imaginativa, casi un pequeño cuento o una pieza artística sobre el sueño. No hay una interpretación "correcta": se busca que sea evocadora, sorprendente y que al usuario le resuene.

## Estilo de la lectura

- **Imaginativa y evocadora.** Usa imágenes, metáforas y un tono cálido y juguetón. Puede ser poético, misterioso o con humor, según el ánimo del sueño.
- **Diversión, no veredictos.** Habla en condicional y como invitación ("quizá", "como si", "esta noche tu mente parece haber pintado…"). Nunca anuncies el futuro ni digas qué "significa de verdad" el sueño.
- **Los portales son musas, no jueces.** No evalúes cuál fuente es más creíble ni si coinciden. Si dicen lo mismo, es un hilo fuerte para tejer; si se contradicen, es una tensión interesante para jugar con ella ("una voz dice protección, otra advierte peligro: tu sueño guarda las dos").
- **Parte del relato del usuario.** Sus emociones, sus detalles raros y su contexto mandan sobre cualquier definición de diccionario. Usa los significados como material, no como guion.
- **Sin sermones ni avisos largos.** Basta el tono de juego; una frase ligera al inicio de la conversación alcanza ("lectura de solo fantasía y diversión 🌙"). La única excepción seria está en "Límites y seguridad".

## Cuándo usar este skill

Úsalo cuando:
- El usuario relata un sueño o pesadilla ("soñé que…", "anoche tuve un sueño…").
- Pregunta qué significa soñar con algo concreto ("¿qué significa soñar con una serpiente?").
- Pide ver patrones, símbolos recurrentes o un resumen de sus sueños.

No lo uses cuando:
- Habla de insomnio, calidad del sueño o salud sin relatar un sueño.
- Se refiere al "dreaming" interno de OpenClaw (`DREAMS.md`, `memory/dreaming/`): es otra función y no se toca desde aquí.

## Recursos web

| Fuente de inspiración | Consulta de un símbolo | Notas |
|---|---|---|
| Dream Bible | `https://www.dreambible.com/search.php?q=TERM` | Gratis, solo inglés. Una palabra por búsqueda. Automatizado en el script |
| AuntyFlo | `https://www.auntyflo.com/dream-dictionary/TERM` | Gratis, solo inglés. URL directa, 404 si no existe la entrada. Automatizado en el script |
| Dream Book (interpretdreams.io) | `https://www.interpretdreams.io/es/dream-dictionary/SLUG/` (el script resuelve el slug contra su índice de ~650 entradas) | **En español**, con escenarios, lectura psicológica y cultural. Sitio comercial de una app: solo se lee el diccionario; **nunca uses su herramienta "describe tu sueño"** (enviaría el relato a un tercero). Los nombres de entrada suelen ser en inglés (`snakes`, `flying`) |
| Dream Dictionary | Sin URL de búsqueda: su `robots.txt` prohíbe el buscador interno (`?s=`). Encuentra la entrada con búsqueda web (`site:dreamdictionary.org snake dreams`) y léela con `--url` | Gratis, solo inglés. Solo manual |
| Dream Moods | No usar | Su buscador devuelve 404 y no hay entradas legibles de forma automática |

**Por defecto se consultan Dream Bible, AuntyFlo y Dream Book a la vez**, para tener más material con el que jugar. Si el usuario prefiere uno solo, guarda la preferencia y usa `--portales`. Si nombra otro portal, úsalo.

## Scripts (úsalos en vez de leer páginas completas)

Ahorran tokens y tiempo: el script descarga, limpia el HTML, quita menús y anuncios, trunca y guarda caché 7 días; el agente solo recibe JSON compacto. Detalles en [references/scripts.md](references/scripts.md).

- Consultar símbolos (varios en una llamada):
  `python3 -I skills/interpretacion-de-suenos/scripts/buscar_simbolos.py snake water --comparar --max-entradas 3 --max-chars 600`
  (consulta los tres portales; `--comparar` marca los hilos en común entre los dos en inglés, ya que Dream Book está en español; `--portales dreambible`, `auntyflo` o `interpretdreams` para elegir; separados por coma)
- Una entrada concreta de otro portal: `... buscar_simbolos.py --url <url>`
- Registrar: `python3 -I skills/interpretacion-de-suenos/scripts/registro.py agregar --titulo ... --simbolos "snake,house" ...`
- Tendencias: `python3 -I skills/interpretacion-de-suenos/scripts/registro.py tendencias`

Si el script falla (red, cambio de formato del portal), recurre a WebFetch con la misma URL y avisa al usuario.

## Flujo

1. **Recibe el relato.** Si el usuario ya lo contó, no preguntes si tiene un sueño: pasa al paso 2. Si solo preguntó por un símbolo suelto, salta al paso 4 sin registrar nada.
2. **Elige el recurso.** Usa la preferencia guardada en `memory/suenos/preferencias.md`; si no existe, consulta los tres portales y menciónalo en una línea ("Me inspiro en Dream Bible, AuntyFlo y Dream Book; dime si prefieres otra fuente"). Pregunta solo si el usuario ya expresó una preferencia ambigua.
3. **Extrae los elementos del relato:** personajes, lugares, acciones, objetos, emociones durante el sueño y al despertar. Elige de 3 a 5 símbolos clave: los más cargados emocionalmente o repetidos, no todas las palabras.
4. **Consulta el recurso** con `buscar_simbolos.py` (todos los símbolos en una sola llamada) para cada símbolo clave:
   - Traduce el símbolo al inglés antes de buscar, con una sola palabra por consulta (Dream Book también lo resuelve así). Del texto en español de Dream Book puedes tomar frases e imágenes directamente para la lectura.
   - Los resultados de Dream Bible no siempre incluyen la entrada exacta (por ejemplo, "house" puede devolver "Beach House" primero). Si el título no corresponde al símbolo, repite con `--max-entradas 5`, o sigue un enlace de `ver_tambien` (como "Snakes") y vuelve a consultar con ese término.
   - Si la búsqueda falla o no hay entrada, prueba un sinónimo. Si sigue sin haberla, improvisa tú el símbolo con imaginación y di que es una invención tuya.
   - Parafrasea, no copies texto textual, y cita siempre el enlace consultado.
5. **Junta la inspiración.** Con `--comparar`, `temas_en_comun` te muestra los hilos que los portales comparten: son buenos motivos centrales. Las ideas que aparecen solo en uno, o que se oponen, sirven de giros y contrastes. No pesa ni decide qué fuente "tiene razón".
6. **Escribe la lectura artística** siguiendo "Estilo de la lectura": integra los símbolos con las emociones y el contexto del usuario en una sola historia, no en una lista suelta de definiciones.
7. **Invita a seguir jugando:** máximo 2 o 3 preguntas, abiertas y curiosas, para enriquecer la historia ("¿qué color tenía la luz?", "¿cómo te sentías cuando ocurrió?"). Si el usuario cuenta algo nuevo, ajusta la lectura.
8. **Registra** el sueño con `registro.py agregar` (ver "Registro"), después de interpretar, e indica al usuario que quedó guardado.
9. **Hilos recurrentes:** ejecuta `registro.py tendencias`; si `umbral_cumplido` es verdadero (ver "Hilos recurrentes"), añade el reporte; si no, no lo menciones.

## Formato de la respuesta

Flexible, siempre con este esqueleto:

1. **Título del sueño:** uno breve y con gancho, como el de una obra ("La casa que aprendió a volar").
2. **Lectura artística:** 1 a 3 párrafos cortos que tejen el relato con los símbolos y las emociones. Es el corazón de la respuesta.
3. **Ingredientes:** los símbolos clave en una línea cada uno, con su idea tradicional parafraseada y el enlace de donde salió.
4. **Preguntas** para seguir jugando (máximo 3).
5. **Hilos recurrentes:** solo si hay datos suficientes.

Para consultas de un símbolo suelto ("¿qué significa soñar con agua?"), responde más corto: una imagen evocadora, los ingredientes y una pregunta.

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

## Hilos recurrentes

- Ofrece este reporte cuando haya al menos 5 sueños registrados, o cuando un símbolo, personaje o emoción aparezca 3 o más veces (`registro.py tendencias` lo calcula).
- Preséntalo como el "mapa" de su mundo onírico: símbolos y personajes que vuelven, emociones predominantes y cómo cambian en el tiempo ("la persecución aparece en 4 de los últimos 6 sueños"). Puedes darle un nombre de temporada o de capítulo.
- Mantén el tono de juego: sin diagnósticos. Pregunta con curiosidad si lo relaciona con algo de su vida.
- Si el usuario lo pide con pocos datos, entrégalo igual y dilo con humor ("aún es un boceto").

## Casos especiales

- **Sueño de un tercero:** interpreta igual, pero marca "tercero" en el registro y no lo mezcles en las tendencias del usuario. Pregunta si prefiere no registrarlo.
- **Sueño incompleto o poco recordado:** interpreta lo que hay como un boceto o un fragmento ("un sueño a medio pintar"); registra con estado "parcial". Ofrece volver a preguntar más tarde ("¿quieres que mañana te pregunte si recuerdas más?"). Solo crea una automatización o recordatorio si el usuario acepta, y cuando lo recuerde, actualiza la misma entrada.
- **Varios sueños en un mensaje:** trátalos por separado y registra cada uno.
- **Sueño recurrente:** enlázalo con las entradas previas y destaca qué cambió entre una y otra.
- **Portal no disponible:** menciónalo brevemente, usa el que funcione; si ninguno responde, haz la lectura con simbolismo general e imaginación y dilo en una línea.

## Límites y seguridad

- Es entretenimiento: no presentes la lectura como hecho, predicción ni diagnóstico.
- Si el usuario describe pesadillas recurrentes con angustia fuerte, miedo a dormir, trauma o ideas de hacerse daño, deja de centrarte en el símbolo: responde con empatía y sugiere con tacto hablar con un profesional de salud mental. Si hay riesgo inmediato, indica servicios de emergencia o líneas de ayuda locales.
- No publiques ni envíes el contenido de los sueños a servicios externos sin que el usuario lo pida.
