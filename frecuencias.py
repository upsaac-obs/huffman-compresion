"""
Estadísticas de frecuencia de aparición de cada carácter en un texto.

Las listas que genera este módulo (símbolos y frecuencias) son la entrada
de huffmanCodes() en huffman.py para construir el árbol de Huffman.

Uso:
    python frecuencias.py textos/es/algoritmo.txt
"""

import sys


def leer_texto(ruta):
    """Lee un archivo de texto en UTF-8 y lo devuelve como string."""
    with open(ruta, encoding="utf-8") as archivo:
        return archivo.read()


def contar_frecuencias(texto):
    """
    Cuenta cuántas veces aparece cada carácter del texto.

    Retorna:
        simbolos: lista de caracteres distintos, del más al menos frecuente
        frecuencias: lista con el número de apariciones de cada símbolo
    """
    conteo = {}
    for caracter in texto:
        conteo[caracter] = conteo.get(caracter, 0) + 1

    ordenados = sorted(conteo.items(), key=lambda par: par[1], reverse=True)
    simbolos = [simbolo for simbolo, _ in ordenados]
    frecuencias = [frecuencia for _, frecuencia in ordenados]
    return simbolos, frecuencias


def mostrar_frecuencias(simbolos, frecuencias, limite=20):
    """Imprime los caracteres más frecuentes con su probabilidad."""
    total = sum(frecuencias)
    print(f"Total de caracteres: {total} | Símbolos distintos: {len(simbolos)}")
    print(f"{'Carácter':>10} {'Frecuencia':>11} {'Probabilidad':>13}")

    for simbolo, frecuencia in zip(simbolos[:limite], frecuencias[:limite]):
        print(f"{repr(simbolo):>10} {frecuencia:>11} {frecuencia / total:>13.4f}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: python frecuencias.py <archivo.txt>")

    simbolos, frecuencias = contar_frecuencias(leer_texto(sys.argv[1]))
    mostrar_frecuencias(simbolos, frecuencias)
