"""Lado Query de CQRS (ADR-03): leen por puertos propios y devuelven View Models.
No dependen de repositorios de agregados ni de UnitOfWork: no modifican estado."""
from typing import List

from vetcare24.aplicacion.comandos import ConsultarCitasProgramadas, ConsultarExpedienteClinico
from vetcare24.aplicacion.puertos import ControlDeAcceso, LecturaDeAgenda, LecturaDeExpedientes
from vetcare24.aplicacion.seguridad import Operacion
from vetcare24.aplicacion.vistas import CitaProgramadaVista, ExpedienteClinicoVista


class ConsultarCitasProgramadasHandler:
    def __init__(self, control_de_acceso: ControlDeAcceso, lectura: LecturaDeAgenda):
        self._acceso = control_de_acceso
        self._lectura = lectura

    def manejar(self, consulta: ConsultarCitasProgramadas) -> List[CitaProgramadaVista]:
        self._acceso.verificar(consulta.usuario, Operacion.CONSULTAR_CITAS)
        return self._lectura.citas_programadas(consulta.fecha)


class ConsultarExpedienteClinicoHandler:
    def __init__(self, control_de_acceso: ControlDeAcceso, lectura: LecturaDeExpedientes):
        self._acceso = control_de_acceso
        self._lectura = lectura

    def manejar(self, consulta: ConsultarExpedienteClinico) -> ExpedienteClinicoVista:
        self._acceso.verificar(consulta.usuario, Operacion.CONSULTAR_EXPEDIENTE)  # R-14
        return self._lectura.expediente_de(consulta.mascota_id)
