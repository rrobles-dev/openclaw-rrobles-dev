# Registro de sueños y hilos recurrentes

## Dónde y cómo
- Carpeta `memory/suenos/` (separada de `memory/dreaming/`, que es de OpenClaw):
  - `registro.md`: un bloque por sueño, el más reciente al final.
  - `preferencias.md`: portal preferido y otras preferencias de este skill.
- Escribe siempre con `registro.py agregar`: añade al final sin sobrescribir (regla de AGENTS.md). No leas el archivo completo; para el balance usa `registro.py tendencias`.
- Ejemplo: `registro.py agregar --titulo "La casa que aprendió a volar" --origen propio --personajes "serpiente" --lugares "casa de la infancia" --acciones "volar,huir" --emociones "miedo,alivio" --simbolos "snake,flying,house" --recurso dreambible --estado completo`

## Formato de cada entrada (lo genera el script)
```md
## YYYY-MM-DD — título corto
- Fuente del relato: propio | tercero
- Personajes:
- Lugares:
- Acciones:
- Emociones:
- Símbolos clave:
- Recurso consultado:
- Estado: completo | parcial
- Notas:
```
Para completar un sueño parcial más tarde, edita esa misma entrada (o añade las aclaraciones en `Notas`) en vez de crear otra.

## Privacidad
- Los sueños son datos sensibles: léelos o menciónalos solo en la sesión principal con el usuario, nunca en grupos ni sesiones compartidas.
- No uses nombres completos de terceros: «mi hermano», «una compañera».
- `memory/suenos/` está en `.gitignore`.

## Hilos recurrentes
- `registro.py tendencias` devuelve `umbral_cumplido` cuando hay al menos 5 sueños propios, o un símbolo, personaje o emoción repetido 3 o más veces. Los sueños de terceros no cuentan.
- Preséntalos como el «mapa» de su mundo onírico: lo que vuelve, las emociones predominantes y cómo cambian («la persecución aparece en 4 de los últimos 6 sueños»). Puedes darle nombre de temporada o capítulo.
- Tono de juego, sin diagnósticos. Pregunta con curiosidad si lo relaciona con algo de su vida.
- Con pocos datos, entrégalo si lo piden y dilo con humor («aún es un boceto»).
