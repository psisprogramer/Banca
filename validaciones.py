"""
Módulo de Validaciones y Sanitización de Entradas
Banco Digital - Sistema Central
"""

import re
from ui import CYAN, ROJO, RESET, BOLD, fmt_dinero


def normalizar_y_validar_nombre(texto):
    """
    Valida y organiza el nombre completo:
    - Convierte todo a MAYÚSCULAS sin importar si ingresó minúsculas o mayúsculas.
    - Admite y limpia espacios consecutivos.
    - Valida que contenga al menos nombre y apellido (mínimo 2 palabras).
    - Solo permite letras del alfabeto español (incluyendo tildes y ñ) y espacios.
    Retorna (es_valido, nombre_procesado_o_error).
    """
    if not texto:
        return False, "El nombre no puede estar vacío."

    # Normaliza espacios y convierte todo a mayúsculas
    nombre_limpio = " ".join(texto.strip().split()).upper()

    # Verifica caracteres válidos (solo letras castellanas y espacios)
    patron = r"^[A-ZÁÉÍÓÚÑÜ\s]+$"
    if not re.match(patron, nombre_limpio):
        return False, "El nombre solo puede contener letras y espacios (sin números ni caracteres especiales)."

    partes = nombre_limpio.split()
    if len(partes) < 2:
        return False, "Debe ingresar nombre y apellido completos (mínimo 2 palabras)."

    # Verifica que cada parte tenga al menos 2 letras
    for parte in partes:
        if len(parte) < 2:
            return False, f"La palabra '{parte}' es demasiado corta para ser un nombre o apellido válido."

    return True, nombre_limpio


def leer_nombre_validado(prompt="Nombre Completo (Nombre y Apellido)"):
    """Lee el nombre y fuerza el cumplimiento de nombre y apellido en mayúsculas."""
    while True:
        entrada = input(f"  {CYAN}▸{RESET} {prompt}: ").strip()
        valido, resultado = normalizar_y_validar_nombre(entrada)
        if valido:
            return resultado
        print(f"    {ROJO}{resultado}{RESET}")


def validar_cedula(texto):
    """
    Valida que la cédula sea un número entre 9 y 10 dígitos.
    Retorna (es_valido, cedula_o_error).
    """
    cedula_limpia = texto.strip().replace(".", "").replace(" ", "")
    if not re.match(r"^\d{9,10}$", cedula_limpia):
        return False, "La cédula debe ser estrictamente numérica y contener entre 9 y 10 dígitos."
    return True, cedula_limpia


def validar_cedula_global(cedula, banco_db=None, excluir_cedula=None):
    """
    Valida formato numérico de cédula (9-10 dígitos) y comprueba que no
    se encuentre duplicada en ningún lugar del sistema (clientes o usuarios internos).
    Retorna (es_valido, cedula_limpia_o_error).
    """
    valido, res = validar_cedula(cedula)
    if not valido:
        return False, res

    cedula_limpia = res
    if banco_db is not None:
        if excluir_cedula and str(excluir_cedula).strip() == cedula_limpia:
            return True, cedula_limpia

        # 1. Comprobar en tabla de clientes
        cli = banco_db.tabla_clientes.buscar(cedula_limpia)
        if cli:
            return False, f"La cédula {cedula_limpia} ya se encuentra registrada para el cliente '{cli.get('nombre', 'Sin Nombre')}'."

        # 2. Comprobar en tabla de usuarios (clientes, empleados, asesores, administradores)
        for u in banco_db.tabla_usuarios.listar_valores():
            if str(u.get("cedula", "")).strip() == cedula_limpia:
                rol = u.get("tipo", "usuario").capitalize()
                return False, f"La cédula {cedula_limpia} ya está registrada en el sistema (asociada al {rol} '{u.get('nombre', u.get('usuario'))}')."

    return True, cedula_limpia


def leer_cedula_validada(prompt="Número de Cédula (9 a 10 dígitos)", tabla_clientes=None, banco_db=None, excluir_cedula=None):
    """Lee la cédula asegurando 9-10 dígitos y que no esté duplicada globalmente."""
    while True:
        entrada = input(f"  {CYAN}▸{RESET} {prompt}: ").strip()
        if banco_db is not None:
            valido, resultado = validar_cedula_global(entrada, banco_db=banco_db, excluir_cedula=excluir_cedula)
        else:
            valido, resultado = validar_cedula(entrada)
            if valido and tabla_clientes and tabla_clientes.buscar(resultado):
                valido = False
                resultado = f"La cédula {resultado} ya se encuentra registrada en el sistema."

        if not valido:
            print(f"    {ROJO}{resultado}{RESET}")
            continue

        return resultado


def validar_usuario(texto):
    """
    Valida que el usuario tenga mínimo 8 caracteres alfanuméricos sin caracteres especiales.
    Retorna (es_valido, usuario_o_error).
    """
    usuario_limpio = texto.strip().lower()
    if len(usuario_limpio) < 8:
        return False, "El nombre de usuario debe tener un mínimo de 8 caracteres alfanuméricos."

    if not re.match(r"^[a-z0-9]{8,}$", usuario_limpio):
        return False, "El usuario solo puede contener letras y números (sin espacios ni caracteres especiales)."

    return True, usuario_limpio


def leer_usuario_validado(prompt="Nombre de usuario (mínimo 8 caracteres alfanuméricos)", tabla_usuarios=None):
    """Lee el usuario asegurando longitud y caracteres permitidos, y verifica duplicados."""
    while True:
        entrada = input(f"  {CYAN}▸{RESET} {prompt}: ").strip()
        valido, resultado = validar_usuario(entrada)
        if not valido:
            print(f"    {ROJO}{resultado}{RESET}")
            continue

        if tabla_usuarios and tabla_usuarios.buscar(resultado):
            print(f"    {ROJO}El usuario '{resultado}' ya está en uso. Elija otro alias.{RESET}")
            continue

        return resultado


def leer_contrasena_confirmada(prompt="Asigne su contraseña / PIN de acceso"):
    """
    Solicita la contraseña y obliga a confirmarla una segunda vez.
    Garantiza que ambas coincidan.
    """
    while True:
        pwd1 = input(f"  {CYAN}▸{RESET} {prompt}: ").strip()
        if len(pwd1) < 4:
            print(f"    {ROJO}La contraseña / PIN debe tener al menos 4 caracteres.{RESET}")
            continue

        pwd2 = input(f"  {CYAN}▸{RESET} Confirme nuevamente su contraseña / PIN: ").strip()
        if pwd1 != pwd2:
            print(f"    {ROJO}Las contraseñas no coinciden. Por seguridad, intente nuevamente.{RESET}\n")
            continue

        return pwd1


def parsear_monto(texto):
    """
    Parsea montos monetarios en formatos diversos, tolerando puntos y comas de miles:
    Ejemplos: '10.000.000', '$ 50,000,000.00', '100000000', '25.500'
    Retorna float con el valor procesado o lanza ValueError.
    """
    if texto is None:
        raise ValueError("Monto vacío")

    s = str(texto).replace("$", "").replace("COP", "").replace("cop", "").replace(" ", "").strip()
    if not s:
        raise ValueError("Monto vacío")

    # Si contiene tanto punto como coma:
    if "." in s and "," in s:
        if s.rfind(",") > s.rfind("."):
            # Formato latino/europeo: 10.000.000,50
            s = s.replace(".", "").replace(",", ".")
        else:
            # Formato anglosajón: 10,000,000.50
            s = s.replace(",", "")
    elif "." in s:
        partes = s.split(".")
        if len(partes) > 2:
            # Varios puntos: separadores de miles (ej: 10.000.000)
            s = s.replace(".", "")
        elif len(partes) == 2:
            # Un solo punto: si después del punto hay 3 dígitos y el entero es > 0, es miles (ej: 50.000)
            if len(partes[1]) == 3 and partes[0].isdigit() and int(partes[0]) > 0 and len(partes[0]) <= 3:
                s = s.replace(".", "")
            # En caso contrario, se asume decimal (ej: 50.50 o 1000.00)
    elif "," in s:
        partes = s.split(",")
        if len(partes) > 2:
            s = s.replace(",", "")
        elif len(partes) == 2:
            if len(partes[1]) == 3 and partes[0].isdigit() and int(partes[0]) > 0 and len(partes[0]) <= 3:
                s = s.replace(",", "")
            else:
                s = s.replace(",", ".")

    val = float(s)
    if val < 0:
        raise ValueError("El monto no puede ser negativo")
    return val


def leer_monto_monetario(prompt="Monto", minimo=0.0, maximo=1000000000000.0, default=None):
    """
    Lectura blindada de montos monetarios de gran escala sin fallos por variables o formato.
    Soporta valores desde centavos hasta billones de pesos.
    """
    while True:
        entrada = input(f"  {CYAN}▸{RESET} {prompt}: ").strip()
        if not entrada and default is not None:
            return default
        try:
            monto = parsear_monto(entrada)
            if minimo is not None and monto < minimo:
                print(f"    {ROJO}El monto mínimo permitido es {fmt_dinero(minimo)}.{RESET}")
                continue
            if maximo is not None and monto > maximo:
                print(f"    {ROJO}El monto máximo permitido es {fmt_dinero(maximo)}.{RESET}")
                continue
            return monto
        except (ValueError, TypeError):
            print(f"    {ROJO}Monto no válido. Ingrese un valor numérico (ej: 5000000 o 5.000.000).{RESET}")


def leer_numero_entero(prompt, minimo=None, maximo=None, default=None):
    """Lectura segura de números enteros."""
    while True:
        entrada = input(f"  {CYAN}▸{RESET} {prompt}: ").strip()
        if not entrada and default is not None:
            return default
        try:
            val = int(entrada.replace(".", "").replace(",", "").replace(" ", ""))
            if minimo is not None and val < minimo:
                print(f"    {ROJO}El valor mínimo permitido es {minimo}.{RESET}")
                continue
            if maximo is not None and val > maximo:
                print(f"    {ROJO}El valor máximo permitido es {maximo}.{RESET}")
                continue
            return val
        except ValueError:
            print(f"    {ROJO}Entrada no válida. Ingrese un número entero.{RESET}")


def leer_texto_simple(prompt, obligatorio=True):
    """Lectura de texto básica."""
    while True:
        valor = input(f"  {CYAN}▸{RESET} {prompt}: ").strip()
        if not valor and obligatorio:
            print(f"    {ROJO}Este campo no puede estar vacío.{RESET}")
            continue
        return valor


def validar_tasa_interes(texto, categoria="General"):
    """
    Valida y normaliza de forma estricta el ingreso de tasas de interés o costos:
    - Para Créditos e Inversión: exige tasa porcentual numérica entre 0.01% y 45.0% M.V. o E.A.
    - Para Cuentas y Servicios: admite porcentajes o tarifas estructuradas (ej: $0 COP).
    Retorna (es_valido, tasa_formateada_o_error, valor_float_si_aplica).
    """
    if not texto or not str(texto).strip():
        return False, "La tasa o costo asociado no puede estar vacía.", None

    s = str(texto).strip()

    # Si es tarifa gratuita o fija en pesos
    if any(k in s.lower() for k in ["$0", "gratis", "sin costo", "0 cop", "tarifa cero"]):
        return True, "$0 COP de tarifa", 0.0

    # Limpieza de sufijos porcentuales para parseo numérico
    s_num = s.replace("%", "").replace("M.V.", "").replace("E.A.", "").replace("m.v.", "").replace("e.a.", "")
    s_num = s_num.replace("mensual", "").replace("anual", "").replace("nominal", "").strip()
    s_num = s_num.replace(",", ".")

    try:
        val = float(s_num)
    except ValueError:
        cat_lower = categoria.lower()
        if any(c in cat_lower for c in ["crédito", "credito", "inversión", "inversion"]):
            return False, "Para créditos e inversión debe ingresar un porcentaje numérico válido (ej: 1.75 o 1.75% M.V.).", None
        else:
            return True, s, None

    if val < 0.0:
        return False, "La tasa de interés no puede ser un valor negativo.", None

    cat_lower = categoria.lower()
    if any(c in cat_lower for c in ["crédito", "credito"]):
        if val > 45.0:
            return False, "La tasa supera el límite legal de usura bancaria (máximo 45% E.A. o 3.50% M.V.).", None
        if "e.a." in s.lower() or "anual" in s.lower() or val > 6.0:
            tasa_fmt = f"{val:.2f}% E.A."
        else:
            tasa_fmt = f"{val:.2f}% M.V."
        return True, tasa_fmt, val

    elif any(c in cat_lower for c in ["inversión", "inversion"]):
        if val > 35.0:
            return False, "La tasa de rendimiento de inversión no puede exceder el 35% E.A.", None
        tasa_fmt = f"{val:.2f}% E.A." if "m.v." not in s.lower() else f"{val:.2f}% M.V."
        return True, tasa_fmt, val

    elif "cuenta" in cat_lower:
        tasa_fmt = f"{val:.2f}% E.A. sobre saldo diario"
        return True, tasa_fmt, val

    else:
        tasa_fmt = f"{val:.2f}% M.V." if "%" in s else (f"{val:.2f}%" if val > 0 else s)
        return True, tasa_fmt, val


def leer_tasa_interes(prompt="Tasa de interés / costo", categoria="General"):
    """Lectura validada estrictamente de la tasa de interés."""
    while True:
        entrada = input(f"  {CYAN}▸{RESET} {prompt}: ").strip()
        valido, res, num = validar_tasa_interes(entrada, categoria)
        if not valido:
            print(f"    {ROJO}{res}{RESET}")
            continue
        return res, num
