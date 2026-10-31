#!/usr/bin/env python3
"""
JOB 2 - Sentimiento. Reducer.
Salida: <fuente|sucursal> TAB n TAB positivos TAB negativos TAB neutros TAB puntaje_promedio TAB indice_neto
indice_neto = (positivos - negativos) / n   -> rango [-1, 1]
"""
import sys

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8", newline="\n")   # LF también en Windows

actual, n, pos, neg, neu, suma = None, 0, 0, 0, 0, 0


def emitir():
    if actual is not None:
        print(f"{actual}\t{n}\t{pos}\t{neg}\t{neu}\t{suma / n:.3f}\t{(pos - neg) / n:.3f}")


for linea in sys.stdin:
    clave, puntaje = linea.rstrip("\r\n").split("\t")
    puntaje = int(puntaje)
    if clave != actual:
        emitir()
        actual, n, pos, neg, neu, suma = clave, 0, 0, 0, 0, 0
    n += 1
    suma += puntaje
    if puntaje > 0:
        pos += 1
    elif puntaje < 0:
        neg += 1
    else:
        neu += 1

emitir()
