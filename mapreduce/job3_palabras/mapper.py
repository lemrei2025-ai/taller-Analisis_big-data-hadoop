#!/usr/bin/env python3
"""
JOB 3 - Frecuencia de palabras (conteo clásico de MapReduce) sobre TEXTO, VOZ y VIDEO.
Entrada : resenas.jsonl, llamadas.jsonl, videos.jsonl
Salida  : <termino> TAB 1

Variables de entorno opcionales (-cmdenv):
    NGRAMA=1|2              palabras individuales o pares de palabras (bigramas)
    CALIFICACION_MAX=2      solo reseñas con calificación <= valor (ej. quejas)
    FUENTES=resena,llamada,video   fuentes a incluir
"""
import json
import os
import sys

sys.path[:0] = [os.getcwd(), os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "comun")]
from texto_utils import cargar_stopwords, tokenizar  # noqa: E402

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8", newline="\n")   # LF también en Windows

STOP = cargar_stopwords()
NGRAMA = int(os.environ.get("NGRAMA", "1"))
CAL_MAX = os.environ.get("CALIFICACION_MAX")
FUENTES = set(os.environ.get("FUENTES", "resena,llamada,video").split(","))

for linea in sys.stdin:
    try:
        reg = json.loads(linea)
    except json.JSONDecodeError:
        continue

    if "id_resena" in reg and "resena" in FUENTES:
        if CAL_MAX and reg["calificacion"] > int(CAL_MAX):
            continue
        texto = reg["texto"]
    elif "id_llamada" in reg and "llamada" in FUENTES:
        texto = reg["transcripcion"]
    elif "id_video" in reg and "video" in FUENTES:
        texto = reg["transcripcion"]
    else:
        continue

    tokens = [t for t in tokenizar(texto) if t not in STOP and len(t) > 2]
    if NGRAMA == 2:
        tokens = [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])]
    for t in tokens:
        print(f"{t}\t1")
