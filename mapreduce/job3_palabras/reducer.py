#!/usr/bin/env python3
"""
JOB 3 - Frecuencia de palabras. Reducer (también se usa como combiner).
Salida: <termino> TAB <conteo>
"""
import sys

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8", newline="\n")   # LF también en Windows

actual, total = None, 0
for linea in sys.stdin:
    termino, conteo = linea.rstrip("\r\n").split("\t")
    if termino != actual:
        if actual is not None:
            print(f"{actual}\t{total}")
        actual, total = termino, 0
    total += int(conteo)

if actual is not None:
    print(f"{actual}\t{total}")
