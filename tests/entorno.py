"""Entorno de pruebas: arma servicios reales con infraestructura en memoria y
espías que dejan una bitácora ordenada de las llamadas importantes."""
from datetime import date, datetime, time

from vetcare24.aplicacion.citas import CitasApplicationService
from vetcare24.aplicacion.consultas import (
    ConsultarCitasProgramadasHandler, ConsultarExpedienteClinicoHandler)
from vetcare24.aplicacion.emergencias import EmergenciasApplicationService
from vetcare24.aplicacion.expediente_clinico import ExpedienteClinicoApplicationService
from vetcare24.aplicacion.hospitalizacion import HospitalizacionApplicationService
from vetcare24.aplicacion.seguridad import Rol, Usuario
from vetcare24.aplicacion.vacunacion import VacunacionApplicationService
from vetcare24.dominio.expediente_clinico import ExpedienteClinico
from vetcare24.dominio.mascota import Mascota
from vetcare24.dominio.servicio_de_programacion_de_citas import ServicioDeProgramacionDeCitas
from vetcare24.dominio.vacunacion import EsquemaDeVacunacion, ServicioDeSeguimientoDeVacunacion
from vetcare24.dominio.valores import ServicioSolicitado
from vetcare24.infraestructura.almacen import AlmacenEnMemoria
from vetcare24.infraestructura.control_de_acceso import ControlDeAccesoPorRol
from vetcare24.infraestructura.lecturas import LecturaDeAgendaImpl, LecturaDeExpedientesImpl
from vetcare24.infraestructura.notificador import NotificadorDeVeterinarioEnMemoria
from vetcare24.infraestructura.repositorios import (
    CitaRepositoryImpl, EmergenciaRepositoryImpl, EsquemaDeVacunacionRepositoryImpl,
    ExpedienteClinicoRepositoryImpl, HospitalizacionRepositoryImpl, MascotaRepositoryImpl,
    VacunacionRepositoryImpl)
from vetcare24.infraestructura.unit_of_work import UnitOfWorkImpl

FECHA = date(2026, 10, 14)
NUEVE = time(9, 0)
CONSULTA = ServicioSolicitado("Consulta general", 30)
AHORA = datetime(2026, 10, 13, 9, 0)


class UnitOfWorkEspia(UnitOfWorkImpl):
    def __init__(self, almacen, bitacora):
        super().__init__(almacen)
        self._b = bitacora

    def iniciar(self):
        self._b.append("uow.iniciar"); super().iniciar()

    def confirmar(self):
        self._b.append("uow.confirmar"); super().confirmar()

    def revertir(self):
        self._b.append("uow.revertir"); super().revertir()


class ControlEspia(ControlDeAccesoPorRol):
    def __init__(self, bitacora):
        self._b = bitacora

    def verificar(self, usuario, operacion):
        self._b.append("acceso.verificar")
        super().verificar(usuario, operacion)


class NotificadorEspia(NotificadorDeVeterinarioEnMemoria):
    def __init__(self, bitacora, disponible=True):
        super().__init__(disponible)
        self._b = bitacora

    def notificar(self, emergencia_id, mensaje):
        self._b.append("notificador.notificar")
        return super().notificar(emergencia_id, mensaje)


class Entorno:
    def __init__(self, citas_repo_factory=None, notificador_disponible=True):
        self.bitacora = []
        self.almacen = AlmacenEnMemoria()
        a = self.almacen
        self.mascotas = MascotaRepositoryImpl(a)
        self.citas = (citas_repo_factory or CitaRepositoryImpl)(a)
        self.expedientes = ExpedienteClinicoRepositoryImpl(a)
        self.vacunaciones = VacunacionRepositoryImpl(a)
        self.esquemas = EsquemaDeVacunacionRepositoryImpl(a)
        self.hospitalizaciones = HospitalizacionRepositoryImpl(a)
        self.emergencias = EmergenciaRepositoryImpl(a)
        self.uow = UnitOfWorkEspia(a, self.bitacora)
        self.acceso = ControlEspia(self.bitacora)
        self.notificador = NotificadorEspia(self.bitacora, notificador_disponible)
        reloj = lambda: AHORA

        self.servicio_citas = CitasApplicationService(
            self.acceso, self.mascotas, self.citas, ServicioDeProgramacionDeCitas(), self.uow)
        self.servicio_notas = ExpedienteClinicoApplicationService(
            self.acceso, self.mascotas, self.expedientes, self.uow, reloj)
        self.servicio_vacunacion = VacunacionApplicationService(
            self.acceso, self.mascotas, self.vacunaciones, self.esquemas,
            ServicioDeSeguimientoDeVacunacion(), self.uow)
        self.servicio_hospitalizacion = HospitalizacionApplicationService(
            self.acceso, self.mascotas, self.hospitalizaciones, self.uow, reloj)
        self.servicio_emergencias = EmergenciasApplicationService(
            self.acceso, self.emergencias, self.notificador, self.uow, reloj)
        self.consulta_citas = ConsultarCitasProgramadasHandler(
            self.acceso, LecturaDeAgendaImpl(a))
        self.consulta_expediente = ConsultarExpedienteClinicoHandler(
            self.acceso, LecturaDeExpedientesImpl(a))

        self.propietario = Usuario("U-PROP", Rol.PROPIETARIO)
        self.recepcion = Usuario("U-REC", Rol.RECEPCION)
        self.veterinario = Usuario("VET-01", Rol.VETERINARIO)
        self.personal_clinico = Usuario("U-CLI", Rol.PERSONAL_CLINICO)
        self._sembrar()

    def _sembrar(self):
        a = self.almacen
        a.mascotas["M-001"] = Mascota("M-001", "Firulais", "Perro", "P-001")
        a.expedientes["M-001"] = ExpedienteClinico("EXP-001", "M-001")
        a.esquemas["Rabia"] = EsquemaDeVacunacion("Rabia", 365, 3, validado=True)
        a.esquemas["Parvovirus"] = EsquemaDeVacunacion("Parvovirus", 21, 3, validado=False)
        # "Moquillo" no tiene esquema definido

    def instantanea(self):
        return self.almacen.instantanea()

    def huella(self):
        """Resumen comparable del estado persistido (claves y número de notas)."""
        a = self.almacen
        return (
            tuple(sorted(a.mascotas)), tuple(sorted(a.citas)),
            tuple(sorted(a.vacunaciones)), tuple(sorted(a.hospitalizaciones)),
            tuple(sorted(a.emergencias)),
            tuple((k, len(e.notas)) for k, e in sorted(a.expedientes.items())),
        )
