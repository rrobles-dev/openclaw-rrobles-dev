# Portales de inspiración

Todos son gratuitos. Las lecturas son simbólicas y sirven como materia prima creativa. Se consultan con `scripts/buscar_simbolos.py` (ver [scripts.md](scripts.md)).

| Portal | Idioma | Consulta de un símbolo | Notas |
|---|---|---|---|
| Dream Bible | inglés | `https://www.dreambible.com/search.php?q=TERM` | Una palabra por búsqueda. Puede devolver entradas parecidas en vez de la exacta («house» → «Beach House»); el script avisa y se resuelve con `--max-entradas 5` o con un término de `ver_tambien` («Snakes»). |
| AuntyFlo | inglés | `https://www.auntyflo.com/dream-dictionary/TERM` | URL directa; 404 si la entrada no existe. |
| Dream Book (interpretdreams.io) | español | `https://www.interpretdreams.io/es/dream-dictionary/SLUG/` | El script resuelve el slug contra el índice de ~650 entradas. Los nombres de entrada suelen estar en inglés (`snakes`, `flying`). Es un sitio comercial de una app: **solo se lee el diccionario; nunca usar su herramienta «describe tu sueño»**, porque enviaría el relato a un tercero. |
| Dream Dictionary (dreamdictionary.org) | inglés | Sin búsqueda automática | Su `robots.txt` prohíbe el buscador interno (`?s=`). Encuentra la entrada con búsqueda web (`site:dreamdictionary.org snake dreams`) y léela con `--url`. |
| Dream Moods | inglés | No usar | Su buscador devuelve 404 y no hay entradas legibles de forma automática. |

## Uso

- Por defecto se consultan los tres automatizados. Para elegir: `--portales dreambible,auntyflo,interpretdreams`.
- La preferencia del usuario se guarda en `memory/suenos/preferencias.md`.
- Traduce el símbolo al inglés antes de buscar, una palabra por consulta. Del texto en español de Dream Book se pueden tomar frases e imágenes para la lectura.
- Parafrasea siempre y cita el enlace; no copies texto textual.
- Si un portal cambia su HTML y devuelve «sin resultados» para símbolos que sí existen, usa WebFetch con la misma URL y avisa al usuario.
