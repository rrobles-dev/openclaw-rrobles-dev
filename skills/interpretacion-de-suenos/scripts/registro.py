#!/usr/bin/env python3
"""Registro de sueños y reporte de tendencias (sin gastar tokens leyendo todo).

  registro.py agregar --titulo "Persecución en casa vieja" --origen propio \
      --personajes "madre,desconocido" --lugares "casa de la infancia" \
      --acciones "huir,esconderse" --emociones "miedo,alivio" \
      --simbolos "house,chase" --recurso dreambible --estado completo
  registro.py tendencias [--min-sueños 5] [--min-repeticiones 3]
  registro.py contar

Archivo: memory/suenos/registro.md (privado, en .gitignore). Los sueños de
terceros (--origen tercero) se guardan pero no cuentan en las tendencias.
"""
import argparse, datetime as dt, json, re, sys
from collections import Counter
from pathlib import Path

REG = Path(__file__).resolve().parents[3] / "memory" / "suenos" / "registro.md"
CAMPOS = ["personajes", "lugares", "acciones", "emociones", "simbolos"]
ETIQ = {"personajes": "Personajes", "lugares": "Lugares", "acciones": "Acciones",
        "emociones": "Emociones", "simbolos": "Símbolos clave"}


def lista(s): return [x.strip().lower() for x in (s or "").split(",") if x.strip()]


def leer():
    txt = REG.read_text(encoding="utf-8") if REG.exists() else ""
    bloques = re.split(r"(?m)^## ", txt)[1:]
    out = []
    for b in bloques:
        d = {"cabecera": b.splitlines()[0]}
        for k in CAMPOS:
            m = re.search(rf"(?m)^- {ETIQ[k]}:(.*)$", b)
            d[k] = lista(m.group(1)) if m else []
        m = re.search(r"(?m)^- Fuente del relato:\s*(\w+)", b)
        d["origen"] = m.group(1).lower() if m else "propio"
        out.append(d)
    return out


def agregar(a):
    REG.parent.mkdir(parents=True, exist_ok=True)
    if not REG.exists(): REG.write_text("# Registro de sueños\n", encoding="utf-8")
    fecha = a.fecha or dt.date.today().isoformat()
    bloque = [f"\n## {fecha} — {a.titulo}", f"- Fuente del relato: {a.origen}"]
    for k in CAMPOS:
        bloque.append(f"- {ETIQ[k]}: {', '.join(lista(getattr(a, k)))}")
    bloque += [f"- Recurso consultado: {a.recurso}", f"- Estado: {a.estado}",
               f"- Notas: {a.notas or ''}"]
    with REG.open("a", encoding="utf-8") as f: f.write("\n".join(bloque) + "\n")
    print(json.dumps({"ok": True, "total": len(leer())}, ensure_ascii=False))


def tendencias(a):
    todos = [d for d in leer() if d["origen"] == "propio"]
    n = len(todos)
    cont = {k: Counter(x for d in todos for x in set(d[k])) for k in CAMPOS}
    rep = {k: [[x, c] for x, c in cont[k].most_common() if c >= a.min_repeticiones] for k in CAMPOS}
    hay = n >= a.min_suenos or any(rep.values())
    print(json.dumps({"suenos_propios": n, "umbral_cumplido": hay,
                      "repetidos": rep if hay else {},
                      "ultimos": [d["cabecera"] for d in todos[-5:]]},
                     ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = ap.add_subparsers(dest="cmd", required=True)
    g = s.add_parser("agregar")
    g.add_argument("--titulo", required=True); g.add_argument("--fecha")
    g.add_argument("--origen", choices=["propio", "tercero"], default="propio")
    for k in CAMPOS: g.add_argument(f"--{k}", default="")
    g.add_argument("--recurso", default="dreambible")
    g.add_argument("--estado", choices=["completo", "parcial"], default="completo")
    g.add_argument("--notas")
    t = s.add_parser("tendencias")
    t.add_argument("--min-suenos", type=int, default=5)
    t.add_argument("--min-repeticiones", type=int, default=3)
    s.add_parser("contar")
    a = ap.parse_args()
    if a.cmd == "agregar": agregar(a)
    elif a.cmd == "tendencias": tendencias(a)
    else: print(json.dumps({"total": len(leer())}))


if __name__ == "__main__":
    main()
