"""ControlDeAccesoPorRol: tabla de permisos por rol.
P7: la matriz definitiva está PENDIENTE; esta tabla es un supuesto de trabajo
tomado de los actores de CU-01 a CU-05 y de R-01, R-02, R-03, R-04, R-09 y R-14."""
from vetcare24.aplicacion.puertos import ControlDeAcceso
from vetcare24.aplicacion.seguridad import Operacion, Rol, Usuario
from vetcare24.dominio.errores import OperacionNoAutorizada

PERMISOS = {
    Operacion.SOLICITAR_CITA: {Rol.PROPIETARIO, Rol.RECEPCION},
    Operacion.GENERAR_NOTA_CLINICA: {Rol.VETERINARIO},
    Operacion.REGISTRAR_VACUNACION: {Rol.VETERINARIO},
    Operacion.REGISTRAR_HOSPITALIZACION: {Rol.VETERINARIO, Rol.PERSONAL_CLINICO},
    Operacion.ATENDER_EMERGENCIA: {Rol.RECEPCION, Rol.PERSONAL_CLINICO, Rol.VETERINARIO},
    Operacion.CONSULTAR_EXPEDIENTE: {Rol.VETERINARIO, Rol.PERSONAL_CLINICO},
    Operacion.CONSULTAR_CITAS: {Rol.RECEPCION, Rol.VETERINARIO},
}


class ControlDeAccesoPorRol(ControlDeAcceso):
    def verificar(self, usuario: Usuario, operacion: Operacion) -> None:
        if usuario.rol not in PERMISOS.get(operacion, set()):
            raise OperacionNoAutorizada()
