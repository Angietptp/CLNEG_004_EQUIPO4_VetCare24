"""Interfaces de Repository en términos del dominio (Etapa 5, ADR-02).
Sin SQL ni tecnología: las implementaciones viven en infraestructura."""
from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from vetcare24.dominio.cita import Cita
from vetcare24.dominio.emergencia import Emergencia
from vetcare24.dominio.expediente_clinico import ExpedienteClinico
from vetcare24.dominio.hospitalizacion import Hospitalizacion
from vetcare24.dominio.mascota import Mascota
from vetcare24.dominio.vacunacion import EsquemaDeVacunacion, Vacunacion


class MascotaRepository(ABC):
    @abstractmethod
    def obtener(self, mascota_id: str) -> Mascota:
        """Lanza MascotaNoRegistrada (R-10)."""


class CitaRepository(ABC):
    @abstractmethod
    def siguiente_id(self) -> str: ...

    @abstractmethod
    def buscar_por_fecha(self, fecha: date) -> List[Cita]: ...

    @abstractmethod
    def agregar(self, cita: Cita) -> None: ...


class ExpedienteClinicoRepository(ABC):
    @abstractmethod
    def obtener_por_mascota(self, mascota_id: str) -> ExpedienteClinico:
        """Lanza ExpedienteNoEncontrado."""

    @abstractmethod
    def guardar(self, expediente: ExpedienteClinico) -> None: ...


class VacunacionRepository(ABC):
    @abstractmethod
    def siguiente_id(self) -> str: ...

    @abstractmethod
    def historial_de(self, mascota_id: str) -> List[Vacunacion]: ...

    @abstractmethod
    def agregar(self, vacunacion: Vacunacion) -> None: ...


class EsquemaDeVacunacionRepository(ABC):
    """Solo lectura (ADR-05)."""

    @abstractmethod
    def obtener_por_vacuna(self, vacuna: str) -> Optional[EsquemaDeVacunacion]: ...


class HospitalizacionRepository(ABC):
    @abstractmethod
    def siguiente_id(self) -> str: ...

    @abstractmethod
    def agregar(self, hospitalizacion: Hospitalizacion) -> None: ...


class EmergenciaRepository(ABC):
    @abstractmethod
    def siguiente_id(self) -> str: ...

    @abstractmethod
    def agregar(self, emergencia: Emergencia) -> None: ...
