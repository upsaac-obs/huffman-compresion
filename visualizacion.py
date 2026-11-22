"""
Visualización del árbol de Huffman con Graphviz.

Las hojas (caracteres) se dibujan como cajas y los nodos internos como
círculos con la suma de frecuencias. Cada arista lleva el bit que le
corresponde: 0 hacia la izquierda y 1 hacia la derecha.

Requiere el paquete `graphviz` de Python y el programa `dot` instalado.

Uso:
    python visualizacion.py                       (ejemplo de clase a-f)
    python visualizacion.py textos/es/algoritmo.txt
"""

import sys

from graphviz import Digraph

from frecuencias import contar_frecuencias, leer_texto
from huffman import huffmanCodes

NOMBRES_ESPECIALES = {" ": "espacio", "\n": "salto", "\t": "tab", "\\": "\\\\"}


def es_hoja(nodo):
    return nodo.left is None and nodo.right is None


def nombre_visible(caracter):
    """Nombre legible para caracteres que no se ven en la imagen."""
    return NOMBRES_ESPECIALES.get(caracter, caracter)


def agregar_nodos(grafo, nodo, id_nodo):
    """Agrega recursivamente el nodo y sus hijos al grafo."""
    if es_hoja(nodo):
        grafo.node(id_nodo, f"{nombre_visible(nodo.char)}\n{nodo.data}", shape="box")
        return

    grafo.node(id_nodo, str(nodo.data), shape="circle")
    for bit, hijo in (("0", nodo.left), ("1", nodo.right)):
        id_hijo = id_nodo + bit
        agregar_nodos(grafo, hijo, id_hijo)
        grafo.edge(id_nodo, id_hijo, label=bit)


def dibujar_arbol(root, nombre_salida="arbol_huffman", formato="png"):
    """
    Dibuja el árbol de Huffman y lo guarda como imagen.

    Parámetros:
        root: raíz del árbol devuelta por huffmanCodes()
        nombre_salida: ruta del archivo sin extensión
        formato: formato de imagen soportado por Graphviz (png, svg, pdf...)

    Retorna la ruta del archivo generado.
    """
    grafo = Digraph(format=formato)
    grafo.attr("node", fontsize="10")
    agregar_nodos(grafo, root, "r")
    return grafo.render(nombre_salida, cleanup=True)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        simbolos, frecuencias = contar_frecuencias(leer_texto(sys.argv[1]))
    else:
        simbolos = ["a", "b", "c", "d", "e", "f"]
        frecuencias = [5, 9, 12, 13, 16, 45]

    _, root = huffmanCodes(simbolos, frecuencias)
    print("Árbol guardado en:", dibujar_arbol(root, "resultados/arbol_huffman"))
