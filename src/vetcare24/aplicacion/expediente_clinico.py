"""CU-02 Generar nota clínica (US12)."""
from datetime import datetime
from typing import Callable

from vetcare24.aplicacion.comandos import GenerarNotaClinica
from vetcare24.aplicacion.puertos import ControlDeAcceso, UnitOfWork
from vetcare24.aplicacion.resultados import ResultadoDeNotaClinica
from vetcare24.aplicacion.seguridad import Operacion
from vetcare24.aplicacion.transaccion import transaccion
from vetcare24.dominio.repositorios import ExpedienteClinicoRepository, MascotaRepository


class ExpedienteClinicoApplicationService:
    def __init__(self, control_de_acceso: ControlDeAcceso, mascotas: MascotaRepository,
                 expedientes: ExpedienteClinicoRepository, unit_of_work: UnitOfWork,
                 reloj: Callable[[], datetime] = datetime.now):
        self._acceso = control_de_acceso
        self._mascotas = mascotas
        self._expedientes = expedientes
        self._uow = unit_of_work
        self._reloj = reloj

    def generar_nota_clinica(self, comando: GenerarNotaClinica) -> ResultadoDeNotaClinica:
        self._acceso.verificar(comando.usuario, Operacion.GENERAR_NOTA_CLINICA)  # R-02, R-03
        with transaccion(self._uow):
            self._mascotas.obtener(comando.mascota_id)
            expediente = self._expedientes.obtener_por_mascota(comando.mascota_id)
            nota = expediente.registrar_nota_clinica(
                autor=comando.usuario.usuario_id,  # ADR-04
                anamnesis=comando.anamnesis, examen_fisico=comando.examen_fisico,
                diagnostico=comando.diagnostico, fecha=self._reloj())
            self._expedientes.guardar(expediente)
        return ResultadoDeNotaClinica(nota.nota_id, expediente.extraer_eventos())
