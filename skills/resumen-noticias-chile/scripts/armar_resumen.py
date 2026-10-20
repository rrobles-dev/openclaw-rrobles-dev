#!/usr/bin/env python3
"""Arma el resumen diario de noticias de Chile: lee, agrupa, elige enlaces libres y redacta un borrador.

Uso:
  armar_resumen.py                    # JSON completo (secciones + borrador + estado)
  armar_resumen.py --formato borrador # solo el borrador en HTML de Telegram
  armar_resumen.py --guardar          # además guarda el resumen en el historial (úsalo tras enviar)

Importancia = número de medios distintos que cubren el tema. Titular principal = el tema nacional con más
medios (puede ser de economía); luego secundarias nacionales, economía, internacional, deportes y "otros".
Enlace = un solo enlace por noticia, del medio de mayor prioridad cuya nota pase verificar_enlaces.py.
Historial en memory/noticias/AAAA-MM-DD.json; se borra lo de más de 7 días en cada ejecución.
"""
import argparse, concurrent.futures as cf, datetime as dt, html, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # con python3 -I el directorio del script no entra solo
from leer_titulares import cargar_fuentes, leer_todas
from agrupar import agrupar
from verificar_enlaces import verificar

HISTORIAL = Path(__file__).resolve().parents[3] / "memory" / "noticias"
RETENCION_DIAS = 7
LIMITES = {"secundarias": 3, "economia": 3, "internacional": 2, "deportes": 2, "otros": 2}
MIN_OTROS = 3          # medios mínimos para que algo caiga en "Otros"
MIN_FUENTES_OK = 4
MIN_ARTICULOS = 30
MAX_CHARS = 4000       # Telegram admite 4096
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
         "octubre", "noviembre", "diciembre"]


def hoy_santiago(ahora=None):
    ahora = ahora or dt.datetime.now(dt.timezone.utc)
    try:
        from zoneinfo import ZoneInfo
        return ahora.astimezone(ZoneInfo("America/Santiago")).date()
    except Exception:
        return (ahora - dt.timedelta(hours=3)).date()


# ---------- historial ----------
def podar_historial(hoy, carpeta=None):
    carpeta = carpeta or HISTORIAL
    if not carpeta.exists():
        return
    for f in carpeta.glob("*.json"):
        try:
            d = dt.date.fromisoformat(f.stem)
        except ValueError:
            continue
        if (hoy - d).days > RETENCION_DIAS:
            f.unlink()


def cargar_historial(hoy, carpeta=None):
    carpeta = carpeta or HISTORIAL
    out = []
    if carpeta.exists():
        for f in carpeta.glob("*.json"):
            try:
                d = dt.date.fromisoformat(f.stem)
                if d < hoy:
                    for it in json.loads(f.read_text(encoding="utf-8")):
                        out.append((d, set(it.get("toks", []))))
            except (ValueError, json.JSONDecodeError):
                continue
    return out


def guardar_historial(resumen, hoy, carpeta=None):
    carpeta = carpeta or HISTORIAL
    carpeta.mkdir(parents=True, exist_ok=True)
    items = [resumen["titular"]] if resumen.get("titular") else []
    for k in LIMITES:
        items += resumen.get(k, [])
    (carpeta / f"{hoy.isoformat()}.json").write_text(
        json.dumps([{"titulo": i["titulo"], "seccion": i["seccion"], "medios": i["medios"], "toks": i["_toks"]}
                    for i in items], ensure_ascii=False), encoding="utf-8")


def repetida_hace(toks, historial, hoy):
    """Días desde que apareció un tema parecido, o None."""
    mejor = None
    for d, t in historial:
        u = set(toks) | t
        if u and len(set(toks) & t) / len(u) >= 0.4:
            dias = (hoy - d).days
            mejor = dias if mejor is None else min(mejor, dias)
    return mejor


# ---------- selección ----------
def puntaje(g):
    return len(g["medios"]) - (2 if g.get("repetida") is not None else 0)


def elegir_enlace(g, fuentes, verif=verificar):
    """Primer medio por prioridad cuya nota pasa la verificación (máx. 4 intentos)."""
    clave = "prioridad_economia" if g["seccion"] == "economia" else "prioridad"
    orden = sorted({a["medio"] for a in g["articulos"]},
                   key=lambda m: fuentes[m].get(clave, fuentes[m]["prioridad"]))
    intentos = 0
    for m in orden:
        if fuentes[m]["acceso"] != "medido" and intentos >= 4:
            break
        art = next(a for a in g["articulos"] if a["medio"] == m)
        if fuentes[m]["acceso"] != "medido":
            intentos += 1
        r = verif(art["link"], fuentes[m]["acceso"])
        if r["ok"]:
            return art["link"], fuentes[m]["nombre"]
    return None, None


def recortar(t, n):
    """Corta en un límite de palabra y añade puntos suspensivos si hubo recorte."""
    t = (t or "").strip()
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0].rstrip(",;:. ") + "…"


def ordenar_centrales(g, fuentes):
    """Titulares del grupo del más central al menos: comparten más palabras con los demás medios (empate: prioridad)."""
    freq = {}
    for a in g["articulos"]:
        for t in a["toks"]:
            freq[t] = freq.get(t, 0) + 1

    def pts(a):
        n = len(a["toks"]) or 1
        return (-sum(freq[t] for t in a["toks"]) / n ** 0.5, fuentes[a["medio"]]["prioridad"])
    return sorted(g["articulos"], key=pts)


def representante(g, fuentes):
    return ordenar_centrales(g, fuentes)[0]


def item(g, fuentes):
    orden = ordenar_centrales(g, fuentes)
    rep = orden[0]
    # la descripción solo vale si viene de uno de los 3 titulares más centrales (si no, hablaría de otra cosa)
    desc = next((a["descripcion"] for a in orden[:3] if a.get("descripcion")), "")
    otros = [a["titulo"] for a in g["articulos"] if a["titulo"] != rep["titulo"]][:2]
    return {"titulo": rep["titulo"], "medios": len(g["medios"]), "nombres": [fuentes[m]["nombre"] for m in g["medios"]],
            "seccion": g["seccion"], "descripcion": recortar(desc, 220), "otros_titulos": otros,
            "repetida_hace_dias": g.get("repetida"), "enlace": None, "enlace_medio": None, "_toks": g["toks"]}


def seleccionar(grupos, fuentes):
    grupos = sorted(grupos, key=lambda g: (-puntaje(g), min(fuentes[m]["prioridad"] for m in g["medios"])))
    usados = set()

    def tomar(pred, n):
        out = []
        for i, g in enumerate(grupos):
            if len(out) >= n:
                break
            if i not in usados and pred(g):
                usados.add(i)
                out.append(g)
        return out

    titular = tomar(lambda g: g["seccion"] not in ("deportes", "internacional", "otros"), 1)
    sel = {"titular": titular[0] if titular else None}
    sel["secundarias"] = tomar(lambda g: g["seccion"] == "nacional", LIMITES["secundarias"])
    for sec in ("economia", "internacional", "deportes"):
        sel[sec] = tomar(lambda g, s=sec: g["seccion"] == s, LIMITES[sec])
    sel["otros"] = tomar(lambda g: len(g["medios"]) >= MIN_OTROS, LIMITES["otros"])
    return sel


# ---------- borrador ----------
def esc(t):
    return html.escape(t, quote=False)


def linea(it, marca="•"):
    n = it["medios"]
    s = f'{marca} {esc(it["titulo"])} — 📰 {n} medio{"s" if n != 1 else ""}'
    if it["enlace"]:
        s += f' · <a href="{html.escape(it["enlace"])}">{esc(it["enlace_medio"])}</a>'
    else:
        s += " · sin enlace libre"
    if it["repetida_hace_dias"] is not None:
        s += " ↻"
    return s


def borrador(res, hoy, lim=None):
    lim = dict(LIMITES, **(lim or {}))
    d = f"{DIAS[hoy.weekday()]} {hoy.day} de {MESES[hoy.month - 1]}"
    L = [f"🗞️ <b>Resumen del día · {d}</b>", ""]
    t = res.get("titular")
    if t:
        n = t["medios"]
        L += ["<b>TITULAR PRINCIPAL</b>", f'<b>{esc(t["titulo"])}</b>',
              f'📰 {n} medio{"s" if n != 1 else ""}' + (f' · <a href="{html.escape(t["enlace"])}">Leer en {esc(t["enlace_medio"])}</a>'
                                                       if t["enlace"] else " · sin enlace libre")]
        if t["descripcion"]:
            L.append(esc(t["descripcion"]))
        L.append("")
    if res["secundarias"][:lim["secundarias"]]:
        L += ["<b>Otras noticias importantes</b>"] + [linea(i) for i in res["secundarias"][:lim["secundarias"]]] + [""]
    for clave, titulo in (("economia", "💰 <b>Economía y finanzas</b>"), ("internacional", "🌎 <b>Internacional</b>"),
                          ("deportes", "⚽ <b>Deportes</b>"), ("otros", "🔎 <b>Otros</b>")):
        visibles = res[clave][:lim[clave]]
        if visibles:
            L += [titulo] + [linea(i) for i in visibles] + [""]
    L.append("📰 = medios que cubren la noticia · ↻ sigue desde días anteriores")
    return "\n".join(L)


def ajustar(res, hoy):
    """Reduce secciones hasta que el borrador quepa en Telegram."""
    lim = {}
    for paso in (("otros", 0), ("secundarias", 2), ("economia", 2), ("internacional", 1), ("deportes", 1),
                 ("economia", 1), ("secundarias", 1)):
        b = borrador(res, hoy, lim)
        if len(b) <= MAX_CHARS:
            return b
        lim[paso[0]] = paso[1]
    return borrador(res, hoy, lim)[:MAX_CHARS]


# ---------- orquestación ----------
def armar(horas=30, refresh=False, verificar_enlaces=True, hoy=None, articulos=None, estado=None,
          verif=verificar, carpeta=None):
    hoy = hoy or hoy_santiago()
    fuentes = {f["id"]: f for f in cargar_fuentes()}
    if articulos is None:
        articulos, estado = leer_todas(None, horas, refresh)
    podar_historial(hoy, carpeta)
    historial = cargar_historial(hoy, carpeta)
    grupos = agrupar(articulos, list(fuentes.values()))
    for g in grupos:
        g["repetida"] = repetida_hace(g["toks"], historial, hoy)
    sel = seleccionar(grupos, fuentes)
    res = {"fecha": hoy.isoformat(), "estado_fuentes": estado}
    res["titular"] = item(sel["titular"], fuentes) if sel["titular"] else None
    for k in LIMITES:
        res[k] = [item(g, fuentes) for g in sel[k]]
    todos = ([res["titular"]] if res["titular"] else []) + [i for k in LIMITES for i in res[k]]
    if verificar_enlaces:
        grupos_sel = ([sel["titular"]] if sel["titular"] else []) + [g for k in LIMITES for g in sel[k]]
        with cf.ThreadPoolExecutor(max_workers=6) as ex:
            for it, (url, medio) in zip(todos, ex.map(lambda g: elegir_enlace(g, fuentes, verif), grupos_sel)):
                it["enlace"], it["enlace_medio"] = url, medio
    ok_f = sum(1 for e in (estado or {}).values() if e.get("ok"))
    avisos = []
    if ok_f < MIN_FUENTES_OK:
        avisos.append(f"solo {ok_f} fuentes respondieron (mínimo {MIN_FUENTES_OK})")
    if len(articulos) < MIN_ARTICULOS:
        avisos.append(f"solo {len(articulos)} notas recientes (mínimo {MIN_ARTICULOS})")
    if not res["titular"]:
        avisos.append("no se pudo determinar un titular principal")
    res["ok_para_enviar"] = not avisos
    res["avisos"] = avisos
    res["borrador"] = ajustar(res, hoy)
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--formato", choices=["json", "borrador"], default="json")
    ap.add_argument("--horas", type=int, default=30)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--sin-verificar", action="store_true", help="no comprueba enlaces (solo pruebas)")
    ap.add_argument("--guardar", action="store_true", help="guarda en el historial (tras enviar)")
    a = ap.parse_args()
    res = armar(a.horas, a.refresh, not a.sin_verificar)
    if a.guardar and res["ok_para_enviar"]:
        guardar_historial(res, hoy_santiago())
    if a.formato == "borrador":
        if not res["ok_para_enviar"]:
            print("NO ENVIAR: " + "; ".join(res["avisos"]), file=sys.stderr)
            sys.exit(2)
        print(res["borrador"])
    else:
        for it in ([res["titular"]] if res["titular"] else []) + [i for k in LIMITES for i in res[k]]:
            it.pop("_toks", None)
        json.dump(res, sys.stdout, ensure_ascii=False, indent=1)
        print()


if __name__ == "__main__":
    main()
