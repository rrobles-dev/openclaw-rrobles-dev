#!/usr/bin/env python3
"""Consulta símbolos en un diccionario de sueños y devuelve JSON compacto.

Uso:
  buscar_simbolos.py snake water "dead person"
  buscar_simbolos.py snake --max-entradas 3 --max-chars 500
  buscar_simbolos.py --url https://www.dreamdictionary.org/meaning/snake-dreams/

Portales:
  dreambible (defecto): search.php?q=TERM, permitido por su robots.txt.
  --url: cualquier página de entrada (p. ej. Dream Dictionary, hallada con
         búsqueda web). dreamdictionary.org prohíbe en robots.txt su buscador
         interno (?s=), por eso no se automatiza la búsqueda allí.

Solo biblioteca estándar. Caché en .cache/ (7 días) para no repetir peticiones.
Salida: extractos truncados + enlace; el agente debe parafrasear y citar.
"""
import argparse, hashlib, html, json, re, sys, time, urllib.parse, urllib.request
from html.parser import HTMLParser
from pathlib import Path

UA = "Mozilla/5.0 (compatible; OpenClaw-dream-skill/1.0)"
CACHE = Path(__file__).resolve().parent.parent / ".cache"
TTL = 7 * 24 * 3600
DREAMBIBLE = "https://www.dreambible.com/search.php?q="


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
        out.append({"titulo": e["titulo"], "extracto": trunc(txt, max_chars),
                    "ver_tambien": e["ver_tambien"][:5]})
    return out


def parse_entry_page(page, max_chars):
    p = EntryContentParser(); p.feed(page)
    txt = clean(" ".join(p.text))
    return [{"titulo": clean(p.title), "extracto": trunc(txt, max_chars), "ver_tambien": []}] if txt else []


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("terminos", nargs="*", help="símbolos en inglés, una palabra o frase corta cada uno")
    ap.add_argument("--url", help="página de entrada concreta (en vez de buscar)")
    ap.add_argument("--max-entradas", type=int, default=3)
    ap.add_argument("--max-chars", type=int, default=600, help="caracteres por extracto")
    ap.add_argument("--refresh", action="store_true", help="ignorar caché")
    a = ap.parse_args()
    if not a.terminos and not a.url: ap.error("indica términos o --url")

    jobs = [(t, DREAMBIBLE + urllib.parse.quote_plus(t), "dreambible") for t in a.terminos]
    if a.url: jobs.append((a.url, a.url, "pagina"))
    res = []
    for term, url, kind in jobs:
        r = {"simbolo": term, "fuente": url}
        try:
            page, cached = fetch(url, a.refresh)
            r["cache"] = cached
            r["entradas"] = (parse_dreambible(page, a.max_entradas, a.max_chars, term) if kind == "dreambible"
                             else parse_entry_page(page, a.max_chars))
            if not r["entradas"]:
                r["aviso"] = "sin resultados; prueba un sinónimo o una sola palabra"
        except Exception as e:
            r["error"] = f"{type(e).__name__}: {e}"
        res.append(r)
    json.dump(res, sys.stdout, ensure_ascii=False, indent=1)
    print()


if __name__ == "__main__":
    main()
