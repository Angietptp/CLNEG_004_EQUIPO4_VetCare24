"""Reglas de negocio protegidas por el dominio (sin aplicación ni infraestructura)."""
import unittest
from datetime import date, datetime, time

from vetcare24.dominio.cita import Cita
from vetcare24.dominio.emergencia import Emergencia
from vetcare24.dominio.errores import (
    EsquemaNoValidado, HorarioNoDisponible, InformacionIncompleta, PeriodoIncoherente)
from vetcare24.dominio.eventos import CitaAgendada, EmergenciaIdentificada, NotaClinicaRegistrada
from vetcare24.dominio.expediente_clinico import ExpedienteClinico
from vetcare24.dominio.servicio_de_programacion_de_citas import ServicioDeProgramacionDeCitas
from vetcare24.dominio.vacunacion import (
    EsquemaDeVacunacion, ServicioDeSeguimientoDeVacunacion, Vacunacion)
from vetcare24.dominio.valores import DosisIndicada, PeriodoDeCita, ServicioSolicitado

FECHA = date(2026, 10, 14)
CONSULTA = ServicioSolicitado("Consulta general", 30)


class TestCitas(unittest.TestCase):
    def test_cita_periodo_coherente_con_duracion(self):
        """NB-06, NB-07, R-05: el periodo coincide con la duración del servicio."""
        coherente = PeriodoDeCita.desde(FECHA, time(9, 0), 30)
        cita = Cita("C-1", "M-001", CONSULTA, coherente)
        self.assertEqual(cita.periodo.termino, time(9, 30))
        incoherente = PeriodoDeCita.desde(FECHA, time(9, 0), 45)
        with self.assertRaises(PeriodoIncoherente):
            Cita("C-2", "M-001", CONSULTA, incoherente)

    def test_horario_traslapado_rechazado(self):
        """Q3, NB-07: no se agenda un horario que se traslape con otra cita del día."""
        prog = ServicioDeProgramacionDeCitas()
        primera = prog.programar("C-1", "M-001", CONSULTA, FECHA, time(9, 0), [])
        with self.assertRaises(HorarioNoDisponible) as ctx:
            prog.programar("C-2", "M-002", CONSULTA, FECHA, time(9, 15), [primera])
        self.assertEqual(ctx.exception.mensaje, "el horario se traslapa con otra cita")

    def test_horarios_contiguos_no_se_consideran_traslape(self):
        prog = ServicioDeProgramacionDeCitas()
        primera = prog.programar("C-1", "M-001", CONSULTA, FECHA, time(9, 0), [])
        segunda = prog.programar("C-2", "M-002", CONSULTA, FECHA, time(9, 30), [primera])
        self.assertEqual(segunda.periodo.inicio, time(9, 30))

    def test_citas_de_otro_dia_no_bloquean_el_horario(self):
        prog = ServicioDeProgramacionDeCitas()
        otra = prog.programar("C-1", "M-001", CONSULTA, date(2026, 10, 15), time(9, 0), [])
        cita = prog.programar("C-2", "M-002", CONSULTA, FECHA, time(9, 0), [otra])
        self.assertEqual(cita.periodo.fecha, FECHA)

    def test_agendar_registra_el_evento_cita_agendada(self):
        cita = Cita.agendar("C-1", "M-001", CONSULTA, PeriodoDeCita.desde(FECHA, time(9, 0), 30))
        self.assertEqual(cita.extraer_eventos(), (CitaAgendada("C-1", "M-001"),))
        self.assertEqual(cita.extraer_eventos(), ())  # los eventos se extraen una sola vez

    def test_servicio_requiere_duracion_positiva(self):
        with self.assertRaises(InformacionIncompleta):
            ServicioSolicitado("Consulta general", 0)


class TestExpedienteClinico(unittest.TestCase):
    def setUp(self):
        self.exp = ExpedienteClinico("EXP-1", "M-001")
        self.ahora = datetime(2026, 10, 13, 9, 0)

    def test_veterinario_registra_nota_con_autor(self):
        """NB-12, R-02: la nota queda a nombre del veterinario que la registra."""
        nota = self.exp.registrar_nota_clinica("VET-01", "anamnesis", "examen", "dx", self.ahora)
        self.assertEqual(nota.autor, "VET-01")
        self.assertEqual(self.exp.notas, (nota,))
        self.assertEqual(self.exp.extraer_eventos(),
                         (NotaClinicaRegistrada(nota.nota_id, "M-001", "VET-01"),))

    def test_nota_sin_autor_se_rechaza(self):
        with self.assertRaises(InformacionIncompleta):
            self.exp.registrar_nota_clinica("", "a", "e", "d", self.ahora)

    def test_expediente_no_ofrece_operaciones_para_modificar_notas(self):
        """R-03 protegida por diseño: no existe forma de editar ni borrar una nota."""
        publicas = {n for n in dir(self.exp) if not n.startswith("_")}
        for prohibida in ("modificar_nota", "editar_nota", "eliminar_nota",
                          "actualizar_nota", "borrar_nota"):
            self.assertNotIn(prohibida, publicas)
        self.assertIsInstance(self.exp.notas, tuple)  # vista inmutable

    def test_cada_nota_conserva_las_anteriores(self):
        self.exp.registrar_nota_clinica("VET-01", "a1", "e1", "d1", self.ahora)
        self.exp.registrar_nota_clinica("VET-02", "a2", "e2", "d2", self.ahora)
        self.assertEqual([n.autor for n in self.exp.notas], ["VET-01", "VET-02"])


class TestVacunacion(unittest.TestCase):
    def _vac(self, id_, vacuna, dia):
        return Vacunacion.registrar(id_, "M-001", DosisIndicada(vacuna, "1 ml", dia))

    def test_sin_esquema_validado_seguimiento_pendiente(self):
        """R-12: sin esquema definido y validado no se calcula la próxima aplicación."""
        servicio = ServicioDeSeguimientoDeVacunacion()
        historial = [self._vac("V-1", "Parvovirus", date(2026, 10, 1))]
        no_validado = EsquemaDeVacunacion("Parvovirus", 21, 3, validado=False)
        with self.assertRaises(EsquemaNoValidado):
            servicio.determinar_proxima(historial, no_validado)
        with self.assertRaises(EsquemaNoValidado):
            servicio.determinar_proxima(historial, None)  # esquema no definido

    def test_refuerzo_identificado_con_esquema_valido(self):
        """NB-16, R-13: con esquema validado se identifica el refuerzo.
        La fórmula de fechas es un supuesto de ejemplo (pendiente en la Unidad 2)."""
        servicio = ServicioDeSeguimientoDeVacunacion()
        esquema = EsquemaDeVacunacion("Rabia", 365, 3, validado=True)
        primera = [self._vac("V-1", "Rabia", date(2026, 10, 1))]
        proxima = servicio.determinar_proxima(primera, esquema)
        self.assertTrue(proxima.es_refuerzo)
        self.assertEqual(proxima.fecha, date(2027, 10, 1))
        self.assertEqual(proxima.vacuna, "Rabia")

    def test_esquema_completo_no_genera_proxima_aplicacion(self):
        servicio = ServicioDeSeguimientoDeVacunacion()
        esquema = EsquemaDeVacunacion("Rabia", 365, 2, validado=True)
        historial = [self._vac("V-1", "Rabia", date(2025, 10, 1)),
                     self._vac("V-2", "Rabia", date(2026, 10, 1))]
        self.assertIsNone(servicio.determinar_proxima(historial, esquema))

    def test_el_seguimiento_solo_considera_la_vacuna_del_esquema(self):
        servicio = ServicioDeSeguimientoDeVacunacion()
        esquema = EsquemaDeVacunacion("Rabia", 365, 2, validado=True)
        historial = [self._vac("V-1", "Rabia", date(2026, 10, 1)),
                     self._vac("V-2", "Parvovirus", date(2026, 10, 2))]
        proxima = servicio.determinar_proxima(historial, esquema)
        self.assertEqual(proxima.fecha, date(2027, 10, 1))


class TestEmergencia(unittest.TestCase):
    def test_emergencia_sin_cita_se_registra(self):
        """NB-19, R-06: la emergencia no exige cita ni, por ahora, mascota (P3)."""
        e = Emergencia.identificar("E-1", "Atropellamiento", "Crítico", datetime(2026, 10, 13, 9, 0))
        self.assertIsNone(e.mascota_id)
        self.assertEqual(e.extraer_eventos(), (EmergenciaIdentificada("E-1"),))
        self.assertNotIn("cita", Emergencia.identificar.__code__.co_varnames)

    def test_emergencia_requiere_motivo(self):
        with self.assertRaises(InformacionIncompleta):
            Emergencia.identificar("E-1", "", "Crítico", datetime(2026, 10, 13, 9, 0))


if __name__ == "__main__":
    unittest.main()
