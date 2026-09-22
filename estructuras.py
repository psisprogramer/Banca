"""
Módulo de Estructuras de Datos Fundamentales
Banco Digital - Sistema Central
"""

import heapq
import datetime
from collections import deque


class NodoDoble:
    """Nodo para la estructura Lista Doblemente Enlazada."""
    def __init__(self, dato):
        self.dato = dato
        self.anterior = None
        self.siguiente = None


class ListaDoble:
    """Lista doblemente enlazada con soporte para inserción, búsqueda y eliminación."""
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.tamano = 0

    def insertar_final(self, dato):
        nodo = NodoDoble(dato)
        if not self.cabeza:
            self.cabeza = self.cola = nodo
        else:
            nodo.anterior = self.cola
            self.cola.siguiente = nodo
            self.cola = nodo
        self.tamano += 1
        return nodo

    def insertar_inicio(self, dato):
        nodo = NodoDoble(dato)
        if not self.cabeza:
            self.cabeza = self.cola = nodo
        else:
            nodo.siguiente = self.cabeza
            self.cabeza.anterior = nodo
            self.cabeza = nodo
        self.tamano += 1
        return nodo

    def buscar(self, predicado):
        actual = self.cabeza
        while actual:
            if predicado(actual.dato):
                return actual.dato
            actual = actual.siguiente
        return None

    def eliminar(self, predicado):
        actual = self.cabeza
        while actual:
            if predicado(actual.dato):
                if actual.anterior:
                    actual.anterior.siguiente = actual.siguiente
                else:
                    self.cabeza = actual.siguiente

                if actual.siguiente:
                    actual.siguiente.anterior = actual.anterior
                else:
                    self.cola = actual.anterior

                self.tamano -= 1
                return True
            actual = actual.siguiente
        return False

    def recorrer_adelante(self):
        actual = self.cabeza
        elementos = []
        while actual:
            elementos.append(actual.dato)
            actual = actual.siguiente
        return elementos

    def recorrer_atras(self):
        actual = self.cola
        elementos = []
        while actual:
            elementos.append(actual.dato)
            actual = actual.anterior
        return elementos

    def vaciar(self):
        self.cabeza = None
        self.cola = None
        self.tamano = 0

    def to_list(self):
        return self.recorrer_adelante()


class ColaFIFO:
    """Cola First-In-First-Out optimizada con tiempo O(1) en desencolado."""
    def __init__(self):
        self._items = deque()

    def encolar(self, item):
        self._items.append(item)

    def desencolar(self):
        return self._items.popleft() if self._items else None

    def esta_vacia(self):
        return len(self._items) == 0

    def contiene(self, item):
        return item in self._items

    def posicion(self, item):
        try:
            return self._items.index(item) + 1
        except ValueError:
            return None

    def eliminar(self, item):
        try:
            self._items.remove(item)
            return True
        except ValueError:
            return False

    def encolar_frente(self, item):
        """Permite reinsertar un elemento al inicio si se revierte una atención."""
        self._items.appendleft(item)

    def tamano(self):
        return len(self._items)

    def listar(self):
        return list(self._items)

    def vaciar(self):
        self._items.clear()


class AccionReversible:
    """Representa una acción apilable en el historial con capacidad de reversión."""
    def __init__(self, descripcion, funcion_deshacer=None):
        self.descripcion = descripcion
        self.funcion_deshacer = funcion_deshacer
        self.fecha = datetime.datetime.now().strftime("%H:%M:%S")

    def deshacer(self):
        if self.funcion_deshacer:
            return self.funcion_deshacer()
        return False


class PilaLIFO:
    """Pila Last-In-First-Out con soporte para deshacer operaciones reales."""
    def __init__(self):
        self._items = []

    def apilar(self, descripcion, funcion_deshacer=None):
        accion = AccionReversible(descripcion, funcion_deshacer)
        self._items.append(accion)

    def desapilar(self):
        return self._items.pop() if self._items else None

    def deshacer_ultima(self):
        if not self._items:
            return False, "No hay acciones registradas en el historial de auditoría."

        # Busca en orden LIFO (de la más reciente a la más antigua) la última acción reversible
        for i in range(len(self._items) - 1, -1, -1):
            accion = self._items[i]
            if accion.funcion_deshacer is not None:
                self._items.pop(i)
                try:
                    exito = accion.deshacer()
                    if exito:
                        return True, f"Revertido con éxito: {accion.descripcion}"
                    return False, f"La operación no pudo ser revertida: {accion.descripcion}"
                except Exception as e:
                    return False, f"Error al revertir '{accion.descripcion}': {str(e)}"

        return False, "No hay acciones reversibles pendientes en la pila (los eventos registrados son informativos)."

    def ver_historial(self):
        return list(reversed(self._items))

    def tamano(self):
        return len(self._items)

    def vaciar(self):
        self._items.clear()


class ColaPrioridad:
    """Cola de prioridad implementada con un Min-Heap garantizando estabilidad temporal."""
    def __init__(self):
        self._heap = []
        self._contador = 0

    def insertar(self, item, prioridad):
        # Prioridad numérica: menor valor = mayor prioridad de atención
        heapq.heappush(self._heap, (prioridad, self._contador, item))
        self._contador += 1

    def extraer_mayor_prioridad(self):
        return heapq.heappop(self._heap)[2] if self._heap else None

    def esta_vacia(self):
        return len(self._heap) == 0

    def listar_ordenado(self):
        return [item for _, _, item in sorted(self._heap)]

    def tamano(self):
        return len(self._heap)

    def vaciar(self):
        self._heap.clear()
        self._contador = 0


class TablaHash:
    """Tabla Hash con encadenamiento por buckets y rehashing dinámico."""
    def __init__(self, tamano_inicial=17):
        self.tamano = tamano_inicial
        self.cantidad_elementos = 0
        self.buckets = [[] for _ in range(self.tamano)]

    def _hash(self, clave):
        return abs(hash(str(clave))) % self.tamano

    def _rehashing(self):
        nuevo_tamano = self.tamano * 2 + 1
        antiguos_buckets = self.buckets
        self.tamano = nuevo_tamano
        self.buckets = [[] for _ in range(nuevo_tamano)]
        self.cantidad_elementos = 0

        for bucket in antiguos_buckets:
            for clave, valor in bucket:
                self.insertar(clave, valor)

    def insertar(self, clave, valor):
        # Rehashing si el factor de carga excede 0.75
        if self.cantidad_elementos / self.tamano > 0.75:
            self._rehashing()

        idx = self._hash(clave)
        for i, (k, _) in enumerate(self.buckets[idx]):
            if k == str(clave):
                self.buckets[idx][i] = (str(clave), valor)
                return
        self.buckets[idx].append((str(clave), valor))
        self.cantidad_elementos += 1

    def buscar(self, clave):
        idx = self._hash(clave)
        for k, v in self.buckets[idx]:
            if k == str(clave):
                return v
        return None

    def eliminar(self, clave):
        idx = self._hash(clave)
        bucket = self.buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == str(clave):
                del bucket[i]
                self.cantidad_elementos -= 1
                return True
        return False

    def listar_claves(self):
        claves = []
        for bucket in self.buckets:
            for clave, _ in bucket:
                claves.append(clave)
        return claves

    def listar_valores(self):
        valores = []
        for bucket in self.buckets:
            for _, valor in bucket:
                valores.append(valor)
        return valores

    def to_dict(self):
        resultado = {}
        for bucket in self.buckets:
            for clave, valor in bucket:
                resultado[clave] = valor
        return resultado

    def vaciar(self):
        self.buckets = [[] for _ in range(self.tamano)]
        self.cantidad_elementos = 0


class Matriz:
    """Matriz bidimensional dispersa indexada por tuplas (fila, columna)."""
    def __init__(self, valor_inicial=0):
        self.datos = {}
        self.valor_inicial = valor_inicial

    def asignar(self, fila, columna, valor):
        self.datos[(str(fila), str(columna))] = valor

    def obtener(self, fila, columna):
        return self.datos.get((str(fila), str(columna)), self.valor_inicial)

    def to_dict(self):
        # Transforma tuplas a strings con formato "fila::columna" para JSON
        return {f"{k[0]}::{k[1]}": v for k, v in self.datos.items()}

    def cargar_desde_dict(self, d):
        self.datos = {}
        for k, v in d.items():
            if "::" in k:
                f, c = k.split("::", 1)
                self.datos[(f, c)] = v

    def vaciar(self):
        self.datos.clear()
