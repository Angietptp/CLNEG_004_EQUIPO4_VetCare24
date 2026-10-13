"""Casos de uso CU-01 a CU-05: flujos normales y flujos con rechazo."""
import unittest
from datetime import date, time

from vetcare24.aplicacion.comandos import (
    AtenderEmergencia, GenerarNotaClinica, RegistrarHospitalizacion, RegistrarVacunacion,
    SolicitarCita)
from vetcare24.dominio.errores import (
    ExpedienteNoEncontrado, HorarioNoDisponible, InformacionIncompleta, MascotaNoRegistrada)
from vetcare24.dominio.eventos import (
    CitaAgendada, EmergenciaIdentificada, HospitalizacionIniciada, NotaClinicaRegistrada,
    VacunacionRegistrada)

from tests.entorno import CONSULTA, FECHA, NUEVE, Entorno


class TestCU01SolicitarCita(unittest.TestCase):
    def setUp(self):
        self.e = Entorno()

    def test_flujo_normal_crea_la_cita_y_registra_el_evento(self):
        r = self.e.servicio_citas.solicitar_cita(
            SolicitarCita(self.e.recepcion, "M-001", CONSULTA, FECHA, NUEVE))
        self.assertEqual(r.periodo.termino, time(9, 30))
        self.assertEqual(r.eventos, (CitaAgendada(r.cita_id, "M-001"),))
        self.assertIn(r.cita_id, self.e.almacen.citas)
        self.assertEqual(self.e.uow.estado, "confirmada")

    def test_horario_traslapado_revierte_y_no_crea_la_cita(self):
        self.e.servicio_citas.solicitar_cita(
            SolicitarCita(self.e.recepcion, "M-001", CONSULTA, FECHA, NUEVE))
        with self.assertRaises(HorarioNoDisponible):
            self.e.servicio_citas.solicitar_cita(
                SolicitarCita(self.e.recepcion, "M-001", CONSULTA, FECHA, time(9, 15)))
        self.assertEqual(len(self.e.almacen.citas), 1)
        self.assertEqual(self.e.uow.estado, "revertida")

    def test_mascota_no_registrada_revierte(self):
        """R-10: no se cita a una mascota que no está registrada."""
        antes = self.e.huella()
        with self.assertRaises(MascotaNoRegistrada):
            self.e.servicio_citas.solicitar_cita(
                SolicitarCita(self.e.recepcion, "M-999", CONSULTA, FECHA, NUEVE))
        self.assertEqual(self.e.huella(), antes)
        self.assertEqual(self.e.uow.estado, "revertida")
        self.assertEqual(self.e.bitacora, ["acceso.verificar", "uow.iniciar", "uow.revertir"])


class TestCU02GenerarNotaClinica(unittest.TestCase):
    def setUp(self):
        self.e = Entorno()

    def test_flujo_normal_agrega_la_nota_con_el_veterinario_como_autor(self):
        r = self.e.servicio_notas.generar_nota_clinica(
            GenerarNotaClinica(self.e.veterinario, "M-001", "anamnesis", "examen", "diagnóstico"))
        expediente = self.e.almacen.expedientes["M-001"]
        self.assertEqual(expediente.notas[0].autor, "VET-01")
        self.assertEqual(r.eventos, (NotaClinicaRegistrada(r.nota_id, "M-001", "VET-01"),))

    def test_expediente_no_encontrado_revierte(self):
        del self.e.almacen.expedientes["M-001"]
        with self.assertRaises(ExpedienteNoEncontrado):
            self.e.servicio_notas.generar_nota_clinica(
                GenerarNotaClinica(self.e.veterinario, "M-001", "a", "e", "d"))
        self.assertEqual(self.e.uow.estado, "revertida")


class TestCU03RegistrarVacunacion(unittest.TestCase):
    def setUp(self):
        self.e = Entorno()

    def _registrar(self, vacuna, dia):
        return self.e.servicio_vacunacion.registrar_vacunacion(
            RegistrarVacunacion(self.e.veterinario, "M-001", vacuna, dia, "1 ml"))

    def test_historial_conserva_aplicaciones_previas(self):
        """NB-14, R-11: registrar una vacuna nueva no borra las anteriores."""
        self._registrar("Rabia", date(2025, 10, 1))
        self._registrar("Rabia", date(2026, 10, 1))
        historial = self.e.vacunaciones.historial_de("M-001")
        self.assertEqual([v.dosis.fecha for v in historial],
                         [date(2025, 10, 1), date(2026, 10, 1)])

    def test_con_esquema_validado_devuelve_la_proxima_aplicacion(self):
        r = self._registrar("Rabia", date(2026, 10, 1))
        self.assertFalse(r.seguimiento_pendiente)
        self.assertEqual(r.proxima_aplicacion.fecha, date(2027, 10, 1))
        self.assertEqual(r.eventos, (VacunacionRegistrada(r.vacunacion_id, "M-001", "Rabia"),))

    def test_esquema_no_validado_confirma_el_registro_y_deja_seguimiento_pendiente(self):
        """ADR-05: EsquemaNoValidado NO es un error ni revierte el registro."""
        r = self._registrar("Parvovirus", date(2026, 10, 1))
        self.assertTrue(r.seguimiento_pendiente)
        self.assertIsNone(r.proxima_aplicacion)
        self.assertIn(r.vacunacion_id, self.e.almacen.vacunaciones)
        self.assertEqual(self.e.uow.estado, "confirmada")

    def test_vacuna_sin_esquema_definido_tambien_queda_registrada(self):
        r = self._registrar("Moquillo", date(2026, 10, 1))
        self.assertTrue(r.seguimiento_pendiente)
        self.assertIn(r.vacunacion_id, self.e.almacen.vacunaciones)

    def test_mascota_no_registrada_revierte(self):
        with self.assertRaises(MascotaNoRegistrada):
            self.e.servicio_vacunacion.registrar_vacunacion(
                RegistrarVacunacion(self.e.veterinario, "M-999", "Rabia", date(2026, 10, 1), "1 ml"))
        self.assertEqual(self.e.almacen.vacunaciones, {})


class TestCU04RegistrarHospitalizacion(unittest.TestCase):
    def setUp(self):
        self.e = Entorno()

    def test_registrar_hospitalizacion_inicia_seguimiento(self):
        """NB-18, R-08: el seguimiento continuo comienza desde el ingreso."""
        r = self.e.servicio_hospitalizacion.registrar_hospitalizacion(
            RegistrarHospitalizacion(self.e.veterinario, "M-001", "Deshidratación severa"))
        guardada = self.e.almacen.hospitalizaciones[r.hospitalizacion_id]
        self.assertTrue(guardada.seguimiento_continuo)
        self.assertTrue(r.seguimiento_iniciado)
        self.assertEqual(r.eventos, (HospitalizacionIniciada(r.hospitalizacion_id, "M-001"),))

    def test_ingreso_sin_motivo_se_rechaza_y_revierte(self):
        with self.assertRaises(InformacionIncompleta):
            self.e.servicio_hospitalizacion.registrar_hospitalizacion(
                RegistrarHospitalizacion(self.e.veterinario, "M-001", ""))
        self.assertEqual(self.e.almacen.hospitalizaciones, {})
        self.assertEqual(self.e.uow.estado, "revertida")

    def test_mascota_no_registrada_revierte(self):
        with self.assertRaises(MascotaNoRegistrada):
            self.e.servicio_hospitalizacion.registrar_hospitalizacion(
                RegistrarHospitalizacion(self.e.veterinario, "M-999", "Motivo"))
        self.assertEqual(self.e.almacen.hospitalizaciones, {})


class TestCU05AtenderEmergencia(unittest.TestCase):
    def setUp(self):
        self.e = Entorno()

    def test_emergencia_sin_cita_se_registra(self):
        """NB-19, R-06: se atiende sin cita previa y sin mascota registrada (P3)."""
        r = self.e.servicio_emergencias.atender_emergencia(
            AtenderEmergencia(self.e.recepcion, "Atropellamiento", "Crítico"))
        self.assertIn(r.emergencia_id, self.e.almacen.emergencias)
        self.assertEqual(self.e.almacen.citas, {})
        self.assertEqual(r.eventos, (EmergenciaIdentificada(r.emergencia_id),))

    def test_el_servicio_de_emergencias_no_depende_de_citas(self):
        import inspect
        from vetcare24.aplicacion.emergencias import EmergenciasApplicationService
        from vetcare24.dominio.repositorios import CitaRepository
        tipos = [p.annotation for p in
                 inspect.signature(EmergenciasApplicationService.__init__).parameters.values()]
        self.assertNotIn(CitaRepository, tipos)

    def test_emergencia_con_mascota_registrada_la_conserva(self):
        r = self.e.servicio_emergencias.atender_emergencia(
            AtenderEmergencia(self.e.veterinario, "Convulsiones", "Grave", mascota_id="M-001"))
        self.assertEqual(self.e.almacen.emergencias[r.emergencia_id].mascota_id, "M-001")


if __name__ == "__main__":
    unittest.main()
