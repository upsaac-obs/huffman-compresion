"""
Estadísticas de compresión para los textos en español, francés e inglés.

Comprime cada archivo de textos/<idioma>/, verifica que la descompresión
reproduzca el texto original y genera dos tablas:
    - Por archivo: nombre, idioma, tamaños, compression factor y bits
      promedio por símbolo.
    - Por idioma: promedio del compression factor y de los bits por símbolo.

Las tablas se guardan en resultados/ como CSV y como Markdown.

Uso:
    python estadisticas_compresion.py
"""

from pathlib import Path

import pandas as pd

from compresor import comprimir
from descompresor import decodificar, leer_huff
from frecuencias import bits_promedio_por_simbolo, contar_frecuencias, leer_texto
from huffman import huffmanCodes

IDIOMAS = {"es": "Español", "fr": "Francés", "en": "Inglés"}
CARPETA_TEXTOS = Path("textos")
CARPETA_COMPRIMIDOS = Path("comprimidos")
CARPETA_RESULTADOS = Path("resultados")


def verificar_descompresion(ruta_huff, texto_original):
    encabezado, bits = leer_huff(ruta_huff)
    if decodificar(encabezado, bits, "diccionario") != texto_original:
        raise RuntimeError(f"La descompresión de {ruta_huff} no coincide con el original")


def estadisticas_archivo(ruta, idioma):
    """Comprime un archivo y devuelve su fila de la tabla de estadísticas."""
    texto = leer_texto(ruta)
    simbolos, frecuencias = contar_frecuencias(texto)
    codes_dic, _ = huffmanCodes(simbolos, frecuencias)

    ruta_huff = comprimir(ruta, CARPETA_COMPRIMIDOS / idioma)
    verificar_descompresion(ruta_huff, texto)

    tamano_original = ruta.stat().st_size
    tamano_comprimido = ruta_huff.stat().st_size
    return {
        "Archivo": ruta.name,
        "Idioma": IDIOMAS[idioma],
        "Tamaño original (bytes)": tamano_original,
        "Tamaño comprimido (bytes)": tamano_comprimido,
        "Compression factor": tamano_comprimido / tamano_original,
        "Bits promedio por símbolo": bits_promedio_por_simbolo(simbolos, frecuencias, codes_dic),
    }


def tabla_por_archivo():
    filas = []
    for idioma in IDIOMAS:
        for ruta in sorted((CARPETA_TEXTOS / idioma).glob("*.txt")):
            filas.append(estadisticas_archivo(ruta, idioma))
    return pd.DataFrame(filas)


def tabla_por_idioma(df_archivos):
    resumen = df_archivos.groupby("Idioma", sort=False).agg({
        "Compression factor": "mean",
        "Bits promedio por símbolo": "mean",
    })
    resumen.columns = ["Promedio compression factor", "Promedio bits por símbolo"]
    return resumen.reset_index()


def tabla_markdown(df, decimales=4):
    """Convierte un DataFrame en una tabla Markdown (para el README)."""
    df = df.round(decimales)
    lineas = [
        "| " + " | ".join(df.columns) + " |",
        "|" + "---|" * len(df.columns),
    ]
    for fila in df.itertuples(index=False):
        lineas.append("| " + " | ".join(str(valor) for valor in fila) + " |")
    return "\n".join(lineas) + "\n"


def guardar_tabla(df, nombre):
    CARPETA_RESULTADOS.mkdir(exist_ok=True)
    df.to_csv(CARPETA_RESULTADOS / f"{nombre}.csv", index=False)
    (CARPETA_RESULTADOS / f"{nombre}.md").write_text(tabla_markdown(df), encoding="utf-8")


if __name__ == "__main__":
    df_archivos = tabla_por_archivo()
    df_idiomas = tabla_por_idioma(df_archivos)

    guardar_tabla(df_archivos, "compresion_por_archivo")
    guardar_tabla(df_idiomas, "compresion_por_idioma")

    print(df_archivos.round(4).to_string(index=False))
    print()
    print(df_idiomas.round(4).to_string(index=False))
