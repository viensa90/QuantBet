"""
Sistema de logging estructurado para QuantBet.
"""
import logging
import json
import sys
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.threadName,
            "process": record.process
        }
        return json.dumps(log_record)

def get_logger(name: str) -> logging.Logger:
    """
    Devuelve un logger configurado con formato JSON.
    Reemplaza al antiguo setup_logger para mantener compatibilidad.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

# Alias para compatibilidad con código antiguo
setup_logger = get_logger