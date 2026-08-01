"""
Sistema de logging estructurado
Versión: 0.3.3
"""

import logging
import logging.config
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from .config_loader import ConfigLoader
from .logging.handlers import (
    ElasticsearchHandler,
    JSONFormatter,
    ColoredConsoleFormatter
)


def setup_logger(
    name: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> logging.Logger:
    """
    Configurar logger con opciones avanzadas
    
    Args:
        name: Nombre del logger (opcional)
        config: Configuración personalizada (opcional)
    
    Returns:
        Logger configurado
    """
    if config is None:
        config = ConfigLoader().config.get("logs", {})
    
    level_str = config.get("level", "INFO")
    level = getattr(logging, level_str.upper(), logging.INFO)
    format_type = config.get("format", "json")
    
    # Crear logger
    logger = logging.getLogger(name or "quantbet")
    logger.setLevel(level)
    
    # Limpiar handlers existentes
    logger.handlers.clear()
    
    # --- Console Handler ---
    if config.get("console", {}).get("enabled", True):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        if config.get("console", {}).get("color", False) and format_type == "text":
            console_formatter = ColoredConsoleFormatter('%(message)s')
        else:
            if format_type == "json":
                console_formatter = JSONFormatter()
            else:
                console_formatter = logging.Formatter(
                    '[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
        
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # --- File Handler ---
    if config.get("file", {}).get("enabled", False):
        file_config = config.get("file", {})
        log_path = file_config.get("path", "logs/quantbet.log")
        
        # Crear directorio si no existe
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        
        if format_type == "json":
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # --- Elasticsearch Handler ---
    if config.get("elasticsearch", {}).get("enabled", False):
        es_config = config.get("elasticsearch", {})
        es_handler = ElasticsearchHandler(
            hosts=es_config.get("hosts", ["http://localhost:9200"]),
            index=es_config.get("index", "quantbet-logs"),
            username=es_config.get("username"),
            password=es_config.get("password"),
            level=level
        )
        
        if format_type == "json":
            es_handler.setFormatter(JSONFormatter())
        
        logger.addHandler(es_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtener logger configurado
    
    Args:
        name: Nombre del logger
    
    Returns:
        Logger
    """
    # Verificar si ya está configurado
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Configurar con defaults
        return setup_logger(name)
    
    return logger