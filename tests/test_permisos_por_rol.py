"""Permisos por rol (R-01, R-02, R-03, R-04, R-09, R-14; ADR-04).
P7: la matriz de permisos es provisional y debe validarse con el negocio."""
import unittest

from vetcare24.aplicacion.comandos import (
    GenerarNotaClinica, RegistrarHospitalizacion, RegistrarVacunacion, SolicitarCita)
from vetcare24.aplicacion.seguridad import Operacion
from vetcare24.dominio.errores import OperacionNoAutorizada

from tests.entorno import CONSULTA, FECHA, NUEVE, Entorno
from datetime import date


class TestPermisosPorRol(unittest.TestCase):
    def setUp(self):
        self.e = Entorno()

    def test_recepcion_puede_solicitar_cita(self):
        """R-01: Recepción administra las citas."""
        r = self.e.servicio_citas.solicitar_cita(
            SolicitarCita(self.e.recepcion, "M-001", CONSULTA, FECHA, NUEVE))
        self.assertTrue(r.cita_id.startswith("CITA-"))

    def test_recepcion_no_registra_nota_clinica(self):
        """R-02, R-03: solo el Veterinario registra información clínica."""
        antes = self.e.huella()
        with self.assertRaises(OperacionNoAutorizada) as ctx:
            self.e.servicio_notas.generar_nota_clinica(
                GenerarNotaClinica(self.e.recepcion, "M-001", "a", "e", "d"))
        self.assertEqual(ctx.exception.mensaje, "su rol no permite esta operación")
        self.assertEqual(self.e.huella(), antes)  # sin cambios
        self.assertEqual(self.e.uow.estado, "sin_iniciar")  # sin transacción

    def test_rol_no_permitido_rechaza_hospitalizacion(self):
        """R-04, R-09: Recepción y Propietario no inician hospitalizaciones."""
        for usuario in (self.e.recepcion, self.e.propietario):
            with self.assertRaises(OperacionNoAutorizada):
                self.e.servicio_hospitalizacion.registrar_hospitalizacion(
                    RegistrarHospitalizacion(usuario, "M-001", "Deshidratación"))
        self.assertEqual(self.e.almacen.hospitalizaciones, {})

    def test_hospitalizacion_la_inician_veterinario_o_personal_clinico(self):
        for usuario in (self.e.veterinario, self.e.personal_clinico):
            r = self.e.servicio_hospitalizacion.registrar_hospitalizacion(
                RegistrarHospitalizacion(usuario, "M-001", "Deshidratación"))
            self.assertTrue(r.seguimiento_iniciado)

    def test_solo_el_veterinario_registra_vacunaciones(self):
        with self.assertRaises(OperacionNoAutorizada):
            self.e.servicio_vacunacion.registrar_vacunacion(
                RegistrarVacunacion(self.e.recepcion, "M-001", "Rabia", date(2026, 10, 13), "1 ml"))

    def test_permiso_verificado_antes_de_transaccion(self):
        """ADR-04: verificar() es el primer paso; sin permiso no se abre transacción."""
        with self.assertRaises(OperacionNoAutorizada):
            self.e.servicio_notas.generar_nota_clinica(
                GenerarNotaClinica(self.e.propietario, "M-001", "a", "e", "d"))
        self.assertEqual(self.e.bitacora, ["acceso.verificar"])

    def test_toda_operacion_tiene_reglas_de_acceso_definidas(self):
        from vetcare24.infraestructura.control_de_acceso import PERMISOS
        self.assertEqual(set(PERMISOS), set(Operacion))


if __name__ == "__main__":
    unittest.main()
