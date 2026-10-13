"""Usuario, roles y operaciones protegidas. La autenticación queda fuera (ADR-04)."""
from dataclasses import dataclass
from enum import Enum


class Rol(Enum):
    PROPIETARIO = "Propietario"
    RECEPCION = "Recepción"
    VETERINARIO = "Veterinario"
    PERSONAL_CLINICO = "Personal clínico"


class Operacion(Enum):
    SOLICITAR_CITA = "solicitar_cita"
    GENERAR_NOTA_CLINICA = "generar_nota_clinica"
    REGISTRAR_VACUNACION = "registrar_vacunacion"
    REGISTRAR_HOSPITALIZACION = "registrar_hospitalizacion"
    ATENDER_EMERGENCIA = "atender_emergencia"
    CONSULTAR_EXPEDIENTE = "consultar_expediente"
    CONSULTAR_CITAS = "consultar_citas"


@dataclass(frozen=True)
class Usuario:
    """Supuesto (ADR-04): el id de un usuario Veterinario es su VeterinarioId."""

    usuario_id: str
    rol: Rol
