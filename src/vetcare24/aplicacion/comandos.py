"""Commands (CQRS básico): cada uno expresa la intención de una User Story."""
from dataclasses import dataclass
from datetime import date, time
from typing import Optional

from vetcare24.aplicacion.seguridad import Usuario
from vetcare24.dominio.valores import ServicioSolicitado


@dataclass(frozen=True)
class SolicitarCita:  # US04
    usuario: Usuario
    mascota_id: str
    servicio: ServicioSolicitado
    fecha: date
    hora_inicio: time


@dataclass(frozen=True)
class GenerarNotaClinica:  # US12
    usuario: Usuario
    mascota_id: str
    anamnesis: str
    examen_fisico: str
    diagnostico: str


@dataclass(frozen=True)
class RegistrarVacunacion:  # US15
    usuario: Usuario
    mascota_id: str
    vacuna: str
    fecha_aplicacion: date
    dosis: str


@dataclass(frozen=True)
class RegistrarHospitalizacion:  # US17
    usuario: Usuario
    mascota_id: str
    motivo: str


@dataclass(frozen=True)
class AtenderEmergencia:  # US20 (sin identificador de cita)
    usuario: Usuario
    motivo: str
    estado_inicial: str
    mascota_id: Optional[str] = None


@dataclass(frozen=True)
class ConsultarCitasProgramadas:  # US07
    usuario: Usuario
    fecha: date


@dataclass(frozen=True)
class ConsultarExpedienteClinico:  # US11
    usuario: Usuario
    mascota_id: str
