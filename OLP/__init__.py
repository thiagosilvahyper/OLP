# OLP - Otimizador de Localidade Preditivo
# Versão: 1.0
# Data: 28/10/2025

"""
Sistema OLP (Otimizador de Localidade Preditivo)
Módulo de otimização de tarefas sensíveis à latência
"""

__version__ = "1.0.0"
__author__ = "Development Team"
__status__ = "Production Ready"

# Imports principais
from src.olp_core_api import OLPCoreAPI
from src.alp_model import ALP_MODEL
from src.olp_hal_driver import OLP_HAL

__all__ = [
    'OLPCoreAPI',
    'ALP_MODEL',
    'OLP_HAL'
]

print(f"OLP v{__version__} carregado com sucesso!")
