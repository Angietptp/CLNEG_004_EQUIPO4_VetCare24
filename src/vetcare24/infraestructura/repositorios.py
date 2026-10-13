"""Implementaciones de las interfaces de Repository del dominio."""
from datetime import date
from typing import List, Optional

from vetcare24.dominio.errores import ExpedienteNoEncontrado, MascotaNoRegistrada
from vetcare24.dominio.repositorios import (
    CitaRepository, EmergenciaRepository, EsquemaDeVacunacionRepository,
    ExpedienteClinicoRepository, HospitalizacionRepository, MascotaRepository,
    VacunacionRepository)
from vetcare24.infraestructura.almacen import AlmacenEnMemoria


class MascotaRepositoryImpl(MascotaRepository):
    def __init__(self, almacen: AlmacenEnMemoria):
        self._a = almacen

    def obtener(self, mascota_id):
        try:
            return self._a.mascotas[mascota_id]
        except KeyError:
            raise MascotaNoRegistrada(mascota_id)


class CitaRepositoryImpl(CitaRepository):
    def __init__(self, almacen: AlmacenEnMemoria):
        self._a = almacen

    def siguiente_id(self) -> str:
        return self._a.siguiente("CITA")

    def buscar_por_fecha(self, fecha: date) -> List:
        return [c for c in self._a.citas.values() if c.periodo.fecha == fecha]

    def agregar(self, cita) -> None:
        self._a.citas[cita.cita_id] = cita


class ExpedienteClinicoRepositoryImpl(ExpedienteClinicoRepository):
    def __init__(self, almacen: AlmacenEnMemoria):
        self._a = almacen

    def obtener_por_mascota(self, mascota_id):
        try:
            return self._a.expedientes[mascota_id]
        except KeyError:
            raise ExpedienteNoEncontrado(mascota_id)

    def guardar(self, expediente) -> None:
        self._a.expedientes[expediente.mascota_id] = expediente


class VacunacionRepositoryImpl(VacunacionRepository):
    def __init__(self, almacen: AlmacenEnMemoria):
        self._a = almacen

    def siguiente_id(self) -> str:
        return self._a.siguiente("VAC")

    def historial_de(self, mascota_id) -> List:
        return [v for v in self._a.vacunaciones.values() if v.mascota_id == mascota_id]

    def agregar(self, vacunacion) -> None:
        self._a.vacunaciones[vacunacion.vacunacion_id] = vacunacion


class EsquemaDeVacunacionRepositoryImpl(EsquemaDeVacunacionRepository):
    """Solo lectura: catálogo de referencia (ADR-05)."""

    def __init__(self, almacen: AlmacenEnMemoria):
        self._a = almacen

    def obtener_por_vacuna(self, vacuna) -> Optional[object]:
        return self._a.esquemas.get(vacuna)


class HospitalizacionRepositoryImpl(HospitalizacionRepository):
    def __init__(self, almacen: AlmacenEnMemoria):
        self._a = almacen

    def siguiente_id(self) -> str:
        return self._a.siguiente("HOSP")

    def agregar(self, hospitalizacion) -> None:
        self._a.hospitalizaciones[hospitalizacion.hospitalizacion_id] = hospitalizacion


class EmergenciaRepositoryImpl(EmergenciaRepository):
    def __init__(self, almacen: AlmacenEnMemoria):
        self._a = almacen

    def siguiente_id(self) -> str:
        return self._a.siguiente("EMER")

    def agregar(self, emergencia) -> None:
        self._a.emergencias[emergencia.emergencia_id] = emergencia
