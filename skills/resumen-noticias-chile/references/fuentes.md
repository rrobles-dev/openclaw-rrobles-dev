# Fuentes de noticias

La lista está en `scripts/fuentes.json` (id, nombre, tipo, URL, prioridad, acceso). Son feeds RSS y *news sitemaps* públicos de cada medio: listas oficiales de notas recientes con título, fecha y enlace. Verificado el 20 de octubre de 2026.

| Prioridad | Medio | Tipo | Acceso | Notas |
|---|---|---|---|---|
| 1 | La Tercera | RSS | **medido** | Muro de pago que cuenta lecturas: **nunca se enlaza**. Cuenta para el ranking y aporta las descripciones. |
| 2 | CNN Chile | news sitemap | libre | |
| 3 | Meganoticias | news sitemap | libre | |
| 4 | Cooperativa | RSS | libre | Solo ~10 notas, sin fecha en el feed (se toma de la URL). |
| 5 | El Mostrador | news sitemap | libre | |
| 6 | El Dínamo | news sitemap | libre | |
| 7 | Pauta | news sitemap | libre | |
| 8 (0 en economía) | Diario Financiero | news sitemap | **mixto** | Primero en economía. Solo se enlaza si la página declara `isAccessibleForFree: true`. |

**Cómo se elige el enlace:** se recorre la lista en ese orden (en economía, DF primero) y se toma el primer medio que cubre la noticia y cuyo enlace pasa `verificar_enlaces.py`. Los medios de pago cuentan para el recuento, pero no se enlazan.

## Venezuela (portales globales)
Lista aparte en `scripts/fuentes_venezuela.json`, con el mismo formato más un campo opcional `filtro` (expresión regular que debe calzar con título, descripción o URL; sirve para medios generalistas). Verificado el 3 de noviembre de 2026. Estas notas se agrupan entre ellas y **no entran en el ranking de Chile**.

| Prioridad | Medio | Tipo | Acceso | Notas |
|---|---|---|---|---|
| 1 | Infobae | RSS | libre | Feed dedicado `category/venezuela` (~5 notas al día), con filtro por si se cuela otro tema. |
| 2 | Noticias ONU | RSS | libre | Feed de las Américas con filtro `venezuel`; publica pocas notas a la semana. |

Con dos fuentes el recuento suele ser de 1 o 2 medios. Para ampliar la sección hay que sumar medios que no bloqueen agentes de IA (ver abajo).

## Excluidos y por qué
- **Bloquean a ClaudeBot u otros agentes de IA en su `robots.txt` (no usar, aunque tengan buena cobertura de Venezuela):** BBC Mundo, DW, France 24, El País, RFI, AP, CNN en Español, Telemundo, El Mundo, La Vanguardia. Euronews bloquea GPTBot y CCBot, y se descartó por el mismo criterio.
- **Voz de América:** sus feeds en español dejaron de actualizarse en marzo de 2025.
- **Europa Press, ABC:** accesibles, pero sin notas de Venezuela en la prueba.
- **Emol:** su `robots.txt` bloquea expresamente a los agentes de IA (ClaudeBot, anthropic-ai, GPTBot, etc.). No se usa.
- **BioBioChile:** su news sitemap está desactualizado (solo notas de 2025).
- **T13 y 24horas:** sin feed ni sitemap de noticias útil.
- **Ex-Ante y The Clinic:** rechazan peticiones automáticas (403).
- **Publimetro:** su `robots.txt` parece bloquear rastreadores.

## Cómo agregar o quitar un medio
1. Revisa su `robots.txt`: no uses medios que bloqueen agentes de IA o rastreadores en general.
2. Busca un RSS o un `news-sitemap` y comprueba que traiga título, enlace y fecha de hoy.
3. Prueba 4 o 5 notas: ¿abren completas sin suscripción? Define `acceso` como `libre`, `mixto` (según la marca `isAccessibleForFree`) o `medido`.
4. Agrégalo a `scripts/fuentes.json` con su prioridad y revisa que las carpetas de sus URLs estén cubiertas en `SECCIONES` de `scripts/agrupar.py` (por ejemplo `/deportes/`, `/mundo/`).
5. Corre las pruebas y `armar_resumen.py` para ver cómo cambia el resultado.
