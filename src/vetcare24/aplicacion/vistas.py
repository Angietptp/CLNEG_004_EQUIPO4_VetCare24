"""View Models de lectura (lado Query); distintos de los agregados de escritura."""
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Tuple


@dataclass(frozen=True)
class CitaProgramadaVista:
    cita_id: str
    mascota_nombre: str
    servicio: str
    fecha: date
    inicio: time
    termino: time


@dataclass(frozen=True)
class NotaClinicaVista:
    autor: str
    fecha_de_registro: datetime
    anamnesis: str
    examen_fisico: str
    diagnostico: str


@dataclass(frozen=True)
class ExpedienteClinicoVista:
    mascota_id: str
    mascota_nombre: str
    notas: Tuple[NotaClinicaVista, ...]
