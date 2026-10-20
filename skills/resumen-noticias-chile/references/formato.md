# Formato del mensaje

Un solo mensaje de Telegram, en HTML, de menos de 4000 caracteres (el límite de Telegram es 4096). `armar_resumen.py` ya lo recorta si hace falta: primero quita "Otros", luego reduce secundarias y secciones.

## Estructura (todos los días)
1. **TITULAR PRINCIPAL:** el tema nacional con más medios. Título en negrita, recuento, un enlace y 1 a 3 líneas.
2. **Otras noticias importantes:** al menos 3 temas nacionales, una línea y un enlace cada uno.
3. 💰 **Economía y finanzas**
4. 🌎 **Internacional**
5. ⚽ **Deportes**
6. 🔎 **Otros:** solo si algo fuera de las secciones anteriores lo cubren 3 o más medios (máx. 2 ítems).

Cada noticia: `• Título — 📰 N medios · <a href="...">Medio</a>`. Sin enlace libre: `· sin enlace libre`. `↻` = sigue desde días anteriores.

## Etiquetas HTML permitidas en Telegram
`<b>`, `<i>`, `<a href="...">`. Escapa `&`, `<` y `>` en los títulos (el script ya lo hace). No uses Markdown.

## Ejemplo (recortado)
```
🗞️ Resumen del día · martes 20 de octubre

TITULAR PRINCIPAL
Osvaldo Macías responde a biministros por pérdidas del Fondo E
📰 7 medios · Leer en Diario Financiero
Resumen en 1–3 líneas propias.

Otras noticias importantes
• Periodista Mónica Rincón sufre encerrona — 📰 6 medios · CNN Chile
...
💰 Economía y finanzas
• Escondida registra caída en producción — 📰 3 medios · CNN Chile
...
📰 = medios que cubren la noticia · ↻ sigue desde días anteriores
```

## Qué se puede ajustar en el texto
- Redacción del titular principal (sin añadir hechos que no estén en el resultado).
- Acortar títulos largos.
- Unir en una línea dos ítems de la misma sección que son el mismo hecho.

## Qué no se toca
- Recuentos de medios, orden y enlaces.
- Las secciones obligatorias.
