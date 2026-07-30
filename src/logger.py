"""
Configuración de logging estructurado para QuantBet.
"""

import logging
import sys
from pathlib import Path


def setup_logging(level: str = "INFO", log_format: str = None, log_file: str = None) -> logging.Logger:
    """
    Configura logging estructurado con handlers de consola y archivo.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        log_format: Formato del mensaje
        log_file: Ruta al archivo de log (None = solo consola)
    
    Returns:
        Logger configurado
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Crear logger raíz
    logger = logging.getLogger("quantbet")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Evitar duplicados
    if logger.handlers:
        return logger
    
    # Formateador
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
    
    # Handler de consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler de archivo
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Obtiene un logger hijo con nombre específico.
    
    Args:
        name: Nombre del submódulo (ej: 'pipeline', 'arbitrage')
    
    Returns:
        Logger configurado
    """
    if name:
        return logging.getLogger(f"quantbet.{name}")
    return logging.getLogger("quantbet")