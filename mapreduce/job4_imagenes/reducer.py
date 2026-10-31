#!/usr/bin/env python3
"""
JOB 4 - Imágenes. Reducer.
Salida: <clave> TAB n_imagenes TAB sentimiento_promedio TAB pct_menciona_marca TAB tamano_total_mb
"""
import sys

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8", newline="\n")   # LF también en Windows

actual, n, sent, marca, kb = None, 0, 0.0, 0, 0


def emitir():
    if actual is not None:
        print(f"{actual}\t{n}\t{sent / n:.3f}\t{100 * marca / n:.1f}\t{kb / 1024:.1f}")


for linea in sys.stdin:
    clave, s, m, t = linea.rstrip("\r\n").split("\t")
    if clave != actual:
        emitir()
        actual, n, sent, marca, kb = clave, 0, 0.0, 0, 0
    n += 1
    sent += float(s)
    marca += int(m)
    kb += int(t)

emitir()
