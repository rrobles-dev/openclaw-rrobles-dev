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
