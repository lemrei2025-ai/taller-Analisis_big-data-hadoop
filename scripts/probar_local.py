#!/usr/bin/env python3
"""
Simula localmente (sin Hadoop) el flujo  map -> shuffle/sort -> reduce
para depurar los scripts antes de enviarlos al cluster. Funciona en Windows,
Linux y macOS.

Uso (desde la raíz del repositorio):
    python scripts\\probar_local.py                 (todos los trabajos)
    python scripts\\probar_local.py ventas_mes      (un trabajo)
    python scripts\\probar_local.py --ver-map ventas_mes   (muestra las primeras líneas del map)
    python scripts\\probar_local.py ventas_mes DIMENSION=medio_pago   (cambia una variable)

Resultados: resultados\\local\\<trabajo>.tsv
"""

import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = json.load(open(os.path.join(RAIZ, "scripts", "trabajos.json"), encoding="utf-8"))


def ejecutar(script, entrada, variables):
    """Ejecuta un mapper/reducer pasándole 'entrada' por stdin; devuelve su stdout."""
    entorno = dict(os.environ, PYTHONIOENCODING="utf-8", **variables)
    proc = subprocess.run([sys.executable, script], input=entrada, capture_output=True, env=entorno)
    if proc.returncode != 0:
        sys.exit(f"ERROR en {script}:\n{proc.stderr.decode('utf-8', 'replace')}")
    return proc.stdout


def clave(linea):
    return linea.split(b"\t", 1)[0]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--") and "=" not in a]
    extra = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a and not a.startswith("--"))
    ver_map = "--ver-map" in sys.argv
    salida = os.path.join(RAIZ, "resultados", "local")
    os.makedirs(salida, exist_ok=True)

    for t in CONFIG["trabajos"]:
        if args and t["nombre"] not in args:
            continue
        carpeta = os.path.join(RAIZ, "mapreduce", t["job"])
        entrada = b"".join(
            open(os.path.join(RAIZ, "datos", "raw", CONFIG["entradas"][e]["archivo"]), "rb").read()
            for e in t["entradas"])

        # MAP
        variables = {**t["variables"], **extra}
        mapeado = ejecutar(os.path.join(carpeta, "mapper.py"), entrada, variables)
        lineas = mapeado.splitlines(keepends=True)
        if ver_map:
            print(f"--- Primeras 10 líneas del map de {t['nombre']} ---")
            sys.stdout.write(b"".join(lineas[:10]).decode("utf-8"))
        # SHUFFLE & SORT: Hadoop ordena por la clave (texto antes del primer tabulador)
        lineas.sort(key=clave)
        # REDUCE
        reducido = ejecutar(os.path.join(carpeta, "reducer.py"), b"".join(lineas), {})

        nombre = t["nombre"] + "".join(f"_{v.lower()}" for v in extra.values())
        ruta = os.path.join(salida, f"{nombre}.tsv")
        with open(ruta, "wb") as f:
            f.write(reducido)
        n_claves = len(set(clave(l) for l in lineas))
        print(f">> {nombre:<26} map: {len(lineas):>7} pares | claves: {n_claves:>4} | "
              f"salida: resultados\\local\\{nombre}.tsv")
        if extra:
            sys.stdout.write(reducido.decode("utf-8"))


if __name__ == "__main__":
    main()
