#!/usr/bin/env python3
"""
JOB 2 - Sentimiento de TEXTO (reseñas) y VOZ (transcripciones de llamadas).
Entrada : resenas.jsonl y llamadas.jsonl (se pueden pasar ambas con dos -input)
Salida  : <fuente>|<id_sucursal> TAB <puntaje>

Archivos auxiliares (enviados con -files): texto_utils.py, lexico_sentimiento.txt
"""
import json
import os
import sys

sys.path[:0] = [os.getcwd(), os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "comun")]
from texto_utils import cargar_lexico, puntaje_sentimiento, tokenizar  # noqa: E402

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8", newline="\n")   # LF también en Windows

LEXICO = cargar_lexico()

for linea in sys.stdin:
    try:
        reg = json.loads(linea)
    except json.JSONDecodeError:
        sys.stderr.write("reporter:counter:Calidad,JSON_invalido,1\n")
        continue

    if "id_resena" in reg:
        fuente, texto = "texto_resena", reg["texto"]
    elif "id_llamada" in reg:
        fuente, texto = "voz_llamada", reg["transcripcion"]
    else:
        continue

    puntaje = puntaje_sentimiento(tokenizar(texto), LEXICO)
    print(f"{fuente}|{reg['id_sucursal']}\t{puntaje}")
