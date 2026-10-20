# Scripts del skill de sueños

Solo biblioteca estándar de Python 3 (sin `pip install`). Ejecutar desde la raíz del repo con `python3 -I`.

## Por qué existen

| Sin script | Con script |
|---|---|
| WebFetch de una página de 25–400 KB con menús, anuncios y scripts | JSON de ~1–2 KB con título, extracto y enlaces |
| Una petición por símbolo, repetida en cada conversación | Varios símbolos por llamada y caché local de 7 días |
| Formato de entrada del registro distinto cada vez | Formato fijo, sin releer el archivo completo para contar tendencias |

## `scripts/buscar_simbolos.py`

```
buscar_simbolos.py TERM [TERM ...] [--portales dreambible,auntyflo] [--comparar]
                   [--max-entradas 3] [--max-chars 600] [--refresh]
buscar_simbolos.py --url URL
```

- Términos en inglés, una palabra por consulta (recomendación de Dream Bible).
- Ordena primero la entrada que coincide exactamente con el término y descarta el menú "Dream Themes Menu".
- Cada resultado trae `simbolo`, `fuente` (para citar), `cache`, `entradas[{titulo, extracto, ver_tambien}]`, y `aviso` o `error` si algo falló.
- Los extractos están truncados a propósito: parafrasea y cita el enlace, no copies.
- Caché en `skills/interpretacion-de-suenos/.cache/` (en `.gitignore`). `--refresh` la ignora.
- Portales automatizados: Dream Bible y AuntyFlo (`/dream-dictionary/TERM`, 404 si no existe). Dream Moods se descartó: su buscador devuelve 404.
- `--comparar` añade `comparacion.temas_en_comun`: palabras relevantes presentes en el texto completo de ambos portales (excluye el propio símbolo y palabras vacías). Es solo una pista creativa: señala motivos que ambos portales comparten para usarlos como hilo central de la lectura. No mide credibilidad ni acuerdo entre portales.
- Dream Dictionary: su `robots.txt` prohíbe `?s=`, así que no hay búsqueda automática. Encuentra la URL con búsqueda web y pásala con `--url`.

## `scripts/registro.py`

```
registro.py agregar --titulo T [--fecha YYYY-MM-DD] [--origen propio|tercero]
    [--personajes a,b] [--lugares ..] [--acciones ..] [--emociones ..] [--simbolos ..]
    [--recurso dreambible] [--estado completo|parcial] [--notas ".."]
registro.py tendencias [--min-suenos 5] [--min-repeticiones 3]
registro.py contar
```

- Escribe en `memory/suenos/registro.md` (privado, en `.gitignore`).
- `tendencias` ignora los sueños de terceros y devuelve `umbral_cumplido`, los elementos repetidos por categoría y los últimos 5 títulos.

## Pruebas

```
python3 -I skills/interpretacion-de-suenos/tests/test_scripts.py
```

No usan red ni tocan el registro real. Si un portal cambia su HTML y `buscar_simbolos.py` devuelve `aviso: sin resultados` para símbolos que sí existen, revisa los parsers `DreamBibleParser` y `EntryContentParser`.

## Mantenimiento

- Dream Bible usa HTML antiguo (`<blockquote><p><b>Título</b></p><p>texto`). Si cambia, ajusta el parser y añade el HTML nuevo a las pruebas.
- Respeta los `robots.txt`: no agregues scraping de rutas prohibidas ni peticiones en masa. El script hace una petición por símbolo y cachea.
