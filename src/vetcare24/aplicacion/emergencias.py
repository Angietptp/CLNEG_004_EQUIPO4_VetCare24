"""CU-05 Atender una emergencia (US20). No usa CitaRepository: R-06."""
from datetime import datetime
from typing import Callable

from vetcare24.aplicacion.comandos import AtenderEmergencia
from vetcare24.aplicacion.puertos import ControlDeAcceso, NotificadorDeVeterinario, UnitOfWork
from vetcare24.aplicacion.resultados import ResultadoDeEmergencia
from vetcare24.aplicacion.seguridad import Operacion
from vetcare24.aplicacion.transaccion import transaccion
from vetcare24.dominio.emergencia import Emergencia
from vetcare24.dominio.repositorios import EmergenciaRepository


class EmergenciasApplicationService:
    def __init__(self, control_de_acceso: ControlDeAcceso, emergencias: EmergenciaRepository,
                 notificador: NotificadorDeVeterinario, unit_of_work: UnitOfWork,
                 reloj: Callable[[], datetime] = datetime.now):
        self._acceso = control_de_acceso
        self._emergencias = emergencias
        self._notificador = notificador
        self._uow = unit_of_work
        self._reloj = reloj

    def atender_emergencia(self, comando: AtenderEmergencia) -> ResultadoDeEmergencia:
        self._acceso.verificar(comando.usuario, Operacion.ATENDER_EMERGENCIA)
        with transaccion(self._uow):
            emergencia = Emergencia.identificar(
                self._emergencias.siguiente_id(), comando.motivo, comando.estado_inicial,
                self._reloj(), comando.mascota_id)
            self._emergencias.agregar(emergencia)
        # CR-8: la notificación se solicita DESPUÉS de confirmar el registro
        notificado = self._notificador.notificar(
            emergencia.emergencia_id, f"Emergencia: {emergencia.motivo}")
        return ResultadoDeEmergencia(emergencia.emergencia_id, notificado,
                                     emergencia.extraer_eventos())
