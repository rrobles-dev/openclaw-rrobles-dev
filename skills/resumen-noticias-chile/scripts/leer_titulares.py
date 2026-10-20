#!/usr/bin/env python3
"""Lee los feeds RSS y news sitemaps de scripts/fuentes.json y devuelve JSON normalizado.

Uso:
  leer_titulares.py                       # todas las fuentes, últimas 30 h
  leer_titulares.py --fuentes cnn,df --horas 12
  leer_titulares.py --refresh             # ignora la caché (20 min)

Salida: {"articulos": [{medio, nombre, titulo, link, fecha, seccion_fuente, descripcion}],
         "estado": {id: {"ok": bool, "n": int, "error"?: str}}}
Solo biblioteca estándar. Solo se usan título, descripción corta, enlace y fecha:
nunca el texto completo de las notas.
"""
import argparse, concurrent.futures as cf, datetime as dt, email.utils, hashlib, html, json, re, sys, time, urllib.request
from pathlib import Path

UA = "Mozilla/5.0 (compatible; OpenClaw-news/1.0)"
AQUI = Path(__file__).resolve().parent
CACHE = AQUI.parent / ".cache"
TTL = 20 * 60


def cargar_fuentes():
    return json.loads((AQUI / "fuentes.json").read_text(encoding="utf-8"))


def fetch(url, refresh=False, ttl=TTL):
    CACHE.mkdir(exist_ok=True)
    f = CACHE / (hashlib.sha1(url.encode()).hexdigest() + ".xml")
    if not refresh and f.exists() and time.time() - f.stat().st_mtime < ttl:
        return f.read_text(encoding="utf-8", errors="replace")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        body = r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")
    f.write_text(body, encoding="utf-8")
    return body


def limpiar(t):
    t = re.sub(r"<!\[CDATA\[|\]\]>", "", t or "")
    t = re.sub(r"<[^>]+>", " ", html.unescape(t))
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def limpiar_sufijo(titulo, nombre):
    """Quita el ' - Meganoticias' o ' | CNN Chile' que algunos medios añaden al título."""
    return re.sub(rf"\s*[-|–]\s*{re.escape(nombre)}\s*$", "", titulo, flags=re.I).strip() or titulo


def parse_fecha(s, link=""):
    """Devuelve datetime en UTC, o None si no hay forma de saberlo."""
    s = (s or "").strip()
    try:
        if s:
            if re.match(r"\d{4}-\d{2}-\d{2}", s):
                d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
            else:
                d = email.utils.parsedate_to_datetime(s)
            if d.tzinfo is None:
                d = d.replace(tzinfo=dt.timezone.utc)
            return d.astimezone(dt.timezone.utc)
    except (ValueError, TypeError):
        pass
    m = re.search(r"/(\d{4})-(\d{2})-(\d{2})/", link)  # Cooperativa lleva la fecha en la URL
    if m:
        return dt.datetime(int(m[1]), int(m[2]), int(m[3]), 12, tzinfo=dt.timezone.utc)
    return None


def _tag(bloque, nombre):
    m = re.search(rf"<{nombre}\b[^>]*>(.*?)</{nombre}>", bloque, re.S)
    return m.group(1) if m else ""


def parse_rss(xml):
    out = []
    for m in re.finditer(r"<item\b.*?</item>", xml, re.S):
        b = m.group(0)
        out.append({"titulo": limpiar(_tag(b, "title")), "link": limpiar(_tag(b, "link")),
                    "fecha": _tag(b, "pubDate"), "seccion_fuente": limpiar(_tag(b, "category")),
                    "descripcion": limpiar(_tag(b, "description"))})
    return out


def parse_sitemap(xml):
    out = []
    for m in re.finditer(r"<url>.*?</url>", xml, re.S):
        b = m.group(0)
        t = re.search(r"<(?:news:|n:)title>(.*?)</(?:news:|n:)title>", b, re.S)
        d = re.search(r"<(?:news:|n:)publication_date>([^<]+)<", b)
        k = re.search(r"<news:keywords>(.*?)</news:keywords>", b, re.S)
        out.append({"titulo": limpiar(t.group(1)) if t else "", "link": limpiar(_tag(b, "loc")),
                    "fecha": d.group(1) if d else "", "seccion_fuente": limpiar(k.group(1)) if k else "",
                    "descripcion": ""})
    return out


def leer_fuente(f, horas=30, refresh=False, ahora=None):
    ahora = ahora or dt.datetime.now(dt.timezone.utc)
    xml = fetch(f["url"], refresh)
    crudos = parse_rss(xml) if f["tipo"] == "rss" else parse_sitemap(xml)
    lim = ahora - dt.timedelta(hours=horas)
    out = []
    for a in crudos:
        if not a["titulo"] or not a["link"].startswith("http"):
            continue
        a["titulo"] = limpiar_sufijo(a["titulo"], f["nombre"])
        d = parse_fecha(a["fecha"], a["link"])
        if d and d < lim:
            continue
        out.append({"medio": f["id"], "nombre": f["nombre"], "titulo": a["titulo"], "link": a["link"],
                    "fecha": d.isoformat() if d else None, "seccion_fuente": a["seccion_fuente"],
                    "descripcion": a["descripcion"][:300]})
    return out


def leer_todas(ids=None, horas=30, refresh=False):
    fuentes = [f for f in cargar_fuentes() if not ids or f["id"] in ids]
    articulos, estado = [], {}

    def uno(f):
        try:
            return f, leer_fuente(f, horas, refresh), None
        except Exception as e:  # una fuente caída no debe romper el resumen
            return f, [], f"{type(e).__name__}: {e}"

    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for f, arts, err in ex.map(uno, fuentes):
            articulos += arts
            estado[f["id"]] = {"ok": err is None and bool(arts), "n": len(arts)}
            if err:
                estado[f["id"]]["error"] = err
            elif not arts:
                estado[f["id"]]["error"] = "sin notas en la ventana de tiempo"
    return articulos, estado


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fuentes", help="ids separados por coma (por defecto, todas)")
    ap.add_argument("--horas", type=int, default=30)
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()
    ids = set(a.fuentes.split(",")) if a.fuentes else None
    arts, est = leer_todas(ids, a.horas, a.refresh)
    json.dump({"articulos": arts, "estado": est}, sys.stdout, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
