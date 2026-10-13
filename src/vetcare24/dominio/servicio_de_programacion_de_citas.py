"""Domain Service: deriva el periodo, revisa traslapes y crea la Cita (Q3, NB-07, R-05)."""
from datetime import date, time
from typing import Iterable

from vetcare24.dominio.cita import Cita
from vetcare24.dominio.errores import HorarioNoDisponible
from vetcare24.dominio.valores import PeriodoDeCita, ServicioSolicitado


class ServicioDeProgramacionDeCitas:
    """Supuesto: la disponibilidad se revisa contra todas las citas del día
    (el criterio por veterinario, consultorio o clínica está pendiente, P1)."""

    def programar(self, cita_id: str, mascota_id: str, servicio: ServicioSolicitado,
                  fecha: date, hora_inicio: time, citas_del_dia: Iterable[Cita]) -> Cita:
        periodo = PeriodoDeCita.desde(fecha, hora_inicio, servicio.duracion_minutos)
        for existente in citas_del_dia:
            if periodo.se_traslapa_con(existente.periodo):
                raise HorarioNoDisponible()
        return Cita.agendar(cita_id, mascota_id, servicio, periodo)
