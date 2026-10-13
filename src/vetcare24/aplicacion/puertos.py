"""Interfaces (puertos) que la aplicación necesita; las realiza infraestructura."""
from abc import ABC, abstractmethod
from datetime import date
from typing import List

from vetcare24.aplicacion.seguridad import Operacion, Usuario
from vetcare24.aplicacion.vistas import CitaProgramadaVista, ExpedienteClinicoVista


class UnitOfWork(ABC):
    """Una transacción por caso de uso (ADR-02)."""

    @abstractmethod
    def iniciar(self) -> None: ...

    @abstractmethod
    def confirmar(self) -> None: ...

    @abstractmethod
    def revertir(self) -> None: ...


class ControlDeAcceso(ABC):
    @abstractmethod
    def verificar(self, usuario: Usuario, operacion: Operacion) -> None:
        """Lanza OperacionNoAutorizada. Es el primer paso de cada caso de uso."""


class NotificadorDeVeterinario(ABC):
    """Interfaz de salida de CU-05. El canal concreto no está definido."""

    @abstractmethod
    def notificar(self, emergencia_id: str, mensaje: str) -> bool:
        """True si se notificó; False si queda pendiente de notificar."""


class LecturaDeAgenda(ABC):
    @abstractmethod
    def citas_programadas(self, fecha: date) -> List[CitaProgramadaVista]: ...


class LecturaDeExpedientes(ABC):
    @abstractmethod
    def expediente_de(self, mascota_id: str) -> ExpedienteClinicoVista: ...
