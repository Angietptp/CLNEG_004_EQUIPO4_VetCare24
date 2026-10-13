"""Delimita la transacción de un caso de uso: iniciar, confirmar o revertir."""
from contextlib import contextmanager

from vetcare24.aplicacion.puertos import UnitOfWork


@contextmanager
def transaccion(uow: UnitOfWork):
    uow.iniciar()
    try:
        yield
    except Exception:
        uow.revertir()
        raise
    else:
        uow.confirmar()
