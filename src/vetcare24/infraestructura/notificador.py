"""Notificador en memoria. El canal real (SMS, correo, etc.) no está definido."""
from vetcare24.aplicacion.puertos import NotificadorDeVeterinario


class NotificadorDeVeterinarioEnMemoria(NotificadorDeVeterinario):
    def __init__(self, disponible: bool = True):
        self.disponible = disponible
        self.enviados = []

    def notificar(self, emergencia_id: str, mensaje: str) -> bool:
        if not self.disponible:
            return False  # queda pendiente de notificar
        self.enviados.append((emergencia_id, mensaje))
        return True
