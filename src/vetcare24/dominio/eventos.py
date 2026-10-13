"""Eventos de dominio (hechos ya ocurridos) y la base común de las raíces.

P6: los agregados solo REGISTRAN sus eventos; no se modela despacho ni consumidores.
"""
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class EventoDeDominio:
    pass


@dataclass(frozen=True)
class CitaAgendada(EventoDeDominio):
    cita_id: str
    mascota_id: str


@dataclass(frozen=True)
class NotaClinicaRegistrada(EventoDeDominio):
    nota_id: str
    mascota_id: str
    autor: str


@dataclass(frozen=True)
class VacunacionRegistrada(EventoDeDominio):
    vacunacion_id: str
    mascota_id: str
    vacuna: str


@dataclass(frozen=True)
class HospitalizacionIniciada(EventoDeDominio):
    hospitalizacion_id: str
    mascota_id: str


@dataclass(frozen=True)
class EmergenciaIdentificada(EventoDeDominio):
    emergencia_id: str


class RaizDeAgregado:
    """Las raíces registran eventos; la aplicación los recoge tras confirmar."""

    def __init__(self) -> None:
        self._eventos: List[EventoDeDominio] = []

    def registrar_evento(self, evento: EventoDeDominio) -> None:
        self._eventos.append(evento)

    def extraer_eventos(self) -> tuple:
        eventos = tuple(self._eventos)
        self._eventos = []
        return eventos
