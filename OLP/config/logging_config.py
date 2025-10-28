# config/logging_config.py - Configuração de Logging Avançada

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

def setup_logging(log_dir='./logs', level=logging.INFO):
    """Configurar logging completo"""
    
    # Criar diretório
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configuração básica
    logging.basicConfig(level=level)
    
    # Handler para arquivo
    log_file = log_dir / f"olp_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formato
    formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Aplicar handlers
    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Usar em main.py
# setup_logging('./logs', logging.INFO)
