#!/usr/bin/env python3
"""
JOB 1 - Ventas (datos estructurados).
Entrada : transacciones.csv
Salida  : <dimension> TAB <valor_total> TAB <cantidad>

La dimensión de agrupación se controla con la variable de entorno DIMENSION
(en Hadoop: -cmdenv DIMENSION=mes):
    ciudad_categoria (por defecto) | mes | sucursal | medio_pago | categoria
"""
import csv
import os
import sys

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8", newline="\n")   # LF también en Windows

DIMENSION = os.environ.get("DIMENSION", "ciudad_categoria")

for fila in csv.reader(sys.stdin):
    if not fila or fila[0] == "id_transaccion":      # se omite el encabezado
        continue
    try:
        (_, _, id_sucursal, ciudad, fecha_hora, _, categoria,
         cantidad, valor_total, medio_pago) = fila
        cantidad, valor_total = int(cantidad), int(valor_total)
    except ValueError:
        sys.stderr.write("reporter:counter:Calidad,Filas_invalidas,1\n")
        continue

    if DIMENSION == "mes":
        clave = fecha_hora[:7]                         # AAAA-MM
    elif DIMENSION == "sucursal":
        clave = id_sucursal
    elif DIMENSION == "medio_pago":
        clave = medio_pago
    elif DIMENSION == "categoria":
        clave = categoria
    else:
        clave = f"{ciudad}|{categoria}"

    print(f"{clave}\t{valor_total}\t{cantidad}")
