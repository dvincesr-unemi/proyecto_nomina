from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import EmpleadoController, DepartamentoController, RolPagoController

# Se crea UN solo controlador de cada tipo.
# A roles de pago se le pasan los MISMOS empleados y departamentos.
empleados = EmpleadoController()
departamentos = DepartamentoController()
roles_pago = RolPagoController(empleados, departamentos)


# AYUDAS DE PANTALLA

def pausa() -> None:
    """
    Detiene la ejecucion hasta que el usuario presione Enter.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    input("\nPresione Enter para continuar...")


def pedir_entero(etiqueta: str) -> int:
    """
    Pide un numero entero por consola y maneja el error si se ingresa texto.
    
    Args:
        etiqueta (str): El texto que se mostrara en el input.
        
    Returns:
        int o None: El numero entero ingresado, o None si el usuario escribio otra cosa.
    """
    try:
        return int(input(etiqueta))
    except ValueError:
        return None


def mostrar_resultado(exito: bool, mensaje: str) -> None:
    """
    Imprime un mensaje en verde o rojo dependiendo de si la operacion fue exitosa.
    
    Args:
        exito (bool): Indica si la accion se completo correctamente.
        mensaje (str): El texto a mostrar al usuario.
        
    Returns:
        None
    """
    # Los controladores devuelven la TUPLA (exito, mensaje)
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos: list, vacio: str = "No hay registros todavia.") -> None:
    """
    Recorre e imprime una lista de objetos. Sirve para cualquier modelo.
    
    Args:
        objetos (list): Lista de instancias a mostrar.
        vacio (str, opcional): Mensaje a mostrar si la lista esta vacia.
        
    Returns:
        None
    """
    # Cada modelo sabe mostrarse gracias a su metodo __str__
    if not objetos:
        imprimir_info(vacio)
        return
    for objeto in objetos:
        print(f"  {objeto}")
    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto: object) -> None:
    """
    Imprime todos los campos de un objeto basandose en su representacion de diccionario.
    
    Args:
        objeto (object): Instancia del modelo a inspeccionar.
        
    Returns:
        None
    """
    # Recorre el DICCIONARIO del objeto: clave y valor a la vez
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {str(clave).replace('_', ' ').capitalize():<16}: {valor}")


# MENU DE EMPLEADOS

def crear_empleado() -> None:
    """
    Solicita los datos por consola para registrar un nuevo empleado.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("REGISTRAR EMPLEADO")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "codigo_emp": input("Codigo Institucional: "),
        "cargo": input("Cargo: "),
        "salario_base": input("Salario Base Mensual: "),
    }
    mostrar_resultado(*empleados.crear(datos))
    pausa()


def listar_empleados() -> None:
    """
    Muestra en pantalla todos los empleados registrados.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("EMPLEADOS REGISTRADOS")
    mostrar_lista(empleados.leer(), "Todavia no hay empleados.")
    pausa()


def buscar_empleado() -> None:
    """
    Busca empleados por coincidencia de texto en sus atributos principales.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("BUSCAR EMPLEADO")
    termino = input("Nombre, email, codigo o cargo: ")
    encontrados = empleados.buscar(termino)
    mostrar_lista(encontrados, f"Ningun empleado coincide con '{termino}'.")
    pausa()


def ver_empleado() -> None:
    """
    Muestra los detalles completos de un empleado buscando por su ID.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("VER EMPLEADO POR ID")
    empleado = empleados.obtener(pedir_entero("Id: "))
    if empleado is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(empleado)
    pausa()


def actualizar_empleado() -> None:
    """
    Permite editar los campos de un empleado. Los campos en blanco no se modifican.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("ACTUALIZAR EMPLEADO")
    id_empleado = pedir_entero("Id: ")
    empleado = empleados.obtener(id_empleado)
    if empleado is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {empleado.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "apellido", "email", "codigo_emp", "cargo", "salario_base"):
        actual = getattr(empleado, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*empleados.actualizar(id_empleado, cambios))
    pausa()


def eliminar_empleado() -> None:
    """
    Elimina un empleado del sistema previa confirmacion.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("ELIMINAR EMPLEADO")
    id_empleado = pedir_entero("Id: ")
    empleado = empleados.obtener(id_empleado)
    if empleado is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminara: {empleado.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*empleados.eliminar(id_empleado))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


# MENU DE DEPARTAMENTOS

def crear_departamento() -> None:
    """
    Solicita los datos por consola para registrar un nuevo departamento.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("CREAR DEPARTAMENTO")
    datos = {
        "nombre": input("Nombre: "),
        "codigo": input("Codigo: "),
        "presupuesto": input("Presupuesto asignado: "),
        "plazas_disponibles": input("Plazas disponibles: "),
    }
    mostrar_resultado(*departamentos.crear(datos))
    pausa()


def listar_departamentos() -> None:
    """
    Muestra en pantalla todos los departamentos registrados.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("DEPARTAMENTOS")
    mostrar_lista(departamentos.leer(), "Todavia no hay departamentos.")
    pausa()


def buscar_departamento() -> None:
    """
    Busca un departamento por nombre o codigo.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("BUSCAR DEPARTAMENTO")
    termino = input("Nombre o codigo: ")
    mostrar_lista(departamentos.buscar(termino), "Sin coincidencias.")
    pausa()


def ver_departamento() -> None:
    """
    Muestra los detalles completos de un departamento buscando por su ID.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("VER DEPARTAMENTO POR ID")
    depto = departamentos.obtener(pedir_entero("Id: "))
    if depto is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(depto)
    pausa()


def actualizar_departamento() -> None:
    """
    Permite editar los campos de un departamento.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("ACTUALIZAR DEPARTAMENTO")
    id_depto = pedir_entero("Id: ")
    depto = departamentos.obtener(id_depto)
    if depto is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {depto.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "codigo", "presupuesto", "plazas_disponibles"):
        actual = getattr(depto, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*departamentos.actualizar(id_depto, cambios))
    pausa()


def eliminar_departamento() -> None:
    """
    Elimina un departamento del sistema previa confirmacion.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("ELIMINAR DEPARTAMENTO")
    id_depto = pedir_entero("Id: ")
    depto = departamentos.obtener(id_depto)
    if depto is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminara: {depto.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*departamentos.eliminar(id_depto))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


# MENU DE ROLES DE PAGO (NOMINA)

def procesar_rol() -> None:
    """
    Inicia el flujo para liquidar el sueldo de un empleado en un mes especifico.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("PROCESAR ROL DE PAGO")
    imprimir_info("Empleados:")
    mostrar_lista(empleados.leer())
    imprimir_info("Departamentos:")
    mostrar_lista(departamentos.leer())

    datos = {
        "empleado_id": pedir_entero("\nId del empleado: "),
        "departamento_id": pedir_entero("Id del departamento: "),
        "mes": input("Mes de liquidacion (ej. Enero 2026): "),
        "horas_extras": input("Ingresos por horas extras (opcional): "),
        "bono": input("Ingresos por bonos (opcional): ")
    }
    
    if datos["empleado_id"] is None or datos["departamento_id"] is None:
        imprimir_error("Los identificadores deben ser numeros enteros")
        return pausa()

    mostrar_resultado(*roles_pago.crear(datos))
    pausa()


def listar_roles() -> None:
    """
    Muestra el listado de todos los roles de pago emitidos.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("ROLES DE PAGO EMITIDOS")
    mostrar_lista(roles_pago.leer(), "Todavia no hay roles procesados.")
    pausa()


def ver_comprobante() -> None:
    """
    Imprime en pantalla el recibo de liquidacion de sueldo.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("RECIBO DE ROL DE PAGO")
    texto = roles_pago.comprobante(pedir_entero("Id del rol de pago: "))
    if texto is None:
        imprimir_error("No existe ese rol de pago")
    else:
        print(texto)
    pausa()


def anular_rol() -> None:
    """
    Anula un rol de pago emitido y restaura la plaza en el departamento.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("ANULAR ROL DE PAGO")
    id_rol = pedir_entero("Id del rol: ")
    if id_rol and confirmar("Se anulara el pago y devolvera la plaza. ¿Confirma?"):
        mostrar_resultado(*roles_pago.eliminar(id_rol))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


def resumen() -> None:
    """
    Muestra un reporte gerencial con estadisticas del sistema de nomina.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("RESUMEN DE NOMINA")
    print(f"  Empleados   : {len(empleados.leer())}")
    print(f"  Cargos      : {', '.join(empleados.cargos()) or '-'}")
    print(f"  Departamentos: {len(departamentos.leer())}")
    
    bajos = departamentos.con_plazas_bajas()
    print(f"  Alerta plazas: {', '.join(d.nombre for d in bajos) or 'ninguna'}")
    
    print(f"  Roles emitid: {len(roles_pago.leer())}")
    print(f"  Total pagado: ${roles_pago.total_nomina_pagada():.2f}")
    pausa()


# MENUS: DICCIONARIOS tecla -> (texto, funcion)

MENU_EMPLEADOS = {
    "1": ("Registrar empleado", crear_empleado),
    "2": ("Ver todos", listar_empleados),
    "3": ("Buscar", buscar_empleado),
    "4": ("Ver por id", ver_empleado),
    "5": ("Actualizar", actualizar_empleado),
    "6": ("Eliminar", eliminar_empleado),
    "0": ("Volver", None),
}

MENU_DEPARTAMENTOS = {
    "1": ("Crear departamento", crear_departamento),
    "2": ("Ver todos", listar_departamentos),
    "3": ("Buscar", buscar_departamento),
    "4": ("Ver por id", ver_departamento),
    "5": ("Actualizar", actualizar_departamento),
    "6": ("Eliminar", eliminar_departamento),
    "0": ("Volver", None),
}

MENU_ROLES = {
    "1": ("Procesar rol de pago", procesar_rol),
    "2": ("Ver todos emitidos", listar_roles),
    "3": ("Imprimir comprobante", ver_comprobante),
    "4": ("Anular rol", anular_rol),
    "0": ("Volver", None),
}


def ejecutar_menu(titulo: str, opciones: dict) -> None:
    """
    Un solo bucle para renderizar y gestionar los tres submenus dinamicamente.
    
    Args:
        titulo (str): Titulo del menu a mostrar en la cabecera.
        opciones (dict): Diccionario de configuracion del menu.
        
    Returns:
        None
    """
    while True:
        imprimir_titulo(titulo)
        for tecla, (texto, _funcion) in opciones.items():
            print(f"  {tecla}. {texto}")
        print()

        tecla = input("Opcion: ").strip()
        if tecla not in opciones:               # busqueda por clave: instantanea
            imprimir_error("Opcion no valida")
            pausa()
            continue

        _texto, funcion = opciones[tecla]
        if funcion is None:                     # la opcion "Volver"
            break
        funcion()


def main() -> None:
    """
    Punto de entrada principal de la aplicacion de consola.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    while True:
        imprimir_titulo("SISTEMA DE NOMINA Y RRHH")
        print("  1. Empleados")
        print("  2. Departamentos")
        print("  3. Roles de Pago")
        print("  4. Resumen Gerencial")
        print("  0. Salir\n")

        tecla = input("Opcion: ").strip()
        if tecla == "1":
            ejecutar_menu("GESTION DE EMPLEADOS", MENU_EMPLEADOS)
        elif tecla == "2":
            ejecutar_menu("GESTION DE DEPARTAMENTOS", MENU_DEPARTAMENTOS)
        elif tecla == "3":
            ejecutar_menu("LIQUIDACION DE NOMINA", MENU_ROLES)
        elif tecla == "4":
            resumen()
        elif tecla == "0":
            imprimir_info("¡Hasta luego! 👋")
            break
        else:
            imprimir_error("Opcion no valida")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")