"""Agregado Emergencia (raíz). R-06: no exige cita previa."""
from datetime import datetime
from typing import Optional

from vetcare24.dominio.errores import InformacionIncompleta
from vetcare24.dominio.eventos import EmergenciaIdentificada, RaizDeAgregado


class Emergencia(RaizDeAgregado):
    def __init__(self, emergencia_id: str, motivo: str, estado_inicial: str,
                 fecha: datetime, mascota_id: Optional[str] = None):
        super().__init__()
        self.emergencia_id = emergencia_id
        self.motivo = motivo
        self.estado_inicial = estado_inicial
        self.fecha = fecha
        self.mascota_id = mascota_id  # P3: mascota 0..1

    @classmethod
    def identificar(cls, emergencia_id: str, motivo: str, estado_inicial: str,
                    fecha: datetime, mascota_id: Optional[str] = None) -> "Emergencia":
        """Sin parámetro de cita: la ausencia de cita ES la regla R-06."""
        if not motivo:
            raise InformacionIncompleta("la emergencia requiere un motivo")
        e = cls(emergencia_id, motivo, estado_inicial, fecha, mascota_id)
        e.registrar_evento(EmergenciaIdentificada(emergencia_id))
        return e
