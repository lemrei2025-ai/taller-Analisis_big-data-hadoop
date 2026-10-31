#!/usr/bin/env python3
"""
JOB 5 - Videos. Reducer.
Salida: <campana|plataforma> TAB n_videos TAB reproducciones TAB interacciones
        TAB tasa_engagement_pct TAB retencion_promedio_pct
tasa_engagement = (me_gusta + comentarios + compartidos) / reproducciones
"""
import sys

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8", newline="\n")   # LF también en Windows

actual = None
n = rep = inter = 0
ret = 0.0


def emitir():
    if actual is not None:
        tasa = 100 * inter / rep if rep else 0
        print(f"{actual}\t{n}\t{rep}\t{inter}\t{tasa:.2f}\t{100 * ret / n:.1f}")


for linea in sys.stdin:
    clave, r, mg, co, cp, pv = linea.rstrip("\r\n").split("\t")
    if clave != actual:
        emitir()
        actual, n, rep, inter, ret = clave, 0, 0, 0, 0.0
    n += 1
    rep += int(r)
    inter += int(mg) + int(co) + int(cp)
    ret += float(pv)

emitir()
