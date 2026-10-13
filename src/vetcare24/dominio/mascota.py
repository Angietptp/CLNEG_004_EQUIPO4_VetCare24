"""Propietario y Mascota. Mascota ancla a los demás agregados por identidad (ADR-02)."""
from dataclasses import dataclass

from vetcare24.dominio.valores import DatosDeContacto


@dataclass
class Propietario:
    """D-03: se conserva en el modelo, pero no interviene en CU-01 a CU-05."""

    propietario_id: str
    nombre: str
    contacto: DatosDeContacto


@dataclass
class Mascota:
    mascota_id: str
    nombre: str
    especie: str
    propietario_id: str
    raza: str = ""


@dataclass(frozen=True)
class Veterinario:
    veterinario_id: str
    nombre: str
    cedula_profesional: str = ""
