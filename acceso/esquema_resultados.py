"""
Esquema de las salidas de MapReduce (capa curada).

Cada resultado es un archivo TSV sin encabezado. Aquí se documentan sus columnas
para poder cargarlo en una base de datos, exponerlo por una API o graficarlo.
Las claves compuestas que usan '|' se separan en varias columnas.
"""

import csv
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ESQUEMAS = {
    "ventas_ciudad_categoria": ["ciudad", "categoria", "n_transacciones", "unidades", "ventas_totales", "ticket_promedio"],
    "ventas_mes": ["mes", "n_transacciones", "unidades", "ventas_totales", "ticket_promedio"],
    "ventas_sucursal": ["id_sucursal", "n_transacciones", "unidades", "ventas_totales", "ticket_promedio"],
    "sentimiento_sucursal": ["fuente", "id_sucursal", "n", "positivos", "negativos", "neutros", "puntaje_promedio", "indice_neto"],
    "palabras_frecuentes": ["termino", "frecuencia"],
    "bigramas_quejas": ["bigrama", "frecuencia"],
    "imagenes_etiquetas": ["etiqueta", "n_imagenes", "sentimiento_promedio", "pct_menciona_marca", "tamano_total_mb"],
    "imagenes_ciudad_etiqueta": ["ciudad", "etiqueta", "n_imagenes", "sentimiento_promedio", "pct_menciona_marca", "tamano_total_mb"],
    "videos_campanas": ["campana", "plataforma", "n_videos", "reproducciones", "interacciones", "tasa_engagement_pct", "retencion_promedio_pct"],
    "llamadas_motivo": ["motivo", "n_llamadas", "duracion_promedio_seg", "pct_resueltas", "horas_totales"],
    "llamadas_sucursal": ["id_sucursal", "n_llamadas", "duracion_promedio_seg", "pct_resueltas", "horas_totales"],
}


def carpeta_resultados(origen="auto"):
    """'hadoop' = resultados exportados de HDFS; 'local' = simulación; 'auto' = hadoop si existe."""
    hadoop = os.path.join(RAIZ, "resultados", "hadoop")
    local = os.path.join(RAIZ, "resultados", "local")
    if origen == "hadoop" or (origen == "auto" and os.path.isdir(hadoop) and os.listdir(hadoop)):
        return hadoop
    return local


def _convertir(valor):
    for tipo in (int, float):
        try:
            return tipo(valor)
        except ValueError:
            pass
    return valor


def leer_resultado(nombre, origen="auto"):
    """Devuelve una lista de diccionarios con las filas del resultado."""
    ruta = os.path.join(carpeta_resultados(origen), f"{nombre}.tsv")
    columnas = ESQUEMAS[nombre]
    filas = []
    with open(ruta, encoding="utf-8") as f:
        for registro in csv.reader(f, delimiter="\t"):
            if not registro:
                continue
            valores = registro[0].split("|") + registro[1:]
            filas.append({c: _convertir(v) for c, v in zip(columnas, valores)})
    return filas


def faltantes(origen="auto"):
    """Nombres de los resultados que no existen en la carpeta de origen."""
    carpeta = carpeta_resultados(origen)
    return [n for n in ESQUEMAS if not os.path.exists(os.path.join(carpeta, f"{n}.tsv"))]


def exigir_completos(origen="auto"):
    """Detiene el programa con un mensaje claro si falta algún resultado."""
    falta = faltantes(origen)
    if falta:
        carpeta = os.path.relpath(carpeta_resultados(origen), RAIZ)
        raise SystemExit(
            f"Faltan {len(falta)} resultado(s) en {carpeta}: {', '.join(falta)}\n"
            f"Ejecútelos con:  .\\scripts\\02_ejecutar_mapreduce.ps1 -Trabajo {','.join(falta)}\n"
            f"y luego:         .\\scripts\\03_exportar_resultados.ps1\n"
            f"(Para usar los resultados de la simulación local: agregar --origen local)")
