"""
Descarga el corpus de prueba: 10 artículos de Wikipedia por idioma
(español, francés e inglés) en texto plano.

Los temas son equivalentes entre idiomas para que la comparación sea
justa. Los textos se guardan en textos/<idioma>/<nombre>.txt.

Uso:
    python descargar_textos.py
"""

import json
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ARTICULOS = {
    "es": ["Algoritmo", "México", "París", "Miguel de Cervantes", "Revolución francesa",
           "Sistema solar", "Química", "Literatura", "Música", "Fútbol"],
    "fr": ["Algorithme", "Mexique", "Paris", "Victor Hugo", "Révolution française",
           "Système solaire", "Chimie", "Littérature", "Musique", "Football"],
    "en": ["Algorithm", "Mexico", "Paris", "William Shakespeare", "French Revolution",
           "Solar System", "Chemistry", "Literature", "Music", "Association football"],
}

CARPETA_TEXTOS = Path("textos")

# Wikipedia responde 429 (Too Many Requests) si se piden muchos artículos seguidos.
PAUSA_ENTRE_DESCARGAS = 3
REINTENTOS = 5


def url_articulo(idioma, titulo):
    parametros = urllib.parse.urlencode({
        "action": "query",
        "prop": "extracts",
        "explaintext": 1,
        "redirects": 1,
        "titles": titulo,
        "format": "json",
    })
    return f"https://{idioma}.wikipedia.org/w/api.php?{parametros}"


def pedir_json(url):
    """Hace la petición y, si Wikipedia responde 429, espera y reintenta."""
    peticion = urllib.request.Request(url, headers={"User-Agent": "huffman-tarea-algoritmos/1.0"})

    for intento in range(1, REINTENTOS + 1):
        try:
            with urllib.request.urlopen(peticion) as respuesta:
                return json.load(respuesta)
        except urllib.error.HTTPError as error:
            if error.code != 429 or intento == REINTENTOS:
                raise
            espera = 30 * intento
            print(f"  Wikipedia pidió esperar; reintento en {espera} s...")
            time.sleep(espera)


def descargar_articulo(idioma, titulo):
    """Devuelve el texto plano de un artículo de Wikipedia."""
    datos = pedir_json(url_articulo(idioma, titulo))

    pagina = next(iter(datos["query"]["pages"].values()))
    return pagina["extract"]


def nombre_archivo(titulo):
    """'Revolución francesa' -> 'revolucion_francesa.txt' (sin acentos ni espacios)."""
    sin_acentos = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode()
    return sin_acentos.lower().replace(" ", "_") + ".txt"


if __name__ == "__main__":
    for idioma, titulos in ARTICULOS.items():
        carpeta = CARPETA_TEXTOS / idioma
        carpeta.mkdir(parents=True, exist_ok=True)

        for titulo in titulos:
            ruta = carpeta / nombre_archivo(titulo)
            if ruta.exists():
                continue

            texto = descargar_articulo(idioma, titulo)
            ruta.write_text(texto, encoding="utf-8")
            print(f"{ruta}: {len(texto)} caracteres")
            time.sleep(PAUSA_ENTRE_DESCARGAS)
