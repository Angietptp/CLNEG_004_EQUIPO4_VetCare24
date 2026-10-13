# Trazabilidad: matriz → pruebas

Cada prueba propuesta en la matriz de trazabilidad (columna "Prueba") existe y se ejecuta.

| Necesidad (BRD) | Regla de negocio | Caso de uso | Prueba | Archivo |
|---|---|---|---|---|
| NB-06, NB-07 | La cita considera el servicio solicitado y su duración (R-05) | CU-01 | `test_cita_periodo_coherente_con_duracion` | `test_reglas_de_negocio.py` |
| NB-07 | No se agenda un horario que se traslape con otra cita del día (criterio de disponibilidad por validar, P1) | CU-01 | `test_horario_traslapado_rechazado` | `test_reglas_de_negocio.py` |
| NB-06 | Recepción administra las citas y los datos administrativos (R-01) | CU-01 | `test_recepcion_puede_solicitar_cita` | `test_permisos_por_rol.py` |
| NB-03, NB-10 | La mascota debe estar registrada antes de citar, vacunar, hospitalizar o atender; un expediente por mascota (R-10) | CU-01 a CU-04 | `test_mascota_no_registrada_revierte` | `test_casos_de_uso.py` |
| NB-10, NB-12 | Solo el Veterinario registra la nota clínica y queda como su autor (R-02) | CU-02 | `test_veterinario_registra_nota_con_autor` | `test_reglas_de_negocio.py` |
| NB-12 | Recepción no modifica notas clínicas; el agregado no ofrece operación para modificarlas (R-03) | CU-02 | `test_recepcion_no_registra_nota_clinica` | `test_permisos_por_rol.py` |
| NB-11 | La información clínica solo está disponible para personal autorizado según su rol (R-14) | Query | `test_consulta_expediente_solo_autorizados` | `test_consultas_cqrs.py` |
| NB-06 | Las consultas no modifican estado ni cargan agregados; devuelven View Models | Query | `test_consultar_citas_no_modifica_estado` | `test_consultas_cqrs.py` |
| NB-14 | El historial conserva las aplicaciones anteriores de cada mascota (R-11) | CU-03 | `test_historial_conserva_aplicaciones_previas` | `test_casos_de_uso.py` |
| NB-15 | La próxima aplicación solo se determina con un esquema definido y validado; si no, el seguimiento queda pendiente sin error (R-12) | CU-03 | `test_sin_esquema_validado_seguimiento_pendiente` | `test_reglas_de_negocio.py` |
| NB-16, NB-17 | Las vacunas con refuerzo se identifican y reciben seguimiento; el resultado apoya los recordatorios, cuyo envío no está definido (R-13) | CU-03 | `test_refuerzo_identificado_con_esquema_valido` | `test_reglas_de_negocio.py` |
| NB-18 | La mascota hospitalizada queda con seguimiento continuo desde el ingreso; estados, evolución y egreso quedan fuera del caso (R-08) | CU-04 | `test_registrar_hospitalizacion_inicia_seguimiento` | `test_casos_de_uso.py` |
| NB-18 | El veterinario determina la hospitalización y el personal clínico la inicia y consulta la información (R-04) | CU-04 | `test_rol_no_permitido_rechaza_hospitalizacion` | `test_permisos_por_rol.py` |
| NB-19 | La emergencia se registra y atiende sin exigir cita previa (R-06) | CU-05 | `test_emergencia_sin_cita_se_registra` | `test_casos_de_uso.py` |
| NB-19 | Tras confirmar el registro se notifica al veterinario; quién identifica la emergencia está pendiente (CR-8) | CU-05 | `test_notifica_veterinario_tras_confirmar` | `test_transacciones_y_eventos.py` |
| NB-20 | Los permisos siguen las responsabilidades de cada rol y se verifican antes de cada operación (R-09) | CU-01 a CU-05 | `test_permiso_verificado_antes_de_transaccion` | `test_permisos_por_rol.py` |
| Todas | Una transacción por caso de uso; cada operación modifica un solo agregado, referido por identidad | CU-01 a CU-05 | `test_error_revierte_transaccion` | `test_transacciones_y_eventos.py` |
| Todas | Regla de dependencias entre capas: el dominio no depende de aplicación ni infraestructura | Todos | `test_arquitectura_dependencias` | `test_coherencia_diseno.py` |
