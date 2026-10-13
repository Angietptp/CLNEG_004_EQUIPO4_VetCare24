"""CU-04 Registrar hospitalización (US17)."""
from datetime import datetime
from typing import Callable

from vetcare24.aplicacion.comandos import RegistrarHospitalizacion
from vetcare24.aplicacion.puertos import ControlDeAcceso, UnitOfWork
from vetcare24.aplicacion.resultados import ResultadoDeHospitalizacion
from vetcare24.aplicacion.seguridad import Operacion
from vetcare24.aplicacion.transaccion import transaccion
from vetcare24.dominio.hospitalizacion import Hospitalizacion
from vetcare24.dominio.repositorios import HospitalizacionRepository, MascotaRepository


class HospitalizacionApplicationService:
    def __init__(self, control_de_acceso: ControlDeAcceso, mascotas: MascotaRepository,
                 hospitalizaciones: HospitalizacionRepository, unit_of_work: UnitOfWork,
                 reloj: Callable[[], datetime] = datetime.now):
        self._acceso = control_de_acceso
        self._mascotas = mascotas
        self._hospitalizaciones = hospitalizaciones
        self._uow = unit_of_work
        self._reloj = reloj

    def registrar_hospitalizacion(self, comando: RegistrarHospitalizacion) -> ResultadoDeHospitalizacion:
        self._acceso.verificar(comando.usuario, Operacion.REGISTRAR_HOSPITALIZACION)  # R-04, R-09
        with transaccion(self._uow):
            self._mascotas.obtener(comando.mascota_id)
            h = Hospitalizacion.iniciar(self._hospitalizaciones.siguiente_id(),
                                        comando.mascota_id, comando.motivo, self._reloj())
            self._hospitalizaciones.agregar(h)
        return ResultadoDeHospitalizacion(h.hospitalizacion_id, h.seguimiento_continuo,
                                          h.extraer_eventos())
