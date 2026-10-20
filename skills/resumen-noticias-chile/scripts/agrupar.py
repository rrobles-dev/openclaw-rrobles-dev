#!/usr/bin/env python3
"""Clasifica titulares por sección y los agrupa por tema entre medios.

Uso: leer_titulares.py | agrupar.py     (lee JSON por stdin, escribe grupos ordenados)

Un grupo reúne titulares de distintos medios sobre lo mismo. Su importancia es el
número de medios distintos que lo cubren. Heurística sin IA: palabras en común.
"""
import json, re, sys, unicodedata
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))  # con python3 -I el directorio del script no entra solo

SECCIONES = {
    "deportes": {"deportes", "deporte", "el-deportivo", "futbol"},
    "internacional": {"mundo", "internacional"},
    "economia": {"economia", "pulso", "negocios", "mercados", "finanzas", "empresas", "emprendimiento",
                 "economia-y-politica", "economia-y-negocios", "tu-dinero"},
    "otros": {"cultura", "culto", "tendencias", "entretencion", "espectaculos", "farandula", "tecnologia",
              "bits", "innovacion", "sostenibilidad", "revista-jengibre", "mujeres-d", "buen-dato",
              "ciencia", "salud", "estilo-de-vida"},
    "excluir": {"opinion", "cnnopinion", "columnas", "cartas-al-director", "videos", "video",
                "presentado-por", "braga", "lodijeronencnn", "noticieros"},
}
SEG2SEC = {seg: sec for sec, segs in SECCIONES.items() for seg in segs}

STOP = set("""de la el en y a los las del que por con un una para se su al lo como mas es sus tras ante sobre entre sin este esta han
ha fue ser son le les no si o u e ya hay desde hasta hacia segun durante cual cuando donde quien luego esto estos estas ese eso anos
ano dias dia nuevo nueva nuevos nuevas primer primera dice afirma asegura aseguro senalo anuncio indico explico mientras ademas
tambien podria puede pueden sera seran hoy ayer manana chile chileno chilena todo todos toda todas otro otra otros otras muy""".split())


def sin_acentos(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def tokens(titulo):
    out = {sin_acentos(w) for w in re.findall(r"\b[A-ZÁÉÍÓÚÑ]{3}\b", titulo)}  # siglas de 3 letras: AFP, PDI, UDI
    for w in re.findall(r"[a-z0-9]{4,}", sin_acentos(titulo)):
        if w in STOP:
            continue
        out.add(w[:-1] if w.endswith("s") and len(w) > 4 else w)
    return out


def clasificar(art, fuente=None):
    """Sección de un titular según la carpeta de su URL; si no hay pista, la categoría de la fuente."""
    segs = [s for s in urlparse(art["link"]).path.strip("/").split("/")[:2]]
    for s in segs:
        if s in SEG2SEC:
            return SEG2SEC[s]
    cat = re.sub(r"[^a-z0-9]+", "-", sin_acentos(art.get("seccion_fuente", ""))).strip("-")
    for c in [cat] + cat.split("-"):
        if c in SEG2SEC:
            return SEG2SEC[c]
    return (fuente or {}).get("seccion_por_defecto", "nacional")


def similares(a, b):
    c = a & b
    return len(c) >= 3 or (len(c) >= 2 and len(c) / len(a | b) >= 0.3)


def agrupar(articulos, fuentes):
    """Devuelve los grupos con el campo 'medios' (ids distintos). Cada titular entra al grupo con el que más comparte."""
    por_id = {f["id"]: f for f in fuentes}
    arts = []
    for a in articulos:
        sec = clasificar(a, por_id.get(a["medio"]))
        if sec == "excluir":
            continue
        arts.append(dict(a, seccion=sec, toks=tokens(a["titulo"])))
    arts.sort(key=lambda a: por_id.get(a["medio"], {}).get("prioridad", 99))
    grupos = []
    for a in arts:
        mejor, puntaje = None, 0
        for g in grupos:
            for m in g["articulos"]:
                if similares(a["toks"], m["toks"]):
                    p = len(a["toks"] & m["toks"])
                    if p > puntaje:
                        mejor, puntaje = g, p
        if mejor:
            mejor["articulos"].append(a)
        else:
            grupos.append({"articulos": [a]})
    for g in grupos:
        g["medios"] = sorted({m["medio"] for m in g["articulos"]})
        g["seccion"] = seccion_grupo(g["articulos"])
        g["toks"] = sorted(set().union(*[m["toks"] for m in g["articulos"]]))
    return grupos


def seccion_grupo(arts):
    """Una sección específica gana si la respaldan al menos 2 medios o la mitad; si no, es nacional."""
    votos = {}
    for m in {a["medio"] for a in arts}:
        secs = [a["seccion"] for a in arts if a["medio"] == m]
        s = max(set(secs), key=secs.count)
        votos.setdefault(s, set()).add(m)
    total = len({a["medio"] for a in arts})
    esp = {s: len(v) for s, v in votos.items() if s != "nacional"}
    if esp:
        s = max(esp, key=esp.get)
        if esp[s] >= 2 or esp[s] * 2 >= total:
            return s
    return "nacional"


def main():
    from leer_titulares import cargar_fuentes
    datos = json.load(sys.stdin)
    gs = agrupar(datos["articulos"], cargar_fuentes())
    gs.sort(key=lambda g: -len(g["medios"]))
    for g in gs:
        for a in g["articulos"]:
            a.pop("toks", None)
    json.dump(gs, sys.stdout, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
