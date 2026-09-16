"""
Módulo de Analítica de Riesgo — Reporte Bidimensional y Vecindad
Banco Digital - Sistema Central
Punto 1 del Parcial (Matrices)
"""

UMBRAL_ALERTA_RIESGO = 50  # score a partir del cual una celda se considera "alto riesgo"


def obtener_productos_credito(banco_db):
    """Extrae los nombres de los productos de categoría 'Créditos' activos en el catálogo."""
    productos = banco_db.catalogo_productos.recorrer_adelante()
    return [p["nombre"] for p in productos if p.get("categoria") == "Créditos" and p.get("activo", True)]


def construir_grilla_riesgo(banco_db):
    """
    Construye la grilla densa (lista de listas) de riesgo crediticio a partir
    de la Matriz dispersa banco_db.matriz_riesgo:
        filas    = clientes con al menos un score de riesgo registrado
        columnas = productos de crédito del catálogo
    """
    productos = obtener_productos_credito(banco_db)
    cedulas_con_riesgo = sorted({ced for (ced, _prod) in banco_db.matriz_riesgo.datos.keys()})

    clientes_info = []
    for ced in cedulas_con_riesgo:
        cli = banco_db.tabla_clientes.buscar(ced)
        nombre = cli["nombre"] if cli else f"Cédula {ced}"
        clientes_info.append({"cedula": ced, "nombre": nombre})

    grilla = []
    for cli in clientes_info:
        fila = [banco_db.matriz_riesgo.obtener(cli["cedula"], prod) or 0 for prod in productos]
        grilla.append(fila)

    return grilla, clientes_info, productos


def generar_reporte_extendido(grilla):
    """
    Reto 1: dada una matriz n x m, genera una matriz extendida (n+1) x (m+1):
        - última columna de cada fila:  promedio de riesgo del cliente (fila)
        - última fila (columnas 0..m-1): promedio de riesgo del producto (columna)
        - celda [n][m]:                  promedio general consolidado del banco
    No modifica la grilla original; retorna una matriz nueva.
    """
    n = len(grilla)
    m = len(grilla[0]) if n > 0 else 0

    extendida = [fila[:] + [0.0] for fila in grilla]  # cada fila gana su columna de promedio
    acumulado_columnas = [0.0] * m

    for i in range(n):
        suma_fila = 0.0
        for j in range(m):
            valor = grilla[i][j]
            suma_fila += valor
            acumulado_columnas[j] += valor
        extendida[i][m] = round(suma_fila / m, 2) if m > 0 else 0.0

    fila_promedios = [round(acumulado_columnas[j] / n, 2) if n > 0 else 0.0 for j in range(m)]
    total_general = sum(acumulado_columnas)
    promedio_general = round(total_general / (n * m), 2) if (n * m) > 0 else 0.0
    fila_promedios.append(promedio_general)

    extendida.append(fila_promedios)
    return extendida


def buscar_vecinos_riesgo(grilla, fila, columna, umbral=UMBRAL_ALERTA_RIESGO):
    """
    Reto 2: dado un cliente/producto seleccionado en la grilla ORIGINAL
    (fila, columna), valida y retorna sus vecinos inmediatos, controlando
    estrictamente los bordes de la matriz.
    """
    n = len(grilla)
    m = len(grilla[0]) if n > 0 else 0

    if not (0 <= fila < n) or not (0 <= columna < m):
        raise IndexError(f"Coordenada fuera de la grilla de riesgo: ({fila}, {columna})")

    direcciones = {
        "arriba": (fila - 1, columna),
        "abajo": (fila + 1, columna),
        "izquierda": (fila, columna - 1),
        "derecha": (fila, columna + 1),
    }

    vecinos = {}
    for nombre_dir, (fi, ci) in direcciones.items():
        if 0 <= fi < n and 0 <= ci < m:
            vecinos[nombre_dir] = grilla[fi][ci]
        else:
            vecinos[nombre_dir] = None  # borde de la grilla

    vecinos_validos = {k: v for k, v in vecinos.items() if v is not None}
    en_zona_de_riesgo = len(vecinos_validos) > 0 and all(v >= umbral for v in vecinos_validos.values())

    vecino_mayor = max(vecinos_validos, key=vecinos_validos.get) if vecinos_validos else None
    score_mayor = vecinos_validos.get(vecino_mayor) if vecino_mayor else None

    return {
        "vecinos": vecinos,
        "en_zona_de_riesgo": en_zona_de_riesgo,
        "vecino_mayor_riesgo": vecino_mayor,
        "score_mayor_riesgo": score_mayor,
    }
