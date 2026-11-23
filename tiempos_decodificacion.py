"""
Medición de tiempos de decodificación: diccionario inverso vs. árbol.

Para un archivo por idioma se decodifica el mismo flujo de bits cientos de
veces con cada versión del decodificador y se reporta el promedio y la
desviación estándar del tiempo.

Uso:
    python tiempos_decodificacion.py [repeticiones]     (por defecto 300)
"""

import statistics
import sys
import time
from pathlib import Path

import pandas as pd

from compresor import comprimir
from descompresor import decodificar, leer_huff
from estadisticas_compresion import IDIOMAS, guardar_tabla

ARCHIVOS_ELEGIDOS = {
    "es": Path("textos/es/literatura.txt"),
    "fr": Path("textos/fr/litterature.txt"),
    "en": Path("textos/en/literature.txt"),
}
METODOS = ["diccionario", "arbol"]


def medir_tiempos(encabezado, bits, metodo, repeticiones):
    """Devuelve la lista de tiempos (en milisegundos) de cada decodificación."""
    tiempos = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        decodificar(encabezado, bits, metodo)
        tiempos.append((time.perf_counter() - inicio) * 1000)
    return tiempos


def tabla_tiempos(repeticiones):
    filas = []
    for idioma, ruta in ARCHIVOS_ELEGIDOS.items():
        encabezado, bits = leer_huff(comprimir(ruta, Path("comprimidos") / idioma))

        for metodo in METODOS:
            tiempos = medir_tiempos(encabezado, bits, metodo, repeticiones)
            filas.append({
                "Idioma": IDIOMAS[idioma],
                "Archivo": ruta.name,
                "Método": metodo,
                "Repeticiones": repeticiones,
                "Promedio (ms)": statistics.mean(tiempos),
                "Desv. estándar (ms)": statistics.stdev(tiempos),
            })
            print(f"{IDIOMAS[idioma]:8} {metodo:12} {statistics.mean(tiempos):8.2f} ms")
    return pd.DataFrame(filas)


if __name__ == "__main__":
    total_repeticiones = int(sys.argv[1]) if len(sys.argv) == 2 else 300

    df_tiempos = tabla_tiempos(total_repeticiones)
    guardar_tabla(df_tiempos, "tiempos_decodificacion")

    print()
    print(df_tiempos.round(3).to_string(index=False))
