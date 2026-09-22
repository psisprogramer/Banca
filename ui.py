"""
Módulo de Interfaz de Usuario (UI) y Formato Visual
Banco Digital - Sistema Central
"""

import os
import sys
import time
import datetime
import re
import textwrap

# Habilita secuencias de escape ANSI y codificación UTF-8 en Windows
if os.name == "nt":
    os.system("")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Códigos de formato ANSI
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

# Paleta de colores
NEGRO = "\033[30m"
ROJO = "\033[31m"
VERDE = "\033[32m"
AMARILLO = "\033[33m"
AZUL = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
BLANCO = "\033[37m"
GRIS = "\033[90m"
ROJO_BRILLANTE = "\033[91m"
VERDE_BRILLANTE = "\033[92m"
AMARILLO_BRILLANTE = "\033[93m"
AZUL_BRILLANTE = "\033[94m"
MAGENTA_BRILLANTE = "\033[95m"
CYAN_BRILLANTE = "\033[96m"
BLANCO_BRILLANTE = "\033[97m"

# Fondos
BG_AZUL = "\033[44m"
BG_VERDE = "\033[42m"
BG_ROJO = "\033[41m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_GRIS = "\033[100m"


def color(texto, codigo_color):
    """Devuelve el texto coloreado asegurando el reset final."""
    return f"{codigo_color}{texto}{RESET}"


def fmt_dinero(monto):
    """Formatea valores monetarios con estilo bancario profesional sin perder precisión."""
    try:
        if monto is None:
            monto = 0.0
        val = float(monto)
        # Formato estándar con comas de miles y 2 decimales
        return f"${val:,.2f} COP"
    except (ValueError, TypeError):
        return f"${monto} COP"


def badge(texto, estado="info"):
    """Genera etiquetas visuales (badges) estilizadas según el estado."""
    estados = {
        "activo": f"{VERDE_BRILLANTE}[● ACTIVO]{RESET}",
        "inactivo": f"{GRIS}[○ INACTIVO]{RESET}",
        "aprobado": f"{VERDE_BRILLANTE}[✓ APROBADO]{RESET}",
        "rechazado": f"{ROJO_BRILLANTE}[✗ RECHAZADO]{RESET}",
        "pendiente": f"{AMARILLO_BRILLANTE}[⏳ PENDIENTE]{RESET}",
        "exito": f"{VERDE_BRILLANTE}[✓ EXITOSO]{RESET}",
        "error": f"{ROJO_BRILLANTE}[✗ ERROR]{RESET}",
        "alerta": f"{AMARILLO_BRILLANTE}[! ALERTA]{RESET}",
        "info": f"{CYAN}[ℹ INFO]{RESET}"
    }
    return estados.get(str(estado).lower(), f"[{texto}]")


def limpiar_pantalla():
    """Limpia la terminal de forma compatible con Windows y Unix."""
    os.system("cls" if os.name == "nt" else "clear")


def pausa(mensaje="Presione [Enter] para continuar..."):
    """Pausa interactiva con estilo limpio."""
    print(f"\n{GRIS}{mensaje}{RESET}", end="")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass


def animacion_timer(segundos=0.4, mensaje="Procesando"):
    """Muestra un spinner interactivo mientras simula procesamiento."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    fin = time.time() + segundos
    idx = 0
    while time.time() < fin:
        sys.stdout.write(f"\r  {CYAN}{frames[idx % len(frames)]}{RESET} {mensaje}...")
        sys.stdout.flush()
        time.sleep(0.06)
        idx += 1
    sys.stdout.write("\r" + " " * (len(mensaje) + 15) + "\r")
    sys.stdout.flush()


def banner_principal():
    """Banner de bienvenida con arte ASCII y estética financiera."""
    print(f"{CYAN}{BOLD}")
    print("  ╔═══════════════════════════════════════════════════════════════════╗") 
    print("  ║                     SISTEMA BANCARIO DIGITAL                      ║")
    print("  ║            Arquitectura Modular • Persistencia en JSON            ║")
    print("  ╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{RESET}")


def banner_credenciales_prueba():
    """Muestra recuadro informativo con credenciales de prueba activas."""
    print(f"  {MAGENTA}{BOLD}┌────────────────────── CREDENCIALES DE PRUEBA ─────────────────────┐{RESET}")
    print(f"  {MAGENTA}│  {BOLD}Rol             Usuario      Contraseña / PIN    Cédula{RESET}{MAGENTA}          │{RESET}")
    print(f"  {MAGENTA}│  Administrador   admin        admin1234 (o 1234)  1000000001      │{RESET}")
    print(f"  {MAGENTA}│  Asesor          asesor       asesor1234 (o 1234) 1000000002      │{RESET}")
    print(f"  {MAGENTA}│  Cliente         valen        1234                1000000003      │{RESET}")
    print(f"  {MAGENTA}{BOLD}└───────────────────────────────────────────────────────────────────┘{RESET}\n")


def cabecera_menu(titulo, rol=None, usuario=None):
    """Genera cabeceras estilizadas según el rol en sesión."""
    limpiar_pantalla()
    color_rol = CYAN_BRILLANTE
    icono_rol = "👤"
    if rol in ("empleado", "asesor"):
        color_rol = AMARILLO_BRILLANTE
        icono_rol = "👔"
    elif rol == "administrador":
        color_rol = MAGENTA_BRILLANTE
        icono_rol = "🛡️ "

    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"{color_rol}{BOLD}┌{'─' * 67}┐{RESET}")
    print(f"{color_rol}{BOLD}│  {titulo.upper().center(63)}  │{RESET}")
    if usuario and rol:
        rol_display = "Asesor" if rol in ("empleado", "asesor") else rol.capitalize()
        detalles = f"{icono_rol} {usuario} | Rol: {rol_display} | {ahora}"
        print(f"{color_rol}│  {detalles.center(63)}  │{RESET}")
    print(f"{color_rol}{BOLD}└{'─' * 67}┘{RESET}\n")


def quitar_ansi(texto):
    """Elimina secuencias de escape ANSI para cálculo visual exacto de longitudes."""
    return re.sub(r'\033\[[0-9;]*[a-zA-Z]', '', str(texto))


def caja_mensaje(tipo, titulo, lineas, ancho=70):
    """Imprime recuadros informativos elegantes con bordes redondeados y ajuste automático de texto."""
    colores = {
        "exito": VERDE_BRILLANTE,
        "error": ROJO_BRILLANTE,
        "alerta": AMARILLO_BRILLANTE,
        "info": CYAN_BRILLANTE,
        "recibo": BLANCO_BRILLANTE
    }
    iconos = {
        "exito": "✓",
        "error": "✗",
        "alerta": "!",
        "info": "ℹ",
        "recibo": "★"
    }
    c = colores.get(tipo, BLANCO)
    icono = iconos.get(tipo, "•")

    if isinstance(lineas, str):
        lineas = [lineas]

    # Determinación dinámica del ancho necesario respetando límites
    ancho_titulo = len(quitar_ansi(titulo)) + 8
    max_contenido = max((len(quitar_ansi(l)) for l in lineas), default=0) + 6
    ancho_calculado = max(ancho, ancho_titulo, min(max_contenido, 76))
    ancho_final = min(ancho_calculado, 78)
    ancho_interno = ancho_final - 2
    max_line_w = ancho_interno - 4

    # Envolver texto para que ninguna línea exceda el ancho interior
    lineas_procesadas = []
    for l in lineas:
        l_str = str(l)
        l_plana = quitar_ansi(l_str)
        if len(l_plana) > max_line_w:
            sublineas = textwrap.wrap(l_str, width=max_line_w, break_long_words=True)
            lineas_procesadas.extend(sublineas if sublineas else [""])
        else:
            lineas_procesadas.append(l_str)

    print(f"\n  {c}╭{'─' * ancho_interno}╮{RESET}")
    titulo_formateado = f" [{icono}] {titulo} "
    print(f"  {c}│{BOLD}{titulo_formateado.center(ancho_interno)}{RESET}{c}│{RESET}")
    print(f"  {c}├{'─' * ancho_interno}┤{RESET}")
    for l in lineas_procesadas:
        l_plana = quitar_ansi(l)
        if len(l_plana) > max_line_w:
            l = l[:max_line_w - 3] + "..."
            l_plana = quitar_ansi(l)
        padding = max_line_w - len(l_plana)
        print(f"  {c}│{RESET}  {l}{' ' * padding}  {c}│{RESET}")
    print(f"  {c}╰{'─' * ancho_interno}╯{RESET}\n")


def leer_pin_enmascarado(prompt="Contraseña / PIN de seguridad"):
    """
    Lee una contraseña o PIN enmascarando los caracteres con puntos ('•').
    Soporta Backspace para borrar y Ctrl+C para interrumpir.
    En entornos interactivos de Windows usa msvcrt; de lo contrario utiliza getpass/input.
    """
    prompt_str = f"  {CYAN}▸{RESET} {prompt}: "
    if sys.platform == "win32" and sys.stdin.isatty():
        import msvcrt
        print(prompt_str, end="", flush=True)
        caracteres = []
        while True:
            try:
                ch = msvcrt.getch()
            except (KeyboardInterrupt, EOFError):
                print()
                raise KeyboardInterrupt

            if ch in (b"\r", b"\n"):
                print()
                break
            elif ch == b"\x08":  # Backspace
                if caracteres:
                    caracteres.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif ch == b"\x03":  # Ctrl+C
                print()
                raise KeyboardInterrupt
            elif ch in (b"\x00", b"\xe0"):  # Teclas especiales de función / flechas
                msvcrt.getch()
            else:
                try:
                    char_decoded = ch.decode("utf-8")
                    caracteres.append(char_decoded)
                    sys.stdout.write("•")
                    sys.stdout.flush()
                except UnicodeDecodeError:
                    pass
        return "".join(caracteres).strip()
    else:
        import getpass
        try:
            return getpass.getpass(prompt_str).strip()
        except Exception:
            return input(prompt_str).strip()


def confirmar(mensaje):
    """Solicita confirmación afirmativa o negativa al usuario."""
    while True:
        resp = input(f"  {AMARILLO}?{RESET} {mensaje} [s/n]: ").strip().lower()
        if resp in ("s", "si", "sí", "y", "yes"):
            return True
        elif resp in ("n", "no"):
            return False
        print(f"    {ROJO}Por favor responde 's' para sí o 'n' para no.{RESET}")
