"""Agregado ExpedienteClinico (raíz) con NotaClinica (entidad)."""
from dataclasses import dataclass
from datetime import datetime
from typing import List

from vetcare24.dominio.errores import InformacionIncompleta
from vetcare24.dominio.eventos import NotaClinicaRegistrada, RaizDeAgregado


@dataclass(frozen=True)
class NotaClinica:
    nota_id: str
    autor: str  # VeterinarioId (ADR-04)
    fecha: datetime
    anamnesis: str
    examen_fisico: str
    diagnostico: str


class ExpedienteClinico(RaizDeAgregado):
    """Un expediente por mascota (R-10). Las notas las registra un Veterinario
    (NB-12, R-02). Recepción no modifica notas (R-03): por diseño, el agregado
    NO ofrece ninguna operación para modificar o eliminar notas."""

    def __init__(self, expediente_id: str, mascota_id: str):
        super().__init__()
        self.expediente_id = expediente_id
        self.mascota_id = mascota_id
        self._notas: List[NotaClinica] = []

    @property
    def notas(self) -> tuple:
        return tuple(self._notas)

    def registrar_nota_clinica(self, autor: str, anamnesis: str, examen_fisico: str,
                               diagnostico: str, fecha: datetime) -> NotaClinica:
        if not autor:
            raise InformacionIncompleta("la nota clínica requiere un veterinario como autor")
        nota = NotaClinica(f"NC-{self.mascota_id}-{len(self._notas) + 1:03d}",
                           autor, fecha, anamnesis, examen_fisico, diagnostico)
        self._notas.append(nota)
        self.registrar_evento(NotaClinicaRegistrada(nota.nota_id, self.mascota_id, autor))
        return nota
