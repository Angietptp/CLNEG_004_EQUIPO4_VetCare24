"""Errores de negocio de VetCare 24, expresados con el lenguaje del glosario."""


class ErrorDeNegocio(Exception):
    """Base de los errores que se pueden explicar en términos del negocio."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class OperacionNoAutorizada(ErrorDeNegocio):
    """Su rol no permite esta operación (R-09, ADR-04)."""

    def __init__(self, mensaje: str = "su rol no permite esta operación"):
        super().__init__(mensaje)


class MascotaNoRegistrada(ErrorDeNegocio):
    """La mascota debe estar registrada antes de operar sobre ella (R-10)."""

    def __init__(self, mascota_id: str = ""):
        super().__init__(f"la mascota {mascota_id} no está registrada".replace("  ", " "))


class HorarioNoDisponible(ErrorDeNegocio):
    def __init__(self):
        super().__init__("el horario se traslapa con otra cita")


class ExpedienteNoEncontrado(ErrorDeNegocio):
    def __init__(self, mascota_id: str = ""):
        super().__init__(f"no existe expediente clínico para la mascota {mascota_id}".replace("  ", " "))


class EsquemaNoValidado(ErrorDeNegocio):
    def __init__(self):
        super().__init__(
            "la vacuna quedó registrada; el seguimiento espera un esquema validado"
        )


class PeriodoIncoherente(ErrorDeNegocio):
    def __init__(self):
        super().__init__("el periodo de la cita no coincide con la duración del servicio")


class InformacionIncompleta(ErrorDeNegocio):
    """Faltan datos mínimos. Los campos obligatorios exactos están pendientes."""
