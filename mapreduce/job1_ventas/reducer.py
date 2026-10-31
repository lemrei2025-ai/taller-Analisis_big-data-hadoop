#!/usr/bin/env python3
"""
JOB 1 - Ventas. Reducer.
Entrada : <clave> TAB <valor_total> TAB <cantidad>   (ordenada por clave)
Salida  : <clave> TAB n_transacciones TAB unidades TAB ventas_totales TAB ticket_promedio
"""
import sys

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8", newline="\n")   # LF también en Windows

clave_actual, n, unidades, ventas = None, 0, 0, 0


def emitir():
    if clave_actual is not None:
        print(f"{clave_actual}\t{n}\t{unidades}\t{ventas}\t{ventas / n:.0f}")


for linea in sys.stdin:
    clave, valor, cantidad = linea.rstrip("\r\n").split("\t")
    if clave != clave_actual:
        emitir()
        clave_actual, n, unidades, ventas = clave, 0, 0, 0
    n += 1
    unidades += int(cantidad)
    ventas += int(valor)

emitir()
