# VetCare 24

Propuesta de arquitectura de software para **VetCare 24**, una clínica veterinaria. El proyecto convierte el análisis de negocio de la Unidad 2 en un diseño por capas (dominio, aplicación e infraestructura) con su código y sus pruebas automatizadas.

## Datos del equipo

| Equipo | Integrante | Matrícula | Carrera |
|--------|------------|-----------|---------|
| 4 | García Cerda Randal Guillermo | 2112493 | ITS |
| 4 | Sarmiento Hernández Cesar Martín | 2119427 | ITS |
| 4 | Torres Pasillas Angela Susana | 2101844 | ITS |

## Datos de la actividad

| Elemento | Valor |
|----------|-------|
| Institución | Universidad Autónoma de Nuevo León (UANL), FIME |
| Curso | Componentes de lógica de negocios |
| Profesor | Miguel Ángel Gómez Marroquín |
| Módulo Netacad | 3 |
| Actividad | Diseño Arquitectural del Sistema |
| Empresa / caso | VetCare 24 |
| Fecha | 13/10/2026 |

## Estructura del repositorio

```
├── diagramas/      Diagramas del diseño (clases, secuencia)
├── documentos/     Entregables de la actividad
├── src/
│   └── vetcare24/
│       ├── dominio/          Reglas de negocio, agregados, eventos y errores
│       ├── aplicacion/       Casos de uso, comandos, consultas y puertos
│       └── infraestructura/  Repositorios, Unit of Work y control de acceso
├── tests/          Pruebas automatizadas y evidencias
│   └── evidencias/
└── README.md
```

## Arquitectura

- **Dominio:** no depende de aplicación ni de infraestructura y solo usa la biblioteca estándar de Python.
- **Aplicación:** un servicio por caso de uso; depende de interfaces (puertos y repositorios), nunca de infraestructura.
- **Infraestructura:** implementa los repositorios, el Unit of Work, el control de acceso por rol y las lecturas.
- **CQRS:** los comandos modifican el estado dentro de una transacción; las consultas no escriben y devuelven View Models.
- **Control de acceso:** el permiso se verifica antes de abrir la transacción.

## Casos de uso

| Caso | Descripción |
|------|-------------|
| CU-01 | Solicitar cita |
| CU-02 | Generar nota clínica |
| CU-03 | Registrar vacunación |
| CU-04 | Registrar hospitalización |
| CU-05 | Atender emergencia |

## Cómo ejecutar las pruebas

Desde la raíz del repositorio (requiere Python 3.10 o superior):

```
py -m unittest discover -s tests -t . -v
```

Si `pytest` está instalado también puede usarse `python -m pytest tests -v`.

## Resultado de las pruebas

| Indicador | Resultado |
|-----------|-----------|
| Pruebas ejecutadas | 60 |
| Pruebas aprobadas | 60 |
| Fallidas / con error / omitidas | 0 / 0 / 0 |
| Tiempo | 0.079 s |
| Resultado final | OK |

| Suite | Pruebas |
|-------|---------|
| `test_reglas_de_negocio.py` | 16 |
| `test_casos_de_uso.py` | 16 |
| `test_permisos_por_rol.py` | 7 |
| `test_transacciones_y_eventos.py` | 8 |
| `test_consultas_cqrs.py` | 6 |
| `test_coherencia_diseno.py` | 7 |

La evidencia completa está en la carpeta `tests/evidencias/`.

## Bibliografía

- Cohn, M. (2004). *User stories applied: For agile software development*. Addison-Wesley.
- Evans, E. (2003). *Domain-driven design: Tackling complexity in the heart of software*. Addison-Wesley.
- Fowler, M. (2003). *Patterns of enterprise application architecture*. Addison-Wesley.
- Martin, R. C. (2017). *Clean architecture: A craftsman's guide to software structure and design*. Prentice Hall.
- Beck, K. (2003). *Test-driven development: By example*. Addison-Wesley.
- Millett, S., & Tune, N. (2015). *Patterns, principles, and practices of domain-driven design*. Wrox.
