"""
Módulo de Banca Personas (Menú Cliente)
Banco Digital - Sistema Central
"""

import datetime
from ui import (
    cabecera_menu, caja_mensaje, pausa, animacion_timer, confirmar,
    fmt_dinero, badge, CYAN, VERDE, VERDE_BRILLANTE, AMARILLO, ROJO, RESET, BOLD, GRIS
)
from validaciones import (
    leer_monto_monetario, leer_numero_entero, leer_texto_simple, validar_cedula
)
from catalogo import consultar_catalogo_interactivo


def menu_cliente(banco_db):
    """Panel de autoservicio y banca digital para clientes."""
    while True:
        sesion = banco_db.sesion_actual
        cedula = sesion.get("cedula")
        cliente = banco_db.tabla_clientes.buscar(cedula)

        if not cliente:
            caja_mensaje("error", "SESIÓN EXPIRADA", ["Su cuenta de cliente no se encuentra activa en el sistema."])
            pausa()
            banco_db.sesion_actual.update({"usuario": None, "tipo": None, "nombre": None, "cedula": None})
            break

        cabecera_menu("Portal de Banca Personas", sesion["tipo"], sesion["nombre"])
        saldo_actual = cliente.get("saldo", 0.0)
        print(f"  {BOLD}SALDO DISPONIBLE:{RESET} {VERDE_BRILLANTE}{fmt_dinero(saldo_actual)}{RESET}\n")
        print(f"  {CYAN}1.{RESET} Consultar perfil y productos activos")
        print(f"  {CYAN}2.{RESET} Ver historial de movimientos de cuenta")
        print(f"  {CYAN}3.{RESET} Realizar depósito / consignación {GRIS}(Soporta grandes montos){RESET}")
        print(f"  {CYAN}4.{RESET} Realizar retiro de fondos")
        print(f"  {CYAN}5.{RESET} Transferir dinero a otro cliente")
        print(f"  {CYAN}6.{RESET} Solicitar crédito o préstamo {GRIS}(Hipotecario / Libre Inversión){RESET}")
        print(f"  {CYAN}7.{RESET} Simular cuotas de crédito")
        print(f"  {CYAN}8.{RESET} Solicitar turno de atención en sucursal")
        print(f"  {CYAN}9.{RESET} Consultar estado de mi turno")
        print(f"  {CYAN}10.{RESET} Consultar catálogo de productos y solicitar vinculación")
        print(f"  {ROJO}0.{RESET} Salir / Cerrar sesión\n")

        opcion = input(f"  {BOLD}Selecciona una opción [0-10]:{RESET} ").strip()

        # ----------------------------------------------------
        # 1. PERFIL
        # ----------------------------------------------------
        if opcion == "1":
            cabecera_menu("Mi Perfil Bancario", sesion["tipo"], sesion["nombre"])
            productos_activos = cliente.get("productos", ["Cuenta de Ahorro"])
            lineas = [
                f"Cédula:          {cliente['cedula']}",
                f"Nombre Completo: {cliente['nombre']}",
                f"Usuario:         {cliente['usuario']}",
                f"Saldo Actual:    {fmt_dinero(cliente['saldo'])}",
                f"Productos:       {', '.join(productos_activos)}"
            ]
            caja_mensaje("info", "DATOS DEL CLIENTE", lineas)
            pausa()

        # ----------------------------------------------------
        # 2. HISTORIAL DE MOVIMIENTOS
        # ----------------------------------------------------
        elif opcion == "2":
            cabecera_menu("Historial de Movimientos", sesion["tipo"], sesion["nombre"])
            movimientos = banco_db.obtener_movimientos_cliente(cedula, limite=15)
            if not movimientos:
                print(f"\n  {AMARILLO}Aún no tienes movimientos registrados en tu cuenta.{RESET}\n")
            else:
                print(f"  {BOLD}{'FECHA':<17} | {'TIPO':<22} | {'MONTO':<20} | {'DETALLE'}{RESET}")
                print(f"  {'─' * 78}")
                for m in reversed(movimientos):
                    tipo_m = m.get("tipo", "")
                    signo = "+" if any(x in tipo_m for x in ["Depósito", "Recibida", "Desembolso"]) else "-"
                    col = VERDE if signo == "+" else ROJO
                    monto_str = f"{signo}{fmt_dinero(m['monto'])}"
                    print(f"  {m.get('fecha', ''):<17} | {tipo_m:<22} | {col}{monto_str:<20}{RESET} | {m.get('detalle', '')}")
                print(f"\n  {GRIS}(Mostrando los últimos {len(movimientos)} movimientos registrados en JSON){RESET}")
            pausa()

        # ----------------------------------------------------
        # 3. DEPÓSITOS (SOPORTE PARA VALORES MUY GRANDES)
        # ----------------------------------------------------
        elif opcion == "3":
            cabecera_menu("Depósito de Fondos", sesion["tipo"], sesion["nombre"])
            print(f"  {GRIS}Ingrese el monto a consignar (admite formatos como 50000000 o 50.000.000):{RESET}\n")
            monto = leer_monto_monetario("Monto a depositar", minimo=1000.0)

            if confirmar(f"¿Confirma el depósito por valor de {fmt_dinero(monto)}?"):
                animacion_timer(0.5, "Procesando abono bancario seguro")
                cliente["saldo"] += monto

                # Registro persistente en transacciones.json y clientes.json
                tx = banco_db.registrar_transaccion(
                    cedula=cedula,
                    nombre=cliente["nombre"],
                    tipo="Depósito",
                    monto=monto,
                    saldo_resultante=cliente["saldo"],
                    detalle="Consignación bancaria de fondos"
                )
                banco_db.guardar_clientes()
                banco_db.auditoria.apilar(f"Depósito de {fmt_dinero(monto)} a {cliente['nombre']}")

                caja_mensaje("recibo", "COMPROBANTE DE DEPÓSITO", [
                    f"Comprobante Nº:  {tx['id']}",
                    f"Titular:         {cliente['nombre']} ({cedula})",
                    f"Fecha y Hora:    {tx['fecha']}",
                    f"Monto Abonado:   {fmt_dinero(monto)}",
                    f"Nuevo Saldo:     {fmt_dinero(cliente['saldo'])}",
                    f"Estado:          {badge('exito', 'exito')}"
                ])
            else:
                print(f"\n  {AMARILLO}Operación de depósito cancelada.{RESET}")
            pausa()

        # ----------------------------------------------------
        # 4. RETIRO
        # ----------------------------------------------------
        elif opcion == "4":
            cabecera_menu("Retiro de Fondos en Cajero", sesion["tipo"], sesion["nombre"])
            print(f"  Saldo disponible actual: {VERDE_BRILLANTE}{fmt_dinero(cliente['saldo'])}{RESET}\n")
            monto = leer_monto_monetario("Monto a retirar", minimo=1000.0)

            if monto > cliente["saldo"]:
                caja_mensaje("error", "FONDOS INSUFICIENTES", [
                    f"El monto solicitado ({fmt_dinero(monto)}) excede tu saldo disponible.",
                    f"Saldo actual: {fmt_dinero(cliente['saldo'])}"
                ])
                pausa()
                continue

            if confirmar(f"¿Desea retirar {fmt_dinero(monto)} de su cuenta?"):
                animacion_timer(0.5, "Dispensando efectivo y actualizando saldos")
                cliente["saldo"] -= monto

                tx = banco_db.registrar_transaccion(
                    cedula=cedula,
                    nombre=cliente["nombre"],
                    tipo="Retiro Cajero",
                    monto=monto,
                    saldo_resultante=cliente["saldo"],
                    detalle="Retiro de efectivo en cajero digital"
                )
                banco_db.guardar_clientes()
                banco_db.auditoria.apilar(f"Retiro de {fmt_dinero(monto)} por {cliente['nombre']}")

                caja_mensaje("recibo", "COMPROBANTE DE RETIRO", [
                    f"Comprobante Nº:  {tx['id']}",
                    f"Titular:         {cliente['nombre']} ({cedula})",
                    f"Fecha y Hora:    {tx['fecha']}",
                    f"Monto Retirado:  {fmt_dinero(monto)}",
                    f"Saldo Restante:  {fmt_dinero(cliente['saldo'])}",
                    f"Estado:          {badge('exito', 'exito')}"
                ])
            else:
                print(f"\n  {AMARILLO}Retiro cancelado.{RESET}")
            pausa()

        # ----------------------------------------------------
        # 5. TRANSFERENCIAS
        # ----------------------------------------------------
        elif opcion == "5":
            cabecera_menu("Transferencia Inmediata entre Cuentas", sesion["tipo"], sesion["nombre"])
            print(f"  Saldo disponible: {VERDE_BRILLANTE}{fmt_dinero(cliente['saldo'])}{RESET}\n")
            cedula_dest = leer_texto_simple("Cédula del cliente destinatario")

            if cedula_dest == cedula:
                print(f"\n  {ROJO}No puedes realizar transferencias a tu propia cuenta.{RESET}")
                pausa()
                continue

            destinatario = banco_db.tabla_clientes.buscar(cedula_dest)
            if not destinatario:
                animacion_timer(0.3, "Buscando titular destinatario")
                caja_mensaje("error", "DESTINATARIO NO ENCONTRADO", [
                    f"No existe ningún cliente registrado con la cédula {cedula_dest}.",
                    "Verifique la cédula e intente de nuevo."
                ])
                pausa()
                continue

            print(f"  {CYAN}Destinatario confirmado:{RESET} {BOLD}{destinatario['nombre']}{RESET}\n")
            monto = leer_monto_monetario("Monto a transferir", minimo=500.0)

            if monto > cliente["saldo"]:
                caja_mensaje("error", "FONDOS INSUFICIENTES", [
                    f"No cuentas con saldo suficiente para transferir {fmt_dinero(monto)}.",
                    f"Saldo actual: {fmt_dinero(cliente['saldo'])}"
                ])
                pausa()
                continue

            if confirmar(f"¿Confirma transferir {fmt_dinero(monto)} a {destinatario['nombre']}?"):
                animacion_timer(0.6, "Validando candados bancarios y procesando transferencia")
                cliente["saldo"] -= monto
                destinatario["saldo"] += monto

                # Registra transacciones para emisor y receptor
                tx_emisor = banco_db.registrar_transaccion(
                    cedula=cedula,
                    nombre=cliente["nombre"],
                    tipo="Transferencia Enviada",
                    monto=monto,
                    saldo_resultante=cliente["saldo"],
                    detalle=f"A: {destinatario['nombre']} ({cedula_dest})"
                )
                banco_db.registrar_transaccion(
                    cedula=cedula_dest,
                    nombre=destinatario["nombre"],
                    tipo="Transferencia Recibida",
                    monto=monto,
                    saldo_resultante=destinatario["saldo"],
                    detalle=f"De: {cliente['nombre']} ({cedula})"
                )
                banco_db.guardar_clientes()
                banco_db.auditoria.apilar(f"Transferencia de {fmt_dinero(monto)} de {cliente['nombre']} a {destinatario['nombre']}")

                caja_mensaje("recibo", "COMPROBANTE DE TRANSFERENCIA", [
                    f"Comprobante Nº:  {tx_emisor['id']}",
                    f"Emisor:          {cliente['nombre']} ({cedula})",
                    f"Destinatario:    {destinatario['nombre']} ({cedula_dest})",
                    f"Fecha y Hora:    {tx_emisor['fecha']}",
                    f"Monto Enviado:   {fmt_dinero(monto)}",
                    f"Saldo Restante:  {fmt_dinero(cliente['saldo'])}",
                    f"Estado:          {badge('exito', 'exito')}"
                ])
            else:
                print(f"\n  {AMARILLO}Transferencia cancelada.{RESET}")
            pausa()

        # ----------------------------------------------------
        # 6. SOLICITUD DE CRÉDITO (REGLAS DE CRÉDITO HIPOTECARIO)
        # ----------------------------------------------------
        elif opcion == "6":
            cabecera_menu("Solicitud de Crédito", sesion["tipo"], sesion["nombre"])
            print("  Líneas de crédito disponibles:")
            print("  1. Crédito Libre Inversión (Mínimo: $500.000 COP, Plazo: 6 a 60 meses)")
            print("  2. Crédito Hipotecario     (Mínimo: $10.000.000 COP, Plazo: 60 a 360 meses)")
            sel = leer_numero_entero("Seleccione el tipo de crédito [1-2]", minimo=1, maximo=2)

            if sel == 1:
                producto = "Crédito Libre Inversión"
                monto_min = 500000.0
                plazo_min = 6
                plazo_max = 60
            else:
                producto = "Crédito Hipotecario"
                monto_min = 10000000.0  # Mínimo 10 millones exigido
                plazo_min = 60          # Plazo mínimo 60 meses exigido
                plazo_max = 360

            print(f"\n  {CYAN}▸ Solicitando:{RESET} {BOLD}{producto}{RESET}")
            print(f"  {GRIS}Condiciones mínimas: Monto mínimo {fmt_dinero(monto_min)} | Plazo mínimo {plazo_min} meses{RESET}\n")

            monto = leer_monto_monetario(f"Monto solicitado para {producto}", minimo=monto_min)
            plazo = leer_numero_entero(f"Plazo en meses deseado [{plazo_min}-{plazo_max}]",
                                       minimo=plazo_min, maximo=plazo_max)

            score_riesgo = banco_db.matriz_riesgo.obtener(cedula, producto)
            if not score_riesgo or score_riesgo == 0:
                score_riesgo = 18 if cliente["saldo"] > 5000000 else 38
                banco_db.matriz_riesgo.asignar(cedula, producto, score_riesgo)
                banco_db.guardar_riesgo()

            solicitud = {
                "cedula": cedula,
                "nombre": cliente["nombre"],
                "producto": producto,
                "monto": monto,
                "plazo": plazo,
                "riesgo": score_riesgo,
                "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            if confirmar(f"¿Confirma radicar la solicitud de {fmt_dinero(monto)} a {plazo} meses para {producto}?"):
                animacion_timer(0.5, "Radicando solicitud en cola de prioridad de evaluación de riesgo")
                banco_db.solicitudes_credito.insertar(solicitud, score_riesgo)
                banco_db.guardar_solicitudes()
                banco_db.auditoria.apilar(f"Solicitud crédito: {cliente['nombre']} - {producto} - {fmt_dinero(monto)}")

                caja_mensaje("exito", "SOLICITUD RADICADA CON ÉXITO", [
                    f"Producto:        {producto}",
                    f"Monto:           {fmt_dinero(monto)}",
                    f"Plazo:           {plazo} meses",
                    f"Score de Riesgo: {score_riesgo} pts (Min-Heap Prioritario)",
                    f"Estado:          {badge('pendiente', 'pendiente')}",
                    "El comité comercial evaluará su solicitud según su prioridad de riesgo."
                ])
            else:
                print(f"\n  {AMARILLO}Solicitud cancelada por el cliente.{RESET}")
            pausa()

        # ----------------------------------------------------
        # 7. SIMULADOR DE CRÉDITO
        # ----------------------------------------------------
        elif opcion == "7":
            cabecera_menu("Simulador de Cuotas de Crédito", sesion["tipo"], sesion["nombre"])
            print("  Seleccione la línea de crédito a simular:")
            print("  1. Crédito Libre Inversión (Mínimo: $500.000 COP, Plazo: 6 a 60 meses)")
            print("  2. Crédito Hipotecario     (Mínimo: $10.000.000 COP, Plazo: 60 a 360 meses)")
            sel = leer_numero_entero("Seleccione opción [1-2]", minimo=1, maximo=2)

            if sel == 1:
                producto = "Crédito Libre Inversión"
                monto_min = 500000.0
                plazo_min = 6
                plazo_max = 60
            else:
                producto = "Crédito Hipotecario"
                monto_min = 10000000.0  # Mínimo 10 millones
                plazo_min = 60          # Mínimo 60 meses
                plazo_max = 360

            print(f"\n  {GRIS}Condiciones mínimas: Monto mínimo {fmt_dinero(monto_min)} | Plazo mínimo {plazo_min} meses{RESET}\n")
            monto = leer_monto_monetario("Monto a simular", minimo=monto_min)
            plazo = leer_numero_entero(f"Plazo en meses [{plazo_min}-{plazo_max}]", minimo=plazo_min, maximo=plazo_max)

            tasa_mensual = banco_db.matriz_tasas.obtener(producto, plazo)
            if not tasa_mensual or tasa_mensual <= 0:
                tasa_mensual = 0.82 if "Hipotecario" in producto else 1.65

            # Fórmula de cuota fija mensual amortizada
            i = tasa_mensual / 100.0
            n = plazo
            cuota = monto * (i * ((1 + i) ** n)) / (((1 + i) ** n) - 1)
            total_pagar = cuota * n
            total_intereses = total_pagar - monto

            animacion_timer(0.4, "Calculando proyección financiera y tabla de cuota")
            caja_mensaje("info", "SIMULACIÓN DE CRÉDITO", [
                f"Línea de Crédito:   {producto}",
                f"Capital Solicitado: {fmt_dinero(monto)}",
                f"Plazo Acordado:     {plazo} meses",
                f"Tasa de Interés:    {tasa_mensual:.2f}% Mes Vencido",
                f"Cuota Mensual Est.: {BOLD}{fmt_dinero(cuota)}{RESET}",
                f"Total en Intereses: {fmt_dinero(total_intereses)}",
                f"Total a Pagar:      {fmt_dinero(total_pagar)}"
            ])
            pausa()

        # ----------------------------------------------------
        # 8. TURNO DE ATENCIÓN
        # ----------------------------------------------------
        elif opcion == "8":
            cabecera_menu("Solicitud de Turno en Sucursal", sesion["tipo"], sesion["nombre"])
            if banco_db.turnos.contiene(cedula):
                pos = banco_db.turnos.posicion(cedula)
                caja_mensaje("alerta", "TURNO ACTIVO", [
                    f"Ya cuentas con un turno asignado en la fila virtual.",
                    f"Tu posición actual es la número: {BOLD}{pos}{RESET}"
                ])
            else:
                animacion_timer(0.3, "Generando ficha virtual de atención")
                banco_db.turnos.encolar(cedula)
                pos = banco_db.turnos.posicion(cedula)
                caja_mensaje("exito", "TURNO GENERADO", [
                    f"Turno asignado:   {BOLD}T-{cedula[-4:]}{RESET}",
                    f"Cliente:          {cliente['nombre']}",
                    f"Posición en fila: #{pos} en espera",
                    "Un asesor comercial lo llamará en breve."
                ])
            pausa()

        # ----------------------------------------------------
        # 9. CONSULTA DE TURNO
        # ----------------------------------------------------
        elif opcion == "9":
            cabecera_menu("Estado de Turno", sesion["tipo"], sesion["nombre"])
            if banco_db.turnos.contiene(cedula):
                pos = banco_db.turnos.posicion(cedula)
                caja_mensaje("info", "ESTADO DE ATENCIÓN", [
                    f"Turno:            T-{cedula[-4:]}",
                    f"Posición actual:  #{pos} de {banco_db.turnos.tamano()} en fila",
                    f"Tiempo estimado:  ~{pos * 3} minutos",
                    f"Estado:           {badge('pendiente', 'pendiente')}"
                ])
            else:
                print(f"  {AMARILLO}No cuentas con ningún turno activo en la fila virtual.{RESET}\n")
                print(f"  {GRIS}Puedes solicitar uno en la opción 8 del menú.{RESET}\n")
            pausa()

        # ----------------------------------------------------
        # 10. CONSULTA PREVIA DEL CATÁLOGO Y SOLICITUD
        # ----------------------------------------------------
        elif opcion == "10":
            consultar_catalogo_interactivo(banco_db, sesion=sesion, permitir_solicitud=True)

        # ----------------------------------------------------
        # 0. CERRAR SESIÓN
        # ----------------------------------------------------
        elif opcion == "0":
            animacion_timer(0.3, "Cerrando sesión de forma segura")
            nombre = sesion.get("nombre", "")
            banco_db.sesion_actual.update({"usuario": None, "tipo": None, "nombre": None, "cedula": None})
            print(f"  {VERDE}Sesión finalizada. ¡Hasta pronto {nombre}!{RESET}")
            pausa()
            break
        else:
            print(f"\n  {ROJO}Opción no válida. Intente nuevamente.{RESET}")
            pausa()
