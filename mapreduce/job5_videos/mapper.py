#!/usr/bin/env python3
"""
JOB 5 - Desempeño de VIDEOS por campaña y plataforma.
Entrada : videos.jsonl
Salida  : <campana>|<plataforma> TAB reproducciones TAB me_gusta TAB comentarios TAB compartidos TAB porcentaje_visto
"""
import json
import sys

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8", newline="\n")   # LF también en Windows

for linea in sys.stdin:
    try:
        v = json.loads(linea)
    except json.JSONDecodeError:
        continue
    print(f"{v['campana']}|{v['plataforma']}\t{v['reproducciones']}\t{v['me_gusta']}"
          f"\t{v['comentarios']}\t{v['compartidos']}\t{v['porcentaje_visto']}")
