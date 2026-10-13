"""Almacenamiento en memoria que sustituye a la base de datos.
La tecnología real no está definida en la Unidad 2 (queda por decidir)."""
import copy


class AlmacenEnMemoria:
    def __init__(self):
        self.mascotas = {}
        self.citas = {}
        self.expedientes = {}
        self.vacunaciones = {}
        self.esquemas = {}
        self.hospitalizaciones = {}
        self.emergencias = {}
        self.contadores = {}

    def _colecciones(self):
        return {k: v for k, v in vars(self).items()}

    def instantanea(self):
        return copy.deepcopy(self._colecciones())

    def restaurar(self, instantanea) -> None:
        for nombre, contenido in instantanea.items():
            actual = getattr(self, nombre)
            actual.clear()
            actual.update(contenido)

    def siguiente(self, prefijo: str) -> str:
        self.contadores[prefijo] = self.contadores.get(prefijo, 0) + 1
        return f"{prefijo}-{self.contadores[prefijo]:03d}"
