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

## Fuentes y scripts

Los scripts descargan, limpian y recortan las páginas, y guardan caché de 7 días: el agente solo recibe JSON compacto (úsalos en vez de leer páginas completas).

- Consultar (varios símbolos en una llamada, en inglés):
  `python3 -I skills/interpretacion-de-suenos/scripts/buscar_simbolos.py snake water --comparar`
- Registrar: `python3 -I skills/interpretacion-de-suenos/scripts/registro.py agregar --titulo ... --simbolos "snake,house" ...`
- Hilos recurrentes: `python3 -I skills/interpretacion-de-suenos/scripts/registro.py tendencias`

Por defecto consulta Dream Bible, AuntyFlo y Dream Book (en español). Portales, opciones y qué hacer si algo falla: [references/portales.md](references/portales.md) y [references/scripts.md](references/scripts.md). **Nunca uses la herramienta «describe tu sueño» de ningún portal.**

## Flujo

1. **Recibe el relato.** Si el usuario ya lo contó, no preguntes si tiene un sueño. Si solo preguntó por un símbolo suelto, salta al paso 4 sin registrar nada.
2. **Elige la fuente.** Usa la preferencia de `memory/suenos/preferencias.md`; si no hay, consulta los tres portales y dilo en una línea ("Me inspiro en Dream Bible, AuntyFlo y Dream Book; dime si prefieres otra").
3. **Extrae del relato** personajes, lugares, acciones, objetos y emociones (durante y al despertar). Elige de 3 a 5 símbolos clave: los más cargados o repetidos.
4. **Consulta** con `buscar_simbolos.py`, una palabra en inglés por símbolo. Si el resultado trae `aviso` (sin entrada exacta o sin resultados), prueba un sinónimo; si sigue sin haberla, improvisa el símbolo y di que es invención tuya. Parafrasea y cita el enlace; no copies texto.
5. **Junta la inspiración.** `temas_en_comun` marca hilos que los portales en inglés comparten: buenos motivos centrales. Lo que aparece en uno solo o se opone sirve de giro o contraste. No decide qué fuente "tiene razón".
6. **Escribe la lectura artística** (ver "Estilo" y "Formato"), integrando símbolos, emociones y contexto en una sola historia.
7. **Invita a seguir jugando:** máximo 2 o 3 preguntas abiertas y curiosas ("¿qué color tenía la luz?"). Si el usuario añade algo, ajusta la lectura.
8. **Registra** con `registro.py agregar` y avisa que quedó guardado ([references/registro.md](references/registro.md)).
9. **Hilos recurrentes:** ejecuta `registro.py tendencias`; si `umbral_cumplido` es verdadero, añade el reporte (cómo presentarlo, en registro.md); si no, no lo menciones.

## Formato de la respuesta

1. **Título del sueño**, breve y con gancho ("La casa que aprendió a volar").
2. **Lectura artística:** 1 a 3 párrafos cortos que tejen el relato con los símbolos y las emociones. Es el corazón de la respuesta.
3. **Ingredientes:** cada símbolo clave en una línea, con su idea tradicional parafraseada y el enlace.
4. **Preguntas** para seguir jugando (máximo 3).
5. **Hilos recurrentes**, solo si hay datos suficientes.

Para un símbolo suelto ("¿qué significa soñar con agua?"): una imagen evocadora, los ingredientes y una pregunta.

## Casos especiales

- **Sueño de un tercero:** interpreta igual; regístralo como "tercero" (no cuenta en los hilos del usuario) y pregunta si prefiere no registrarlo.
- **Sueño incompleto:** léelo como un boceto ("un sueño a medio pintar") y regístralo como "parcial". Ofrece preguntar más tarde si recuerda más; solo programa un recordatorio si acepta.
- **Varios sueños en un mensaje:** trátalos y regístralos por separado.
- **Sueño recurrente:** enlázalo con los anteriores y destaca qué cambió.
- **Portales caídos:** dilo en una línea y haz la lectura con simbolismo general e imaginación.

## Límites y seguridad

- Es entretenimiento: no presentes la lectura como hecho, predicción ni diagnóstico.
- Si el usuario describe pesadillas recurrentes con angustia fuerte, miedo a dormir, trauma o ideas de hacerse daño, deja el juego: responde con empatía y sugiere con tacto hablar con un profesional de salud mental. Si hay riesgo inmediato, indica servicios de emergencia o líneas de ayuda locales.
- Los sueños son datos sensibles: no los menciones fuera de la sesión principal ni los envíes a servicios externos sin que el usuario lo pida.
