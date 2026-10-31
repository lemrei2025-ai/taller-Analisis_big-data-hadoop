#!/usr/bin/env python3
"""
CAPA 4 - COMUNICACIÓN.

API REST mínima (solo biblioteca estándar de Python) que expone los resultados
almacenados en resultados/analitica.db para que otras aplicaciones
(tableros, aplicaciones móviles, hojas de cálculo) los consuman en formato JSON.

Uso:
    python acceso\\cargar_sqlite.py      # primero se crea la base de datos
    python acceso\\api_resultados.py     # http://localhost:8000

Rutas:
    GET /                         -> lista de recursos disponibles
    GET /resultados/<tabla>       -> filas de un resultado (JSON)
    GET /resultados/<tabla>?limite=5&orden=ventas_totales&desc=1
    GET /tablero                  -> vista integrada por sucursal
"""

import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_DB = os.path.join(RAIZ, "resultados", "analitica.db")
PUERTO = int(os.environ.get("PUERTO", "8000"))


def consultar(sql, parametros=()):
    con = sqlite3.connect(RUTA_DB)
    con.row_factory = sqlite3.Row
    filas = [dict(r) for r in con.execute(sql, parametros)]
    con.close()
    return filas


def tablas_disponibles():
    return [r["name"] for r in consultar(
        "SELECT name FROM sqlite_master WHERE type IN ('table','view') ORDER BY name")]


class Manejador(BaseHTTPRequestHandler):
    def responder(self, codigo, cuerpo):
        datos = json.dumps(cuerpo, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        url = urlparse(self.path)
        partes = [p for p in url.path.split("/") if p]
        q = parse_qs(url.query)
        tablas = tablas_disponibles()

        if not partes:
            return self.responder(200, {"recursos": [f"/resultados/{t}" for t in tablas] + ["/tablero"]})

        if partes == ["tablero"]:
            return self.responder(200, consultar("SELECT * FROM v_tablero_sucursal"))

        if len(partes) == 2 and partes[0] == "resultados":
            tabla = partes[1]
            if tabla not in tablas:                       # evita inyección SQL en el nombre
                return self.responder(404, {"error": f"recurso '{tabla}' no existe"})
            sql = f"SELECT * FROM {tabla}"
            columnas = [c for c in consultar(f"SELECT * FROM {tabla} LIMIT 1")[0]]
            orden = q.get("orden", [None])[0]
            if orden in columnas:
                sql += f" ORDER BY {orden} {'DESC' if q.get('desc') else 'ASC'}"
            limite = q.get("limite", [None])[0]
            if limite and limite.isdigit():
                sql += f" LIMIT {int(limite)}"
            return self.responder(200, consultar(sql))

        return self.responder(404, {"error": "ruta no encontrada"})


if __name__ == "__main__":
    if not os.path.exists(RUTA_DB):
        raise SystemExit("No existe resultados\\analitica.db. Ejecute primero: python acceso\\cargar_sqlite.py")
    print(f"API disponible en http://localhost:{PUERTO}  (Ctrl+C para detener)")
    HTTPServer(("0.0.0.0", PUERTO), Manejador).serve_forever()
