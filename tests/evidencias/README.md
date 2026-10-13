# Evidencias

- `resultado_pruebas.txt`: salida de la ejecución completa (`python -m unittest discover -s tests -t . -v`).
- `trazabilidad_pruebas.md`: relación entre la matriz de trazabilidad y las pruebas que la respaldan.

Para regenerar la evidencia, desde la raíz del repositorio:

```
python -m unittest discover -s tests -t . -v > tests/evidencias/resultado_pruebas.txt 2>&1
```
