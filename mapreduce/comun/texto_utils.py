"""
Utilidades de procesamiento de texto compartidas por los mappers.

En Hadoop Streaming este archivo se distribuye con la opción -files, de modo
que queda disponible en el directorio de trabajo de cada tarea.
"""

import os
import re
import unicodedata

_TOKEN = re.compile(r"[a-zñ]+")


def rutas_busqueda():
    """Directorios donde se buscan los archivos auxiliares (léxico, stopwords)."""
    aqui = os.path.dirname(os.path.abspath(__file__))
    return [os.getcwd(), aqui, os.path.join(aqui, "..", "comun")]


def buscar_archivo(nombre):
    for base in rutas_busqueda():
        ruta = os.path.join(base, nombre)
        if os.path.exists(ruta):
            return ruta
    raise FileNotFoundError(nombre)


def normalizar(texto):
    """Minúsculas y sin tildes (conserva la ñ)."""
    texto = texto.lower().replace("ñ", "\0")
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto.replace("\0", "ñ")


def tokenizar(texto):
    return _TOKEN.findall(normalizar(texto))


def cargar_lexico(nombre="lexico_sentimiento.txt"):
    lexico = {}
    with open(buscar_archivo(nombre), encoding="utf-8") as f:
        for linea in f:
            if not linea.strip() or linea.startswith("#"):
                continue
            palabra, puntaje = linea.rstrip("\n").split("\t")
            lexico[palabra] = int(puntaje)
    return lexico


def cargar_stopwords(nombre="stopwords_es.txt"):
    with open(buscar_archivo(nombre), encoding="utf-8") as f:
        return set(f.read().split())


def puntaje_sentimiento(tokens, lexico):
    """Suma de puntajes del léxico; 'no' invierte el puntaje de la palabra siguiente."""
    total, invertir = 0, False
    for t in tokens:
        if t == "no":
            invertir = True
            continue
        valor = lexico.get(t, 0)
        total += -valor if invertir else valor
        invertir = False
    return total
