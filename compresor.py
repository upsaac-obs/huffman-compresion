"""
Codificación (compresión) de un archivo de texto con Huffman.

El archivo .huff generado tiene dos partes:
    1. Encabezado serializado con pickle: diccionario de códigos
       (codes_dic), bits de padding y el árbol de Huffman.
    2. Los bits de la compresión, escritos con bitarray.

Uso:
    python compresor.py textos/es/algoritmo.txt [carpeta_salida]
"""

import pickle
import sys
from pathlib import Path

from bitarray import bitarray

from frecuencias import contar_frecuencias, leer_texto
from huffman import huffmanCodes


def asegurar_codigo_no_vacio(codes_dic):
    """
    Si el texto tiene un solo carácter distinto, el árbol es solo una hoja
    y su código queda vacío (''). Se le asigna '0' para que cada carácter
    ocupe un bit y el texto se pueda reconstruir.
    """
    if len(codes_dic) == 1:
        return {caracter: "0" for caracter in codes_dic}
    return codes_dic


def construir_codigos(codes_dic):
    """Convierte cada código de Huffman (string de 0 y 1) a bitarray."""
    codes = {}
    for c in codes_dic:
        codes[c] = bitarray(codes_dic[c])
    return codes


def codificar_texto(texto, codes):
    """Concatena el código de cada carácter del texto en un solo bitarray."""
    bits = bitarray()
    for caracter in texto:
        bits.extend(codes[caracter])
    return bits


def calcular_padding(bits):
    """Bits de relleno necesarios para completar el último byte."""
    return (8 - len(bits) % 8) % 8


def comprimir(ruta_entrada, carpeta_salida=None):
    """
    Comprime un archivo de texto y genera un archivo con extensión .huff.

    Parámetros:
        ruta_entrada: archivo de texto en UTF-8
        carpeta_salida: dónde guardar el .huff (por defecto, junto al original)

    Retorna la ruta del archivo .huff generado.
    """
    ruta_entrada = Path(ruta_entrada)
    texto = leer_texto(ruta_entrada)

    simbolos, frecuencias = contar_frecuencias(texto)
    codes_dic, root = huffmanCodes(simbolos, frecuencias)
    codes_dic = asegurar_codigo_no_vacio(codes_dic)

    bits = codificar_texto(texto, construir_codigos(codes_dic))
    encabezado = {
        "codes_dic": codes_dic,
        "padding": calcular_padding(bits),
        "arbol": root,
    }

    carpeta = Path(carpeta_salida) if carpeta_salida else ruta_entrada.parent
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta_salida = carpeta / (ruta_entrada.stem + ".huff")

    with open(ruta_salida, "wb") as archivo:
        pickle.dump(encabezado, archivo)
        bits.tofile(archivo)

    return ruta_salida


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit("Uso: python compresor.py <archivo.txt> [carpeta_salida]")

    ruta_original = Path(sys.argv[1])
    ruta_huff = comprimir(ruta_original, sys.argv[2] if len(sys.argv) == 3 else None)

    tamano_original = ruta_original.stat().st_size
    tamano_comprimido = ruta_huff.stat().st_size
    print(f"Archivo comprimido: {ruta_huff}")
    print(f"Tamaño original:    {tamano_original} bytes")
    print(f"Tamaño comprimido:  {tamano_comprimido} bytes")
    print(f"Compression factor: {tamano_comprimido / tamano_original:.4f}")
