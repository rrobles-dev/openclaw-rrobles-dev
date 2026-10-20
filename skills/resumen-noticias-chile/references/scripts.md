# Scripts del skill de noticias

Solo biblioteca estándar de Python 3 (sin `pip install`). Ejecutar desde la raíz del repo con `python3 -I`. Probados con Python 3.14; no usan nada exclusivo de versiones nuevas, pero conviene correr las pruebas en el VPS (Python 3.10).

| Script | Para qué | Salida |
|---|---|---|
| `leer_titulares.py` | Baja los feeds de `fuentes.json`, normaliza y filtra a las últimas 30 h. Caché de 20 min en `.cache/`. | `{articulos: [...], estado: {fuente: {ok, n, error?}}}` |
| `agrupar.py` | Clasifica cada titular por sección (por la carpeta de su URL) y los agrupa por tema entre medios. | Lista de grupos con `medios`, `seccion` |
| `verificar_enlaces.py` | Comprueba que un enlace abre y se lee sin pagar. | `{ok, motivo, url}` |
| `armar_resumen.py` | Orquesta todo, elige enlaces, aplica el historial y redacta el borrador HTML. | JSON completo o solo el borrador |

## `armar_resumen.py`
```
armar_resumen.py [--formato json|borrador] [--horas 30] [--refresh] [--sin-verificar] [--guardar]
```
- `ok_para_enviar` es falso si responden menos de 4 fuentes, hay menos de 30 notas recientes o no hay titular. Con `--formato borrador` en ese caso no imprime el borrador, escribe `NO ENVIAR: ...` en stderr y sale con código 2.
- Cada ítem trae `titulo`, `medios` (cuántos), `nombres`, `seccion`, `descripcion` (si algún feed la da), `otros_titulos`, `repetida_hace_dias`, `enlace` y `enlace_medio` (nulos si ningún medio tiene enlace libre).
- **Orden y selección:** titular = tema nacional con más medios (puede ser de economía); secundarias = 3 nacionales; luego economía (3), internacional (2), deportes (2) y otros (2, con 3 o más medios). Los temas repetidos de días anteriores pierden 2 puntos.
- **Historial:** `memory/noticias/AAAA-MM-DD.json` (ignorado por git). Cada ejecución borra los archivos con más de 7 días.
- `--sin-verificar` salta la comprobación de enlaces; solo para pruebas.

## `verificar_enlaces.py URL --acceso libre|mixto|medido`
- `medido`: nunca ok. `mixto`: ok solo si la página declara `isAccessibleForFree: true`. `libre`: ok si no declara `false` ni pide suscripción.
- Siempre: responde 200, se queda en el mismo sitio y no pide suscripción. Si algo no se puede comprobar, devuelve `ok: false`.

## Limitaciones conocidas
- La agrupación usa palabras en común entre titulares, sin IA. Los temas muy grandes a veces quedan divididos en dos o tres grupos (p. ej. varias notas del temporal); el agente puede unirlos al redactar.
- Un titular se asigna a la sección que dice su URL; si ningún medio tiene carpeta clara, cae en "nacional".
- Si un medio cambia el formato de su feed o de sus URLs, `estado` mostrará `ok: false` o `n: 0` para esa fuente.

## Pruebas
```
python3 -I skills/resumen-noticias-chile/tests/test_scripts.py
```
Sin red. Cubren lectura de feeds, clasificación, agrupación, verificación de enlaces, prioridad con medios de pago, historial con caducidad y recorte a 4000 caracteres.
