"""Value Objects: se definen por sus valores, sin identidad propia."""
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from vetcare24.dominio.errores import InformacionIncompleta


@dataclass(frozen=True)
class DatosDeContacto:
    telefono: str
    correo: str
    direccion: str


@dataclass(frozen=True)
class ServicioSolicitado:
    """Servicio veterinario con su duración. P1: la duración llega en el comando."""

    tipo: str
    duracion_minutos: int

    def __post_init__(self):
        if not self.tipo or self.duracion_minutos <= 0:
            raise InformacionIncompleta("el servicio requiere tipo y una duración positiva")


@dataclass(frozen=True)
class PeriodoDeCita:
    fecha: date
    inicio: time
    termino: time

    def __post_init__(self):
        if self.inicio >= self.termino:
            raise InformacionIncompleta("el periodo debe terminar después de iniciar")

    @classmethod
    def desde(cls, fecha: date, inicio: time, duracion_minutos: int) -> "PeriodoDeCita":
        termino = (datetime.combine(fecha, inicio) + timedelta(minutes=duracion_minutos)).time()
        return cls(fecha, inicio, termino)

    @property
    def duracion_minutos(self) -> int:
        a = datetime.combine(self.fecha, self.inicio)
        b = datetime.combine(self.fecha, self.termino)
        return int((b - a).total_seconds() // 60)

    def se_traslapa_con(self, otro: "PeriodoDeCita") -> bool:
        return (
            self.fecha == otro.fecha
            and self.inicio < otro.termino
            and otro.inicio < self.termino
        )


@dataclass(frozen=True)
class DosisIndicada:
    """Campos y reglas exactas de la dosis aún por definir (glosario)."""

    vacuna: str
    dosis: str
    fecha: date
