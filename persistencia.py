"""
Módulo de Persistencia en Archivos JSON
Banco Digital - Sistema Central
"""

import os
import json
import datetime
from estructuras import ListaDoble, TablaHash, ColaFIFO, PilaLIFO, ColaPrioridad, Matriz

CARPETA_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

RUTA_USUARIOS = os.path.join(CARPETA_DATA, "usuarios.json")
RUTA_CLIENTES = os.path.join(CARPETA_DATA, "clientes.json")
RUTA_TRANSACCIONES = os.path.join(CARPETA_DATA, "transacciones.json")
RUTA_PRODUCTOS = os.path.join(CARPETA_DATA, "productos.json")
RUTA_SOLICITUDES = os.path.join(CARPETA_DATA, "solicitudes_credito.json")
RUTA_TASAS = os.path.join(CARPETA_DATA, "tasas.json")
RUTA_RIESGO = os.path.join(CARPETA_DATA, "riesgo.json")
RUTA_AUDITORIA = os.path.join(CARPETA_DATA, "auditoria.json")


def asegurar_directorio():
    """Garantiza que la carpeta data exista."""
    os.makedirs(CARPETA_DATA, exist_ok=True)


def escribir_json(ruta, datos):
    """Escribe datos a un archivo JSON con formato legible y codificación UTF-8."""
    asegurar_directorio()
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def leer_json(ruta, por_defecto=None):
    """Lee un archivo JSON o retorna el valor por defecto si no existe o falla."""
    if not os.path.exists(ruta):
        return por_defecto
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return por_defecto


# ============================================================
# DATOS POR DEFECTO DE PRUEBA
# ============================================================
def obtener_usuarios_defecto():
    return {
        "admin": {
            "usuario": "admin",
            "tipo": "administrador",
            "nombre": "ADMINISTRADOR GENERAL",
            "cedula": "1000000001",
            "pin": "1234",
            "activo": True
        },
        "asesor": {
            "usuario": "asesor",
            "tipo": "asesor",
            "nombre": "CARLOS ASESOR BANCARIO",
            "cedula": "1000000002",
            "pin": "1234",
            "activo": True
        },
        "empleado1": {
            "usuario": "empleado1",
            "tipo": "empleado",
            "nombre": "JORGE SALAS",
            "cedula": "1000000004",
            "pin": "1234",
            "activo": True
        },
        "valen": {
            "usuario": "valen",
            "tipo": "cliente",
            "nombre": "VALENTINA MORALES",
            "cedula": "1000000003",
            "pin": "1234",
            "activo": True
        }
    }


def obtener_clientes_defecto():
    return {
        "1000000003": {
            "cedula": "1000000003",
            "nombre": "VALENTINA MORALES",
            "usuario": "valen",
            "pin": "1234",
            "saldo": 35000000.0,  # 35 millones iniciales
            "productos": ["Cuenta de Ahorro", "Tarjeta de Crédito Oro"]
        }
    }


def obtener_transacciones_defecto():
    return [
        {
            "id": "TX-0001",
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "cedula": "1000000003",
            "nombre": "VALENTINA MORALES",
            "tipo": "Depósito Inicial",
            "monto": 35000000.0,
            "saldo_resultante": 35000000.0,
            "detalle": "Apertura de cuenta de ahorros"
        }
    ]


def obtener_productos_defecto():
    return [
        {
            "nombre": "Cuenta de Ahorro",
            "categoria": "Cuentas",
            "descripcion": "Cuenta transaccional con rentabilidad diaria y tarjeta débito Visa sin costo de manejo.",
            "beneficios": "Transferencias gratuitas a cualquier banco, retiros sin tarjeta en red nacional.",
            "requisitos": "Cédula original de 9-10 dígitos, mayoría de edad o autorización de tutor legal.",
            "tasa_o_costo": "Rentabilidad del 3.50% E.A. sobre saldo diario.",
            "monto_minimo": 0.0,
            "plazo_minimo_meses": 0,
            "activo": True
        },
        {
            "nombre": "CDT Digital",
            "categoria": "Inversión",
            "descripcion": "Certificado de Depósito a Término de alta rentabilidad con tasa fija garantizada.",
            "beneficios": "Inversión 100% segura amparada por seguro FOGAFIN, plazos a tu medida.",
            "requisitos": "Monto mínimo desde $500,000 COP y cuenta de ahorros activa.",
            "tasa_o_costo": "Tasa fija entre 10.5% y 11.8% E.A. según plazo.",
            "monto_minimo": 500000.0,
            "plazo_minimo_meses": 3,
            "activo": True
        },
        {
            "nombre": "Tarjeta de Crédito Oro",
            "categoria": "Tarjetas",
            "descripcion": "Tarjeta de crédito con cupo en pesos y dólares, compras sin contacto y millas.",
            "beneficios": "6 meses sin cuota de manejo, asistencias médicas en viajes y casillero virtual.",
            "requisitos": "Ingresos mensuales demostrables desde $2,000,000 COP.",
            "tasa_o_costo": "Tasa de interés de 1.95% M.V. para compras a cuotas.",
            "monto_minimo": 1000000.0,
            "plazo_minimo_meses": 1,
            "activo": True
        },
        {
            "nombre": "Crédito Libre Inversión",
            "categoria": "Créditos",
            "descripcion": "Préstamo de libre destinación con desembolso inmediato y tasa fija en cuota mensual.",
            "beneficios": "Sin cobro por estudio de crédito, plazo hasta 60 meses, abonos a capital sin penalidad.",
            "requisitos": "Edad entre 18 y 75 años, cédula y buen comportamiento crediticio.",
            "tasa_o_costo": "Tasa desde 1.55% a 1.75% mensual según plazo.",
            "monto_minimo": 500000.0,
            "plazo_minimo_meses": 6,
            "activo": True
        },
        {
            "nombre": "Crédito Hipotecario",
            "categoria": "Créditos",
            "descripcion": "Financiación para compra de vivienda nueva o usada (VIS y No VIS) con beneficios tributarios.",
            "beneficios": "Financiación de hasta el 80% del avalúo, cuota fija en pesos o UVR, plazos de 5 a 30 años.",
            "requisitos": "Monto mínimo de $10,000,000 COP, plazo mínimo de 60 meses, soporte de ingresos demostrables.",
            "tasa_o_costo": "Tasa preferencial desde 0.72% a 0.85% mensual (~9.0% a 10.7% E.A.).",
            "monto_minimo": 10000000.0,  # 10 millones mínimo
            "plazo_minimo_meses": 60,    # 60 meses mínimo
            "activo": True
        },
        {
            "nombre": "Pagos Inmediatos QR",
            "categoria": "Servicios Digitales",
            "descripcion": "Ecosistema de pagos y transferencias inmediatas e interoperables mediante código QR.",
            "beneficios": "Sin costo de transacción, acreditación en 5 segundos las 24 horas del día.",
            "requisitos": "Teléfono inteligente y cuenta de ahorros activa.",
            "tasa_o_costo": "$0 COP de tarifa.",
            "monto_minimo": 1000.0,
            "plazo_minimo_meses": 0,
            "activo": True
        }
    ]


def obtener_tasas_defecto():
    return {
        "Crédito Libre Inversión::12": 1.75,
        "Crédito Libre Inversión::24": 1.65,
        "Crédito Libre Inversión::36": 1.55,
        "Crédito Libre Inversión::48": 1.50,
        "Crédito Libre Inversión::60": 1.45,
        "Crédito Hipotecario::60": 0.95,
        "Crédito Hipotecario::120": 0.85,
        "Crédito Hipotecario::180": 0.78,
        "Crédito Hipotecario::240": 0.72,
        "Crédito Hipotecario::360": 0.69
    }


# ============================================================
# CARGA Y SINCRONIZACIÓN
# ============================================================
class EstadoSistema:
    """Contenedor de estado global y estructuras en memoria con soporte JSON."""
    def __init__(self):
        self.lista_clientes = ListaDoble()
        self.tabla_clientes = TablaHash()
        self.tabla_usuarios = TablaHash()
        self.catalogo_productos = ListaDoble()
        self.turnos = ColaFIFO()
        self.auditoria = PilaLIFO()
        self.solicitudes_credito = ColaPrioridad()
        self.matriz_riesgo = Matriz()
        self.matriz_tasas = Matriz()
        self.matriz_transacciones = Matriz()
        self.historial_transacciones = []
        self.sesion_actual = {"usuario": None, "tipo": None, "nombre": None, "cedula": None}

    def cargar_todo(self):
        asegurar_directorio()

        # 1. Usuarios
        usuarios_data = leer_json(RUTA_USUARIOS)
        if not usuarios_data:
            usuarios_data = obtener_usuarios_defecto()
            escribir_json(RUTA_USUARIOS, usuarios_data)
        self.tabla_usuarios.vaciar()
        for k, u in usuarios_data.items():
            self.tabla_usuarios.insertar(k, u)

        # 2. Clientes
        clientes_data = leer_json(RUTA_CLIENTES)
        if not clientes_data:
            clientes_data = obtener_clientes_defecto()
            escribir_json(RUTA_CLIENTES, clientes_data)
        self.tabla_clientes.vaciar()
        self.lista_clientes.vaciar()
        for ced, cli in clientes_data.items():
            self.tabla_clientes.insertar(ced, cli)
            self.lista_clientes.insertar_final(cli)

        # 3. Transacciones
        txs_data = leer_json(RUTA_TRANSACCIONES)
        if txs_data is None:
            txs_data = obtener_transacciones_defecto()
            escribir_json(RUTA_TRANSACCIONES, txs_data)
        self.historial_transacciones = txs_data
        self.matriz_transacciones.vaciar()
        for t in self.historial_transacciones:
            ced = str(t.get("cedula"))
            monto = float(t.get("monto", 0.0))
            acum = self.matriz_transacciones.obtener(ced, "acumulado")
            self.matriz_transacciones.asignar(ced, "acumulado", acum + monto)

        # 4. Productos
        prods_data = leer_json(RUTA_PRODUCTOS)
        if not prods_data:
            prods_data = obtener_productos_defecto()
            escribir_json(RUTA_PRODUCTOS, prods_data)
        self.catalogo_productos.vaciar()
        for p in prods_data:
            self.catalogo_productos.insertar_final(p)

        # 5. Tasas
        tasas_data = leer_json(RUTA_TASAS)
        if not tasas_data:
            tasas_data = obtener_tasas_defecto()
            escribir_json(RUTA_TASAS, tasas_data)
        self.matriz_tasas.cargar_desde_dict(tasas_data)

        # 6. Riesgo
        riesgo_data = leer_json(RUTA_RIESGO)
        if not riesgo_data:
            riesgo_data = {
                "1000000003::Crédito Libre Inversión": 15,
                "1000000003::Crédito Hipotecario": 12
            }
            escribir_json(RUTA_RIESGO, riesgo_data)
        self.matriz_riesgo.cargar_desde_dict(riesgo_data)

        # 7. Solicitudes de crédito
        solicitudes_data = leer_json(RUTA_SOLICITUDES, [])
        self.solicitudes_credito.vaciar()
        for s in solicitudes_data:
            self.solicitudes_credito.insertar(s, s.get("riesgo", 30))

    def guardar_usuarios(self):
        datos = self.tabla_usuarios.to_dict()
        escribir_json(RUTA_USUARIOS, datos)

    def guardar_clientes(self):
        datos = self.tabla_clientes.to_dict()
        escribir_json(RUTA_CLIENTES, datos)

    def guardar_transacciones(self):
        escribir_json(RUTA_TRANSACCIONES, self.historial_transacciones)

    def registrar_transaccion(self, cedula, nombre, tipo, monto, saldo_resultante, detalle):
        """Registra una transacción con persistencia inmediata en transacciones.json."""
        nuevo_id = f"TX-{len(self.historial_transacciones) + 1:04d}"
        tx = {
            "id": nuevo_id,
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "cedula": str(cedula),
            "nombre": nombre,
            "tipo": tipo,
            "monto": float(monto),
            "saldo_resultante": float(saldo_resultante),
            "detalle": detalle
        }
        self.historial_transacciones.append(tx)
        self.guardar_transacciones()

        # Actualiza acumulado en la matriz analítica
        acum = self.matriz_transacciones.obtener(str(cedula), "acumulado")
        self.matriz_transacciones.asignar(str(cedula), "acumulado", acum + float(monto))
        return tx

    def obtener_movimientos_cliente(self, cedula, limite=10):
        """Filtra y devuelve los últimos movimientos de un cliente."""
        ced = str(cedula)
        txs = [t for t in self.historial_transacciones if str(t.get("cedula")) == ced]
        return txs[-limite:]

    def guardar_productos(self):
        prods = self.catalogo_productos.to_list()
        escribir_json(RUTA_PRODUCTOS, prods)

    def guardar_solicitudes(self):
        solicitudes = self.solicitudes_credito.listar_ordenado()
        escribir_json(RUTA_SOLICITUDES, solicitudes)

    def guardar_tasas(self):
        datos = self.matriz_tasas.to_dict()
        escribir_json(RUTA_TASAS, datos)

    def guardar_riesgo(self):
        datos = self.matriz_riesgo.to_dict()
        escribir_json(RUTA_RIESGO, datos)

    def guardar_todo(self):
        self.guardar_usuarios()
        self.guardar_clientes()
        self.guardar_transacciones()
        self.guardar_productos()
        self.guardar_solicitudes()
        self.guardar_tasas()
        self.guardar_riesgo()


# Instancia única del estado del sistema
banco_db = EstadoSistema()
