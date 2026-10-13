"""Pruebas de VetCare 24. Ejecutar desde la raíz del repositorio:

    python -m unittest discover -s tests -t . -v      (biblioteca estándar)
    python -m pytest tests -v                          (si pytest está instalado)
"""
import os
import sys

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
