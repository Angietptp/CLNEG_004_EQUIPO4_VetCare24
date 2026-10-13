"""Adaptadores de lectura (CQRS): arman View Models sin devolver agregados."""
from datetime import date
from typing import List

from vetcare24.aplicacion.puertos import LecturaDeAgenda, LecturaDeExpedientes
from vetcare24.aplicacion.vistas import (
    CitaProgramadaVista, ExpedienteClinicoVista, NotaClinicaVista)
from vetcare24.dominio.errores import ExpedienteNoEncontrado
from vetcare24.infraestructura.almacen import AlmacenEnMemoria


class LecturaDeAgendaImpl(LecturaDeAgenda):
    def __init__(self, almacen: AlmacenEnMemoria):
        self._a = almacen

    def citas_programadas(self, fecha: date) -> List[CitaProgramadaVista]:
        vistas = []
        for c in self._a.citas.values():
            if c.periodo.fecha == fecha:
                m = self._a.mascotas.get(c.mascota_id)
                vistas.append(CitaProgramadaVista(
                    c.cita_id, m.nombre if m else "", c.servicio.tipo,
                    c.periodo.fecha, c.periodo.inicio, c.periodo.termino))
        return sorted(vistas, key=lambda v: v.inicio)


class LecturaDeExpedientesImpl(LecturaDeExpedientes):
    def __init__(self, almacen: AlmacenEnMemoria):
        self._a = almacen

    def expediente_de(self, mascota_id: str) -> ExpedienteClinicoVista:
        e = self._a.expedientes.get(mascota_id)
        if e is None:
            raise ExpedienteNoEncontrado(mascota_id)
        m = self._a.mascotas.get(mascota_id)
        notas = tuple(NotaClinicaVista(n.autor, n.fecha, n.anamnesis, n.examen_fisico,
                                       n.diagnostico) for n in e.notas)
        return ExpedienteClinicoVista(mascota_id, m.nombre if m else "", notas)
