"""Pruebas sin red: python3 -I skills/resumen-noticias-chile/tests/test_scripts.py"""
import datetime as dt, json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import leer_titulares as lt, agrupar as ag, verificar_enlaces as ve, armar_resumen as ar

# ---- lectura ----
RSS = """<rss><channel><item><title><![CDATA[Irán &amp; EE.UU.]]></title><link>https://x.cl/mundo/noticia/a/</link>
<description><![CDATA[<p>Resumen <b>corto</b></p>]]></description><pubDate>Tue, 20 Oct 2026 14:07:41 +0000</pubDate>
<category>Mundo</category><content:encoded><![CDATA[<p>TEXTO COMPLETO NO USAR</p>]]></content:encoded></item></channel></rss>"""
r = lt.parse_rss(RSS)[0]
assert r["titulo"] == "Irán & EE.UU." and r["descripcion"] == "Resumen corto" and r["seccion_fuente"] == "Mundo", r
assert "COMPLETO" not in json.dumps(r)
SM = """<urlset><url><loc>https://df.cl/mercados/a</loc><news:news><news:publication_date>2026-10-19T20:35:00-03:00</news:publication_date>
<news:title><![CDATA[Dólar sube]]></news:title><news:keywords><![CDATA[Mercados, Bolsa &#38; Monedas]]></news:keywords></news:news></url>
<url><loc>https://elmostrador.cl/noticias/pais/x</loc><n:news><n:title>Otro titular</n:title><n:publication_date>2026-10-20T11:13:00-03:00</n:publication_date></n:news></url></urlset>"""
s = lt.parse_sitemap(SM)
assert s[0]["titulo"] == "Dólar sube" and s[0]["seccion_fuente"] == "Mercados, Bolsa & Monedas" and s[1]["titulo"] == "Otro titular", s
d = lt.parse_fecha("2026-10-19T20:35:00-03:00")
assert d == dt.datetime(2026, 10, 19, 23, 35, tzinfo=dt.timezone.utc), d
assert lt.parse_fecha("", "https://c.cl/noticias/x/2026-10-20/110339.html").date() == dt.date(2026, 10, 20)
assert lt.parse_fecha("basura") is None

# ---- clasificación y agrupación ----
def A(medio, titulo, link, cat=""):
    return {"medio": medio, "nombre": medio, "titulo": titulo, "link": link, "fecha": None, "seccion_fuente": cat, "descripcion": ""}
F = [{"id": "cnn", "prioridad": 2}, {"id": "mega", "prioridad": 3}, {"id": "df", "prioridad": 8, "seccion_por_defecto": "economia"},
     {"id": "lt", "prioridad": 1}, {"id": "coop", "prioridad": 4}]
assert ag.clasificar(A("lt", "x", "https://lt.cl/el-deportivo/futbol/a")) == "deportes"
assert ag.clasificar(A("lt", "x", "https://lt.cl/pulso/a")) == "economia"
assert ag.clasificar(A("coop", "x", "https://c.cl/noticias/economia/afp/a")) == "economia"
assert ag.clasificar(A("lt", "x", "https://lt.cl/opinion/a")) == "excluir"
assert ag.clasificar(A("cnn", "x", "https://cnn.cl/pais/a")) == "nacional"
assert ag.clasificar(A("lt", "x", "https://lt.cl/algo/a", "Culto")) == "otros"
assert ag.clasificar(A("df", "x", "https://df.cl/empresas/a"), F[2]) == "economia"
assert ag.clasificar(A("df", "x", "https://df.cl/internacional/a"), F[2]) == "internacional"
assert ag.tokens("Pérdidas del Fondo E de las AFP") == {"perdida", "fondo", "afp"} or "afp" in ag.tokens("Pérdidas del Fondo E de las AFP")

arts = [
    A("lt", "Superintendencia sanciona a las siete AFP por pérdidas del Fondo E", "https://lt.cl/pulso/a"),
    A("cnn", "Regulador inicia sanción a siete AFP por pérdidas en el Fondo E", "https://cnn.cl/pais/a"),
    A("mega", "Siete AFP enfrentan proceso sancionatorio por pérdidas del Fondo E", "https://mega.cl/nacional/1-a"),
    A("cnn", "Lluvia intensa en Santiago: sistema frontal alcanza su peak", "https://cnn.cl/pais/b"),
    A("mega", "Sistema frontal en Santiago: peak de lluvia intensa durante la mañana", "https://mega.cl/nacional/2-b"),
    A("lt", "Columna de opinión sobre las AFP y el Fondo E pérdidas", "https://lt.cl/opinion/c"),
    A("lt", "Colo Colo gana el clásico", "https://lt.cl/el-deportivo/d"),
]
gs = sorted(ag.agrupar(arts, F), key=lambda g: -len(g["medios"]))
assert gs[0]["medios"] == ["cnn", "lt", "mega"] and len(gs) == 3, [(g["medios"], len(g["articulos"])) for g in gs]
assert gs[1]["medios"] == ["cnn", "mega"] and gs[2]["seccion"] == "deportes"
assert all("opinion" not in a["link"] for g in gs for a in g["articulos"])

# palabras genéricas de noticias no deben unir temas distintos (SII en Chile vs. Macron en Francia)
sii = "SII anuncia medidas de alivio tributario para propiedades afectadas por catástrofes naturales en 2026"
mac = "Macron anuncia nuevas medidas a favor de empresas afectadas por violencia callejera en Francia"
assert not ag.similares(ag.tokens(sii), ag.tokens(mac))
assert ag.similares(ag.tokens("Marcel pide a las AFP evaluar compensaciones por pérdidas del Fondo E"),
                    ag.tokens("Mario Marcel apunta contra las AFP por pérdidas del Fondo E y pide evaluar compensación"))

# ---- verificación de enlaces ----
def pagina(cuerpo): return lambda u: (200, u, cuerpo)
assert ve.verificar("https://x.cl/a", "medido")["ok"] is False
assert ve.verificar("https://x.cl/a", "libre", pagina("<p>texto libre</p>"))["ok"]
assert not ve.verificar("https://x.cl/a", "libre", pagina('{"isAccessibleForFree": false}'))["ok"]
assert not ve.verificar("https://x.cl/a", "libre", pagina("<p>Contenido exclusivo para suscriptores</p>"))["ok"]
assert not ve.verificar("https://x.cl/a", "mixto", pagina("<p>sin marca</p>"))["ok"]
assert ve.verificar("https://x.cl/a", "mixto", pagina('{"isAccessibleForFree":"true"}'))["ok"]
assert not ve.verificar("https://x.cl/a", "libre", lambda u: (200, "https://otro.com/z", "ok"))["ok"]
assert not ve.verificar("https://x.cl/a", "libre", lambda u: (_ for _ in ()).throw(TimeoutError()))["ok"]
assert not ve.verificar("https://x.cl/a", "libre", lambda u: (404, u, ""))["ok"]

# ---- selección de enlace: prioridad respetada, saltando lo de pago ----
FU = {"lt": {"nombre": "LT", "prioridad": 1, "acceso": "medido"}, "cnn": {"nombre": "CNN", "prioridad": 2, "acceso": "libre"},
      "df": {"nombre": "DF", "prioridad": 8, "prioridad_economia": 0, "acceso": "mixto"}, "mega": {"nombre": "Mega", "prioridad": 3, "acceso": "libre"}}
g = gs[0]
url, medio = ar.elegir_enlace(g, FU, ve.verificar if False else (lambda u, ac: {"ok": ac != "medido"}))
assert medio == "CNN", medio                       # La Tercera tiene prioridad 1 pero es de pago
url, medio = ar.elegir_enlace(g, FU, lambda u, ac: {"ok": u.startswith("https://mega")})
assert medio == "Mega"                             # CNN falla la verificación: baja al siguiente
assert ar.elegir_enlace(g, FU, lambda u, ac: {"ok": False}) == (None, None)
ge = {"seccion": "economia", "articulos": [dict(arts[0], medio="cnn"), dict(arts[1], medio="df", link="https://df.cl/e/a")]}
assert ar.elegir_enlace(ge, FU, lambda u, ac: {"ok": True})[1] == "DF"   # en economía, DF primero

# titular representativo (el más central) y recorte de descripción
FR = {"a": {"prioridad": 1}, "b": {"prioridad": 2}, "c": {"prioridad": 3}}
def art(m, t): return {"medio": m, "titulo": t, "toks": ag.tokens(t), "link": "https://x/" + m, "descripcion": ""}
gr = {"articulos": [art("a", "Explicativo: qué conviene hacer si quiero pensionarme con la caída del Fondo E"),
                    art("b", "Fondo E: AFP sufren pérdidas millonarias por swaps"),
                    art("c", "Pérdidas del Fondo E: AFP y swaps bajo la lupa del regulador")]}
assert ar.representante(gr, FR)["medio"] in ("b", "c")   # no el explicativo aunque tenga más prioridad
assert lt.limpiar_sufijo("Encerrona a periodista - Meganoticias", "Meganoticias") == "Encerrona a periodista"
assert lt.limpiar_sufijo("Meganoticias abre sede", "Meganoticias") == "Meganoticias abre sede"
assert lt.limpiar_sufijo("Título | CNN Chile", "CNN Chile") == "Título"
gd = {"articulos": [dict(art("a", "Explicativo: qué conviene hacer si quiero pensionarme con la caída del Fondo E"), descripcion="Texto del explicativo"),
                    art("b", "Fondo E: AFP sufren pérdidas millonarias por swaps"),
                    art("c", "Pérdidas del Fondo E: AFP y swaps bajo la lupa del regulador")],
      "medios": ["a", "b", "c"], "seccion": "economia", "toks": []}
FA = {k: dict(v, nombre=k, acceso="libre") for k, v in FR.items()}
it = ar.item(gd, FA)
assert it["titulo"] != gd["articulos"][0]["titulo"]
largo = "palabra " * 60
rc = ar.recortar(largo, 100)
assert rc.endswith("…") and len(rc) <= 101 and not rc[:-1].endswith("palabr") and ar.recortar("corto", 100) == "corto"

# ---- historial: caducidad a 7 días y detección de repetidas ----
carpeta = Path(tempfile.mkdtemp())
hoy = dt.date(2026, 10, 20)
for dias in (1, 5, 7, 8, 12):
    (carpeta / f"{(hoy - dt.timedelta(days=dias)).isoformat()}.json").write_text(json.dumps([{"toks": ["afp", "fondo", "sancion"]}]))
(carpeta / "notas.txt").write_text("no tocar")
ar.podar_historial(hoy, carpeta)
quedan = sorted(p.name for p in carpeta.iterdir())
assert quedan == ["2026-10-13.json", "2026-10-15.json", "2026-10-19.json", "notas.txt"], quedan
h = ar.cargar_historial(hoy, carpeta)
assert ar.repetida_hace(["afp", "fondo", "sancion", "siete"], h, hoy) == 1
assert ar.repetida_hace(["lluvia", "santiago"], h, hoy) is None

# ---- resumen completo con datos falsos y enlaces simulados ----
fuentes = {f["id"]: f for f in lt.cargar_fuentes()}
base = []
temas = [("Fondo E AFP pérdidas sanción Superintendencia", "nacional", ["latercera", "cnn", "mega", "cooperativa", "mostrador"]),
         ("Encerrona periodista Mónica Rincón autopista", "nacional", ["cnn", "mega", "mostrador", "dinamo"]),
         ("Dólar cierra alza cobre mercados bolsa", "economia", ["df", "latercera", "cnn"]),
         ("Lula Bolsonaro debate Brasil elecciones", "internacional", ["cnn", "mostrador", "latercera"]),
         ("Selección chilena clasificatorias partido goles", "deportes", ["mega", "pauta", "latercera"])]
carpetas = {"nacional": "pais", "economia": "negocios", "internacional": "mundo", "deportes": "deportes"}
for t, sec, medios in temas:
    for i, m in enumerate(medios):
        base.append({"medio": m, "nombre": fuentes[m]["nombre"], "titulo": t + (" " * i), "link": f"https://{m}.cl/{carpetas[sec]}/{t[:5]}-{m}",
                     "fecha": None, "seccion_fuente": "", "descripcion": ""})
for i in range(30):
    base.append({"medio": "dinamo", "nombre": "El Dínamo", "titulo": f"Nota suelta número {i} sobre algo distinto zeta{i}", "link": f"https://dinamo.cl/pais/s{i}",
                 "fecha": None, "seccion_fuente": "", "descripcion": ""})
estado = {k: {"ok": True, "n": 5} for k in fuentes}
res = ar.armar(articulos=base, estado=estado, hoy=hoy, verif=lambda u, ac: {"ok": ac != "medido"}, carpeta=Path(tempfile.mkdtemp()))
assert res["ok_para_enviar"], res["avisos"]
assert res["titular"]["medios"] == 5 and res["titular"]["enlace_medio"] == "CNN Chile", res["titular"]
assert res["secundarias"][0]["medios"] == 4 and res["economia"][0]["enlace_medio"] == "Diario Financiero"
assert res["internacional"] and res["deportes"] and not res["otros"]
b = res["borrador"]
assert len(b) <= ar.MAX_CHARS and "TITULAR PRINCIPAL" in b and "Otros" not in b and "📰 5 medios" in b and "martes 20 de octubre" in b
import re
assert b.count("<a href=") == len(re.findall(r"📰 \d+ medio", b))   # un solo enlace por noticia
for i in [res["titular"]] + res["secundarias"] + res["economia"] + res["internacional"] + res["deportes"]:
    assert i["enlace_medio"] != "La Tercera"       # nunca se enlaza un medio de pago medido
# sin enlace libre: la noticia se queda, sin enlace
res2 = ar.armar(articulos=base, estado=estado, hoy=hoy, verif=lambda u, ac: {"ok": False}, carpeta=Path(tempfile.mkdtemp()))
assert res2["titular"]["enlace"] is None and "sin enlace libre" in res2["borrador"] and "<a href=" not in res2["borrador"]
# pocas fuentes -> no enviar
res3 = ar.armar(articulos=base, estado={"cnn": {"ok": True, "n": 1}}, hoy=hoy, verif=lambda u, ac: {"ok": True}, carpeta=Path(tempfile.mkdtemp()))
assert not res3["ok_para_enviar"] and "fuentes respondieron" in res3["avisos"][0]
# borrador largo se recorta a 4000 caracteres sin dejar secciones vacías
largo = dict(res, otros=[dict(res["deportes"][0], titulo="x" * 900) for _ in range(2)],
             economia=[dict(res["economia"][0], titulo="y" * 900) for _ in range(3)])
bl = ar.ajustar(largo, hoy)

assert len(bl) <= ar.MAX_CHARS and "y" * 200 not in bl   # los títulos se acotan a 150 caracteres
# temas nacionales grandes que no caben en las 3 secundarias van como secundarias, no en "Otros"
mas = list(base)
for t, ms in [("Kast instruye expulsión extranjeros detenidos marcha desmanes", ["cnn", "mega", "mostrador", "dinamo", "pauta"]),
              ("Cathy Barriga juicio oral juez inhabilitó audiencia", ["cnn", "mega", "mostrador", "dinamo", "pauta"]),
              ("Seremi anuncia cierre temporal carretera cordillera nieve", ["cnn", "mega", "mostrador"])]:
    for i, m in enumerate(ms):
        mas.append({"medio": m, "nombre": fuentes[m]["nombre"], "titulo": t + (" " * i), "link": f"https://{m}.cl/pais/{t[:5]}-{m}",
                    "fecha": None, "seccion_fuente": "", "descripcion": ""})
r4 = ar.armar(articulos=mas, estado=estado, hoy=hoy, verif=lambda u, ac: {"ok": ac != "medido"}, carpeta=Path(tempfile.mkdtemp()))
medios_sec = [i["medios"] for i in r4["secundarias"]]
assert len(medios_sec) == 5 and medios_sec[:2] == [4, 5] or sorted(medios_sec, reverse=True)[:3] == [5, 5, 4], medios_sec
assert not r4["otros"]
# recorte por importancia: cae primero lo que menos medios tiene, nunca por debajo de 3 secundarias
cargado = dict(r4, deportes=[dict(r4["deportes"][0], titulo="d" * 140, medios=2) for _ in range(2)],
               internacional=[dict(r4["internacional"][0], titulo="i" * 140, medios=2) for _ in range(2)],
               economia=[dict(r4["economia"][0], titulo="e" * 140, medios=m) for m in (6, 5, 3)],
               secundarias=[dict(r4["secundarias"][0], titulo="s" * 140, medios=m) for m in (6, 6, 5, 5, 5)])
cargado["otros"] = [dict(r4["deportes"][0], titulo="o" * 140, medios=3)]
for k in ("secundarias", "economia", "internacional", "deportes", "otros"):
    for it in cargado[k]:
        it["enlace"] = "https://x.cl/" + "z" * 200           # enlaces largos para forzar el recorte
cargado["titular"] = dict(cargado["titular"], enlace="https://x.cl/" + "z" * 200)
assert len(ar.borrador(cargado, hoy)) > ar.MAX_CHARS
bc = ar.ajustar(cargado, hoy)
assert len(bc) <= ar.MAX_CHARS and bc.count("•") >= 3 + 2 + 1 + 1   # 3 secundarias + economía + internacional + deportes mínimos
assert bc.count("s" * 140) >= ar.SECUNDARIAS_MIN                   # las 3 secundarias obligatorias siguen
assert bc.count("d" * 140) + bc.count("i" * 140) < 4                 # lo de 2 medios se recorta antes que lo de 5 o 6
assert all(i["medios"] >= ar.SECUNDARIAS_EXTRA for i in r4["secundarias"][3:]) or len(r4["secundarias"]) <= 3
# el enlace sale de la nota más cercana al titular dentro del medio elegido
gcen = {"seccion": "nacional", "articulos": [dict(art("cnn", "Tema distinto sin relación con el grupo principal"), link="https://cnn/periferica"),
        dict(art("cnn", "Fondo E AFP pérdidas sanción Superintendencia"), link="https://cnn/central"),
        art("mega", "Fondo E AFP pérdidas sanción Superintendencia regulador")]}
FC = {"cnn": {"nombre": "CNN", "prioridad": 1, "acceso": "libre"}, "mega": {"nombre": "Mega", "prioridad": 2, "acceso": "libre"}}
assert ar.elegir_enlace(gcen, FC, lambda u, ac: {"ok": True})[0] == "https://cnn/central"

# guardado de historial
c = Path(tempfile.mkdtemp()); ar.guardar_historial(res, hoy, c)
assert json.loads((c / "2026-10-20.json").read_text())[0]["medios"] == 5
print("OK")
