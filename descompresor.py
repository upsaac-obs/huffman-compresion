"""
Decodificación (descompresión) de archivos .huff.

Versión con diccionario inverso: se lee el flujo bit a bit acumulando un
código; en cuanto el código acumulado existe en el diccionario inverso
{código: carácter} se emite el carácter y se reinicia la acumulación.
Funciona porque los códigos de Huffman son libres de prefijo.

Uso:
    python descompresor.py comprimidos/algoritmo.huff
"""

import pickle
import sys
from pathlib import Path

from bitarray import bitarray


def leer_huff(ruta_huff):
    """
    Lee un archivo .huff y separa el encabezado de los bits comprimidos.

    Retorna:
        encabezado: dict con 'codes_dic', 'padding' y 'arbol'
        bits: bitarray sin los bits de relleno del final
    """
    with open(ruta_huff, "rb") as archivo:
        encabezado = pickle.load(archivo)
        bits = bitarray()
        bits.fromfile(archivo)

    bits_reales = len(bits) - encabezado["padding"]
    return encabezado, bits[:bits_reales]


def invertir_diccionario(codes_dic):
    """De {carácter: código} a {código: carácter}."""
    return {codigo: caracter for caracter, codigo in codes_dic.items()}


def decodificar_con_diccionario(bits, codes_dic):
    """Reconstruye el texto usando el diccionario inverso de códigos."""
    inverso = invertir_diccionario(codes_dic)
    caracteres = []
    codigo_actual = ""

    for bit in bits.to01():
        codigo_actual += bit
        if codigo_actual in inverso:
            caracteres.append(inverso[codigo_actual])
            codigo_actual = ""

    return "".join(caracteres)


def descomprimir(ruta_huff, ruta_salida=None):
    """
    Descomprime un archivo .huff y guarda el texto reconstruido.

    Por defecto el resultado se guarda junto al .huff como <nombre>.dec.txt.
    Retorna la ruta del archivo de texto generado.
    """
    ruta_huff = Path(ruta_huff)
    encabezado, bits = leer_huff(ruta_huff)
    texto = decodificar_con_diccionario(bits, encabezado["codes_dic"])

    ruta_salida = Path(ruta_salida) if ruta_salida else ruta_huff.with_suffix(".dec.txt")
    with open(ruta_salida, "w", encoding="utf-8", newline="") as archivo:
        archivo.write(texto)

    return ruta_salida


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: python descompresor.py <archivo.huff>")

    print("Texto reconstruido en:", descomprimir(sys.argv[1]))
