"""
Handlers personalizados para logs estructurados
Versión: 0.3.3
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from elasticsearch import Elasticsearch, exceptions


class ElasticsearchHandler(logging.Handler):
    """Handler para enviar logs a Elasticsearch"""
    
    def __init__(
        self,
        hosts: list,
        index: str = "quantbet-logs",
        username: Optional[str] = None,
        password: Optional[str] = None,
        level: int = logging.INFO
    ):
        super().__init__(level)
        self.index = index
        
        # Configurar cliente Elasticsearch
        es_kwargs = {"hosts": hosts}
        if username and password:
            es_kwargs["basic_auth"] = (username, password)
        
        self.es = Elasticsearch(**es_kwargs)
        
        # Verificar conexión
        if not self.es.ping():
            logging.warning(f"No se pudo conectar a Elasticsearch en {hosts}")
    
    def emit(self, record: logging.LogRecord) -> None:
        """Enviar log a Elasticsearch"""
        try:
            # Construir documento
            doc = {
                "@timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "thread": record.threadName,
                "process": record.process,
                "extra": getattr(record, "extra", {})
            }
            
            # Enviar a Elasticsearch
            self.es.index(
                index=self.index,
                document=doc
            )
            
        except Exception as e:
            # Si falla, loggear a stderr (no usar logging para evitar loops)
            import sys
            print(f"Error enviando log a Elasticsearch: {e}", file=sys.stderr)
    
    def close(self) -> None:
        """Cerrar conexión con Elasticsearch"""
        if hasattr(self, 'es'):
            self.es.close()


class JSONFormatter(logging.Formatter):
    """Formatter para logs en formato JSON estructurado"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatear registro como JSON"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.threadName,
            "process": record.process
        }
        
        # Añadir extra si existe
        if hasattr(record, "extra"):
            log_data["extra"] = record.extra
        
        # Añadir excepción si existe
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """Formatter con colores para consola"""
    
    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[41m"  # Red background
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatear con colores"""
        color = self.COLORS.get(record.levelname, self.RESET)
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        
        # Formato: [timestamp] [LEVEL] logger - message
        message = super().format(record)
        return f"{color}[{timestamp}] [{record.levelname}] {record.name} - {message}{self.RESET}"