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

## Excluidos y por qué
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
