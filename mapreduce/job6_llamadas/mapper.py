#!/usr/bin/env python3
"""
JOB 6 - Atención telefónica (VOZ): metadatos de los audios del call center.
Entrada : llamadas.jsonl
Salida  : <clave> TAB duracion_seg TAB resuelta(0|1)

DIMENSION=motivo (por defecto) | sucursal | sucursal_motivo | hora
"""
import json
import os
import sys

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8", newline="\n")   # LF también en Windows

DIMENSION = os.environ.get("DIMENSION", "motivo")

for linea in sys.stdin:
    try:
        ll = json.loads(linea)
    except json.JSONDecodeError:
        continue
    if DIMENSION == "sucursal":
        clave = ll["id_sucursal"]
    elif DIMENSION == "sucursal_motivo":
        clave = f"{ll['id_sucursal']}|{ll['motivo']}"
    elif DIMENSION == "hora":
        clave = ll["fecha_hora"][11:13]
    else:
        clave = ll["motivo"]
    print(f"{clave}\t{ll['duracion_seg']}\t{1 if ll['resuelta'] else 0}")
