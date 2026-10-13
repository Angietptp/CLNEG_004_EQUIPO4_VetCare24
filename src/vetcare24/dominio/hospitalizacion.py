"""Agregado Hospitalizacion (raíz). Estados, evolución y egreso quedan fuera (HZ-10)."""
from datetime import datetime

from vetcare24.dominio.errores import InformacionIncompleta
from vetcare24.dominio.eventos import HospitalizacionIniciada, RaizDeAgregado


class Hospitalizacion(RaizDeAgregado):
    def __init__(self, hospitalizacion_id: str, mascota_id: str, motivo: str,
                 fecha_ingreso: datetime):
        super().__init__()
        self.hospitalizacion_id = hospitalizacion_id
        self.mascota_id = mascota_id
        self.motivo = motivo
        self.fecha_ingreso = fecha_ingreso
        self.seguimiento_continuo = False

    @classmethod
    def iniciar(cls, hospitalizacion_id: str, mascota_id: str, motivo: str,
                fecha_ingreso: datetime) -> "Hospitalizacion":
        if not motivo:
            raise InformacionIncompleta("el ingreso requiere el motivo de hospitalización")
        h = cls(hospitalizacion_id, mascota_id, motivo, fecha_ingreso)
        h.seguimiento_continuo = True  # NB-18, R-08: desde el ingreso
        h.registrar_evento(HospitalizacionIniciada(hospitalizacion_id, mascota_id))
        return h
