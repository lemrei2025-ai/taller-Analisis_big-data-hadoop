#!/usr/bin/env python3
"""
JOB 4 - Análisis de IMÁGENES a partir de sus metadatos y etiquetas de visión.
Entrada : imagenes.jsonl
Salida  : <etiqueta> TAB <sentimiento_visual> TAB <menciona_marca 0|1> TAB <tamano_kb>

DIMENSION=etiqueta (por defecto) | ciudad_etiqueta | origen
"""
import json
import os
import sys

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8", newline="\n")   # LF también en Windows

DIMENSION = os.environ.get("DIMENSION", "etiqueta")
CIUDAD = {"S01": "Bogotá", "S02": "Bogotá", "S03": "Medellín", "S04": "Cali",
          "S05": "Barranquilla", "S06": "Bucaramanga", "S07": "Online"}

for linea in sys.stdin:
    try:
        reg = json.loads(linea)
    except json.JSONDecodeError:
        continue
    marca = 1 if reg.get("menciona_marca") else 0
    valores = f"{reg['sentimiento_visual']}\t{marca}\t{reg['tamano_kb']}"
    if DIMENSION == "origen":
        print(f"{reg['origen']}\t{valores}")
        continue
    for etiqueta in reg["etiquetas"]:
        if DIMENSION == "ciudad_etiqueta":
            print(f"{CIUDAD.get(reg['id_sucursal'], 'otra')}|{etiqueta}\t{valores}")
        else:
            print(f"{etiqueta}\t{valores}")
