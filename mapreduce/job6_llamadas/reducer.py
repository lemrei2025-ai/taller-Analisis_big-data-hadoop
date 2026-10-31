#!/usr/bin/env python3
"""
JOB 6 - Llamadas. Reducer.
Salida: <clave> TAB n_llamadas TAB duracion_promedio_seg TAB pct_resueltas TAB horas_totales
"""
import sys

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8", newline="\n")   # LF también en Windows

actual, n, dur, res = None, 0, 0, 0


def emitir():
    if actual is not None:
        print(f"{actual}\t{n}\t{dur / n:.0f}\t{100 * res / n:.1f}\t{dur / 3600:.1f}")


for linea in sys.stdin:
    clave, d, r = linea.rstrip("\r\n").split("\t")
    if clave != actual:
        emitir()
        actual, n, dur, res = clave, 0, 0, 0
    n += 1
    dur += int(d)
    res += int(r)

emitir()
