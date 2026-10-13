"""CU-01 Solicitar cita (US04)."""
from vetcare24.aplicacion.comandos import SolicitarCita
from vetcare24.aplicacion.puertos import ControlDeAcceso, UnitOfWork
from vetcare24.aplicacion.resultados import ResultadoDeSolicitudDeCita
from vetcare24.aplicacion.seguridad import Operacion
from vetcare24.aplicacion.transaccion import transaccion
from vetcare24.dominio.repositorios import CitaRepository, MascotaRepository
from vetcare24.dominio.servicio_de_programacion_de_citas import ServicioDeProgramacionDeCitas


class CitasApplicationService:
    """Coordina; las reglas (duración, traslape) viven en el dominio."""

    def __init__(self, control_de_acceso: ControlDeAcceso, mascotas: MascotaRepository,
                 citas: CitaRepository, programacion: ServicioDeProgramacionDeCitas,
                 unit_of_work: UnitOfWork):
        self._acceso = control_de_acceso
        self._mascotas = mascotas
        self._citas = citas
        self._programacion = programacion
        self._uow = unit_of_work

    def solicitar_cita(self, comando: SolicitarCita) -> ResultadoDeSolicitudDeCita:
        self._acceso.verificar(comando.usuario, Operacion.SOLICITAR_CITA)
        with transaccion(self._uow):
            self._mascotas.obtener(comando.mascota_id)  # R-10
            cita = self._programacion.programar(
                self._citas.siguiente_id(), comando.mascota_id, comando.servicio,
                comando.fecha, comando.hora_inicio, self._citas.buscar_por_fecha(comando.fecha))
            self._citas.agregar(cita)
        return ResultadoDeSolicitudDeCita(cita.cita_id, cita.servicio, cita.periodo,
                                          cita.extraer_eventos())
