#!/usr/bin/env python3
"""Consulta símbolos en un diccionario de sueños y devuelve JSON compacto.

Uso:
  buscar_simbolos.py snake water "dead person"
  buscar_simbolos.py snake --max-entradas 3 --max-chars 500
  buscar_simbolos.py --url https://www.dreamdictionary.org/meaning/snake-dreams/

Portales (--portales dreambible,auntyflo,interpretdreams; por defecto los tres):
  interpretdreams: en español (Dream Book). Resuelve el símbolo contra su índice
              de ~650 entradas (nombres mayormente en inglés: snakes, flying,
              house…). Solo lee el diccionario; NUNCA usa su herramienta de
              "describe tu sueño" (enviaría el relato a un tercero).
  dreambible: search.php?q=TERM, permitido por su robots.txt.
  auntyflo:   /dream-dictionary/TERM (slug directo; 404 si no existe).
              Dream Moods se descartó: su buscador devuelve 404 y no hay
              entradas legibles de forma automática.
Con --comparar añade, por símbolo, los temas que coinciden entre portales
(pista creativa de palabras compartidas; solo entre los portales en inglés,
porque Dream Book está en español).
  --url: cualquier página de entrada (p. ej. Dream Dictionary, hallada con
         búsqueda web). dreamdictionary.org prohíbe en robots.txt su buscador
         interno (?s=), por eso no se automatiza la búsqueda allí.

Solo biblioteca estándar. Caché en .cache/ (7 días) para no repetir peticiones.
Salida: extractos truncados + enlace; el agente debe parafrasear y citar.
"""
import argparse, hashlib, html, json, re, sys, time, urllib.error, urllib.parse, urllib.request
from html.parser import HTMLParser
from pathlib import Path

UA = "Mozilla/5.0 (compatible; OpenClaw-dream-skill/1.0)"
CACHE = Path(__file__).resolve().parent.parent / ".cache"
TTL = 7 * 24 * 3600
DREAMBIBLE = "https://www.dreambible.com/search.php?q="
AUNTY = "https://www.auntyflo.com/dream-dictionary/"
INTERPRET = "https://www.interpretdreams.io/es/dream-dictionary/"
PORTALES = ("dreambible", "auntyflo", "interpretdreams")


def fetch(url, refresh=False):
    CACHE.mkdir(exist_ok=True)
    f = CACHE / (hashlib.sha1(url.encode()).hexdigest() + ".html")
    if not refresh and f.exists() and time.time() - f.stat().st_mtime < TTL:
        return f.read_text(encoding="utf-8", errors="replace"), True
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        body = r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")
    f.write_text(body, encoding="utf-8")
    return body, False


def clean(t):
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


class DreamBibleParser(HTMLParser):
    """Entradas: <blockquote><p><b>Título</b></p><p>texto…</p>…"""
    def __init__(self):
        super().__init__()
        self.in_bq = self.in_b = self.in_a = False
        self.entries, self.cur = [], None
        self.buf, self.href = [], None

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "blockquote": self.in_bq = True
        elif self.in_bq and tag == "b": self.in_b = True; self.buf = []
        elif self.in_bq and tag == "a": self.href = a.get("href")
        elif self.in_bq and tag == "br": self.buf.append(" ")
        elif tag in ("script", "style"): self.skip = True

    def handle_endtag(self, tag):
        if tag == "blockquote": self.in_bq = False
        elif tag == "b" and self.in_b:
            self.in_b = False
            title = clean("".join(self.buf))
            if title:
                self.cur = {"titulo": title, "texto": [], "ver_tambien": []}
                self.entries.append(self.cur)
            self.buf = []
        elif tag == "a": self.href = None

    def handle_data(self, d):
        if not self.in_bq: return
        if self.in_b: self.buf.append(d); return
        if self.cur is not None:
            if self.href and "q=" in self.href:
                q = urllib.parse.parse_qs(urllib.parse.urlparse(self.href).query).get("q", [""])[0]
                if q and q not in self.cur["ver_tambien"]: self.cur["ver_tambien"].append(q)
            self.cur["texto"].append(d)


class EntryContentParser(HTMLParser):
    """Páginas WordPress (Dream Dictionary): h1.entry-title + div.entry-content."""
    def __init__(self):
        super().__init__()
        self.title, self.text = "", []
        self.mode, self.depth = None, 0

    def handle_starttag(self, tag, a):
        c = dict(a).get("class", "") or ""
        if tag == "h1" and "entry-title" in c: self.mode = "t"
        elif tag == "div" and "entry-content" in c and self.depth == 0: self.depth = 1
        elif self.depth and tag == "div": self.depth += 1
        elif self.depth and tag in ("script", "style", "aside", "figure"): self.depth += 100
        elif self.depth and tag in ("p", "li", "h2", "h3", "br"): self.text.append(" ")

    def handle_endtag(self, tag):
        if tag == "h1": self.mode = None
        elif self.depth and tag == "div": self.depth -= 1
        elif self.depth >= 100 and tag in ("script", "style", "aside", "figure"): self.depth -= 100

    def handle_data(self, d):
        if self.mode == "t": self.title += d
        elif 0 < self.depth < 100: self.text.append(d)


class AuntyParser:
    """Drupal: el artículo va entre <span>Título</span> (node-title) y 'You may also like'."""
    @staticmethod
    def parse(page):
        m = re.search(r'<h2 class="node-title field-wrapper[^>]*><span>(.*?)</span>', page, re.S)
        if not m: return []
        seg = page[m.end(): page.find("You may also like", m.end()) if "You may also like" in page else None]
        seg = re.sub(r"<(script|style|picture|nav)[^>]*>.*?</\1>|<source[^>]*>|<img[^>]*>", "", seg, flags=re.S)
        txt = clean(re.sub(r"<[^>]+>", " ", seg))
        return [{"titulo": clean(m.group(1)), "texto": txt, "ver_tambien": []}] if txt else []


STOP = set("""a about above after again all also an and any are as at be because been before being between both but by can could did do does
doing down during each few for from further had has have having he her here hers him his how i if in into is it its just me more most my no nor not
now of off on once only or other our out over own same she should so some such than that the their them then there these they this those through to
too doesn don didn isn aren wasn good look looks think believe feel feels need want under until up very was we were what when where which while who whom why will with would you your yours dream dreams dreaming dreamt represents
represent represented meaning means mean feelings feeling something someone may might often generally important often one two person people life
waking see seeing seen like way thing things time know make made get gets also even much many well""".split())


def temas(texto):
    from collections import Counter
    c = Counter(w for w in re.findall(r"[a-z]{4,}", texto.lower()) if w not in STOP)
    return c


def coincidencias(textos, top=8, excluir=()):
    """Palabras presentes en todos los portales, ordenadas por la frecuencia mínima."""
    cs = [temas(t) for t in textos if t]
    if len(cs) < 2: return []
    comunes = set.intersection(*[set(c) for c in cs]) - {w.rstrip("s") for w in excluir} - set(excluir)
    comunes = {w for w in comunes if w.rstrip("s") not in {x.rstrip("s") for x in excluir}}
    return [w for w in sorted(comunes, key=lambda w: -min(c[w] for c in cs))[:top]]


class InterpretParser:
    """Dream Book: h1 + párrafos del <main>, sin promociones ni el widget de la app."""
    PROMO = re.compile(r"Dream Book|app gratuita|Imágenes de ejemplo|Toca una imagen|Descub|Describe tu sueño|Gratis|Sin registro", re.I)

    @staticmethod
    def parse(page):
        m = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
        if not m: return []
        titulo = clean(re.sub(r"<[^>]+>", " ", m.group(1)))
        body = re.sub(r"<(script|style|svg|nav|header|footer)[^>]*>.*?</\1>", "", page, flags=re.S)
        mm = re.search(r"<main.*?</main>", body, re.S)
        body = mm.group(0) if mm else body
        body = re.sub(r"<h2\b[^>]*>", "\n##", body)
        body = re.sub(r"</?(p|h1|h3|li|div|br|section|article|ul)\b[^>]*>", "\n", body)
        partes = []
        for linea in re.sub(r"<[^>]+>", "", body).split("\n"):
            t = clean(linea)
            if t.startswith("##"):
                if re.search(r"relacionados|pregunta", t, re.I): break  # fin del contenido útil
                continue
            if len(t) >= 100 and not InterpretParser.PROMO.search(t): partes.append(t)
        txt = " ".join(partes)
        return [{"titulo": titulo, "texto": txt, "ver_tambien": []}] if txt else []


def slug_interpret(term, indice):
    """Elige la entrada del índice que mejor encaja con el símbolo (o None)."""
    base = re.sub(r"[^a-z0-9ñáéíóúü]+", "-", term.lower()).strip("-")
    sing = base[:-1] if base.endswith("s") else base
    for c in (base, base + "s", sing, "dream-about-" + base, "dream-about-" + base + "s", "dream-about-" + sing + "s"):
        if c in indice: return c
    palabras = [w for w in (base.split("-") + [sing]) if w]
    cand = [s for s in indice if all(re.search(rf"(^|-){re.escape(w.rstrip('s'))}s?(-|$)", s) for w in palabras[:len(base.split('-'))])]
    return min(cand, key=len) if cand else None


def trunc(t, n):
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"


RUIDO = {"dream themes menu"}


def parse_dreambible(page, max_ent, max_chars, term=""):
    p = DreamBibleParser(); p.feed(page)
    ents = [e for e in p.entries if e["titulo"].lower() not in RUIDO]
    t = term.lower()  # primero la entrada exacta, luego las que contienen el término
    ents.sort(key=lambda e: (e["titulo"].lower() != t, t not in e["titulo"].lower()))
    out = []
    for e in ents[:max_ent]:
        txt = clean(" ".join(e["texto"]))
        txt = re.sub(r"\*?Please See.*$", "", txt).strip()
        out.append({"titulo": e["titulo"], "_completo": txt, "extracto": trunc(txt, max_chars),
                    "ver_tambien": e["ver_tambien"][:5]})
    return out


def parse_entry_page(page, max_chars):
    p = EntryContentParser(); p.feed(page)
    txt = clean(" ".join(p.text))
    return [{"titulo": clean(p.title), "_completo": txt, "extracto": trunc(txt, max_chars), "ver_tambien": []}] if txt else []


def consultar(portal, term, a):
    """Devuelve el dict de resultado de un símbolo en un portal."""
    if portal == "dreambible":
        url = DREAMBIBLE + urllib.parse.quote_plus(term)
    elif portal == "interpretdreams":
        try:
            idx_html, _ = fetch(INTERPRET, a.refresh)
            indice = set(re.findall(r'href="/es/dream-dictionary/([^"/#?]+)/?"', idx_html))
        except Exception as e:
            return {"portal": portal, "fuente": INTERPRET, "entradas": [], "error": f"{type(e).__name__}: {e}"}
        slug = slug_interpret(term, indice)
        if not slug:
            return {"portal": portal, "fuente": INTERPRET, "entradas": [], "aviso": "sin entrada en el índice; prueba un sinónimo (suele estar en inglés)"}
        url = INTERPRET + slug + "/"
    else:
        url = AUNTY + urllib.parse.quote(re.sub(r"\s+", "-", term.strip().lower()))
    r = {"portal": portal, "fuente": url}
    try:
        page, cached = fetch(url, a.refresh)
        r["cache"] = cached
        if portal == "dreambible":
            ents = parse_dreambible(page, a.max_entradas, a.max_chars, term)
        else:
            parser = InterpretParser if portal == "interpretdreams" else AuntyParser
            ents = [dict(e, extracto=trunc(e["texto"], a.max_chars), _completo=e["texto"]) for e in parser.parse(page)]
            for e in ents: e.pop("texto", None)
        r["entradas"] = ents
        if ents and not any(e["titulo"].lower() == term.lower() for e in ents):
            r["aviso"] = "sin entrada exacta; son entradas parecidas (prueba --max-entradas 5 o un término de ver_tambien)"
        if not ents: r["aviso"] = "sin resultados; prueba un sinónimo o una sola palabra"
    except urllib.error.HTTPError as e:
        gone = e.code in (404, 410)
        r["aviso" if gone else "error"] = f"no existe la entrada ({e.code})" if gone else f"HTTP {e.code}"
        r["entradas"] = []
    except Exception as e:
        r["error"] = f"{type(e).__name__}: {e}"
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("terminos", nargs="*", help="símbolos en inglés, una palabra o frase corta cada uno")
    ap.add_argument("--url", help="página de entrada concreta (en vez de buscar)")
    ap.add_argument("--portales", default=",".join(PORTALES))
    ap.add_argument("--comparar", action="store_true", help="añade coincidencias entre portales")
    ap.add_argument("--max-entradas", type=int, default=3)
    ap.add_argument("--max-chars", type=int, default=600, help="caracteres por extracto")
    ap.add_argument("--refresh", action="store_true", help="ignorar caché")
    a = ap.parse_args()
    if not a.terminos and not a.url: ap.error("indica términos o --url")
    portales = [x for x in a.portales.split(",") if x in PORTALES]
    if not portales: ap.error("portales válidos: " + ", ".join(PORTALES))

    res = []
    for term in a.terminos:
        r = {"simbolo": term, "portales": [consultar(p, term, a) for p in portales]}
        if a.comparar:
            textos = [" ".join(e["_completo"] for e in p["entradas"]) for p in r["portales"] if p.get("entradas") and p["portal"] != "interpretdreams"]  # solo inglés entre sí
            r["comparacion"] = {"portales_con_resultado": len(textos), "temas_en_comun": coincidencias(textos, excluir=term.lower().split())}
        for p in r["portales"]:
            for e in p.get("entradas", []): e.pop("_completo", None)
        res.append(r)
    if a.url:
        r = {"portal": "url", "fuente": a.url}
        try:
            page, cached = fetch(a.url, a.refresh); r["cache"] = cached
            r["entradas"] = parse_entry_page(page, a.max_chars)
            for e in r["entradas"]: e.pop("_completo", None)
        except Exception as e:
            r["error"] = f"{type(e).__name__}: {e}"
        res.append(r)
    json.dump(res, sys.stdout, ensure_ascii=False, indent=1)
    print()


if __name__ == "__main__":
    main()
