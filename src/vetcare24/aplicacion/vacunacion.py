"""CU-03 Registrar vacunación (US15)."""
from vetcare24.aplicacion.comandos import RegistrarVacunacion
from vetcare24.aplicacion.puertos import ControlDeAcceso, UnitOfWork
from vetcare24.aplicacion.resultados import ResultadoDeVacunacion
from vetcare24.aplicacion.seguridad import Operacion
from vetcare24.aplicacion.transaccion import transaccion
from vetcare24.dominio.errores import EsquemaNoValidado
from vetcare24.dominio.repositorios import (
    EsquemaDeVacunacionRepository, MascotaRepository, VacunacionRepository)
from vetcare24.dominio.vacunacion import ServicioDeSeguimientoDeVacunacion, Vacunacion
from vetcare24.dominio.valores import DosisIndicada


class VacunacionApplicationService:
    def __init__(self, control_de_acceso: ControlDeAcceso, mascotas: MascotaRepository,
                 vacunaciones: VacunacionRepository, esquemas: EsquemaDeVacunacionRepository,
                 seguimiento: ServicioDeSeguimientoDeVacunacion, unit_of_work: UnitOfWork):
        self._acceso = control_de_acceso
        self._mascotas = mascotas
        self._vacunaciones = vacunaciones
        self._esquemas = esquemas
        self._seguimiento = seguimiento
        self._uow = unit_of_work

    def registrar_vacunacion(self, comando: RegistrarVacunacion) -> ResultadoDeVacunacion:
        self._acceso.verificar(comando.usuario, Operacion.REGISTRAR_VACUNACION)
        pendiente, proxima = False, None
        with transaccion(self._uow):
            self._mascotas.obtener(comando.mascota_id)
            historial = self._vacunaciones.historial_de(comando.mascota_id)
            vacunacion = Vacunacion.registrar(
                self._vacunaciones.siguiente_id(), comando.mascota_id,
                DosisIndicada(comando.vacuna, comando.dosis, comando.fecha_aplicacion))
            self._vacunaciones.agregar(vacunacion)
            try:  # el cálculo de seguimiento no persiste nada
                esquema = self._esquemas.obtener_por_vacuna(comando.vacuna)
                proxima = self._seguimiento.determinar_proxima(historial + [vacunacion], esquema)
            except EsquemaNoValidado:
                pendiente = True  # NO revierte: el registro se confirma (R-11, R-12)
        return ResultadoDeVacunacion(vacunacion.vacunacion_id, proxima, pendiente,
                                     vacunacion.extraer_eventos())
