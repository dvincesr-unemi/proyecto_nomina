from abc import ABC, abstractmethod

from models import Empleado, Departamento, RolPago
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# CLASE BASE (ABSTRACTA)
# Solo dice QUE metodos debe tener todo controlador.
# COMO se hace cada uno lo escribe cada controlador, de la forma mas simple.
class CrudBase(ABC):

    @abstractmethod
    def leer(self):
        """
        Retorna la lista completa de registros.
        
        Args:
            Ninguno
            
        Returns:
            list: Lista de objetos del modelo.
        """
        pass

    @abstractmethod
    def obtener(self, id_registro):
        """
        Busca un registro por su identificador unico.
        
        Args:
            id_registro (int): Identificador a buscar.
            
        Returns:
            object o None: El objeto encontrado o None si no existe.
        """
        pass

    @abstractmethod
    def buscar(self, texto):
        """
        Filtra registros que coincidan con el texto proporcionado.
        
        Args:
            texto (str): Cadena de busqueda.
            
        Returns:
            list: Lista de objetos que coinciden con el criterio.
        """
        pass

    @abstractmethod
    def siguiente(self):
        """
        Calcula el proximo identificador disponible.
        
        Args:
            Ninguno
            
        Returns:
            int: Siguiente ID numerico.
        """
        pass

    @abstractmethod
    def crear(self, datos):
        """
        Crea un nuevo registro a partir de un diccionario de datos.
        
        Args:
            datos (dict): Diccionario con la informacion del registro.
            
        Returns:
            tuple: (bool: exito, str: mensaje).
        """
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        """
        Modifica un registro existente.
        
        Args:
            id_registro (int): Identificador del registro a modificar.
            datos (dict): Diccionario con los campos a actualizar.
            
        Returns:
            tuple: (bool: exito, str: mensaje).
        """
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        """
        Elimina un registro del sistema.
        
        Args:
            id_registro (int): Identificador del registro a eliminar.
            
        Returns:
            tuple: (bool: exito, str: mensaje).
        """
        pass


# CONTROLADOR DE EMPLEADOS
class EmpleadoController(CrudBase):

    def __init__(self, archivo="data/empleados.json"):
        """
        Inicializa el controlador y carga los datos desde el JSON.
        
        Args:
            archivo (str, opcional): Ruta del archivo JSON. Por defecto "data/empleados.json".
            
        Returns:
            None
        """
        self.gestor = GestorJSON(archivo)

        # Leemos el JSON y convertimos cada diccionario en un objeto Empleado
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Empleado.desde_diccionario(datos))

    def guardar(self):
        """
        Guarda la lista actual de empleados en el archivo JSON.
        
        Args:
            Ninguno
            
        Returns:
            None
        """
        datos = []
        for empleado in self.lista:
            datos.append(empleado.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        """
        Valida las reglas de negocio antes de crear o actualizar un empleado.
        
        Args:
            datos (dict): Diccionario con la informacion a validar.
            id_actual (int, opcional): ID del empleado si se esta actualizando.
            
        Returns:
            str o None: Mensaje de error si falla la validacion, None si todo esta bien.
        """
        # Al crear hay que traer los obligatorios; al actualizar, solo lo que cambia
        if id_actual is None:
            for campo in ("nombre", "apellido", "email", "codigo_emp"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email invalido: '{email}'"
            # CONJUNTO con los emails de los OTROS empleados
            usados = {e.email for e in self.lista if e.id != id_actual}
            if email in usados:
                return "Ese email ya esta registrado"

        if "salario_base" in datos:
            if not Departamento.es_salario_valido(datos["salario_base"]):
                return "El salario base debe ser un numero mayor a 0"

        return None

    def leer(self):
        """
        Devuelve la lista de empleados.
        
        Args:
            Ninguno
            
        Returns:
            list: Lista de instancias de Empleado.
        """
        return self.lista

    def obtener(self, id_empleado):
        """
        Busca un empleado por ID.
        
        Args:
            id_empleado (int): ID a buscar.
            
        Returns:
            Empleado o None: Empleado encontrado o None.
        """
        for empleado in self.lista:
            if empleado.id == id_empleado:
                return empleado
        return None

    def buscar(self, texto):
        """
        Busca empleados por coincidencia en texto.
        
        Args:
            texto (str): Texto a buscar.
            
        Returns:
            list: Empleados que coinciden.
        """
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for empleado in self.lista:
            if (texto in empleado.nombre.lower()
                    or texto in empleado.apellido.lower()
                    or texto in empleado.email
                    or texto in empleado.codigo_emp.lower()
                    or texto in empleado.cargo.lower()):
                encontrados.append(empleado)
        return encontrados

    def siguiente(self):
        """
        Obtiene el siguiente ID.
        
        Args:
            Ninguno
            
        Returns:
            int: Siguiente ID.
        """
        mayor = 0
        for empleado in self.lista:
            if empleado.id > mayor:
                mayor = empleado.id
        return mayor + 1

    def crear(self, datos):
        """
        Crea un empleado si los datos son validos.
        
        Args:
            datos (dict): Datos del empleado.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        error = self.validar(datos)
        if error:
            return False, error

        empleado = Empleado(self.siguiente(),
                            str(datos["nombre"]).strip().title(),
                            str(datos["apellido"]).strip().title(),
                            str(datos["email"]).strip().lower(),
                            str(datos.get("codigo_emp", "")).strip().upper(),
                            str(datos.get("cargo", "")).strip().title(),
                            float(datos.get("salario_base", 0.0)))
        self.lista.append(empleado)
        self.guardar()
        return True, f"Empleado creado: {empleado.etiqueta()}"

    def actualizar(self, id_empleado, datos):
        """
        Actualiza los datos de un empleado.
        
        Args:
            id_empleado (int): ID del empleado a actualizar.
            datos (dict): Datos nuevos.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        empleado = self.obtener(id_empleado)
        if empleado is None:
            return False, f"No existe un empleado con id {id_empleado}"
        if not datos:
            return False, "No se indico ningun cambio"

        # DIFERENCIA de conjuntos: campos que no existen en un empleado
        permitidos = {"nombre", "apellido", "email", "codigo_emp", "cargo", "salario_base"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no validos: {', '.join(sorted(desconocidos))}"

        # Se valida ANTES de tocar el objeto: si algo falla, no cambia nada
        error = self.validar(datos, id_empleado)
        if error:
            return False, error

        for campo, valor in datos.items():
            if campo in ("nombre", "apellido", "cargo"):
                valor = str(valor).strip().title()
            elif campo == "codigo_emp":
                valor = str(valor).strip().upper()
            elif campo == "email":
                valor = str(valor).strip().lower()
            elif campo == "salario_base":
                valor = float(valor)
            setattr(empleado, campo, valor)

        self.guardar()
        return True, f"Empleado {id_empleado} actualizado"

    def eliminar(self, id_empleado):
        """
        Elimina un empleado por su ID.
        
        Args:
            id_empleado (int): ID del empleado.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        empleado = self.obtener(id_empleado)
        if empleado is None:
            return False, f"No existe un empleado con id {id_empleado}"

        self.lista.remove(empleado)
        self.guardar()
        return True, f"Empleado {id_empleado} eliminado"

    # --- propio de empleados ---
    def cargos(self):
        """
        Obtiene los cargos unicos en la empresa.
        
        Args:
            Ninguno
            
        Returns:
            list: CONJUNTO de cargos sin repetidos, convertidos a lista ordenada.
        """
        return sorted({e.cargo for e in self.lista if e.cargo != ""})


# CONTROLADOR DE DEPARTAMENTOS
class DepartamentoController(CrudBase):

    def __init__(self, archivo="data/departamentos.json"):
        """
        Inicializa el controlador y carga los departamentos.
        
        Args:
            archivo (str, opcional): Ruta del archivo JSON. Por defecto "data/departamentos.json".
            
        Returns:
            None
        """
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Departamento.desde_diccionario(datos))

    def guardar(self):
        """
        Guarda los departamentos en el JSON.
        
        Args:
            Ninguno
            
        Returns:
            None
        """
        datos = []
        for depto in self.lista:
            datos.append(depto.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        """
        Valida que un departamento tenga datos correctos.
        
        Args:
            datos (dict): Datos a evaluar.
            id_actual (int, opcional): ID del departamento si se esta editando.
            
        Returns:
            str o None: Error si lo hay, de lo contrario None.
        """
        if id_actual is None:
            for campo in ("nombre", "codigo"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "presupuesto" in datos and not Departamento.es_salario_valido(datos["presupuesto"]):
            return f"Presupuesto invalido: '{datos['presupuesto']}' (debe ser un numero mayor a 0)"

        plazas = str(datos.get("plazas_disponibles", "")).strip()
        if plazas != "" and not plazas.isdigit():
            return "Las plazas deben ser un numero entero positivo"

        if "nombre" in datos:
            nombre = str(datos["nombre"]).strip().title()
            for otro in self.lista:
                if otro.nombre == nombre and otro.id != id_actual:
                    return f"Ya existe un departamento llamado {nombre}"
        return None

    def leer(self):
        """
        Obtiene la lista de departamentos.
        
        Args:
            Ninguno
            
        Returns:
            list: Lista de departamentos.
        """
        return self.lista

    def obtener(self, id_depto):
        """
        Obtiene un departamento por ID.
        
        Args:
            id_depto (int): ID del departamento.
            
        Returns:
            Departamento o None: Departamento si existe, o None.
        """
        for depto in self.lista:
            if depto.id == id_depto:
                return depto
        return None

    def buscar(self, texto):
        """
        Busca departamentos por nombre o codigo.
        
        Args:
            texto (str): Criterio de busqueda.
            
        Returns:
            list: Departamentos coincidentes.
        """
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for depto in self.lista:
            if texto in depto.nombre.lower() or texto in depto.codigo.lower():
                encontrados.append(depto)
        return encontrados

    def siguiente(self):
        """
        Genera el proximo ID.
        
        Args:
            Ninguno
            
        Returns:
            int: Proximo ID.
        """
        mayor = 0
        for depto in self.lista:
            if depto.id > mayor:
                mayor = depto.id
        return mayor + 1

    def crear(self, datos):
        """
        Crea un nuevo departamento.
        
        Args:
            datos (dict): Datos del departamento.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        error = self.validar(datos)
        if error:
            return False, error

        # Si no escribieron las plazas, empieza con el maximo por defecto
        plazas = str(datos.get("plazas_disponibles", "")).strip()
        plazas_final = int(plazas) if plazas != "" else Departamento.CAPACIDAD_MAXIMA
        
        depto = Departamento(self.siguiente(),
                             str(datos["nombre"]).strip().title(),
                             str(datos["codigo"]).strip().upper(),
                             float(datos.get("presupuesto", 0.0)),
                             plazas_final)
        self.lista.append(depto)
        self.guardar()
        return True, f"Departamento creado: {depto.etiqueta()}"

    def actualizar(self, id_depto, datos):
        """
        Actualiza un departamento existente.
        
        Args:
            id_depto (int): ID del departamento.
            datos (dict): Datos nuevos.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        depto = self.obtener(id_depto)
        if depto is None:
            return False, f"No existe un departamento con id {id_depto}"
        if not datos:
            return False, "No se indico ningun cambio"

        desconocidos = set(datos) - {"nombre", "codigo", "presupuesto", "plazas_disponibles"}
        if desconocidos:
            return False, f"Campos no validos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_depto)
        if error:
            return False, error

        if "nombre" in datos:
            depto.nombre = str(datos["nombre"]).strip().title()
        if "codigo" in datos:
            depto.codigo = str(datos["codigo"]).strip().upper()
        if "presupuesto" in datos:
            depto.presupuesto = float(datos["presupuesto"])
        if "plazas_disponibles" in datos:
            depto.plazas_disponibles = int(datos["plazas_disponibles"])

        self.guardar()
        return True, f"Departamento {id_depto} actualizado"

    def eliminar(self, id_depto):
        """
        Elimina un departamento.
        
        Args:
            id_depto (int): ID del departamento.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        depto = self.obtener(id_depto)
        if depto is None:
            return False, f"No existe un departamento con id {id_depto}"

        self.lista.remove(depto)
        self.guardar()
        return True, f"Departamento {id_depto} eliminado"

    # --- propio de departamentos ---
    def con_plazas_bajas(self):
        """
        Encuentra departamentos con 2 o menos plazas disponibles.
        
        Args:
            Ninguno
            
        Returns:
            list: Departamentos con alerta de plazas.
        """
        bajos = []
        for depto in self.lista:
            if depto.plazas_bajas():
                bajos.append(depto)
        return bajos


# CONTROLADOR DE ROLES DE PAGO (NÓMINA)
class RolPagoController(CrudBase):

    def __init__(self, empleados, departamentos, archivo="data/roles_pago.json"):
        """
        Inicializa el controlador vinculando Empleados y Departamentos.
        
        Args:
            empleados (EmpleadoController): Instancia del controlador de empleados.
            departamentos (DepartamentoController): Instancia del controlador de departamentos.
            archivo (str, opcional): Ruta del archivo JSON. Por defecto "data/roles_pago.json".
            
        Returns:
            None
        """
        # El rol USA a los otros dos controladores.
        # Hay que pasarle los MISMOS que usa main.py.
        self.empleados = empleados
        self.departamentos = departamentos
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(RolPago.desde_diccionario(datos))

    def guardar(self):
        """
        Guarda los roles de pago en JSON.
        
        Args:
            Ninguno
            
        Returns:
            None
        """
        datos = []
        for rol in self.lista:
            datos.append(rol.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos):
        """
        Valida que un empleado y departamento existan antes de pagar, y que haya plazas.
        
        Args:
            datos (dict): Datos del rol de pago.
            
        Returns:
            str o None: Error si existe, si no None.
        """
        try:
            empleado_id = int(datos.get("empleado_id", 0))
            departamento_id = int(datos.get("departamento_id", 0))
        except (TypeError, ValueError):
            return "empleado_id y departamento_id deben ser numeros enteros"

        if self.empleados.obtener(empleado_id) is None:
            return f"No existe un empleado con id {empleado_id}"

        depto = self.departamentos.obtener(departamento_id)
        if depto is None:
            return f"No existe un departamento con id {departamento_id}"
            
        # Regla de negocio: no se puede procesar pago si el departamento no tiene plazas activas (simulando aprobacion)
        if not depto.hay_plaza():
            return (f"No hay plazas administrativas en el departamento {depto.nombre} "
                    f"para procesar este pago.")
        return None

    def leer(self):
        """
        Obtiene todos los roles de pago.
        
        Args:
            Ninguno
            
        Returns:
            list: Lista de roles de pago.
        """
        return self.lista

    def obtener(self, id_rol):
        """
        Busca un rol de pago por ID.
        
        Args:
            id_rol (int): ID del rol de pago.
            
        Returns:
            RolPago o None: Objeto si se encuentra, o None.
        """
        for rol in self.lista:
            if rol.id == id_rol:
                return rol
        return None

    def buscar(self, texto):
        """
        Busca roles de pago por el periodo/mes (ej: 'Enero 2026').
        
        Args:
            texto (str): Mes a buscar.
            
        Returns:
            list: Roles de pago coincidentes.
        """
        # Los roles se buscan por mes/periodo, ej: "Octubre"
        texto = texto.strip().lower()
        encontradas = []
        if texto == "":
            return encontradas

        for rol in self.lista:
            if texto in rol.mes.lower():
                encontradas.append(rol)
        return encontradas

    def siguiente(self):
        """
        Genera el siguiente ID disponible para roles.
        
        Args:
            Ninguno
            
        Returns:
            int: Proximo ID.
        """
        mayor = 0
        for rol in self.lista:
            if rol.id > mayor:
                mayor = rol.id
        return mayor + 1

    def crear(self, datos):
        """
        Genera un nuevo rol de pago tomando el salario base del empleado en ese momento.
        
        Args:
            datos (dict): Datos base para el rol (empleado, depto, mes, extras).
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        error = self.validar(datos)
        if error:
            return False, error

        empleado = self.empleados.obtener(int(datos["empleado_id"]))
        depto = self.departamentos.obtener(int(datos["departamento_id"]))
        
        # Limpiamos los textos; si vienen vacios ("", espacio en blanco), toman "0"
        h_extras_str = str(datos.get("horas_extras", "")).strip() or "0"
        bono_str = str(datos.get("bono", "")).strip() or "0"
        
        rol = RolPago(self.siguiente(),
                      empleado.id,
                      depto.id,
                      str(datos["mes"]).strip(),
                      empleado.salario_base,          # foto del sueldo base del momento
                      float(h_extras_str),
                      float(bono_str))

        depto.ocupar_plaza()
        self.departamentos.guardar()                # guarda la plaza ocupada
        self.lista.append(rol)
        self.guardar()                              # guarda el rol en roles_pago.json
        return True, f"Rol de pago {rol.id} procesado con Neto: ${rol.calcular_sueldo_neto():.2f}"
    
    def actualizar(self, id_rol, datos):
        """
        Bloquea la modificacion de roles ya emitidos.
        
        Args:
            id_rol (int): ID del rol.
            datos (dict): Datos nuevos.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        # Un rol registrado no se modifica: se anula y se procesa otro por temas de auditoria
        return False, "Los roles de pago emitidos no se pueden modificar: anulelo y genere uno nuevo"

    def eliminar(self, id_rol):
        """
        Anula un rol de pago devolviendo la plaza administrativa.
        
        Args:
            id_rol (int): ID del rol a eliminar.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        # Anular un rol: se borra y la plaza vuelve al departamento.
        rol = self.obtener(id_rol)
        if rol is None:
            return False, f"No existe el rol de pago {id_rol}"

        depto = self.departamentos.obtener(rol.departamento_id)
        if depto is not None:
            depto.liberar_plaza()
            self.departamentos.guardar()

        self.lista.remove(rol)
        self.guardar()
        return True, f"Rol de pago {id_rol} anulado (plaza devuelta)"

    # --- propio de nomina ---
    def comprobante(self, id_rol):
        """
        Genera el recibo de pago en texto formateado para imprimir.
        
        Args:
            id_rol (int): ID del rol de pago.
            
        Returns:
            str o None: Texto formateado del comprobante o None si no existe.
        """
        rol = self.obtener(id_rol)
        if rol is None:
            return None

        empleado = self.empleados.obtener(rol.empleado_id)
        depto = self.departamentos.obtener(rol.departamento_id)
        
        ingresos = rol.total_ingresos()
        descuentos = rol.total_descuentos()
        neto = rol.calcular_sueldo_neto()

        texto = f"COMPROBANTE ROL #{rol.id}   Emision: {rol.fecha}\n"
        texto += f"Empleado: {empleado.nombre_completo() if empleado else 'eliminado'} "
        texto += f"({empleado.codigo_emp if empleado else 'N/A'})\n"
        texto += f"Depto   : {depto.nombre if depto else 'eliminado'}\n"
        texto += f"Periodo : {rol.mes}\n"
        texto += "-" * 45 + "\n"
        texto += f"Sueldo Base : ${rol.sueldo_base:.2f}\n"
        texto += f"Horas Extras: ${rol.horas_extras:.2f}\n"
        texto += f"Bonos       : ${rol.bono:.2f}\n"
        texto += f"TOTAL INGRES: ${ingresos:.2f}\n"
        texto += "-" * 45 + "\n"
        texto += f"Aportes IESS: ${descuentos:.2f} (-)\n"
        texto += "=" * 45 + "\n"
        texto += f"LIQUIDO A RECIBIR: ${neto:.2f}"
        return texto

    def roles_por_empleado(self):
        """
        Agrupa el historial de roles de pago por empleado.
        
        Args:
            Ninguno
            
        Returns:
            dict: DICCIONARIO de LISTAS: {empleado_id: [roles de ese empleado]}.
        """
        agrupadas = {}
        for rol in self.lista:
            if rol.empleado_id not in agrupadas:
                agrupadas[rol.empleado_id] = []
            agrupadas[rol.empleado_id].append(rol)
        return agrupadas

    def total_nomina_pagada(self):
        """
        Calcula el valor liquido total desembolsado por la empresa.
        
        Args:
            Ninguno
            
        Returns:
            float: Suma de todos los sueldos netos generados.
        """
        total = 0
        for rol in self.lista:
            total += rol.calcular_sueldo_neto()
        return round(total, 2)