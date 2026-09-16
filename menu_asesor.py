"""
Módulo de Operaciones para Asesor Comercial / Empleado
Banco Digital - Sistema Central
"""

import datetime
from ui import (
    cabecera_menu, caja_mensaje, pausa, animacion_timer, confirmar,
    fmt_dinero, badge, CYAN, VERDE, VERDE_BRILLANTE, AMARILLO, ROJO, ROJO_BRILLANTE, RESET, BOLD, GRIS, MAGENTA
)
from validaciones import (
    leer_nombre_validado, leer_cedula_validada, leer_usuario_validado,
    leer_contrasena_confirmada, leer_monto_monetario, leer_texto_simple, normalizar_y_validar_nombre
)


def registrar_nuevo_cliente(banco_db):
    """
    Registro completo de clientes con validaciones estrictas:
    - Nombre y apellido en mayúsculas automáticas.
    - Cédula válida de 9 a 10 dígitos numéricos.
    - Usuario mínimo 8 caracteres alfanuméricos sin caracteres especiales.
    - Contraseña con confirmación doble.
    - Persistencia inmediata en archivos JSON.
    """
    cabecera_menu("Registro Asistido de Cliente", banco_db.sesion_actual.get("tipo"), banco_db.sesion_actual.get("nombre"))
    print(f"  {GRIS}Ingrese la información verificada del nuevo cliente:{RESET}\n")

    # 1. Cédula: 9 a 10 dígitos, no duplicada
    cedula = leer_cedula_validada("Número de Cédula (9 a 10 dígitos)", tabla_clientes=banco_db.tabla_clientes)

    # 2. Nombre: Organizado a mayúsculas, nombre y apellido obligatorios
    nombre = leer_nombre_validado("Nombre Completo (Nombre y Apellido)")

    # 3. Usuario: Mínimo 8 dígitos/caracteres alfanuméricos, sin caracteres especiales
    usuario = leer_usuario_validado("Nombre de Usuario deseado (mínimo 8 caracteres alfanuméricos)", tabla_usuarios=banco_db.tabla_usuarios)

    # 4. Contraseña: Se confirma dos veces obligatoriamente
    pin = leer_contrasena_confirmada("Cree la contraseña / PIN de acceso (mínimo 4 caracteres)")

    # 5. Depósito inicial (soporta valores grandes)
    deposito_inicial = leer_monto_monetario("Depósito de apertura inicial", minimo=0.0, default=0.0)

    print("\n" + "─" * 55)
    if not confirmar(f"¿Confirma registrar al cliente '{nombre}' con cédula {cedula}?"):
        print(f"\n  {AMARILLO}Registro cancelado por el operador.{RESET}")
        pausa()
        return

    animacion_timer(0.5, "Creando cuenta bancaria y generando registros JSON")

    nuevo_cliente = {
        "cedula": cedula,
        "nombre": nombre,
        "usuario": usuario,
        "pin": pin,
        "saldo": deposito_inicial,
        "productos": ["Cuenta de Ahorro"]
    }

    datos_usuario = {
        "usuario": usuario,
        "tipo": "cliente",
        "nombre": nombre,
        "cedula": cedula,
        "pin": pin
    }

    # Inserción en estructuras en memoria
    banco_db.lista_clientes.insertar_final(nuevo_cliente)
    banco_db.tabla_clientes.insertar(cedula, nuevo_cliente)
    banco_db.tabla_usuarios.insertar(usuario, datos_usuario)

    # Registro de depósito inicial si aplica
    if deposito_inicial > 0:
        banco_db.registrar_transaccion(
            cedula=cedula,
            nombre=nombre,
            tipo="Depósito Apertura",
            monto=deposito_inicial,
            saldo_resultante=deposito_inicial,
            detalle="Consignación inicial de fondos en apertura"
        )

    # Persistencia en disco
    banco_db.guardar_clientes()
    banco_db.guardar_usuarios()
    banco_db.auditoria.apilar(f"Cliente registrado: {nombre} ({cedula})")

    caja_mensaje("exito", "CLIENTE REGISTRADO CON ÉXITO", [
        f"Titular:       {nombre}",
        f"Cédula:        {cedula}",
        f"Usuario Login: {BOLD}{usuario}{RESET}",
        f"Saldo Inicial: {fmt_dinero(deposito_inicial)}",
        "Datos guardados permanentemente en data/clientes.json y data/usuarios.json"
    ])
    pausa()


def submenu_gestion_clientes(banco_db):
    """Submenú de administración de clientes para asesores."""
    while True:
        cabecera_menu("Gestión Administrativa de Clientes", banco_db.sesion_actual.get("tipo"), banco_db.sesion_actual.get("nombre"))
        print(f"  {CYAN}1.{RESET} Registrar nuevo cliente {GRIS}(Validaciones estrictas y formato mayúsculas){RESET}")
        print(f"  {CYAN}2.{RESET} Buscar expediente de cliente por cédula")
        print(f"  {CYAN}3.{RESET} Modificar datos de cliente")
        print(f"  {CYAN}4.{RESET} Eliminar cliente del sistema {GRIS}(Sincronización total){RESET}")
        print(f"  {CYAN}5.{RESET} Listar directorio de clientes")
        print(f"  {ROJO}0.{RESET} Volver al menú de asesor\n")

        op = input(f"  {BOLD}Selecciona una opción [0-5]:{RESET} ").strip()

        if op == "1":
            registrar_nuevo_cliente(banco_db)

        elif op == "2":
            cabecera_menu("Búsqueda de Cliente", banco_db.sesion_actual.get("tipo"), banco_db.sesion_actual.get("nombre"))
            cedula = leer_texto_simple("Cédula a consultar")
            animacion_timer(0.3, "Consultando índice en Tabla Hash")
            cliente = banco_db.tabla_clientes.buscar(cedula)
            if cliente:
                caja_mensaje("info", "EXPEDIENTE DE CLIENTE", [
                    f"Cédula:          {cliente['cedula']}",
                    f"Nombre Completo: {cliente['nombre']}",
                    f"Usuario Login:   {cliente['usuario']}",
                    f"Saldo Disponible:{fmt_dinero(cliente['saldo'])}",
                    f"Productos:       {', '.join(cliente.get('productos', []))}"
                ])
            else:
                caja_mensaje("alerta", "NO ENCONTRADO", [f"No existe ningún cliente registrado con la cédula {cedula}."])
            pausa()

        elif op == "3":
            cabecera_menu("Modificación de Datos de Cliente", banco_db.sesion_actual.get("tipo"), banco_db.sesion_actual.get("nombre"))
            cedula = leer_texto_simple("Cédula del cliente a modificar")
            cliente = banco_db.tabla_clientes.buscar(cedula)
            if not cliente:
                print(f"\n  {ROJO}Cliente no encontrado.{RESET}")
                pausa()
                continue

            nombre_anterior = cliente["nombre"]
            print(f"  Nombre actual: {CYAN}{nombre_anterior}{RESET}")
            nuevo_nombre = leer_nombre_validado("Nuevo nombre completo (Nombre y Apellido)")

            if confirmar(f"¿Confirma modificar el nombre a '{nuevo_nombre}'?"):
                animacion_timer(0.4, "Actualizando cliente y usuario en JSON")
                cliente["nombre"] = nuevo_nombre
                usr_data = banco_db.tabla_usuarios.buscar(cliente["usuario"])
                if usr_data:
                    usr_data["nombre"] = nuevo_nombre

                banco_db.guardar_clientes()
                banco_db.guardar_usuarios()

                def reversor():
                    cliente["nombre"] = nombre_anterior
                    if usr_data:
                        usr_data["nombre"] = nombre_anterior
                    banco_db.guardar_clientes()
                    banco_db.guardar_usuarios()
                    return True

                banco_db.auditoria.apilar(f"Modificado nombre {cedula} a {nuevo_nombre}", reversor)
                caja_mensaje("exito", "DATOS ACTUALIZADOS", [f"Nuevo nombre: {nuevo_nombre}"])
            pausa()

        elif op == "4":
            cabecera_menu("Eliminación de Cliente", banco_db.sesion_actual.get("tipo"), banco_db.sesion_actual.get("nombre"))
            cedula = leer_texto_simple("Cédula del cliente a eliminar")
            cliente = banco_db.tabla_clientes.buscar(cedula)
            if not cliente:
                print(f"\n  {ROJO}Cliente no encontrado.{RESET}")
                pausa()
                continue

            if confirmar(f"{ROJO_BRILLANTE}¿Está totalmente seguro de ELIMINAR al cliente {cliente['nombre']} ({cedula})?{RESET}"):
                animacion_timer(0.4, "Eliminando registros asociados y cancelando turnos")
                usr = cliente.get("usuario")
                banco_db.lista_clientes.eliminar(lambda c: str(c["cedula"]) == str(cedula))
                banco_db.tabla_clientes.eliminar(cedula)
                if usr:
                    banco_db.tabla_usuarios.eliminar(usr)
                if banco_db.turnos.contiene(cedula):
                    banco_db.turnos.eliminar(cedula)

                banco_db.guardar_clientes()
                banco_db.guardar_usuarios()
                banco_db.auditoria.apilar(f"Cliente eliminado: {cliente['nombre']} ({cedula})")

                caja_mensaje("exito", "CLIENTE ELIMINADO", [
                    f"El cliente {cliente['nombre']} fue retirado con éxito del sistema.",
                    "Los cambios han sido guardados en los archivos JSON."
                ])
            pausa()

        elif op == "5":
            cabecera_menu("Directorio Completo de Clientes", banco_db.sesion_actual.get("tipo"), banco_db.sesion_actual.get("nombre"))
            todos = banco_db.lista_clientes.recorrer_adelante()
            if not todos:
                print(f"  {AMARILLO}No hay clientes registrados en el sistema.{RESET}\n")
            else:
                print(f"  {BOLD}{'CÉDULA':<12} | {'NOMBRE COMPLETO':<28} | {'USUARIO':<14} | {'SALDO'}{RESET}")
                print(f"  {'─' * 74}")
                for c in todos:
                    print(f"  {c['cedula']:<12} | {c['nombre']:<28} | {c['usuario']:<14} | {fmt_dinero(c['saldo'])}")
                print(f"\n  {GRIS}Total de clientes registrados: {len(todos)}{RESET}")
            pausa()

        elif op == "0":
            break


def submenu_solicitudes_credito(banco_db):
    """Gestión y evaluación de solicitudes de crédito ordenadas por Min-Heap."""
    while True:
        cabecera_menu("Comité de Crédito - Cola de Prioridad", banco_db.sesion_actual.get("tipo"), banco_db.sesion_actual.get("nombre"))
        print(f"  {CYAN}1.{RESET} Ver solicitudes pendientes en orden de prioridad")
        print(f"  {CYAN}2.{RESET} Evaluar y decidir sobre la solicitud con mayor prioridad")
        print(f"  {ROJO}0.{RESET} Volver al menú de asesor\n")

        op = input(f"  {BOLD}Selecciona una opción [0-2]:{RESET} ").strip()

        if op == "1":
            cabecera_menu("Solicitudes en Espera (Ordenadas por Prioridad)", banco_db.sesion_actual.get("tipo"), banco_db.sesion_actual.get("nombre"))
            if banco_db.solicitudes_credito.esta_vacia():
                print(f"  {VERDE}No hay solicitudes de crédito pendientes en la cola.{RESET}\n")
            else:
                items = banco_db.solicitudes_credito.listar_ordenado()
                print(f"  {BOLD}{'#':<3} | {'CLIENTE':<24} | {'PRODUCTO':<24} | {'MONTO':<16} | {'RIESGO'}{RESET}")
                print(f"  {'─' * 78}")
                for i, s in enumerate(items, 1):
                    col_r = VERDE if s['riesgo'] <= 25 else (AMARILLO if s['riesgo'] <= 50 else ROJO)
                    print(f"  {i:<3} | {s['nombre']:<24} | {s['producto']:<24} | {fmt_dinero(s['monto']):<16} | {col_r}{s['riesgo']} pts{RESET}")
                print(f"\n  {GRIS}(Menor score de riesgo = Mayor prioridad de atención){RESET}")
            pausa()

        elif op == "2":
            cabecera_menu("Evaluación de Solicitud Prioritaria", banco_db.sesion_actual.get("tipo"), banco_db.sesion_actual.get("nombre"))
            if banco_db.solicitudes_credito.esta_vacia():
                print(f"  {VERDE}No hay solicitudes pendientes de evaluación.{RESET}\n")
                pausa()
                continue

            solicitud = banco_db.solicitudes_credito.extraer_mayor_prioridad()
            caja_mensaje("info", "EXPEDIENTE CREDITICIO A EVALUAR", [
                f"Titular:       {solicitud['nombre']} ({solicitud['cedula']})",
                f"Producto:      {solicitud['producto']}",
                f"Monto:         {fmt_dinero(solicitud['monto'])}",
                f"Plazo:         {solicitud['plazo']} meses",
                f"Score Riesgo:  {solicitud['riesgo']} puntos"
            ])

            print("  Decisión del comité comercial:")
            print(f"  {VERDE}A.{RESET} Aprobar crédito y realizar desembolso")
            print(f"  {ROJO}R.{RESET} Rechazar crédito")
            print(f"  {AMARILLO}C.{RESET} Devolver solicitud a la cola")
            decision = input(f"\n  {BOLD}Decisión [A/R/C]:{RESET} ").strip().upper()

            if decision == "A":
                if confirmar(f"¿Confirma la APROBACIÓN de {fmt_dinero(solicitud['monto'])} para {solicitud['nombre']}?"):
                    animacion_timer(0.5, "Acreditando desembolso en cuenta bancaria y guardando JSON")
                    cliente = banco_db.tabla_clientes.buscar(solicitud["cedula"])
                    if cliente:
                        cliente["saldo"] += solicitud["monto"]
                        banco_db.registrar_transaccion(
                            cedula=solicitud["cedula"],
                            nombre=cliente["nombre"],
                            tipo="Desembolso Crédito",
                            monto=solicitud["monto"],
                            saldo_resultante=cliente["saldo"],
                            detalle=f"Aprobación de {solicitud['producto']}"
                        )
                        banco_db.guardar_clientes()

                    banco_db.guardar_solicitudes()
                    banco_db.auditoria.apilar(f"Crédito aprobado: {solicitud['nombre']} - {fmt_dinero(solicitud['monto'])}")

                    caja_mensaje("exito", "CRÉDITO APROBADO", [
                        f"Monto desembolsado: {fmt_dinero(solicitud['monto'])}",
                        "Los fondos han sido acreditados y guardados en data/transacciones.json."
                    ])
                else:
                    banco_db.solicitudes_credito.insertar(solicitud, solicitud["riesgo"])
                    banco_db.guardar_solicitudes()
                    print(f"\n  {AMARILLO}Operación cancelada. Solicitud devuelta a la cola.{RESET}")

            elif decision == "R":
                if confirmar("¿Confirma el RECHAZO definitivo de la solicitud?"):
                    animacion_timer(0.4, "Registrando dictamen de rechazo en auditoría")
                    banco_db.guardar_solicitudes()
                    banco_db.auditoria.apilar(f"Crédito rechazado: {solicitud['nombre']} ({solicitud['producto']})")
                    caja_mensaje("error", "SOLICITUD RECHAZADA", [
                        f"La solicitud de {solicitud['nombre']} ha sido rechazada."
                    ])
                else:
                    banco_db.solicitudes_credito.insertar(solicitud, solicitud["riesgo"])
                    banco_db.guardar_solicitudes()
                    print(f"\n  {AMARILLO}Solicitud devuelta a la cola.{RESET}")
            else:
                banco_db.solicitudes_credito.insertar(solicitud, solicitud["riesgo"])
                banco_db.guardar_solicitudes()
                print(f"\n  {AMARILLO}Solicitud devuelta a la cola.{RESET}")
            pausa()

        elif op == "0":
            break


def menu_asesor(banco_db):
    """Panel de operaciones y atención al público para asesores comerciales."""
    while True:
        sesion = banco_db.sesion_actual
        cabecera_menu("Consola de Operaciones - Asesor", sesion.get("tipo"), sesion.get("nombre"))

        pendientes_turnos = banco_db.turnos.tamano()
        pendientes_creditos = banco_db.solicitudes_credito.tamano()

        print(f"  {BOLD}ESTADO EN TIEMPO REAL:{RESET} {CYAN}Turnos en espera:{RESET} {pendientes_turnos} | {MAGENTA}Solicitudes crédito:{RESET} {pendientes_creditos}\n")
        print(f"  {CYAN}1.{RESET} Gestión de clientes (Registrar / Buscar / Modificar / Eliminar)")
        print(f"  {CYAN}2.{RESET} Llamar y atender siguiente turno en ventanilla")
        print(f"  {CYAN}3.{RESET} Gestión de solicitudes de crédito (Aprobar / Rechazar)")
        print(f"  {CYAN}4.{RESET} Consultar matriz de evaluación de riesgo")
        print(f"  {CYAN}5.{RESET} Deshacer última acción {GRIS}(Pila LIFO de reversión){RESET}")
        print(f"  {CYAN}6.{RESET} Ver historial reciente de auditoría")
        print(f"  {ROJO}0.{RESET} Cerrar sesión\n")

        opcion = input(f"  {BOLD}Selecciona una opción [0-6]:{RESET} ").strip()

        if opcion == "1":
            submenu_gestion_clientes(banco_db)

        elif opcion == "2":
            cabecera_menu("Atención de Turnos en Ventanilla", sesion.get("tipo"), sesion.get("nombre"))
            if banco_db.turnos.esta_vacia():
                print(f"  {VERDE}No hay turnos pendientes en la fila de espera.{RESET}\n")
            else:
                animacion_timer(0.4, "Llamando siguiente cliente en fila")
                cedula_turno = banco_db.turnos.desencolar()
                cliente = banco_db.tabla_clientes.buscar(cedula_turno)
                nombre_cliente = cliente["nombre"] if cliente else f"Identificación {cedula_turno}"

                def reversor_turno():
                    banco_db.turnos.encolar_frente(cedula_turno)
                    return True

                banco_db.auditoria.apilar(f"Turno atendido: {nombre_cliente} ({cedula_turno})", reversor_turno)

                caja_mensaje("info", "LLAMANDO A VENTANILLA", [
                    f"Cliente:      {BOLD}{nombre_cliente}{RESET}",
                    f"Documento:    {cedula_turno}",
                    f"Turno:        T-{cedula_turno[-4:]}",
                    f"Atendido por: {sesion.get('nombre')}"
                ])
            pausa()

        elif opcion == "3":
            submenu_solicitudes_credito(banco_db)

        elif opcion == "4":
            cabecera_menu("Consulta de Matriz de Riesgo", sesion.get("tipo"), sesion.get("nombre"))
            cedula = leer_texto_simple("Cédula del cliente a consultar")
            cliente = banco_db.tabla_clientes.buscar(cedula)
            if cliente:
                lineas = [f"Titular: {cliente['nombre']} ({cedula})"]
                for p in ["Crédito Libre Inversión", "Crédito Hipotecario"]:
                    score = banco_db.matriz_riesgo.obtener(cedula, p)
                    score_str = f"{score} puntos" if score else "Sin registro previo (Est: 35)"
                    lineas.append(f"{p}: {score_str}")
                caja_mensaje("info", "SCORES DE RIESGO CREDITICIO", lineas)
            else:
                print(f"\n  {AMARILLO}No se encontró ningún cliente con esa cédula.{RESET}\n")
            pausa()

        elif opcion == "5":
            cabecera_menu("Deshacer Última Operación", sesion.get("tipo"), sesion.get("nombre"))
            animacion_timer(0.4, "Verificando pila LIFO de reversión")
            exito, msj = banco_db.auditoria.deshacer_ultima()
            tipo_caja = "exito" if exito else "alerta"
            caja_mensaje(tipo_caja, "RESULTADO DE DESHACER", [msj])
            pausa()

        elif opcion == "6":
            cabecera_menu("Historial de Auditoría (Pila LIFO)", sesion.get("tipo"), sesion.get("nombre"))
            historial = banco_db.auditoria.ver_historial()
            if not historial:
                print(f"  {AMARILLO}No hay acciones registradas en la pila de auditoría.{RESET}\n")
            else:
                print(f"  {BOLD}{'HORA':<10} | {'ACCIÓN REGISTRADA'}{RESET}")
                print(f"  {'─' * 60}")
                for acc in historial[:15]:
                    rev_txt = f"{VERDE_BRILLANTE}[Reversible]{RESET}" if acc.funcion_deshacer else f"{GRIS}[Log]{RESET}"
                    print(f"  {acc.fecha:<10} | {acc.descripcion:<38} {rev_txt}")
                print(f"\n  {GRIS}(Mostrando las 15 acciones más recientes){RESET}")
            pausa()

        elif opcion == "0":
            animacion_timer(0.3, "Cerrando sesión de asesor")
            banco_db.sesion_actual.update({"usuario": None, "tipo": None, "nombre": None, "cedula": None})
            break
        else:
            print(f"\n  {ROJO}Opción no válida.{RESET}")
            pausa()
