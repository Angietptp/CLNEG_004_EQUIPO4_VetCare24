"""Agregado Cita (raíz) con PeriodoDeCita y ServicioSolicitado como Value Objects."""
from vetcare24.dominio.errores import PeriodoIncoherente
from vetcare24.dominio.eventos import CitaAgendada, RaizDeAgregado
from vetcare24.dominio.valores import PeriodoDeCita, ServicioSolicitado


class Cita(RaizDeAgregado):
    """NB-06, NB-07, R-05: el periodo es coherente con la duración del servicio."""

    def __init__(self, cita_id: str, mascota_id: str,
                 servicio: ServicioSolicitado, periodo: PeriodoDeCita, motivo: str = ""):
        super().__init__()
        if periodo.duracion_minutos != servicio.duracion_minutos:
            raise PeriodoIncoherente()
        self.cita_id = cita_id
        self.mascota_id = mascota_id  # referencia por identidad (ADR-02)
        self.servicio = servicio
        self.periodo = periodo
        self.motivo = motivo

    @classmethod
    def agendar(cls, cita_id: str, mascota_id: str,
                servicio: ServicioSolicitado, periodo: PeriodoDeCita) -> "Cita":
        cita = cls(cita_id, mascota_id, servicio, periodo)
        cita.registrar_evento(CitaAgendada(cita_id, mascota_id))
        return cita
