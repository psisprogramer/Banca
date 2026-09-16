"""
Módulo de Administración Central (Menú Administrador)
Banco Digital - Sistema Central
"""

from ui import (
    cabecera_menu, caja_mensaje, pausa, animacion_timer, confirmar,
    fmt_dinero, badge, CYAN, CYAN_BRILLANTE, VERDE, VERDE_BRILLANTE, AMARILLO, ROJO, ROJO_BRILLANTE, RESET, BOLD, GRIS, MAGENTA
)
from validaciones import (
    leer_nombre_validado, leer_cedula_validada, leer_usuario_validado,
    leer_contrasena_confirmada, leer_numero_entero, leer_monto_monetario,
    leer_texto_simple
)
from analitica_riesgo import (
    construir_grilla_riesgo, generar_reporte_extendido,
    buscar_vecinos_riesgo, UMBRAL_ALERTA_RIESGO
)


def submenu_catalogo_productos(banco_db):
    """Mantenimiento del catálogo maestro de productos financieros."""
    while True:
        sesion = banco_db.sesion_actual
        cabecera_menu("Catálogo Maestro de Productos", sesion.get("tipo"), sesion.get("nombre"))
        productos = banco_db.catalogo_productos.recorrer_adelante()

        print(f"  {BOLD}{'#':<3} | {'PRODUCTO':<28} | {'CATEGORÍA':<18} | {'ESTADO'}{RESET}")
        print(f"  {'─' * 65}")
        for i, p in enumerate(productos, 1):
            est = badge("activo", "activo") if p.get("activo", True) else badge("inactivo", "inactivo")
            print(f"  {i:<3} | {p['nombre']:<28} | {p.get('categoria', 'General'):<18} | {est}")

        print(f"\n  {CYAN}1.{RESET} Crear nuevo producto financiero")
        print(f"  {CYAN}2.{RESET} Activar / Desactivar producto")
        print(f"  {CYAN}3.{RESET} Modificar producto existente")
        print(f"  {CYAN}4.{RESET} Eliminar producto del catálogo")
        print(f"  {ROJO}0.{RESET} Volver al menú de administrador\n")

        op = input(f"  {BOLD}Selecciona una opción [0-4]:{RESET} ").strip()

        if op == "1":
            nombre = leer_texto_simple("Nombre del nuevo producto")
            categoria = leer_texto_simple("Categoría (Cuentas/Créditos/Tarjetas/Inversión)", obligatorio=False) or "General"
            desc = leer_texto_simple("Descripción del producto")
            beneficios = leer_texto_simple("Principales beneficios")
            requisitos = leer_texto_simple("Requisitos para contratación")
            tasa = leer_texto_simple("Tasa o costo asociado")
            monto_min = leer_monto_monetario("Monto mínimo de apertura/solicitud", minimo=0.0, default=0.0)
            plazo_min = leer_numero_entero("Plazo mínimo en meses (0 si no aplica)", minimo=0, default=0)

            if confirmar(f"¿Confirma incorporar '{nombre}' al catálogo bancario?"):
                animacion_timer(0.4, "Guardando producto en JSON")
                nuevo_prod = {
                    "nombre": nombre,
                    "categoria": categoria,
                    "descripcion": desc,
                    "beneficios": beneficios,
                    "requisitos": requisitos,
                    "tasa_o_costo": tasa,
                    "monto_minimo": monto_min,
                    "plazo_minimo_meses": plazo_min,
                    "activo": True
                }
                banco_db.catalogo_productos.insertar_final(nuevo_prod)
                banco_db.guardar_productos()
                banco_db.auditoria.apilar(f"Producto creado: {nombre}")
                caja_mensaje("exito", "PRODUCTO CREADO", [
                    f"Producto '{nombre}' incorporado exitosamente.",
                    "Guardado en data/productos.json."
                ])
            pausa()

        elif op == "2":
            if not productos:
                print(f"  {AMARILLO}No hay productos registrados.{RESET}\n")
                pausa()
                continue

            idx = leer_numero_entero(f"Número del producto a alternar [1-{len(productos)}]", minimo=1, maximo=len(productos))
            prod = productos[idx - 1]
            prod["activo"] = not prod.get("activo", True)
            estado_txt = "activado" if prod["activo"] else "desactivado"

            animacion_timer(0.3, "Actualizando estado en JSON")
            banco_db.guardar_productos()
            banco_db.auditoria.apilar(f"Producto {estado_txt}: {prod['nombre']}")
            print(f"\n  {VERDE}Producto '{prod['nombre']}' {estado_txt} correctamente.{RESET}")
            pausa()

        elif op == "3":
            if not productos:
                print(f"  {AMARILLO}No hay productos registrados.{RESET}\n")
                pausa()
                continue

            idx = leer_numero_entero(f"Número del producto a editar [1-{len(productos)}]", minimo=1, maximo=len(productos))
            prod = productos[idx - 1]
            print(f"  Editando: {BOLD}{prod['nombre']}{RESET}")
            nuevo_nombre = leer_texto_simple(f"Nuevo nombre (Actual: {prod['nombre']})", obligatorio=False) or prod['nombre']
            nueva_desc = leer_texto_simple("Nueva descripción", obligatorio=False) or prod.get('descripcion', '')
            nueva_tasa = leer_texto_simple("Nueva tasa/costo", obligatorio=False) or prod.get('tasa_o_costo', '')

            if confirmar(f"¿Confirma actualizar los datos de '{prod['nombre']}'?"):
                prod["nombre"] = nuevo_nombre
                prod["descripcion"] = nueva_desc
                prod["tasa_o_costo"] = nueva_tasa
                banco_db.guardar_productos()
                banco_db.auditoria.apilar(f"Producto modificado: {nuevo_nombre}")
                print(f"\n  {VERDE}Producto actualizado con éxito.{RESET}")
            pausa()

        elif op == "4":
            if not productos:
                print(f"  {AMARILLO}No hay productos registrados.{RESET}\n")
                pausa()
                continue

            idx = leer_numero_entero(f"Número del producto a eliminar [1-{len(productos)}]", minimo=1, maximo=len(productos))
            prod = productos[idx - 1]
            if confirmar(f"{ROJO_BRILLANTE}¿Está seguro de ELIMINAR '{prod['nombre']}' del catálogo?{RESET}"):
                animacion_timer(0.4, "Eliminando producto y guardando JSON")
                banco_db.catalogo_productos.eliminar(lambda p: p["nombre"] == prod["nombre"])
                banco_db.guardar_productos()
                banco_db.auditoria.apilar(f"Producto eliminado: {prod['nombre']}")
                print(f"\n  {VERDE}Producto eliminado del catálogo.{RESET}")
            pausa()

        elif op == "0":
            break


def submenu_tasas_interes(banco_db):
    """Gestión y parametrización de la matriz de tasas de interés."""
    cabecera_menu("Matriz de Tasas de Interés", banco_db.sesion_actual.get("tipo"), banco_db.sesion_actual.get("nombre"))
    print("  Líneas de crédito parametrizables:")
    print("  1. Crédito Libre Inversión")
    print("  2. Crédito Hipotecario")
    sel = leer_numero_entero("Seleccione la línea [1-2]", minimo=1, maximo=2)
    producto = "Crédito Libre Inversión" if sel == 1 else "Crédito Hipotecario"

    plazo_min = 60 if "Hipotecario" in producto else 6
    plazo_max = 360 if "Hipotecario" in producto else 60
    plazo = leer_numero_entero(f"Plazo en meses [{plazo_min}-{plazo_max}]", minimo=plazo_min, maximo=plazo_max)

    tasa_actual = banco_db.matriz_tasas.obtener(producto, plazo)
    if tasa_actual:
        print(f"  Tasa registrada actual: {CYAN}{tasa_actual:.2f}% M.V.{RESET}")
    else:
        print(f"  {GRIS}Sin tasa previa configurada para este plazo.{RESET}")

    nueva_tasa = leer_monto_monetario("Nueva tasa mensual (%) (ej: 0.85 o 1.75)", minimo=0.01, maximo=15.0)

    if confirmar(f"¿Confirma asignar tasa de {nueva_tasa:.2f}% M.V. a {producto} a {plazo} meses?"):
        animacion_timer(0.3, "Actualizando matriz de tasas en JSON")
        banco_db.matriz_tasas.asignar(producto, plazo, nueva_tasa)
        banco_db.guardar_tasas()
        banco_db.auditoria.apilar(f"Tasa actualizada: {producto} ({plazo}m -> {nueva_tasa}%)")
        caja_mensaje("exito", "TASA ACTUALIZADA", [
            f"Producto:   {producto}",
            f"Plazo:      {plazo} meses",
            f"Nueva Tasa: {nueva_tasa:.2f}% Mes Vencido"
        ])
    pausa()


def submenu_reportes_gerenciales(banco_db):
    """Reportes ejecutivos y matrices analíticas del banco."""
    while True:
        sesion = banco_db.sesion_actual
        cabecera_menu("Centro de Reportes y Analítica", sesion.get("tipo"), sesion.get("nombre"))
        print(f"  {CYAN}1.{RESET} Matriz de transacciones acumuladas por cliente")
        print(f"  {CYAN}2.{RESET} Matriz de riesgo y perfiles crediticios")
        print(f"  {CYAN}3.{RESET} Indicadores clave de desempeño (KPIs de sucursal)")
        print(f"  {CYAN}4.{RESET} Reporte bidimensional de riesgo y análisis de vecindad")
        print(f"  {ROJO}0.{RESET} Volver al menú de administrador\n")

        op = input(f"  {BOLD}Selecciona una opción [0-4]:{RESET} ").strip()

        if op == "1":
            cabecera_menu("Matriz de Transacciones Acumuladas", sesion.get("tipo"), sesion.get("nombre"))
            animacion_timer(0.3, "Generando matriz analítica")
            if not banco_db.matriz_transacciones.datos:
                print(f"  {AMARILLO}No hay transacciones registradas en la matriz.{RESET}\n")
            else:
                print(f"  {BOLD}{'CÉDULA':<14} | {'TITULAR':<28} | {'VOLUMEN ACUMULADO'}{RESET}")
                print(f"  {'─' * 66}")
                for (ced, concepto), monto in banco_db.matriz_transacciones.datos.items():
                    cli = banco_db.tabla_clientes.buscar(ced)
                    nombre = cli["nombre"] if cli else "Cliente registrado"
                    print(f"  {ced:<14} | {nombre:<28} | {VERDE}{fmt_dinero(monto)}{RESET}")
            pausa()

        elif op == "2":
            cabecera_menu("Matriz de Evaluación de Riesgo", sesion.get("tipo"), sesion.get("nombre"))
            animacion_timer(0.3, "Extrayendo scores de riesgo crediticio")
            if not banco_db.matriz_riesgo.datos:
                print(f"  {AMARILLO}No hay registros en la matriz de riesgo.{RESET}\n")
            else:
                print(f"  {BOLD}{'CÉDULA':<14} | {'PRODUCTO':<26} | {'SCORE':<8} | {'CLASIFICACIÓN'}{RESET}")
                print(f"  {'─' * 68}")
                for (ced, prod), score in banco_db.matriz_riesgo.datos.items():
                    clasif = f"{VERDE}Bajo Riesgo (Prioritario){RESET}" if score <= 25 else (f"{AMARILLO}Riesgo Medio{RESET}" if score <= 50 else f"{ROJO}Alto Riesgo{RESET}")
                    print(f"  {ced:<14} | {prod:<26} | {score:<8} | {clasif}")
            pausa()

        elif op == "3":
            cabecera_menu("Indicadores Clave de Desempeño (KPIs)", sesion.get("tipo"), sesion.get("nombre"))
            total_clientes = banco_db.lista_clientes.tamano
            turnos_espera = banco_db.turnos.tamano()
            creditos_espera = banco_db.solicitudes_credito.tamano()
            total_usuarios = banco_db.tabla_usuarios.cantidad_elementos
            total_txs = len(banco_db.historial_transacciones)

            caja_mensaje("info", "MÉTRICAS DEL SISTEMA BANCARIO", [
                f"Clientes registrados:          {BOLD}{total_clientes}{RESET}",
                f"Usuarios en el sistema:        {BOLD}{total_usuarios}{RESET}",
                f"Transacciones en JSON:         {BOLD}{total_txs}{RESET}",
                f"Turnos en fila virtual:        {BOLD}{turnos_espera}{RESET}",
                f"Solicitudes crédito en cola:   {BOLD}{creditos_espera}{RESET}",
                f"Eventos en auditoría LIFO:     {BOLD}{banco_db.auditoria.tamano()}{RESET}"
            ])
            pausa()

        elif op == "4":
            cabecera_menu("Reporte Bidimensional de Riesgo", sesion.get("tipo"), sesion.get("nombre"))
            animacion_timer(0.3, "Construyendo grilla densa y calculando totales cruzados")

            grilla, clientes_info, productos = construir_grilla_riesgo(banco_db)
            if not grilla or not productos:
                print(f"  {AMARILLO}No hay suficientes datos de riesgo o productos de crédito para construir la grilla.{RESET}\n")
                pausa()
                continue

            extendida = generar_reporte_extendido(grilla)
            n = len(grilla)
            m = len(productos)

            ancho_cli = 28
            ancho_col = 18
            ancho_prom = 16

            encabezado = f"  {BOLD}{'#  CLIENTE / TITULAR':<{ancho_cli}}"
            for j, p in enumerate(productos):
                p_label = f"[{j}] {p[:13]}"
                encabezado += f" | {p_label:<{ancho_col}}"
            encabezado += f" | {'PROM. CLIENTE':<{ancho_prom}}{RESET}"

            longitud_tabla = ancho_cli + (m * (ancho_col + 3)) + (ancho_prom + 3)
            sep = f"  {'─' * longitud_tabla}"
            sep_doble = f"  {'═' * longitud_tabla}"

            print(encabezado)
            print(sep)

            for i in range(n):
                cli = clientes_info[i]
                c_nom = cli["nombre"][:16]
                c_ced = cli["cedula"][-4:]
                c_str = f"[{i}] {c_nom} (..{c_ced})"
                fila_str = f"  {c_str:<{ancho_cli}}"
                for j in range(m):
                    score = extendida[i][j]
                    color_s = ROJO if score >= UMBRAL_ALERTA_RIESGO else (AMARILLO if score > 25 else VERDE)
                    score_str = f"{score:.2f} pts"
                    pad = ancho_col - len(score_str)
                    fila_str += f" | {color_s}{score_str}{RESET}{' ' * max(0, pad)}"

                prom_cli = extendida[i][m]
                color_p = ROJO if prom_cli >= UMBRAL_ALERTA_RIESGO else (AMARILLO if prom_cli > 25 else VERDE)
                prom_str = f"{prom_cli:.2f} pts"
                pad_p = ancho_prom - len(prom_str)
                fila_str += f" | {BOLD}{color_p}{prom_str}{RESET}{' ' * max(0, pad_p)}"
                print(fila_str)

            print(sep)

            fila_prod = f"  {BOLD}{'PROMEDIO PRODUCTO':<{ancho_cli}}"
            for j in range(m):
                prom_p = extendida[n][j]
                color_p = ROJO if prom_p >= UMBRAL_ALERTA_RIESGO else (AMARILLO if prom_p > 25 else VERDE)
                prom_p_str = f"{prom_p:.2f} pts"
                pad_prod = ancho_col - len(prom_p_str)
                fila_prod += f" | {color_p}{prom_p_str}{RESET}{' ' * max(0, pad_prod)}"

            prom_gen = extendida[n][m]
            prom_gen_str = f"{prom_gen:.2f} pts"
            pad_gen = ancho_prom - len(prom_gen_str)
            fila_prod += f" | {CYAN_BRILLANTE}{BOLD}{prom_gen_str}{RESET}{' ' * max(0, pad_gen)}"
            print(fila_prod)
            print(sep_doble)

            print(f"  {GRIS}Criterio: Score >= {UMBRAL_ALERTA_RIESGO} pts marca Alto Riesgo ({ROJO}Rojo{RESET}{GRIS}) | Promedio General Banco: {CYAN_BRILLANTE}{prom_gen:.2f} pts{RESET}\n")

            if confirmar("¿Desea consultar el análisis de vecindad para una celda (Reto 2)?"):
                fila = leer_numero_entero(f"Ingrese índice de fila del cliente [0 a {n - 1}]", minimo=0, maximo=n - 1)
                columna = leer_numero_entero(f"Ingrese índice de columna del producto [0 a {m - 1}]", minimo=0, maximo=m - 1)

                try:
                    res_vecinos = buscar_vecinos_riesgo(grilla, fila, columna, UMBRAL_ALERTA_RIESGO)

                    cli_sel = clientes_info[fila]
                    prod_sel = productos[columna]
                    score_sel = grilla[fila][columna]

                    def fmt_val_vecino(v):
                        if v is None:
                            return f"{GRIS}Borde de matriz (Sin vecino){RESET}"
                        c = ROJO if v >= UMBRAL_ALERTA_RIESGO else (AMARILLO if v > 25 else VERDE)
                        return f"{c}{v:.1f} pts{RESET}"

                    tipo_caja = "alerta" if res_vecinos["en_zona_de_riesgo"] else "info"
                    estado_zona = f"{ROJO_BRILLANTE}¡ZONA DE ALTO RIESGO! (Todos los vecinos >= {UMBRAL_ALERTA_RIESGO}){RESET}" if res_vecinos["en_zona_de_riesgo"] else f"{VERDE_BRILLANTE}ZONA CONTROLADA (Sin concentración de alto riesgo){RESET}"

                    mayor_dir = res_vecinos["vecino_mayor_riesgo"]
                    mayor_score = res_vecinos["score_mayor_riesgo"]
                    mayor_txt = f"{mayor_dir.upper()} ({fmt_val_vecino(mayor_score)})" if mayor_dir else f"{GRIS}No aplica{RESET}"

                    lineas_vecinos = [
                        f"Celda:               Fila [{fila}] | Columna [{columna}]",
                        f"Cliente:             {cli_sel['nombre']} ({cli_sel['cedula']})",
                        f"Producto:            {prod_sel}",
                        f"Score Evaluado:      {BOLD}{score_sel:.1f} pts{RESET}",
                        "─" * 45,
                        f"Vecino Arriba (↑):   {fmt_val_vecino(res_vecinos['vecinos']['arriba'])}",
                        f"Vecino Abajo (↓):    {fmt_val_vecino(res_vecinos['vecinos']['abajo'])}",
                        f"Vecino Izq. (←):     {fmt_val_vecino(res_vecinos['vecinos']['izquierda'])}",
                        f"Vecino Der. (→):     {fmt_val_vecino(res_vecinos['vecinos']['derecha'])}",
                        "─" * 45,
                        f"Diagnóstico:         {estado_zona}",
                        f"Mayor Riesgo Vecino: {mayor_txt}"
                    ]

                    caja_mensaje(tipo_caja, "ANÁLISIS DE VECINDAD - RETO 2", lineas_vecinos, ancho=70)
                except IndexError as e:
                    print(f"  {ROJO}Error al consultar coordenadas: {e}{RESET}")

            pausa()

        elif op == "0":
            break


def submenu_usuarios_internos(banco_db):
    """Gestión de usuarios internos con validaciones estrictas y doble confirmación."""
    while True:
        sesion = banco_db.sesion_actual
        cabecera_menu("Control de Usuarios Internos", sesion.get("tipo"), sesion.get("nombre"))
        print(f"  {CYAN}1.{RESET} Crear nuevo usuario interno {GRIS}(Asesor o Administrador){RESET}")
        print(f"  {CYAN}2.{RESET} Desactivar / Eliminar usuario interno")
        print(f"  {CYAN}3.{RESET} Listar usuarios registrados en el sistema")
        print(f"  {ROJO}0.{RESET} Volver al menú de administrador\n")

        op = input(f"  {BOLD}Selecciona una opción [0-3]:{RESET} ").strip()

        if op == "1":
            cabecera_menu("Creación de Funcionario Interno", sesion.get("tipo"), sesion.get("nombre"))

            # Validaciones estrictas:
            # 1. Cédula
            cedula = leer_cedula_validada("Cédula de ciudadanía del funcionario (9 a 10 dígitos)")

            # 2. Nombre y apellido en mayúsculas
            nombre = leer_nombre_validado("Nombre Completo (Nombre y Apellido)")

            # 3. Usuario >= 8 caracteres alfanuméricos
            usuario = leer_usuario_validado("Usuario de acceso (mínimo 8 caracteres alfanuméricos)", tabla_usuarios=banco_db.tabla_usuarios)

            # Rol
            print("  Seleccione el rol del funcionario:")
            print("  1. Asesor comercial de sucursal / empleado")
            print("  2. Administrador general del sistema")
            sel_rol = leer_numero_entero("Opción [1-2]", minimo=1, maximo=2)
            rol = "asesor" if sel_rol == 1 else "administrador"

            # 4. Doble confirmación de contraseña
            pin = leer_contrasena_confirmada(f"Asigne la contraseña para el usuario '{usuario}'")

            if confirmar(f"¿Confirma crear al funcionario '{nombre}' con rol {rol.upper()}?"):
                animacion_timer(0.4, "Creando credenciales en JSON")
                datos_nuevo_usuario = {
                    "usuario": usuario,
                    "tipo": rol,
                    "nombre": nombre,
                    "cedula": cedula,
                    "pin": pin
                }
                banco_db.tabla_usuarios.insertar(usuario, datos_nuevo_usuario)
                banco_db.guardar_usuarios()
                banco_db.auditoria.apilar(f"Usuario interno creado: {usuario} ({rol})")

                caja_mensaje("exito", "USUARIO INTERNO CREADO", [
                    f"Usuario:  {usuario}",
                    f"Nombre:   {nombre}",
                    f"Cédula:   {cedula}",
                    f"Rol:      {rol.capitalize()}",
                    "Guardado en data/usuarios.json con acceso inmediato."
                ])
            pausa()

        elif op == "2":
            usuario = leer_texto_simple("Usuario a retirar").lower()
            if usuario == sesion.get("usuario"):
                print(f"\n  {ROJO}No puedes desactivar tu propio usuario en sesión activa.{RESET}")
                pausa()
                continue

            datos = banco_db.tabla_usuarios.buscar(usuario)
            if not datos:
                print(f"\n  {ROJO}El usuario '{usuario}' no existe en el sistema.{RESET}")
                pausa()
                continue

            if confirmar(f"¿Está seguro de ELIMINAR permanentemente las credenciales de '{usuario}'?"):
                animacion_timer(0.4, "Revocando accesos en JSON")
                banco_db.tabla_usuarios.eliminar(usuario)
                banco_db.guardar_usuarios()
                banco_db.auditoria.apilar(f"Usuario interno eliminado: {usuario}")
                print(f"\n  {VERDE}Usuario '{usuario}' retirado con éxito.{RESET}")
            pausa()

        elif op == "3":
            cabecera_menu("Usuarios Registrados en el Sistema", sesion.get("tipo"), sesion.get("nombre"))
            usuarios = banco_db.tabla_usuarios.listar_valores()
            print(f"  {BOLD}{'USUARIO':<14} | {'NOMBRE':<30} | {'CÉDULA':<12} | {'ROL'}{RESET}")
            print(f"  {'─' * 70}")
            for u in usuarios:
                tipo = u.get("tipo", "cliente")
                col_r = CYAN if tipo == "cliente" else (AMARILLO if tipo in ("asesor", "empleado") else MAGENTA)
                rol_txt = "Asesor" if tipo in ("asesor", "empleado") else tipo.capitalize()
                ced = u.get("cedula", "N/A")
                print(f"  {u['usuario']:<14} | {u['nombre']:<30} | {ced:<12} | {col_r}{rol_txt}{RESET}")
            print(f"\n  {GRIS}Total de usuarios activos: {len(usuarios)}{RESET}")
            pausa()

        elif op == "0":
            break


def menu_administrador(banco_db):
    """Panel de control total para administradores del banco."""
    while True:
        sesion = banco_db.sesion_actual
        cabecera_menu("Panel de Administración Central", sesion.get("tipo"), sesion.get("nombre"))
        print(f"  {CYAN}1.{RESET} Gestión del catálogo maestro de productos")
        print(f"  {CYAN}2.{RESET} Gestión y parametrización de matriz de tasas")
        print(f"  {CYAN}3.{RESET} Reportes ejecutivos y matrices analíticas")
        print(f"  {CYAN}4.{RESET} Consulta de auditoría general del sistema")
        print(f"  {CYAN}5.{RESET} Gestión de usuarios internos {GRIS}(Asesores y Administradores){RESET}")
        print(f"  {ROJO}0.{RESET} Cerrar sesión\n")

        opcion = input(f"  {BOLD}Selecciona una opción [0-5]:{RESET} ").strip()

        if opcion == "1":
            submenu_catalogo_productos(banco_db)
        elif opcion == "2":
            submenu_tasas_interes(banco_db)
        elif opcion == "3":
            submenu_reportes_gerenciales(banco_db)
        elif opcion == "4":
            cabecera_menu("Auditoría Completa del Sistema", sesion.get("tipo"), sesion.get("nombre"))
            historial = banco_db.auditoria.ver_historial()
            if not historial:
                print(f"  {AMARILLO}No hay registros de auditoría almacenados.{RESET}\n")
            else:
                print(f"  {BOLD}{'HORA':<10} | {'ACCIÓN REGISTRADA':<44} | {'TIPO'}{RESET}")
                print(f"  {'─' * 70}")
                for h in historial:
                    tipo_txt = f"{VERDE}Reversible{RESET}" if h.funcion_deshacer else f"{GRIS}Informativo{RESET}"
                    print(f"  {h.fecha:<10} | {h.descripcion:<44} | {tipo_txt}")
                print(f"\n  {GRIS}Total de eventos en auditoría: {len(historial)}{RESET}")
            pausa()
        elif opcion == "5":
            submenu_usuarios_internos(banco_db)
        elif opcion == "0":
            animacion_timer(0.3, "Cerrando sesión de administrador")
            banco_db.sesion_actual.update({"usuario": None, "tipo": None, "nombre": None, "cedula": None})
            break
        else:
            print(f"\n  {ROJO}Opción no válida.{RESET}")
            pausa()
