from datetime import date
from typing import Dict, Any


# CLASE BASE: lo que los tres modelos comparten
class ModeloBase:
    """Padre de todos los modelos. Guarda el id y define el comportamiento comun."""

    def __init__(self, id_registro: int) -> None:
        """
        Inicializa la entidad base con su identificador unico.

        Args:
            id_registro (int): Identificador numerico unico para el registro.

        Returns:
            None
        """
        self.id = int(id_registro)

    # UNICO METODO DE CLASE DEL PROYECTO
    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> "ModeloBase":
        """
        Diccionario a objeto. Escrito UNA vez y usado por los tres modelos.
        cls es la clase que llamo: Empleado, Departamento o RolPago.

        Args:
            datos (Dict[str, Any]): Diccionario con los datos leidos del JSON.

        Returns:
            ModeloBase: Instancia de la clase que hizo la llamada.
        """
        datos_copia = dict(datos)
        id_registro = datos_copia.pop("id")
        return cls(id_registro, **datos_copia)

    # METODOS DE INSTANCIA
    def a_diccionario(self) -> Dict[str, Any]:
        """
        Objeto a diccionario. Cada hijo agrega sus campos.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario base conteniendo solo el id.
        """
        return {"id": self.id}

    def etiqueta(self) -> str:
        """
        Polimorfismo: cada hijo la reescribe a su manera para listados.

        Args:
            Ninguno

        Returns:
            str: Texto generico con el numero de registro.
        """
        return f"registro {self.id}"

    def __str__(self) -> str:
        """
        Representacion visible al imprimir el objeto. Llama a etiqueta().

        Args:
            Ninguno

        Returns:
            str: Representacion final formateada para la consola.
        """
        return f"[{self.id}] {self.etiqueta()}"


# HERENCIA: Persona es la base de Empleado
class Persona(ModeloBase):
    """Todo lo que tiene una persona del sistema."""

    def __init__(self, id_registro: int, nombre: str, apellido: str, email: str) -> None:
        """
        Inicializa una Persona con sus datos civiles basicos.

        Args:
            id_registro (int): Identificador unico numerico.
            nombre (str): Nombre de la persona.
            apellido (str): Apellido de la persona.
            email (str): Correo electronico de contacto.

        Returns:
            None
        """
        super().__init__(id_registro)
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self) -> str:
        """
        Concatena de forma limpia el nombre y el apellido.

        Args:
            Ninguno

        Returns:
            str: Nombre y apellido unidos por un espacio.
        """
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Agrega los atributos de Persona al diccionario del padre.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario con id, nombre, apellido y email.
        """
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["apellido"] = self.apellido
        datos["email"] = self.email
        return datos

    def etiqueta(self) -> str:
        """
        Sobrescribe la representacion base para devolver el nombre completo.

        Args:
            Ninguno

        Returns:
            str: Nombre completo.
        """
        return self.nombre_completo()


class Empleado(Persona):
    """Empleado ES UNA Persona, con codigo laboral, cargo y salario base contractual."""

    def __init__(
        self, id_registro: int, nombre: str, apellido: str, email: str,
        codigo_emp: str = "", cargo: str = "", salario_base: float = 0.0
    ) -> None:
        """
        Inicializa un Empleado con sus atributos contractuales.

        Args:
            id_registro (int): Identificador unico numerico.
            nombre (str): Nombre del empleado.
            apellido (str): Apellido del empleado.
            email (str): Correo institucional o personal.
            codigo_emp (str, opcional): Codigo institucional del trabajador. Por defecto "".
            cargo (str, opcional): Puesto que desempena. Por defecto "".
            salario_base (float, opcional): Salario mensual asignado. Por defecto 0.0.

        Returns:
            None
        """
        super().__init__(id_registro, nombre, apellido, email)
        self.codigo_emp = codigo_emp
        self.cargo = cargo
        self.salario_base = float(salario_base)

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Extiende el diccionario de Persona con los datos contractuales.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario completo del Empleado.
        """
        datos = super().a_diccionario()
        datos["codigo_emp"] = self.codigo_emp
        datos["cargo"] = self.cargo
        datos["salario_base"] = self.salario_base
        return datos

    def etiqueta(self) -> str:
        """
        Sobrescribe y extiende la etiqueta de Persona.

        Args:
            Ninguno

        Returns:
            str: Representacion con nombre, codigo, cargo y salario base.
        """
        codigo_txt = self.codigo_emp or "sin codigo"
        cargo_txt = self.cargo or "sin cargo"
        return f"{super().etiqueta()} · [{codigo_txt}] {cargo_txt} · Base: ${self.salario_base:.2f}"


# UNICA CLASE CON ATRIBUTOS Y METODOS ESTATICOS
class Departamento(ModeloBase):
    """Departamento ES UN ModeloBase. Contiene las reglas estaticas laborales de nomina."""

    # ATRIBUTOS ESTATICOS (de clase): reglas de negocio generales
    CAPACIDAD_MAXIMA = 20
    APORTE_IESS = 0.0945
    total_creados = 0

    def __init__(
        self, id_registro: int, nombre: str, codigo: str,
        presupuesto: float = 0.0, plazas_disponibles: int = 20
    ) -> None:
        """
        Inicializa un departamento de la empresa.

        Args:
            id_registro (int): Identificador unico numerico.
            nombre (str): Nombre del departamento.
            codigo (str): Codigo institucional del departamento.
            presupuesto (float, opcional): Presupuesto asignado al departamento. Por defecto 0.0.
            plazas_disponibles (int, opcional): Plazas libres para contratar. Por defecto 20.

        Returns:
            None
        """
        super().__init__(id_registro)
        self.nombre = nombre
        self.codigo = codigo
        self.presupuesto = float(presupuesto)
        self.plazas_disponibles = int(plazas_disponibles)
        Departamento.total_creados += 1

    # METODOS ESTATICOS: validaciones y calculos legales que no requieren una instancia
    @staticmethod
    def es_salario_valido(valor: Any) -> bool:
        """
        Valida que el valor ingresado sea un monto positivo razonable.

        Args:
            valor (Any): Valor a evaluar, sea string o numerico.

        Returns:
            bool: True si el salario es mayor a cero.
        """
        try:
            return float(valor) > 0
        except (TypeError, ValueError):
            return False

    @staticmethod
    def calcular_descuento_seguro(monto: float) -> float:
        """
        Calcula la retencion de aporte personal a la seguridad social.

        Args:
            monto (float): Monto sobre el cual se calcula el aporte.

        Returns:
            float: Valor del descuento redondeado a dos decimales.
        """
        return round(monto * Departamento.APORTE_IESS, 2)

    # METODOS DE INSTANCIA: estado particular de este departamento
    def plazas_bajas(self) -> bool:
        """
        Evalua si el departamento esta proximo a agotar vacantes.

        Args:
            Ninguno

        Returns:
            bool: True si quedan 2 o menos plazas disponibles.
        """
        return self.plazas_disponibles <= 2

    def hay_plaza(self) -> bool:
        """
        Verifica si hay vacantes disponibles para incorporar personal.

        Args:
            Ninguno

        Returns:
            bool: True si existen plazas libres.
        """
        return self.plazas_disponibles > 0

    def ocupar_plaza(self) -> None:
        """
        Resta una plaza disponible si existen cupos en el area.

        Args:
            Ninguno

        Returns:
            None
        """
        if self.hay_plaza():
            self.plazas_disponibles -= 1

    def liberar_plaza(self) -> None:
        """
        Suma una plaza disponible sin sobrepasar la capacidad maxima del departamento.

        Args:
            Ninguno

        Returns:
            None
        """
        if self.plazas_disponibles < Departamento.CAPACIDAD_MAXIMA:
            self.plazas_disponibles += 1

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Empaqueta los datos del departamento para persistencia en JSON.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario con los datos del departamento.
        """
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["codigo"] = self.codigo
        datos["presupuesto"] = self.presupuesto
        datos["plazas_disponibles"] = self.plazas_disponibles
        return datos

    def etiqueta(self) -> str:
        """
        Genera la representacion en texto del departamento indicando alertas.

        Args:
            Ninguno

        Returns:
            str: Detalle formateado del departamento y sus vacantes.
        """
        alerta = " ⚠ sin plazas" if not self.hay_plaza() else ""
        return (f"[{self.codigo}] {self.nombre} · "
                f"Presupuesto: ${self.presupuesto:.2f} · "
                f"Plazas: {self.plazas_disponibles}/{Departamento.CAPACIDAD_MAXIMA}{alerta}")


# ENTIDAD TRANSACCIONAL: Rol de pago mensual de un empleado
class RolPago(ModeloBase):
    """Rol de pago individual: conecta un empleado con un departamento en un mes y liquida su sueldo neto."""

    def __init__(
        self, id_registro: int, empleado_id: int, departamento_id: int,
        mes: str, sueldo_base: float, horas_extras: float = 0.0,
        bono: float = 0.0, fecha: str = ""
    ) -> None:
        """
        Inicializa la liquidacion de rol de pago.

        Args:
            id_registro (int): Identificador unico del registro de rol.
            empleado_id (int): Identificador del empleado asignado.
            departamento_id (int): Identificador del departamento al que pertenece.
            mes (str): Periodo o mes de liquidacion (ej. 'Enero 2026').
            sueldo_base (float): Salario base computado en la liquidacion.
            horas_extras (float, opcional): Valor adicional por horas extraordinarias. Por defecto 0.0.
            bono (float, opcional): Monto adicional por rendimiento o incentivos. Por defecto 0.0.
            fecha (str, opcional): Fecha de emision del rol. Por defecto fecha del dia.

        Returns:
            None
        """
        super().__init__(id_registro)
        self.empleado_id = int(empleado_id)
        self.departamento_id = int(departamento_id)
        self.mes = mes
        self.sueldo_base = float(sueldo_base)
        self.horas_extras = float(horas_extras)
        self.bono = float(bono)
        self.fecha = fecha or date.today().isoformat()

    def total_ingresos(self) -> float:
        """
        Calcula la sumatoria bruta de ingresos del empleado en el periodo.

        Args:
            Ninguno

        Returns:
            float: Suma de sueldo base, horas extras y bono.
        """
        return round(self.sueldo_base + self.horas_extras + self.bono, 2)

    def total_descuentos(self) -> float:
        """
        Calcula los egresos o retenciones legales aplicadas al ingreso total.

        Args:
            Ninguno

        Returns:
            float: Monto retenido por concepto de seguridad social.
        """
        return Departamento.calcular_descuento_seguro(self.total_ingresos())

    def calcular_sueldo_neto(self) -> float:
        """
        Calcula en tiempo real el valor liquido a percibir.

        Args:
            Ninguno

        Returns:
            float: Total de ingresos menos deducciones de ley.
        """
        return round(self.total_ingresos() - self.total_descuentos(), 2)

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Genera el diccionario para persistir el rol de pago en el JSON.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario con las llaves requeridas para roles_pago.json.
        """
        datos = super().a_diccionario()
        datos["empleado_id"] = self.empleado_id
        datos["departamento_id"] = self.departamento_id
        datos["mes"] = self.mes
        datos["sueldo_base"] = self.sueldo_base
        datos["horas_extras"] = self.horas_extras
        datos["bono"] = self.bono
        datos["fecha"] = self.fecha
        return datos

    def etiqueta(self) -> str:
        """
        Resume la informacion relevante del rol de pago para pantallas y comprobantes.

        Args:
            Ninguno

        Returns:
            str: Detalle con fecha, empleado, periodo y valor neto a percibir.
        """
        return (f"{self.fecha} · Empleado {self.empleado_id} · Depto {self.departamento_id} "
                f"({self.mes}) -> Ingresos: ${self.total_ingresos():.2f} - "
                f"Desc: ${self.total_descuentos():.2f} = Neto: ${self.calcular_sueldo_neto():.2f}")