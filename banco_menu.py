"""
Sistema Bancario Digital
Punto de Entrada Principal (Orquestador Central)
Arquitectura Modular y Persistencia en Archivos JSON
"""

import sys
import time

# Re-exportaciones para máxima compatibilidad
from estructuras import NodoDoble, ListaDoble, ColaFIFO, AccionReversible, PilaLIFO, ColaPrioridad, TablaHash, Matriz
from ui import (
    limpiar_pantalla, banner_principal, banner_credenciales_prueba,
    cabecera_menu, caja_mensaje, animacion_timer, pausa, leer_pin_enmascarado,
    CYAN, VERDE, VERDE_BRILLANTE, AMARILLO, ROJO, MAGENTA, RESET, BOLD, GRIS, fmt_dinero
)
from validaciones import leer_texto_simple
from persistencia import banco_db
from catalogo import ver_portafolio_publico
from menu_cliente import menu_cliente
from menu_asesor import menu_asesor, registrar_nuevo_cliente
from menu_admin import menu_administrador


def iniciar_sesion():
    cabecera_menu("Inicio de Sesión")
    print(f"  {GRIS}Ingrese sus credenciales registradas:{RESET}\n")

    usuario = leer_texto_simple("Usuario").lower()
    datos = banco_db.tabla_usuarios.buscar(usuario)

    if not datos:
        animacion_timer(0.3, "Verificando credenciales")
        caja_mensaje("error", "ACCESO DENEGADO", [
            f"El usuario '{usuario}' no fue encontrado en el sistema.",
            "Verifique la ortografía o puede crear un usuario si es nuevo cliente."
        ])
        pausa()
        return False

    # Comprobar si el usuario se encuentra activo
    if not datos.get("activo", True):
        animacion_timer(0.3, "Verificando estado de cuenta")
        caja_mensaje("error", "CUENTA DESACTIVADA", [
            f"El usuario '{usuario}' ha sido desactivado temporalmente.",
            "Comuníquese con el Administrador General para reactivar su acceso."
        ])
        banco_db.auditoria.apilar(f"Intento de ingreso usuario inactivo: {usuario}")
        pausa()
        return False

    pin_ingresado = leer_pin_enmascarado("Contraseña / PIN de seguridad")

    animacion_timer(0.3, "Validando credenciales bancarias")
    if datos.get("pin") != pin_ingresado:
        caja_mensaje("error", "CONTRASEÑA INCORRECTA", [
            "La contraseña o PIN ingresado no coincide con el registrado.",
            "Por seguridad, el intento fallido ha sido registrado."
        ])
        banco_db.auditoria.apilar(f"Intento fallido de login para: {usuario}")
        pausa()
        return False

    # Actualiza sesión activa
    tipo_rol = datos.get("tipo", "cliente")
    banco_db.sesion_actual.update({
        "usuario": usuario,
        "tipo": tipo_rol,
        "nombre": datos.get("nombre"),
        "cedula": datos.get("cedula")
    })

    print(f"\n  {VERDE_BRILLANTE}✓ Autenticación exitosa como {tipo_rol.upper()}.{RESET}")
    time.sleep(0.4)
    return True


def mostrar_credenciales_prueba():
    """Muestra cuadro modal con todas las credenciales de prueba disponibles."""
    cabecera_menu("Credenciales de Prueba Preconfiguradas")
    banner_credenciales_prueba()
    print(f"  {GRIS}Estas cuentas están listas para ser utilizadas en las pruebas.{RESET}")
    print(f"  {GRIS}Cualquier nuevo cliente o usuario registrado también se guardará en los archivos JSON.{RESET}\n")
    pausa()


def menu_principal():
    """Bucle principal de la aplicación bancaria."""
    # Carga datos desde archivos JSON (o inicializa por defecto)
    banco_db.cargar_todo()

    while True:
        limpiar_pantalla()
        banner_principal()

        print(f"  {BOLD}Bienvenido a la plataforma bancaria central.{RESET}")
        print(f"  {GRIS}Seleccione una opción para interactuar con el sistema:{RESET}\n")
        print(f"  {CYAN}1.{RESET} {BOLD}Iniciar sesión{RESET}")
        print(f"  {CYAN}2.{RESET} {BOLD}Registrarme como nuevo cliente{RESET}")
        print(f"  {CYAN}3.{RESET} {BOLD}Consultar portafolio de productos y tasas{RESET}")
        print(f"  {ROJO}0.{RESET} Salir del sistema\n")

        opcion = input(f"  {BOLD}Selecciona una opción [0-3]:{RESET} ").strip()

        if opcion == "1":
            if iniciar_sesion():
                rol = banco_db.sesion_actual.get("tipo")
                if rol == "cliente":
                    menu_cliente(banco_db)
                elif rol in ("asesor", "empleado"):
                    menu_asesor(banco_db)
                elif rol == "administrador":
                    menu_administrador(banco_db)

        elif opcion == "2":
            registrar_nuevo_cliente(banco_db)

        elif opcion == "3":
            ver_portafolio_publico(banco_db)

        elif opcion == "0":
            limpiar_pantalla()
            animacion_timer(0.3, "Cerrando canales de conexión segura y guardando datos")
            banco_db.guardar_todo()
            caja_mensaje("info", "GRACIAS POR SU VISITA", [
                "Gracias por utilizar los servicios de Banco Digital.",
                "Todas sus transacciones e información han sido almacenadas en archivos JSON.",
                "¡Que tenga un excelente día!"
            ])
            break
        else:
            print(f"\n  {ROJO}Opción no válida.{RESET}")
            time.sleep(0.5)


if __name__ == "__main__":
    try:
        menu_principal()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n{AMARILLO}Programa interrumpido por el usuario. Saliendo limpiamente...{RESET}")
        sys.exit(0)
