"""Agregado Vacunacion (raíz), esquema de referencia y servicio de seguimiento."""
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, Optional

from vetcare24.dominio.errores import EsquemaNoValidado
from vetcare24.dominio.eventos import RaizDeAgregado, VacunacionRegistrada
from vetcare24.dominio.valores import DosisIndicada


class Vacunacion(RaizDeAgregado):
    """Cada aplicación se conserva en el historial (NB-14, R-11)."""

    def __init__(self, vacunacion_id: str, mascota_id: str, dosis: DosisIndicada):
        super().__init__()
        self.vacunacion_id = vacunacion_id
        self.mascota_id = mascota_id
        self.dosis = dosis

    @classmethod
    def registrar(cls, vacunacion_id: str, mascota_id: str, dosis: DosisIndicada) -> "Vacunacion":
        v = cls(vacunacion_id, mascota_id, dosis)
        v.registrar_evento(VacunacionRegistrada(vacunacion_id, mascota_id, dosis.vacuna))
        return v


@dataclass(frozen=True)
class EsquemaDeVacunacion:
    """Concepto de referencia (ADR-05). Debe estar definido y validado (R-12)."""

    vacuna: str
    intervalo_dias: int
    aplicaciones_requeridas: int
    validado: bool


@dataclass(frozen=True)
class ProximaAplicacion:
    vacuna: str
    fecha: date
    es_refuerzo: bool


class ServicioDeSeguimientoDeVacunacion:
    """Identifica la próxima aplicación o refuerzo a partir del historial y de un
    esquema VALIDADO. Si no está validado, no calcula (R-12).

    Supuesto solo de ejemplo: la fórmula de fechas NO está definida en la
    Unidad 2; aquí se usa última aplicación + intervalo del esquema."""

    def determinar_proxima(self, historial: Iterable[Vacunacion],
                           esquema: Optional[EsquemaDeVacunacion]) -> Optional[ProximaAplicacion]:
        if esquema is None or not esquema.validado:
            raise EsquemaNoValidado()
        aplicadas = sorted((v.dosis.fecha for v in historial
                            if v.dosis.vacuna == esquema.vacuna))
        if len(aplicadas) >= esquema.aplicaciones_requeridas:
            return None  # esquema completo: no hay próxima aplicación
        return ProximaAplicacion(
            esquema.vacuna,
            aplicadas[-1] + timedelta(days=esquema.intervalo_dias),
            es_refuerzo=len(aplicadas) >= 1,
        )
