"""Lado Query de CQRS (ADR-03): las consultas no modifican estado y devuelven View Models."""
import unittest
from datetime import time

from vetcare24.aplicacion.comandos import (
    ConsultarCitasProgramadas, ConsultarExpedienteClinico, GenerarNotaClinica, SolicitarCita)
from vetcare24.aplicacion.vistas import (
    CitaProgramadaVista, ExpedienteClinicoVista, NotaClinicaVista)
from vetcare24.dominio.cita import Cita
from vetcare24.dominio.errores import OperacionNoAutorizada

from tests.entorno import CONSULTA, FECHA, NUEVE, Entorno


class TestConsultarCitasProgramadas(unittest.TestCase):
    def setUp(self):
        self.e = Entorno()
        self.e.servicio_citas.solicitar_cita(
            SolicitarCita(self.e.recepcion, "M-001", CONSULTA, FECHA, time(10, 0)))
        self.e.servicio_citas.solicitar_cita(
            SolicitarCita(self.e.recepcion, "M-001", CONSULTA, FECHA, NUEVE))
        self.e.bitacora.clear()

    def test_consultar_citas_no_modifica_estado(self):
        """US07: la consulta no escribe, no abre transacción y no devuelve agregados."""
        antes = self.e.huella()
        vistas = self.e.consulta_citas.manejar(ConsultarCitasProgramadas(self.e.recepcion, FECHA))
        self.assertEqual(self.e.huella(), antes)
        self.assertEqual(self.e.bitacora, ["acceso.verificar"])  # sin uow
        self.assertTrue(all(isinstance(v, CitaProgramadaVista) for v in vistas))
        self.assertFalse(any(isinstance(v, Cita) for v in vistas))

    def test_la_vista_une_la_cita_con_el_nombre_de_la_mascota_ordenada_por_hora(self):
        vistas = self.e.consulta_citas.manejar(ConsultarCitasProgramadas(self.e.recepcion, FECHA))
        self.assertEqual([v.inicio for v in vistas], [time(9, 0), time(10, 0)])
        self.assertEqual(vistas[0].mascota_nombre, "Firulais")
        self.assertEqual(vistas[0].servicio, "Consulta general")

    def test_el_handler_de_consultas_no_depende_de_repositorios_ni_unit_of_work(self):
        import inspect
        from vetcare24.aplicacion.consultas import ConsultarCitasProgramadasHandler
        from vetcare24.aplicacion.puertos import UnitOfWork
        from vetcare24.dominio import repositorios
        tipos = {p.annotation for p in
                 inspect.signature(ConsultarCitasProgramadasHandler.__init__).parameters.values()}
        self.assertNotIn(UnitOfWork, tipos)
        for nombre in dir(repositorios):
            if nombre.endswith("Repository"):
                self.assertNotIn(getattr(repositorios, nombre), tipos)


class TestConsultarExpedienteClinico(unittest.TestCase):
    def setUp(self):
        self.e = Entorno()
        self.e.servicio_notas.generar_nota_clinica(
            GenerarNotaClinica(self.e.veterinario, "M-001", "anamnesis", "examen", "dx"))

    def test_consulta_expediente_solo_autorizados(self):
        """NB-11, R-14: la información clínica es solo para personal autorizado."""
        with self.assertRaises(OperacionNoAutorizada):
            self.e.consulta_expediente.manejar(
                ConsultarExpedienteClinico(self.e.recepcion, "M-001"))
        with self.assertRaises(OperacionNoAutorizada):
            self.e.consulta_expediente.manejar(
                ConsultarExpedienteClinico(self.e.propietario, "M-001"))
        for autorizado in (self.e.veterinario, self.e.personal_clinico):
            vista = self.e.consulta_expediente.manejar(
                ConsultarExpedienteClinico(autorizado, "M-001"))
            self.assertIsInstance(vista, ExpedienteClinicoVista)

    def test_la_vista_expone_autor_y_fecha_sin_reutilizar_el_agregado(self):
        vista = self.e.consulta_expediente.manejar(
            ConsultarExpedienteClinico(self.e.veterinario, "M-001"))
        self.assertEqual(vista.mascota_nombre, "Firulais")
        self.assertIsInstance(vista.notas[0], NotaClinicaVista)
        self.assertEqual(vista.notas[0].autor, "VET-01")
        self.assertEqual(vista.notas[0].diagnostico, "dx")

    def test_consultar_el_expediente_no_modifica_el_estado(self):
        antes = self.e.huella()
        self.e.consulta_expediente.manejar(ConsultarExpedienteClinico(self.e.veterinario, "M-001"))
        self.assertEqual(self.e.huella(), antes)


if __name__ == "__main__":
    unittest.main()
