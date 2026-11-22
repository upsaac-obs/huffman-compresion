"""
Decodificación (descompresión) de archivos .huff, en dos versiones:

1. Diccionario inverso: se lee el flujo bit a bit acumulando un código;
   en cuanto el código acumulado existe en el diccionario inverso
   {código: carácter} se emite el carácter y se reinicia la acumulación.
   Funciona porque los códigos de Huffman son libres de prefijo.

2. Árbol de Huffman: se parte de la raíz y cada bit indica a qué hijo
   bajar (0 izquierda, 1 derecha). Al llegar a una hoja se emite su
   carácter y se regresa a la raíz.

Uso:
    python descompresor.py comprimidos/algoritmo.huff [diccionario|arbol]
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


def es_hoja(nodo):
    return nodo.left is None and nodo.right is None


def decodificar_con_arbol(bits, root):
    """Reconstruye el texto recorriendo el árbol de Huffman bit a bit."""
    if es_hoja(root):
        return root.char * len(bits)

    caracteres = []
    nodo = root
    for bit in bits:
        nodo = nodo.right if bit else nodo.left
        if es_hoja(nodo):
            caracteres.append(nodo.char)
            nodo = root

    return "".join(caracteres)


def decodificar(encabezado, bits, metodo="arbol"):
    """Decodifica los bits con el método indicado: 'diccionario' o 'arbol'."""
    if metodo == "diccionario":
        return decodificar_con_diccionario(bits, encabezado["codes_dic"])
    if metodo == "arbol":
        return decodificar_con_arbol(bits, encabezado["arbol"])
    raise ValueError(f"Método desconocido: {metodo}")


def descomprimir(ruta_huff, metodo="arbol", ruta_salida=None):
    """
    Descomprime un archivo .huff y guarda el texto reconstruido.

    metodo: 'diccionario' (diccionario inverso) o 'arbol' (árbol de Huffman).

    Por defecto el resultado se guarda junto al .huff como <nombre>.dec.txt.
    Retorna la ruta del archivo de texto generado.
    """
    ruta_huff = Path(ruta_huff)
    encabezado, bits = leer_huff(ruta_huff)
    texto = decodificar(encabezado, bits, metodo)

    ruta_salida = Path(ruta_salida) if ruta_salida else ruta_huff.with_suffix(".dec.txt")
    with open(ruta_salida, "w", encoding="utf-8", newline="") as archivo:
        archivo.write(texto)

    return ruta_salida


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit("Uso: python descompresor.py <archivo.huff> [diccionario|arbol]")

    metodo_elegido = sys.argv[2] if len(sys.argv) == 3 else "arbol"
    print("Texto reconstruido en:", descomprimir(sys.argv[1], metodo_elegido))
