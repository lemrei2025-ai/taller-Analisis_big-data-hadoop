#!/usr/bin/env python3
r"""
Generador de datos sintéticos multimodales para el taller de Big Data.

Empresa de ejemplo: Café Andino S.A.S. (empresa ficticia).

El script produce los archivos de la capa de recopilación:

    datos/raw/clientes.csv          -> datos estructurados de clientes
    datos/raw/sucursales.csv        -> catálogo de sucursales
    datos/raw/productos.csv         -> catálogo de productos
    datos/raw/transacciones.csv     -> ventas (estructurado)
    datos/raw/resenas.jsonl         -> reseñas escritas (TEXTO)
    datos/raw/imagenes.jsonl        -> metadatos de fotos publicadas (IMAGEN)
    datos/raw/videos.jsonl          -> métricas y transcripción de videos (VIDEO)
    datos/raw/llamadas.jsonl        -> llamadas al call center transcritas (VOZ)

Para adaptar el taller a otra empresa, el estudiante modifica únicamente el
bloque CONFIGURACIÓN DE LA EMPRESA (ciudades, productos, frases, campañas,
motivos de llamada, etiquetas de imagen).

Uso:
    python recopilacion\generar_datos.py                # escala 1 (por defecto)
    python recopilacion\generar_datos.py --escala 5     # 5 veces más registros
    python recopilacion\generar_datos.py --salida otra\carpeta --semilla 7
"""

import argparse
import csv
import json
import os
import random
from datetime import date, datetime, timedelta

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DE LA EMPRESA (modificar para adaptar a otro contexto)
# ---------------------------------------------------------------------------

EMPRESA = "Café Andino S.A.S."

SUCURSALES = [
    # id, nombre, ciudad, tipo
    ("S01", "Andino Chapinero", "Bogotá", "tienda"),
    ("S02", "Andino Centro", "Bogotá", "tienda"),
    ("S03", "Andino El Poblado", "Medellín", "tienda"),
    ("S04", "Andino Granada", "Cali", "tienda"),
    ("S05", "Andino El Prado", "Barranquilla", "tienda"),
    ("S06", "Andino Cabecera", "Bucaramanga", "tienda"),
    ("S07", "Andino Online", "Bogotá", "digital"),
]

# Calidad de servicio "oculta" por sucursal (0 = mala, 1 = excelente).
# Se usa para que los datos contengan patrones que el análisis debe descubrir.
CALIDAD_SUCURSAL = {"S01": 0.70, "S02": 0.55, "S03": 0.85, "S04": 0.72,
                    "S05": 0.40, "S06": 0.75, "S07": 0.60}

PRODUCTOS = [
    # id, nombre, categoria, precio
    ("P01", "Café americano", "bebidas_calientes", 6500),
    ("P02", "Capuchino", "bebidas_calientes", 9500),
    ("P03", "Latte de vainilla", "bebidas_calientes", 11000),
    ("P04", "Chocolate santandereano", "bebidas_calientes", 8500),
    ("P05", "Café frío de la casa", "bebidas_frias", 10500),
    ("P06", "Granizado de café", "bebidas_frias", 12000),
    ("P07", "Limonada de coco", "bebidas_frias", 9000),
    ("P08", "Pandebono", "panaderia", 3500),
    ("P09", "Almojábana", "panaderia", 3500),
    ("P10", "Croissant de queso", "panaderia", 7000),
    ("P11", "Torta de zanahoria", "postres", 9500),
    ("P12", "Cheesecake de maracuyá", "postres", 12500),
    ("P13", "Café en grano 500 g", "cafe_empacado", 38000),
    ("P14", "Café molido 250 g", "cafe_empacado", 21000),
]

# Ciudades cálidas: mayor preferencia por bebidas frías.
CIUDADES_CALIDAS = {"Barranquilla", "Cali"}

SEGMENTOS = ["estudiante", "profesional", "familia", "turista", "empresa"]
CANALES = ["tienda", "app", "web"]
MEDIOS_PAGO = ["efectivo", "tarjeta_debito", "tarjeta_credito", "billetera_digital"]

NOMBRES = ["Ana", "Luis", "María", "Carlos", "Laura", "Andrés", "Valentina",
           "Juan", "Camila", "Santiago", "Daniela", "Felipe", "Sofía", "Mateo",
           "Paula", "Sebastián", "Natalia", "Diego", "Juliana", "Óscar"]
APELLIDOS = ["Gómez", "Rodríguez", "Martínez", "López", "García", "Pérez",
             "Ramírez", "Torres", "Díaz", "Vargas", "Rojas", "Moreno",
             "Castro", "Herrera", "Suárez", "Mejía", "Ortiz", "Álvarez"]

# Frases para construir reseñas (texto) y transcripciones (voz).
FRASES_POSITIVAS = [
    "el café es excelente y muy aromático",
    "la atención fue rápida y amable",
    "el lugar es acogedor y limpio",
    "me encantó el capuchino",
    "los postres son deliciosos",
    "el barista fue muy atento",
    "buena relación entre precio y calidad",
    "el pandebono estaba fresco y caliente",
    "excelente ambiente para trabajar",
    "recomiendo el café frío de la casa",
]
FRASES_NEGATIVAS = [
    "la demora en la entrega fue excesiva",
    "el café llegó frío",
    "el servicio fue lento y desorganizado",
    "los precios son muy caros",
    "el baño estaba sucio",
    "el pedido llegó incompleto",
    "la atención fue grosera",
    "el aire acondicionado no funcionaba y hacía mucho calor",
    "la aplicación falló al momento de pagar",
    "tuve que esperar demasiado en la fila",
]
FRASES_NEUTRAS = [
    "pedí un americano y un pandebono",
    "fui a la sucursal un martes en la tarde",
    "es la segunda vez que visito el lugar",
    "compré café en grano para la casa",
    "hice el pedido por la aplicación",
]

# Problemas específicos por sucursal (patrón que el análisis debe encontrar).
PROBLEMA_SUCURSAL = {
    "S05": ["el aire acondicionado no funcionaba y hacía mucho calor",
            "la demora en la entrega fue excesiva"],
    "S02": ["los precios son muy caros", "tuve que esperar demasiado en la fila"],
    "S07": ["la aplicación falló al momento de pagar", "el pedido llegó incompleto"],
}

ETIQUETAS_IMAGEN = ["taza", "latte_art", "postre", "pandebono", "empaque",
                    "local_interior", "terraza", "persona", "selfie",
                    "logo_marca", "bebida_fria", "mesa_trabajo", "portatil"]

CAMPANAS_VIDEO = {
    # campaña: (factor de alcance, factor de retención)
    "Origen del grano": (1.0, 0.75),
    "Baristas en acción": (1.3, 0.55),
    "Promo 2x1 frías": (1.8, 0.35),
    "Contenido de clientes": (0.7, 0.50),
}
PLATAFORMAS_VIDEO = ["tiktok", "instagram", "youtube"]

MOTIVOS_LLAMADA = {
    # motivo: (peso, duración media en segundos, probabilidad de resolución)
    "pedido_tardio": (0.32, 420, 0.62),
    "pedido_incompleto": (0.18, 360, 0.70),
    "cobro_incorrecto": (0.12, 540, 0.55),
    "falla_aplicacion": (0.15, 480, 0.48),
    "felicitacion": (0.08, 150, 0.98),
    "informacion_productos": (0.10, 200, 0.95),
    "franquicias": (0.05, 300, 0.90),
}

FRASES_LLAMADA = {
    "pedido_tardio": "buenas tardes llamo porque mi pedido lleva más de una hora y no ha llegado la demora es excesiva",
    "pedido_incompleto": "hola el pedido llegó incompleto faltó el croissant y la limonada",
    "cobro_incorrecto": "me cobraron dos veces el mismo pedido en la tarjeta y necesito el reembolso",
    "falla_aplicacion": "la aplicación falló al momento de pagar y no me deja finalizar la compra",
    "felicitacion": "quería felicitar al barista la atención fue excelente y el café delicioso",
    "informacion_productos": "quisiera saber si el café en grano es de origen huila y qué precio tiene",
    "franquicias": "me interesa conocer las condiciones para abrir una franquicia de la marca",
}

FECHA_INICIO = date(2025, 1, 1)
FECHA_FIN = date(2025, 12, 31)

# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------


def fecha_aleatoria(rnd, inicio=FECHA_INICIO, fin=FECHA_FIN):
    dias = (fin - inicio).days
    return inicio + timedelta(days=rnd.randint(0, dias))


def fecha_hora_aleatoria(rnd):
    d = fecha_aleatoria(rnd)
    return datetime(d.year, d.month, d.day, rnd.randint(6, 21), rnd.randint(0, 59))


def construir_texto(rnd, id_sucursal, calificacion):
    """Construye una reseña coherente con la calificación y la sucursal."""
    partes = []
    if rnd.random() < 0.5:
        partes.append(rnd.choice(FRASES_NEUTRAS))
    if calificacion >= 4:
        partes += rnd.sample(FRASES_POSITIVAS, k=rnd.randint(1, 2))
    elif calificacion <= 2:
        candidatas = FRASES_NEGATIVAS + PROBLEMA_SUCURSAL.get(id_sucursal, []) * 3
        partes += rnd.sample(candidatas, k=2)
    else:
        partes.append(rnd.choice(FRASES_POSITIVAS))
        partes.append(rnd.choice(FRASES_NEGATIVAS + PROBLEMA_SUCURSAL.get(id_sucursal, [])))
    rnd.shuffle(partes)
    return ". ".join(p[0].upper() + p[1:] for p in partes) + "."


def escribir_csv(ruta, encabezado, filas):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(encabezado)
        w.writerows(filas)


def escribir_jsonl(ruta, registros):
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        for r in registros:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Generación
# ---------------------------------------------------------------------------


def generar(salida, escala, semilla):
    rnd = random.Random(semilla)
    os.makedirs(salida, exist_ok=True)

    n_clientes = 2000 * escala
    n_transacciones = 30000 * escala
    n_resenas = 6000 * escala
    n_imagenes = 2500 * escala
    n_videos = 400 * escala
    n_llamadas = 1500 * escala

    suc_por_id = {s[0]: s for s in SUCURSALES}
    prod_por_id = {p[0]: p for p in PRODUCTOS}
    ciudades = sorted({s[2] for s in SUCURSALES})

    # --- Catálogos -------------------------------------------------------
    escribir_csv(os.path.join(salida, "sucursales.csv"),
                 ["id_sucursal", "nombre", "ciudad", "tipo"], SUCURSALES)
    escribir_csv(os.path.join(salida, "productos.csv"),
                 ["id_producto", "nombre", "categoria", "precio"], PRODUCTOS)

    # --- Clientes (estructurado) ----------------------------------------
    clientes = []
    for i in range(1, n_clientes + 1):
        ciudad = rnd.choice(ciudades)
        clientes.append([
            f"C{i:06d}",
            f"{rnd.choice(NOMBRES)} {rnd.choice(APELLIDOS)}",
            rnd.choice(["F", "M"]),
            rnd.randint(16, 70),
            ciudad,
            rnd.choices(SEGMENTOS, weights=[30, 35, 15, 10, 10])[0],
            fecha_aleatoria(rnd, date(2020, 1, 1), date(2025, 12, 31)).isoformat(),
            rnd.choices(CANALES, weights=[55, 35, 10])[0],
            rnd.choice(["si", "no"]),
        ])
    escribir_csv(os.path.join(salida, "clientes.csv"),
                 ["id_cliente", "nombre", "genero", "edad", "ciudad", "segmento",
                  "fecha_registro", "canal_preferido", "acepta_marketing"], clientes)

    # Sucursales posibles por ciudad (el canal digital atiende a todas).
    suc_ciudad = {}
    for s in SUCURSALES:
        suc_ciudad.setdefault(s[2], []).append(s[0])

    def sucursal_de(cliente):
        # 75 % de las compras ocurre en tiendas físicas de su ciudad; 25 % en línea.
        fisicas = [s for s in suc_ciudad.get(cliente[4], []) if s != "S07"]
        if not fisicas or rnd.random() < 0.25:
            return "S07"
        return rnd.choice(fisicas)

    # --- Transacciones (estructurado) -----------------------------------
    transacciones = []
    for i in range(1, n_transacciones + 1):
        c = rnd.choice(clientes)
        id_suc = sucursal_de(c)
        ciudad = suc_por_id[id_suc][2]
        pesos = []
        for p in PRODUCTOS:
            peso = 1.0
            if p[2] == "bebidas_frias" and ciudad in CIUDADES_CALIDAS:
                peso = 3.0
            if p[2] == "cafe_empacado" and id_suc == "S07":
                peso = 4.0
            pesos.append(peso)
        p = rnd.choices(PRODUCTOS, weights=pesos)[0]
        cantidad = rnd.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
        fh = fecha_hora_aleatoria(rnd)
        # Estacionalidad: diciembre vende más café empacado (regalos).
        if fh.month == 12 and p[2] == "cafe_empacado":
            cantidad += 1
        transacciones.append([
            f"T{i:07d}", c[0], id_suc, ciudad, fh.strftime("%Y-%m-%d %H:%M"),
            p[0], p[2], cantidad, p[3] * cantidad,
            rnd.choices(MEDIOS_PAGO, weights=[20, 30, 25, 25])[0],
        ])
    escribir_csv(os.path.join(salida, "transacciones.csv"),
                 ["id_transaccion", "id_cliente", "id_sucursal", "ciudad", "fecha_hora",
                  "id_producto", "categoria", "cantidad", "valor_total", "medio_pago"],
                 transacciones)

    # --- Reseñas (TEXTO) -------------------------------------------------
    resenas = []
    for i in range(1, n_resenas + 1):
        c = rnd.choice(clientes)
        id_suc = sucursal_de(c)
        q = CALIDAD_SUCURSAL[id_suc]
        # Calificación sesgada por la calidad oculta de la sucursal.
        base = 1 + 4 * q + rnd.gauss(0, 1.1)
        calificacion = max(1, min(5, round(base)))
        resenas.append({
            "id_resena": f"R{i:06d}",
            "id_cliente": c[0],
            "id_sucursal": id_suc,
            "ciudad": suc_por_id[id_suc][2],
            "fecha": fecha_aleatoria(rnd).isoformat(),
            "canal": rnd.choice(["app", "google_maps", "instagram", "web"]),
            "calificacion": calificacion,
            "texto": construir_texto(rnd, id_suc, calificacion),
        })
    escribir_jsonl(os.path.join(salida, "resenas.jsonl"), resenas)

    # --- Imágenes (IMAGEN: metadatos + etiquetas de visión) --------------
    imagenes = []
    for i in range(1, n_imagenes + 1):
        c = rnd.choice(clientes)
        id_suc = sucursal_de(c)
        etiquetas = rnd.sample(ETIQUETAS_IMAGEN, k=rnd.randint(2, 4))
        if suc_por_id[id_suc][2] in CIUDADES_CALIDAS and rnd.random() < 0.6:
            etiquetas.append("bebida_fria")
        etiquetas = sorted(set(etiquetas))
        formato = rnd.choice(["jpg", "png", "heic"])
        ancho, alto = rnd.choice([(1080, 1080), (1080, 1350), (1920, 1080), (3024, 4032)])
        sentimiento = round(min(1, max(-1, rnd.gauss(0.6 * CALIDAD_SUCURSAL[id_suc] - 0.1, 0.35))), 2)
        imagenes.append({
            "id_imagen": f"I{i:06d}",
            "id_cliente": c[0],
            "id_sucursal": id_suc,
            "fecha": fecha_aleatoria(rnd).isoformat(),
            "origen": rnd.choice(["instagram", "app", "google_maps"]),
            "ruta_hdfs": f"/datalake/raw/multimedia/imagenes/I{i:06d}.{formato}",
            "formato": formato,
            "ancho": ancho,
            "alto": alto,
            "tamano_kb": rnd.randint(150, 4500),
            "etiquetas": etiquetas,
            "menciona_marca": "logo_marca" in etiquetas or rnd.random() < 0.25,
            "sentimiento_visual": sentimiento,
        })
    escribir_jsonl(os.path.join(salida, "imagenes.jsonl"), imagenes)

    # --- Videos (VIDEO: métricas + transcripción) ------------------------
    videos = []
    transcripciones_video = {
        "Origen del grano": "visitamos la finca en el huila donde nace nuestro café de origen",
        "Baristas en acción": "nuestro barista prepara un latte con arte en la espuma",
        "Promo 2x1 frías": "este fin de semana todas las bebidas frías al dos por uno",
        "Contenido de clientes": "nuestros clientes comparten su momento favorito en la tienda",
    }
    for i in range(1, n_videos + 1):
        campana = rnd.choice(list(CAMPANAS_VIDEO))
        alcance, retencion = CAMPANAS_VIDEO[campana]
        plataforma = rnd.choice(PLATAFORMAS_VIDEO)
        factor_plat = {"tiktok": 1.6, "instagram": 1.0, "youtube": 0.6}[plataforma]
        reproducciones = int(rnd.lognormvariate(8.5, 0.8) * alcance * factor_plat)
        pct_visto = round(min(0.99, max(0.05, rnd.gauss(retencion, 0.1))), 2)
        me_gusta = int(reproducciones * rnd.uniform(0.03, 0.09) * (0.5 + pct_visto))
        videos.append({
            "id_video": f"V{i:05d}",
            "campana": campana,
            "plataforma": plataforma,
            "fecha_publicacion": fecha_aleatoria(rnd).isoformat(),
            "ruta_hdfs": f"/datalake/raw/multimedia/videos/V{i:05d}.mp4",
            "duracion_seg": rnd.randint(15, 180),
            "resolucion": rnd.choice(["720p", "1080p", "4k"]),
            "reproducciones": reproducciones,
            "me_gusta": me_gusta,
            "comentarios": int(me_gusta * rnd.uniform(0.02, 0.12)),
            "compartidos": int(me_gusta * rnd.uniform(0.05, 0.25)),
            "porcentaje_visto": pct_visto,
            "transcripcion": transcripciones_video[campana],
        })
    escribir_jsonl(os.path.join(salida, "videos.jsonl"), videos)

    # --- Llamadas (VOZ: metadatos de audio + transcripción) --------------
    llamadas = []
    motivos = list(MOTIVOS_LLAMADA)
    pesos_motivo = [MOTIVOS_LLAMADA[m][0] for m in motivos]
    for i in range(1, n_llamadas + 1):
        c = rnd.choice(clientes)
        id_suc = sucursal_de(c)
        motivo = rnd.choices(motivos, weights=pesos_motivo)[0]
        # Las sucursales con problemas generan más reclamos.
        if id_suc in PROBLEMA_SUCURSAL and rnd.random() < 0.35:
            motivo = "pedido_tardio" if id_suc == "S05" else (
                "falla_aplicacion" if id_suc == "S07" else "cobro_incorrecto")
        _, dur_media, p_res = MOTIVOS_LLAMADA[motivo]
        llamadas.append({
            "id_llamada": f"L{i:06d}",
            "id_cliente": c[0],
            "id_sucursal": id_suc,
            "fecha_hora": fecha_hora_aleatoria(rnd).strftime("%Y-%m-%d %H:%M"),
            "ruta_audio": f"/datalake/raw/multimedia/audios/L{i:06d}.wav",
            "duracion_seg": max(30, int(rnd.gauss(dur_media, dur_media * 0.3))),
            "motivo": motivo,
            "resuelta": rnd.random() < p_res,
            "transcripcion": FRASES_LLAMADA[motivo],
        })
    escribir_jsonl(os.path.join(salida, "llamadas.jsonl"), llamadas)

    resumen = {
        "clientes.csv": len(clientes), "transacciones.csv": len(transacciones),
        "resenas.jsonl": len(resenas), "imagenes.jsonl": len(imagenes),
        "videos.jsonl": len(videos), "llamadas.jsonl": len(llamadas),
    }
    print(f"Datos generados para {EMPRESA} en '{salida}':")
    for archivo, n in resumen.items():
        print(f"  {archivo:<22}{n:>10,} registros")


if __name__ == "__main__":
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser(description="Genera datos sintéticos multimodales.")
    ap.add_argument("--salida", default=os.path.join(raiz, "datos", "raw"))
    ap.add_argument("--escala", type=int, default=1, help="Multiplicador de volumen")
    ap.add_argument("--semilla", type=int, default=2025)
    args = ap.parse_args()
    generar(args.salida, args.escala, args.semilla)
