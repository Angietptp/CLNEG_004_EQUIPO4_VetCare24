"""Resultados de los comandos. Llevan los eventos que registró el agregado (P6)."""
from dataclasses import dataclass, field
from typing import Optional, Tuple

from vetcare24.dominio.valores import PeriodoDeCita, ServicioSolicitado
from vetcare24.dominio.vacunacion import ProximaAplicacion


@dataclass(frozen=True)
class ResultadoDeSolicitudDeCita:
    """No dice 'cita confirmada': el momento de confirmación no está definido."""
    cita_id: str
    servicio: ServicioSolicitado
    periodo: PeriodoDeCita
    eventos: Tuple = field(default_factory=tuple)


@dataclass(frozen=True)
class ResultadoDeNotaClinica:
    nota_id: str
    eventos: Tuple = field(default_factory=tuple)


@dataclass(frozen=True)
class ResultadoDeVacunacion:
    vacunacion_id: str
    proxima_aplicacion: Optional[ProximaAplicacion]
    seguimiento_pendiente: bool  # esquema no validado: NO es un error (R-12)
    eventos: Tuple = field(default_factory=tuple)


@dataclass(frozen=True)
class ResultadoDeHospitalizacion:
    hospitalizacion_id: str
    seguimiento_iniciado: bool
    eventos: Tuple = field(default_factory=tuple)


@dataclass(frozen=True)
class ResultadoDeEmergencia:
    emergencia_id: str
    notificado: bool  # False = pendiente de notificar
    eventos: Tuple = field(default_factory=tuple)
