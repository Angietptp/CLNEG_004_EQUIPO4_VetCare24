"""UnitOfWorkImpl: confirmar() conserva los cambios; revertir() los deshace."""
from vetcare24.aplicacion.puertos import UnitOfWork
from vetcare24.infraestructura.almacen import AlmacenEnMemoria


class UnitOfWorkImpl(UnitOfWork):
    SIN_INICIAR, ACTIVA, CONFIRMADA, REVERTIDA = "sin_iniciar", "activa", "confirmada", "revertida"

    def __init__(self, almacen: AlmacenEnMemoria):
        self._almacen = almacen
        self._instantanea = None
        self.estado = self.SIN_INICIAR

    def iniciar(self) -> None:
        self._instantanea = self._almacen.instantanea()
        self.estado = self.ACTIVA

    def confirmar(self) -> None:
        self._instantanea = None
        self.estado = self.CONFIRMADA

    def revertir(self) -> None:
        if self._instantanea is not None:
            self._almacen.restaurar(self._instantanea)
        self._instantanea = None
        self.estado = self.REVERTIDA
