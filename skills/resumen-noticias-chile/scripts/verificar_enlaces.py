#!/usr/bin/env python3
"""Comprueba que un enlace abre y que la nota se lee completa, sin muro de pago.

Uso:
  verificar_enlaces.py URL [--acceso libre|mixto|medido]

Reglas:
  medido -> nunca se enlaza (muro que cuenta lecturas; no se puede saber desde fuera).
  mixto  -> la página debe declarar isAccessibleForFree: true.
  libre  -> vale si no declara isAccessibleForFree: false ni pide suscripción.
  En todos los casos: debe responder 200, quedarse en el mismo sitio y no pedir suscripción.
  Si no se puede comprobar (tiempo agotado, error), se trata como NO seguro.
Salida: {"ok": bool, "motivo": str, "url": str}
"""
import argparse, json, re, sys, urllib.request
from urllib.parse import urlparse

UA = "Mozilla/5.0 (compatible; OpenClaw-news/1.0)"
FRASES = re.compile(r"(solo|sólo) para suscriptores|exclusivo para suscriptores|contenido exclusivo para|"
                    r"suscr[ií]bete para (leer|seguir|continuar|acceder)|inicia sesi[oó]n para (leer|continuar)", re.I)


def dominio(u):
    h = urlparse(u).netloc.lower()
    return h[4:] if h.startswith("www.") else h


def bajar(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.status, r.geturl(), r.read(700_000).decode(r.headers.get_content_charset() or "utf-8", "replace")


def analizar(html_txt, acceso):
    """Decide a partir del HTML de la nota."""
    banderas = [b.lower() for b in re.findall(r'"isAccessibleForFree"\s*:\s*"?(true|false)"?', html_txt, re.I)]
    if "false" in banderas:
        return False, "la página declara que es de pago"
    texto = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html_txt, flags=re.S | re.I)
    texto = re.sub(r"<[^>]+>", " ", texto)
    if FRASES.search(texto):
        return False, "pide suscripción"
    if acceso == "mixto" and "true" not in banderas:
        return False, "no declara que sea libre"
    return True, "libre"


def verificar(url, acceso="libre", bajador=bajar):
    if acceso == "medido":
        return {"ok": False, "motivo": "medio con muro de pago medido", "url": url}
    try:
        status, final, cuerpo = bajador(url)
    except Exception as e:
        return {"ok": False, "motivo": f"no se pudo comprobar ({type(e).__name__})", "url": url}
    if status != 200:
        return {"ok": False, "motivo": f"HTTP {status}", "url": url}
    if dominio(final) != dominio(url):
        return {"ok": False, "motivo": "redirige a otro sitio", "url": url}
    ok, motivo = analizar(cuerpo, acceso)
    return {"ok": ok, "motivo": motivo, "url": url}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--acceso", default="libre", choices=["libre", "mixto", "medido"])
    a = ap.parse_args()
    json.dump(verificar(a.url, a.acceso), sys.stdout, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
