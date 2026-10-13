"""Unit of Work (ADR-02), orden de las reacciones y eventos de dominio (P6)."""
import unittest

from vetcare24.aplicacion.comandos import AtenderEmergencia, GenerarNotaClinica, SolicitarCita
from vetcare24.infraestructura.repositorios import CitaRepositoryImpl

from tests.entorno import CONSULTA, FECHA, NUEVE, Entorno


class CitaRepositoryQueFallaDespuesDeGuardar(CitaRepositoryImpl):
    """Simula un fallo de persistencia DESPUÉS de haber escrito la cita."""

    def agregar(self, cita):
        super().agregar(cita)
        raise RuntimeError("falla de almacenamiento simulada")


class TestUnitOfWork(unittest.TestCase):
    def test_error_revierte_transaccion(self):
        """Ante cualquier error: revertir() deshace lo escrito y el error se propaga."""
        e = Entorno(citas_repo_factory=CitaRepositoryQueFallaDespuesDeGuardar)
        with self.assertRaises(RuntimeError):
            e.servicio_citas.solicitar_cita(
                SolicitarCita(e.recepcion, "M-001", CONSULTA, FECHA, NUEVE))
        self.assertEqual(e.almacen.citas, {})  # la cita escrita fue deshecha
        self.assertEqual(e.uow.estado, "revertida")

    def test_exito_confirma_la_transaccion(self):
        e = Entorno()
        e.servicio_citas.solicitar_cita(SolicitarCita(e.recepcion, "M-001", CONSULTA, FECHA, NUEVE))
        self.assertEqual(e.bitacora, ["acceso.verificar", "uow.iniciar", "uow.confirmar"])

    def test_la_transaccion_inicia_despues_de_autorizar(self):
        e = Entorno()
        e.servicio_notas.generar_nota_clinica(
            GenerarNotaClinica(e.veterinario, "M-001", "a", "e", "d"))
        self.assertLess(e.bitacora.index("acceso.verificar"), e.bitacora.index("uow.iniciar"))

    def test_cada_caso_de_uso_modifica_un_solo_agregado(self):
        e = Entorno()
        antes = e.huella()
        e.servicio_citas.solicitar_cita(SolicitarCita(e.recepcion, "M-001", CONSULTA, FECHA, NUEVE))
        despues = e.huella()
        cambios = [i for i, (a, b) in enumerate(zip(antes, despues)) if a != b]
        self.assertEqual(len(cambios), 1)  # solo cambió la colección de citas


class TestReaccionesYEventos(unittest.TestCase):
    def test_notifica_veterinario_tras_confirmar(self):
        """CR-8: la notificación se solicita después de confirmar el registro."""
        e = Entorno()
        r = e.servicio_emergencias.atender_emergencia(
            AtenderEmergencia(e.recepcion, "Atropellamiento", "Crítico"))
        self.assertTrue(r.notificado)
        self.assertEqual(e.bitacora, ["acceso.verificar", "uow.iniciar", "uow.confirmar",
                                      "notificador.notificar"])
        self.assertEqual(len(e.notificador.enviados), 1)

    def test_notificacion_no_disponible_deja_pendiente_sin_deshacer_el_registro(self):
        e = Entorno(notificador_disponible=False)
        r = e.servicio_emergencias.atender_emergencia(
            AtenderEmergencia(e.recepcion, "Atropellamiento", "Crítico"))
        self.assertFalse(r.notificado)  # pendiente de notificar
        self.assertIn(r.emergencia_id, e.almacen.emergencias)
        self.assertEqual(e.uow.estado, "confirmada")

    def test_emergencia_rechazada_por_rol_no_notifica(self):
        from vetcare24.dominio.errores import OperacionNoAutorizada
        e = Entorno()
        with self.assertRaises(OperacionNoAutorizada):
            e.servicio_emergencias.atender_emergencia(
                AtenderEmergencia(e.propietario, "Atropellamiento", "Crítico"))
        self.assertNotIn("notificador.notificar", e.bitacora)

    def test_los_eventos_se_devuelven_solo_si_la_operacion_se_completa(self):
        e = Entorno(citas_repo_factory=CitaRepositoryQueFallaDespuesDeGuardar)
        with self.assertRaises(RuntimeError):
            e.servicio_citas.solicitar_cita(
                SolicitarCita(e.recepcion, "M-001", CONSULTA, FECHA, NUEVE))
        ok = Entorno()
        r = ok.servicio_citas.solicitar_cita(
            SolicitarCita(ok.recepcion, "M-001", CONSULTA, FECHA, NUEVE))
        self.assertEqual(len(r.eventos), 1)


if __name__ == "__main__":
    unittest.main()
