#!/usr/bin/env python3
r"""
Extracción de metadatos a partir de archivos multimedia REALES (opcional).

Convierte una carpeta de imágenes, videos o audios en un archivo JSON Lines
con la misma estructura que usan los trabajos MapReduce del taller, para que el
estudiante pueda trabajar con material propio de la empresa seleccionada.

Requisitos:
    pip install Pillow              # imágenes
    ffmpeg (incluye ffprobe)        # videos y audios distintos de WAV
                                    # instalador: https://www.gyan.dev/ffmpeg/builds  o  winget install Gyan.FFmpeg

Uso (tipo, carpeta de entrada, archivo de salida):
    python recopilacion\extraer_metadatos_multimedia.py imagenes datos\multimedia\imagenes datos\raw\imagenes_reales.jsonl
    python recopilacion\extraer_metadatos_multimedia.py videos   datos\multimedia\videos   datos\raw\videos_reales.jsonl
    python recopilacion\extraer_metadatos_multimedia.py audios   datos\multimedia\audios   datos\raw\llamadas_reales.jsonl

    El archivo se escribe en UTF-8 con saltos de línea LF, como lo requiere Hadoop
    (no se recomienda usar '>' en PowerShell 5, porque genera archivos UTF-16).

Los campos que dependen de modelos de inteligencia artificial (etiquetas de
visión, sentimiento visual, transcripción) se dejan vacíos para que el
estudiante los complete con la herramienta de su elección, por ejemplo:
    - Etiquetas de imagen: modelos preentrenados de clasificación (ResNet, CLIP)
      o servicios en la nube (Google Vision, Azure AI Vision, AWS Rekognition).
    - Transcripción de voz: Whisper (código abierto) o servicios speech-to-text.
"""

import json
import os
import shutil
import subprocess
import sys
import wave
from datetime import datetime

EXT_IMAGEN = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
EXT_VIDEO = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
EXT_AUDIO = {".wav", ".mp3", ".m4a", ".ogg", ".flac"}


def fecha_archivo(ruta):
    return datetime.fromtimestamp(os.path.getmtime(ruta)).date().isoformat()


def ffprobe(ruta):
    """Devuelve (duracion_seg, ancho, alto) usando ffprobe, si está instalado."""
    if not shutil.which("ffprobe"):
        return None, None, None
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", ruta],
        capture_output=True, text=True).stdout
    info = json.loads(salida or "{}")
    duracion = float(info.get("format", {}).get("duration", 0) or 0)
    video = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
    return round(duracion), video.get("width"), video.get("height")


def procesar_imagenes(carpeta):
    from PIL import Image  # importación diferida: solo se necesita para imágenes
    for i, nombre in enumerate(sorted(os.listdir(carpeta)), 1):
        ruta = os.path.join(carpeta, nombre)
        ext = os.path.splitext(nombre)[1].lower()
        if ext not in EXT_IMAGEN:
            continue
        with Image.open(ruta) as img:
            ancho, alto = img.size
            formato = (img.format or ext[1:]).lower()
        yield {
            "id_imagen": f"IR{i:05d}",
            "id_cliente": None,
            "id_sucursal": None,
            "fecha": fecha_archivo(ruta),
            "origen": "carga_manual",
            "ruta_hdfs": f"/datalake/raw/multimedia/imagenes/{nombre}",
            "formato": formato,
            "ancho": ancho,
            "alto": alto,
            "tamano_kb": os.path.getsize(ruta) // 1024,
            "etiquetas": [],              # completar con un modelo de visión
            "menciona_marca": False,
            "sentimiento_visual": 0.0,    # completar con un modelo de análisis
        }


def procesar_videos(carpeta):
    for i, nombre in enumerate(sorted(os.listdir(carpeta)), 1):
        ruta = os.path.join(carpeta, nombre)
        if os.path.splitext(nombre)[1].lower() not in EXT_VIDEO:
            continue
        duracion, ancho, alto = ffprobe(ruta)
        yield {
            "id_video": f"VR{i:04d}",
            "campana": "sin_campana",
            "plataforma": "propia",
            "fecha_publicacion": fecha_archivo(ruta),
            "ruta_hdfs": f"/datalake/raw/multimedia/videos/{nombre}",
            "duracion_seg": duracion,
            "resolucion": f"{alto}p" if alto else None,
            "reproducciones": 0, "me_gusta": 0, "comentarios": 0, "compartidos": 0,
            "porcentaje_visto": 0.0,
            "transcripcion": "",          # completar con speech-to-text
        }


def procesar_audios(carpeta):
    for i, nombre in enumerate(sorted(os.listdir(carpeta)), 1):
        ruta = os.path.join(carpeta, nombre)
        ext = os.path.splitext(nombre)[1].lower()
        if ext not in EXT_AUDIO:
            continue
        if ext == ".wav":
            with wave.open(ruta) as w:
                duracion = round(w.getnframes() / w.getframerate())
        else:
            duracion = ffprobe(ruta)[0]
        yield {
            "id_llamada": f"LR{i:05d}",
            "id_cliente": None,
            "id_sucursal": None,
            "fecha_hora": datetime.fromtimestamp(os.path.getmtime(ruta)).strftime("%Y-%m-%d %H:%M"),
            "ruta_audio": f"/datalake/raw/multimedia/audios/{nombre}",
            "duracion_seg": duracion,
            "motivo": "sin_clasificar",
            "resuelta": False,
            "transcripcion": "",          # completar con speech-to-text
        }


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in {"imagenes", "videos", "audios"}:
        sys.exit(__doc__)
    tipo, carpeta, archivo_salida = sys.argv[1:4]
    funcion = {"imagenes": procesar_imagenes, "videos": procesar_videos, "audios": procesar_audios}[tipo]
    n = 0
    with open(archivo_salida, "w", encoding="utf-8", newline="\n") as salida:
        for registro in funcion(carpeta):
            salida.write(json.dumps(registro, ensure_ascii=False) + "\n")
            n += 1
    print(f"{n} archivos procesados -> {archivo_salida}")
