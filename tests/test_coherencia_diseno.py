"""Coherencia entre el diseño (diagrama de clases, ADR-01 a ADR-05) y el código.

Cubre: test_arquitectura_dependencias (regla de dependencias entre capas) y
verifica que los componentes del diagrama existan y se realicen en infraestructura."""
import ast
import importlib
import inspect
import os
import pkgutil
import sys
import unittest

import vetcare24
from vetcare24.aplicacion.citas import CitasApplicationService
from vetcare24.aplicacion.consultas import (
    ConsultarCitasProgramadasHandler, ConsultarExpedienteClinicoHandler)
from vetcare24.aplicacion.emergencias import EmergenciasApplicationService
from vetcare24.aplicacion.expediente_clinico import ExpedienteClinicoApplicationService
from vetcare24.aplicacion.hospitalizacion import HospitalizacionApplicationService
from vetcare24.aplicacion.vacunacion import VacunacionApplicationService
from vetcare24.dominio import repositorios as repos_dominio
from vetcare24.infraestructura import repositorios as repos_infra

RAIZ_PAQUETE = os.path.dirname(vetcare24.__file__)


def _importaciones(capa: str):
    """Devuelve {archivo: set(módulos importados)} de una capa, leyendo el AST."""
    resultado = {}
    carpeta = os.path.join(RAIZ_PAQUETE, capa)
    for nombre in os.listdir(carpeta):
        if not nombre.endswith(".py"):
            continue
        with open(os.path.join(carpeta, nombre), encoding="utf-8") as f:
            arbol = ast.parse(f.read())
        mods = set()
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                mods.update(a.name for a in nodo.names)
            elif isinstance(nodo, ast.ImportFrom) and nodo.module:
                mods.add(nodo.module)
        resultado[f"{capa}/{nombre}"] = mods
    return resultado


class TestReglaDeDependenciasEntreCapas(unittest.TestCase):
    def test_arquitectura_dependencias(self):
        """El dominio no depende de aplicación ni infraestructura; la aplicación
        no depende de infraestructura (ADR-01, ADR-02)."""
        for archivo, mods in _importaciones("dominio").items():
            for m in mods:
                self.assertFalse(m.startswith("vetcare24.aplicacion"), f"{archivo} importa {m}")
                self.assertFalse(m.startswith("vetcare24.infraestructura"), f"{archivo} importa {m}")
        for archivo, mods in _importaciones("aplicacion").items():
            for m in mods:
                self.assertFalse(m.startswith("vetcare24.infraestructura"), f"{archivo} importa {m}")

    def test_dominio_solo_usa_biblioteca_estandar(self):
        """El dominio queda libre de frameworks y de tecnología de persistencia."""
        permitidos = set(sys.stdlib_module_names)
        for archivo, mods in _importaciones("dominio").items():
            for m in mods:
                raiz = m.split(".")[0]
                self.assertTrue(raiz in permitidos or raiz == "vetcare24",
                                f"{archivo} depende de {m}")


class TestComponentesDelDiagramaDeClases(unittest.TestCase):
    COMPONENTES = {
        "vetcare24.dominio.cita": ["Cita"],
        "vetcare24.dominio.valores": ["PeriodoDeCita", "ServicioSolicitado", "DosisIndicada",
                                       "DatosDeContacto"],
        "vetcare24.dominio.servicio_de_programacion_de_citas": ["ServicioDeProgramacionDeCitas"],
        "vetcare24.dominio.expediente_clinico": ["ExpedienteClinico", "NotaClinica"],
        "vetcare24.dominio.vacunacion": ["Vacunacion", "EsquemaDeVacunacion", "ProximaAplicacion",
                                          "ServicioDeSeguimientoDeVacunacion"],
        "vetcare24.dominio.hospitalizacion": ["Hospitalizacion"],
        "vetcare24.dominio.emergencia": ["Emergencia"],
        "vetcare24.dominio.mascota": ["Propietario", "Mascota", "Veterinario"],
        "vetcare24.dominio.eventos": ["CitaAgendada", "NotaClinicaRegistrada", "VacunacionRegistrada",
                                       "HospitalizacionIniciada", "EmergenciaIdentificada"],
        "vetcare24.dominio.errores": ["OperacionNoAutorizada", "MascotaNoRegistrada",
                                       "HorarioNoDisponible", "ExpedienteNoEncontrado",
                                       "EsquemaNoValidado"],
        "vetcare24.aplicacion.puertos": ["UnitOfWork", "ControlDeAcceso", "NotificadorDeVeterinario",
                                          "LecturaDeAgenda", "LecturaDeExpedientes"],
        "vetcare24.aplicacion.vistas": ["CitaProgramadaVista", "ExpedienteClinicoVista",
                                         "NotaClinicaVista"],
        "vetcare24.infraestructura.unit_of_work": ["UnitOfWorkImpl"],
        "vetcare24.infraestructura.control_de_acceso": ["ControlDeAccesoPorRol"],
        "vetcare24.infraestructura.lecturas": ["LecturaDeAgendaImpl", "LecturaDeExpedientesImpl"],
    }

    def test_componentes_del_diagrama_existen(self):
        for modulo, nombres in self.COMPONENTES.items():
            mod = importlib.import_module(modulo)
            for nombre in nombres:
                self.assertTrue(hasattr(mod, nombre), f"falta {nombre} en {modulo}")

    def test_cada_repository_tiene_su_implementacion(self):
        interfaces = [c for _, c in inspect.getmembers(repos_dominio, inspect.isclass)
                      if c.__module__ == repos_dominio.__name__]
        self.assertEqual(len(interfaces), 7)
        for interfaz in interfaces:
            impl = getattr(repos_infra, interfaz.__name__ + "Impl", None)
            self.assertIsNotNone(impl, f"falta {interfaz.__name__}Impl")
            self.assertTrue(issubclass(impl, interfaz))
            self.assertFalse(inspect.isabstract(impl), f"{impl.__name__} deja métodos abstractos")

    def test_servicios_dependen_de_interfaces_no_de_implementaciones(self):
        servicios = [CitasApplicationService, ExpedienteClinicoApplicationService,
                     VacunacionApplicationService, HospitalizacionApplicationService,
                     EmergenciasApplicationService, ConsultarCitasProgramadasHandler,
                     ConsultarExpedienteClinicoHandler]
        for servicio in servicios:
            for nombre, param in inspect.signature(servicio.__init__).parameters.items():
                anotacion = param.annotation
                if inspect.isclass(anotacion) and anotacion.__module__.startswith("vetcare24."):
                    self.assertFalse(
                        anotacion.__module__.startswith("vetcare24.infraestructura"),
                        f"{servicio.__name__}.{nombre} depende de infraestructura")

    def test_los_servicios_son_uno_por_caso_de_uso(self):
        metodos = {
            CitasApplicationService: "solicitar_cita",
            ExpedienteClinicoApplicationService: "generar_nota_clinica",
            VacunacionApplicationService: "registrar_vacunacion",
            HospitalizacionApplicationService: "registrar_hospitalizacion",
            EmergenciasApplicationService: "atender_emergencia",
        }
        for clase, metodo in metodos.items():
            self.assertTrue(callable(getattr(clase, metodo)))

    def test_todos_los_modulos_del_paquete_se_importan(self):
        for info in pkgutil.walk_packages(vetcare24.__path__, "vetcare24."):
            importlib.import_module(info.name)


if __name__ == "__main__":
    unittest.main()
