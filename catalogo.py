"""
Módulo de Catálogo de Productos y Consulta Previa
Banco Digital - Sistema Central
"""

from ui import (
    cabecera_menu, caja_mensaje, pausa, animacion_timer,
    fmt_dinero, badge, CYAN, VERDE, VERDE_BRILLANTE, AMARILLO, ROJO, ROJO_BRILLANTE, RESET, BOLD, GRIS, MAGENTA
)
from validaciones import leer_numero_entero


def mostrar_ficha_producto(producto):
    """Muestra la ficha técnica detallada de un producto financiero."""
    lineas = [
        f"Nombre:        {BOLD}{producto['nombre']}{RESET}",
        f"Categoría:     {producto.get('categoria', 'General')}",
        f"Estado:        {badge('activo', 'activo') if producto.get('activo', True) else badge('inactivo', 'inactivo')}",
        f"Descripción:   {producto.get('descripcion', 'Sin descripción')}",
        f"Beneficios:    {producto.get('beneficios', 'Beneficios estándar')}",
        f"Requisitos:    {producto.get('requisitos', 'Mayor de edad, cédula vigente')}",
        f"Tasa / Costo:  {producto.get('tasa_o_costo', 'A consultar en sucursal')}",
        f"Monto Mínimo:  {fmt_dinero(producto.get('monto_minimo', 0.0))}"
    ]
    if producto.get("plazo_minimo_meses", 0) > 0:
        lineas.append(f"Plazo Mínimo:  {producto.get('plazo_minimo_meses')} meses")

    caja_mensaje("info", f"FICHA TÉCNICA: {producto['nombre'].upper()}", lineas)


def consultar_catalogo_interactivo(banco_db, sesion=None, permitir_solicitud=False):
    """
    Permite consultar el portafolio y ver detalles de cualquier producto
    ANTES de proceder a solicitarlo o contratarlo.
    """
    while True:
        titulo = "Portafolio de Productos y Servicios"
        cabecera_menu(titulo, sesion.get("tipo") if sesion else None, sesion.get("nombre") if sesion else None)
        print(f"  {GRIS}Explore nuestros productos bancarios y consulte sus condiciones antes de contratar:{RESET}\n")

        productos = [p for p in banco_db.catalogo_productos.recorrer_adelante() if p.get("activo", True)]
        if not productos:
            print(f"  {AMARILLO}No hay productos disponibles en el catálogo en este momento.{RESET}\n")
            pausa()
            break

        cliente = None
        productos_cliente = []
        if sesion and sesion.get("cedula"):
            cliente = banco_db.tabla_clientes.buscar(sesion["cedula"])
            if cliente:
                productos_cliente = cliente.get("productos", [])

        print(f"  {BOLD}{'#':<3} | {'PRODUCTO':<28} | {'CATEGORÍA':<18} | {'ESTADO EN MI CUENTA'}{RESET}")
        print(f"  {'─' * 70}")
        for i, p in enumerate(productos, 1):
            tiene = f"{VERDE_BRILLANTE}[Ya lo tienes]{RESET}" if p["nombre"] in productos_cliente else f"{CYAN}[Disponible]{RESET}"
            print(f"  {CYAN}{i:<3}{RESET} | {p['nombre']:<28} | {p.get('categoria', 'General'):<18} | {tiene}")

        print(f"\n  {CYAN}▸{RESET} Ingrese el número del producto para ver detalles completos y requisitos.")
        print(f"  {ROJO}0.{RESET} Regresar al menú anterior\n")

        sel = leer_numero_entero("Seleccione un producto para consultar [0-" + str(len(productos)) + "]",
                                 minimo=0, maximo=len(productos))
        if sel == 0:
            break

        producto_sel = productos[sel - 1]
        cabecera_menu(f"Detalle de Producto - {producto_sel['nombre']}",
                      sesion.get("tipo") if sesion else None,
                      sesion.get("nombre") if sesion else None)
        mostrar_ficha_producto(producto_sel)

        # Si el usuario es un cliente autenticado y se permite la solicitud directa
        if permitir_solicitud and cliente:
            nombre_prod = producto_sel["nombre"]
            if nombre_prod in productos_cliente:
                print(f"  {AMARILLO}Ya cuentas con el producto '{nombre_prod}' contratado en tu cuenta.{RESET}\n")
                pausa()
            elif "Crédito" in nombre_prod:
                print(f"  {CYAN}ℹ Los productos de crédito requieren radicación y análisis de riesgo.{RESET}")
                print(f"  {GRIS}Puedes solicitarlo formalmente desde la opción de Créditos del menú.{RESET}\n")
                pausa()
            else:
                resp = input(f"  {AMARILLO}?{RESET} ¿Desea vincular y solicitar '{nombre_prod}' a su cuenta ahora? [s/n]: ").strip().lower()
                if resp in ("s", "si", "sí", "y", "yes"):
                    animacion_timer(0.5, f"Vinculando {nombre_prod}")
                    cliente.setdefault("productos", []).append(nombre_prod)
                    banco_db.guardar_clientes()
                    banco_db.auditoria.apilar(f"Producto vinculado: {nombre_prod} por {cliente['nombre']}")
                    caja_mensaje("exito", "PRODUCTO VINCULADO", [
                        f"El producto '{nombre_prod}' ha sido agregado exitosamente a su portafolio.",
                        "Ya se encuentra activo para su uso inmediato."
                    ])
                    pausa()
        else:
            pausa()


def ver_portafolio_publico(banco_db):
    """Consulta pública del catálogo sin necesidad de haber iniciado sesión."""
    consultar_catalogo_interactivo(banco_db, sesion=None, permitir_solicitud=False)
