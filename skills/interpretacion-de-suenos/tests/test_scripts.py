"""Pruebas sin red: python3 -I skills/interpretacion-de-suenos/tests/test_scripts.py"""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import buscar_simbolos as b, registro as r

BIBLE = """<body><blockquote><p><b>Mamba Snake</b></p><p>To dream of a mamba <i>x</i>
represents danger.<br/><br/>*Please See <a href="https://www.dreambible.com/search.php?q=Snakes">Snakes</a></p>
<p><b>Snake Skin</b></p><p>Skin text.</p></blockquote></body>"""
e = b.parse_dreambible(BIBLE, 5, 600)
assert [x["titulo"] for x in e] == ["Mamba Snake", "Snake Skin"], e
assert e[0]["ver_tambien"] == ["Snakes"] and "Please See" not in e[0]["extracto"], e
assert len(b.parse_dreambible(BIBLE, 1, 600)) == 1
assert b.parse_dreambible(BIBLE, 5, 600, "snake skin")[0]["titulo"] == "Snake Skin"
assert not b.parse_dreambible("<blockquote><p><b>Dream Themes Menu</b></p><p>x</p></blockquote>", 5, 600)
assert len(b.trunc("palabra " * 200, 50)) <= 51

WP = '<h1 class="entry-title">Snake Dreams</h1><div class="entry-content"><p>Hola <b>mundo</b></p><script>x()</script><div><p>dentro</p></div></div><p>fuera</p>'
w = b.parse_entry_page(WP, 600)
assert w[0]["titulo"] == "Snake Dreams" and "dentro" in w[0]["extracto"] and "fuera" not in w[0]["extracto"] and "x()" not in w[0]["extracto"], w

assert b.coincidencias(["fear of failure and loss", "loss brings fear", "unrelated words only"]) == []
assert b.coincidencias(["snake brings fear and loss", "fear of loss from snake"], excluir=["snake"]) == ["fear", "loss"] or set(b.coincidencias(["snake brings fear and loss", "fear of loss from snake"], excluir=["snake"])) == {"fear", "loss"}
assert b.AuntyParser.parse('<h2 class="node-title field-wrapper text-center"><span>Snake</span></h2><div>Un <b>texto</b></div>You may also like<p>fuera</p>')[0]["texto"] == "Un texto"

IP = '<main><h1>Soñar con volar</h1><p>Promo Dream Book app gratuita que conecta tus sueños con el tiempo y mucho más texto relleno aquí para pasar el largo mínimo de cien caracteres.</p><h2>Escenarios</h2><h3>Alto</h3>Imagina que te deslizas sin esfuerzo por el cielo, con el viento bajo tus alas. Esta sensación de liberación indica deseo de libertad. <a href="/x">agua</a> mientras vuelas.<p>corto</p><h2>Significados de sueños relacionados</h2><p>Esto no debe aparecer porque ya terminó el contenido útil del artículo, aunque sea largo de sobra para pasar el filtro.</p></main>'
ip = b.InterpretParser.parse(IP)
assert ip[0]["titulo"] == "Soñar con volar" and "libertad" in ip[0]["texto"] and "Promo" not in ip[0]["texto"] and "no debe aparecer" not in ip[0]["texto"], ip
IDX = {"snakes", "dream-about-snakes", "black-snake", "flying", "water", "dead-snake", "house-fire", "aguacate"}
assert b.slug_interpret("snake", IDX) == "snakes" and b.slug_interpret("Flying", IDX) == "flying"
assert b.slug_interpret("fire", IDX) == "house-fire" and b.slug_interpret("zzz", IDX) is None and b.slug_interpret("aguacate", IDX) == "aguacate"

r.REG = Path(tempfile.mkdtemp()) / "registro.md"
class A: pass
def add(origen, sim):
    a = A(); a.titulo, a.fecha, a.origen, a.recurso, a.estado, a.notas = "t", "2026-01-01", origen, "dreambible", "completo", ""
    for k in r.CAMPOS: setattr(a, k, "")
    a.simbolos = sim; r.agregar(a)
for _ in range(3): add("propio", "Snake, house")
add("tercero", "snake")
d = r.leer()
assert len(d) == 4 and d[0]["simbolos"] == ["snake", "house"], d
t = A(); t.min_suenos, t.min_repeticiones = 5, 3
import io, contextlib, json
buf = io.StringIO()
with contextlib.redirect_stdout(buf): r.tendencias(t)
o = json.loads(buf.getvalue())
assert o["suenos_propios"] == 3 and ["snake", 3] in o["repetidos"]["simbolos"], o
print("OK")
