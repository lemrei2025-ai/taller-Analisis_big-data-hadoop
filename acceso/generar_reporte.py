#!/usr/bin/env python3
"""
CAPA 4/5 - COMUNICACIÓN Y ANÁLISIS.

Genera gráficos (PNG) y un reporte en Markdown a partir de los resultados de
MapReduce. El reporte es el insumo para la etapa 5 (análisis de la información).

Uso:
    pip install matplotlib
    python acceso\\generar_reporte.py                 # usa resultados/hadoop o resultados/local
    python acceso\\generar_reporte.py --origen local

Salida:
    resultados/graficos/*.png
    resultados/reporte_resultados.md
"""

import argparse
import csv
import os
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from esquema_resultados import RAIZ, carpeta_resultados, leer_resultado  # noqa: E402

AZUL, ROJO, GRIS = "#2a78d6", "#e34948", "#b8b7b2"
TINTA, TINTA_2 = "#0b0b0b", "#52514e"
SALIDA = os.path.join(RAIZ, "resultados")
GRAFICOS = os.path.join(SALIDA, "graficos")

plt.rcParams.update({
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
    "axes.edgecolor": GRIS, "axes.labelcolor": TINTA_2, "text.color": TINTA,
    "xtick.color": TINTA_2, "ytick.color": TINTA_2, "axes.grid": True,
    "grid.color": "#e6e5e0", "grid.linewidth": 0.8, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
    "axes.titleweight": "bold", "axes.titlesize": 12, "axes.titlelocation": "left",
})


def miles(x):
    return f"{x:,.0f}".replace(",", ".")


def guardar(fig, nombre):
    os.makedirs(GRAFICOS, exist_ok=True)
    fig.tight_layout()
    ruta = os.path.join(GRAFICOS, nombre)
    fig.savefig(ruta, dpi=140)
    plt.close(fig)
    return f"graficos/{nombre}"


def barras_h(etiquetas, valores, titulo, xlabel, nombre, color=AZUL, fmt=miles):
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(etiquetas) + 1.2))
    y = range(len(etiquetas))
    ax.barh(y, valores, color=color, height=0.6)
    ax.set_yticks(list(y), etiquetas)
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    ax.set_title(titulo)
    ax.set_xlabel(xlabel)
    for i, v in enumerate(valores):
        ax.text(v, i, f" {fmt(v)}", va="center", color=TINTA_2, fontsize=9)
    ax.margins(x=0.15)
    return guardar(fig, nombre)


def tabla_md(filas, columnas, limite=None):
    filas = filas[:limite] if limite else filas
    md = ["| " + " | ".join(columnas) + " |", "|" + "---|" * len(columnas)]
    for f in filas:
        md.append("| " + " | ".join(
            miles(f[c]) if isinstance(f[c], int) else str(f[c]) for c in columnas) + " |")
    return "\n".join(md)


def nombres_sucursal():
    with open(os.path.join(RAIZ, "datos", "raw", "sucursales.csv"), encoding="utf-8") as f:
        return {r["id_sucursal"]: r["nombre"] for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--origen", choices=["auto", "hadoop", "local"], default="auto")
    origen = ap.parse_args().origen
    leer = lambda n: leer_resultado(n, origen)  # noqa: E731
    suc = nombres_sucursal()
    secciones = [
        "# Reporte de resultados del procesamiento MapReduce\n",
        f"Origen de los datos: `{os.path.relpath(carpeta_resultados(origen), RAIZ)}`\n",
    ]

    # 1. Ventas por mes ---------------------------------------------------
    vm = sorted(leer("ventas_mes"), key=lambda r: r["mes"])
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.plot([r["mes"][5:] for r in vm], [r["ventas_totales"] / 1e6 for r in vm],
            color=AZUL, linewidth=2, marker="o", markersize=5)
    ax.set_title("Ventas totales por mes (millones COP)")
    ax.set_xlabel("Mes"); ax.set_ylabel("Millones COP")
    pico = max(vm, key=lambda r: r["ventas_totales"])
    ax.annotate(f"Pico: {pico['mes']}", (vm.index(pico), pico["ventas_totales"] / 1e6),
                textcoords="offset points", xytext=(-70, -5), color=TINTA_2)
    img = guardar(fig, "01_ventas_mes.png")
    secciones += ["## 1. Ventas por mes (estructurado)\n", f"![Ventas por mes]({img})\n",
                  tabla_md(vm, ["mes", "n_transacciones", "unidades", "ventas_totales", "ticket_promedio"]) + "\n"]

    # 2. Mezcla de categorías por ciudad -----------------------------------
    vcc = leer("ventas_ciudad_categoria")
    ciudades = sorted({r["ciudad"] for r in vcc})
    categorias = sorted({r["categoria"] for r in vcc})
    total_ciudad = defaultdict(int)
    for r in vcc:
        total_ciudad[r["ciudad"]] += r["ventas_totales"]
    matriz = [[0.0] * len(categorias) for _ in ciudades]
    for r in vcc:
        matriz[ciudades.index(r["ciudad"])][categorias.index(r["categoria"])] = \
            100 * r["ventas_totales"] / total_ciudad[r["ciudad"]]
    fig, ax = plt.subplots(figsize=(9, 3.8))
    im = ax.imshow(matriz, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(categorias)), [c.replace("_", "\n") for c in categorias])
    ax.set_yticks(range(len(ciudades)), ciudades)
    ax.grid(False)
    for i, fila in enumerate(matriz):
        for j, v in enumerate(fila):
            ax.text(j, i, f"{v:.0f}%", ha="center", va="center",
                    color="white" if v > 30 else TINTA, fontsize=9)
    ax.set_title("Participación de cada categoría en las ventas de la ciudad (%)")
    fig.colorbar(im, ax=ax, shrink=0.8)
    img = guardar(fig, "02_mezcla_ciudad_categoria.png")
    secciones += ["## 2. Mezcla de categorías por ciudad\n", f"![Mezcla]({img})\n"]

    # 3. Sentimiento por sucursal (texto y voz) ---------------------------
    sent = leer("sentimiento_sucursal")
    sent_txt = sorted([r for r in sent if r["fuente"] == "texto_resena"], key=lambda r: r["indice_neto"])
    etiquetas = [suc.get(r["id_sucursal"], r["id_sucursal"]) for r in sent_txt]
    valores = [r["indice_neto"] for r in sent_txt]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(etiquetas, valores, color=[ROJO if v < 0 else AZUL for v in valores], height=0.6)
    ax.axvline(0, color=GRIS, linewidth=1)
    ax.grid(axis="y", visible=False)
    for i, v in enumerate(valores):
        ax.text(v, i, f" {v:+.2f} ", va="center", ha="left" if v >= 0 else "right", color=TINTA_2, fontsize=9)
    ax.set_xlim(-1, 1)
    ax.set_title("Índice neto de sentimiento en reseñas (−1 a +1)")
    ax.set_xlabel("(positivas − negativas) / total")
    img = guardar(fig, "03_sentimiento_sucursal.png")
    secciones += ["## 3. Sentimiento de reseñas (texto) y llamadas (voz)\n", f"![Sentimiento]({img})\n",
                  tabla_md(sorted(sent, key=lambda r: (r["fuente"], r["id_sucursal"])),
                           ["fuente", "id_sucursal", "n", "positivos", "negativos", "neutros", "indice_neto"]) + "\n"]

    # 4. Bigramas en quejas ------------------------------------------------
    big = sorted(leer("bigramas_quejas"), key=lambda r: -r["frecuencia"])[:15]
    img = barras_h([b["bigrama"].replace("_", " ") for b in big], [b["frecuencia"] for b in big],
                   "Pares de palabras más frecuentes en reseñas de 1–2 estrellas", "Frecuencia",
                   "04_bigramas_quejas.png")
    pal = sorted(leer("palabras_frecuentes"), key=lambda r: -r["frecuencia"])[:20]
    secciones += ["## 4. Texto: temas de las quejas\n", f"![Bigramas]({img})\n",
                  "Top 20 de palabras en todas las fuentes de texto, voz y video:\n",
                  tabla_md(pal, ["termino", "frecuencia"]) + "\n"]

    # 5. Imágenes -----------------------------------------------------------
    imgs = sorted(leer("imagenes_etiquetas"), key=lambda r: -r["n_imagenes"])
    img = barras_h([r["etiqueta"] for r in imgs], [r["n_imagenes"] for r in imgs],
                   "Etiquetas detectadas en imágenes publicadas por clientes", "Número de imágenes",
                   "05_imagenes_etiquetas.png")
    secciones += ["## 5. Imágenes\n", f"![Imágenes]({img})\n",
                  tabla_md(imgs, ["etiqueta", "n_imagenes", "sentimiento_promedio", "pct_menciona_marca"]) + "\n"]

    # 6. Videos (dos métricas -> dos paneles, sin doble eje) ---------------
    vid = leer("videos_campanas")
    por_campana = defaultdict(lambda: {"rep": 0, "inter": 0, "ret": 0.0, "n": 0})
    for r in vid:
        c = por_campana[r["campana"]]
        c["rep"] += r["reproducciones"]; c["inter"] += r["interacciones"]
        c["ret"] += r["retencion_promedio_pct"] * r["n_videos"]; c["n"] += r["n_videos"]
    camp = sorted(por_campana)
    eng = [100 * por_campana[c]["inter"] / por_campana[c]["rep"] for c in camp]
    ret = [por_campana[c]["ret"] / por_campana[c]["n"] for c in camp]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
    for ax, vals, tit in ((a1, eng, "Tasa de engagement (%)"), (a2, ret, "Retención promedio (% visto)")):
        ax.barh(camp, vals, color=AZUL, height=0.6)
        ax.grid(axis="y", visible=False)
        ax.set_title(tit)
        for i, v in enumerate(vals):
            ax.text(v, i, f" {v:.1f}", va="center", color=TINTA_2, fontsize=9)
        ax.margins(x=0.18)
    a1.invert_yaxis()
    img = guardar(fig, "06_videos_campanas.png")
    secciones += ["## 6. Videos por campaña\n", f"![Videos]({img})\n",
                  tabla_md(sorted(vid, key=lambda r: -r["tasa_engagement_pct"]),
                           ["campana", "plataforma", "n_videos", "reproducciones",
                            "tasa_engagement_pct", "retencion_promedio_pct"]) + "\n"]

    # 7. Llamadas -----------------------------------------------------------
    llm = sorted(leer("llamadas_motivo"), key=lambda r: -r["n_llamadas"])
    img = barras_h([r["motivo"].replace("_", " ") for r in llm], [r["pct_resueltas"] for r in llm],
                   "Porcentaje de llamadas resueltas por motivo", "% resueltas",
                   "07_llamadas_resolucion.png", fmt=lambda v: f"{v:.0f}%")
    secciones += ["## 7. Voz: llamadas al centro de contacto\n", f"![Llamadas]({img})\n",
                  tabla_md(llm, ["motivo", "n_llamadas", "duracion_promedio_seg", "pct_resueltas", "horas_totales"]) + "\n",
                  tabla_md(sorted(leer("llamadas_sucursal"), key=lambda r: r["id_sucursal"]),
                           ["id_sucursal", "n_llamadas", "duracion_promedio_seg", "pct_resueltas"]) + "\n"]

    ruta = os.path.join(SALIDA, "reporte_resultados.md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(secciones))
    print(f"Reporte: {os.path.relpath(ruta, RAIZ)}  |  Gráficos: resultados/graficos/")


if __name__ == "__main__":
    main()
