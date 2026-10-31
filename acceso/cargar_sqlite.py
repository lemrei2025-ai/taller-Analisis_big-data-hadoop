#!/usr/bin/env python3
"""
CAPA 4 - ACCESO A LOS DATOS.

Carga los resultados de MapReduce en una base de datos SQLite
(resultados/analitica.db) junto con los catálogos de sucursales y productos,
de modo que puedan consultarse con SQL desde cualquier herramienta
(DBeaver, Power BI, Excel, Python, etc.).

Uso:
    python acceso\\cargar_sqlite.py                 # usa resultados/hadoop o, si no existe, resultados/local
    python acceso\\cargar_sqlite.py --origen local
"""

import argparse
import csv
import os
import sqlite3

from esquema_resultados import ESQUEMAS, RAIZ, carpeta_resultados, leer_resultado


def tipo_sql(valor):
    if isinstance(valor, int):
        return "INTEGER"
    if isinstance(valor, float):
        return "REAL"
    return "TEXT"


def cargar_tabla(con, nombre, filas):
    if not filas:
        return
    columnas = list(filas[0])
    definicion = ", ".join(f"{c} {tipo_sql(filas[0][c])}" for c in columnas)
    con.execute(f"DROP TABLE IF EXISTS {nombre}")
    con.execute(f"CREATE TABLE {nombre} ({definicion})")
    marcadores = ", ".join("?" for _ in columnas)
    con.executemany(f"INSERT INTO {nombre} VALUES ({marcadores})",
                    [tuple(f[c] for c in columnas) for f in filas])


def cargar_catalogo(con, archivo, tabla):
    ruta = os.path.join(RAIZ, "datos", "raw", archivo)
    with open(ruta, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    cargar_tabla(con, tabla, filas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--origen", choices=["auto", "hadoop", "local"], default="auto")
    args = ap.parse_args()

    ruta_db = os.path.join(RAIZ, "resultados", "analitica.db")
    con = sqlite3.connect(ruta_db)
    print(f"Origen de resultados: {carpeta_resultados(args.origen)}")

    cargar_catalogo(con, "sucursales.csv", "dim_sucursal")
    cargar_catalogo(con, "productos.csv", "dim_producto")
    for nombre in ESQUEMAS:
        try:
            filas = leer_resultado(nombre, args.origen)
        except FileNotFoundError:
            print(f"  (sin archivo) {nombre}")
            continue
        cargar_tabla(con, nombre, filas)
        print(f"  tabla {nombre:<26} {len(filas):>5} filas")

    # Vista de ejemplo que integra varias fuentes (ventas + texto + voz).
    con.executescript("""
        DROP VIEW IF EXISTS v_tablero_sucursal;
        CREATE VIEW v_tablero_sucursal AS
        SELECT s.id_sucursal, s.nombre, s.ciudad,
               v.ventas_totales, v.ticket_promedio,
               t.indice_neto  AS sentimiento_resenas,
               t.n            AS n_resenas,
               l.n_llamadas, l.pct_resueltas
        FROM dim_sucursal s
        LEFT JOIN ventas_sucursal v ON v.id_sucursal = s.id_sucursal
        LEFT JOIN sentimiento_sucursal t ON t.id_sucursal = s.id_sucursal AND t.fuente = 'texto_resena'
        LEFT JOIN llamadas_sucursal l ON l.id_sucursal = s.id_sucursal;
    """)
    con.commit()

    print("\nVista integrada v_tablero_sucursal:")
    cur = con.execute("SELECT * FROM v_tablero_sucursal ORDER BY sentimiento_resenas DESC")
    columnas = [d[0] for d in cur.description]
    print(" | ".join(columnas))
    for fila in cur:
        print(" | ".join(str(x) for x in fila))
    con.close()
    print(f"\nBase de datos creada: {os.path.relpath(ruta_db, RAIZ)}")


if __name__ == "__main__":
    main()
