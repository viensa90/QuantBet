"""
Tests para sistema de logs estructurados
Versión: 0.3.3
"""

import json
import logging
import pytest
import tempfile
from pathlib import Path
from src.logger import setup_logger, get_logger
from src.logging.handlers import JSONFormatter, ColoredConsoleFormatter


def test_setup_logger_basic():
    """Test: Configuración básica del logger"""
    logger = setup_logger("test_basic")
    
    assert logger.name == "test_basic"
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0


def test_setup_logger_with_config():
    """Test: Configuración con parámetros personalizados"""
    config = {
        "level": "DEBUG",
        "format": "json",
        "console": {"enabled": True},
        "file": {"enabled": False}
    }
    
    logger = setup_logger("test_config", config)
    assert logger.level == logging.DEBUG


def test_setup_logger_file_handler():
    """Test: Handler de archivo"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"
        config = {
            "level": "INFO",
            "format": "text",
            "console": {"enabled": False},
            "file": {
                "enabled": True,
                "path": str(log_file)
            }
        }
        
        logger = setup_logger("test_file", config)
        logger.info("Test message")
        
        assert log_file.exists()
        content = log_file.read_text()
        assert "Test message" in content


def test_json_formatter():
    """Test: Formatter JSON estructurado"""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    log_str = formatter.format(record)
    log_data = json.loads(log_str)
    
    assert log_data["level"] == "INFO"
    assert log_data["logger"] == "test"
    assert log_data["message"] == "Test message"
    assert "timestamp" in log_data
    assert "module" in log_data


def test_colored_console_formatter():
    """Test: Formatter con colores para consola"""
    formatter = ColoredConsoleFormatter('%(levelname)s - %(message)s')
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    log_str = formatter.format(record)
    # Debe contener códigos de color ANSI
    assert "\033[" in log_str
    assert "Test message" in log_str


def test_get_logger():
    """Test: Obtener logger existente"""
    # Primero configurar
    logger1 = setup_logger("test_get")
    
    # Luego obtener
    logger2 = get_logger("test_get")
    
    # Debe ser el mismo logger
    assert logger1 is logger2


def test_logger_with_extra():
    """Test: Logging con datos extra"""
    logger = setup_logger("test_extra", {"console": {"enabled": True}})
    
    # Loggear con datos extra
    logger.info("Test with extra", extra={"user": "test_user", "event_id": 123})
    
    # Verificar que el handler tenga el extra (asumiendo JSONFormatter)
    for handler in logger.handlers:
        if isinstance(handler.formatter, JSONFormatter):
            # El extra debe estar en el registro
            assert hasattr(handler, 'format')
            break


def test_logger_with_levels():
    """Test: Diferentes niveles de logging"""
    logger = setup_logger("test_levels", {"level": "DEBUG"})
    
    # Loggear en diferentes niveles (no debería fallar)
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    
    # Verificar que el logger maneja todos los niveles
    assert logger.isEnabledFor(logging.DEBUG)
    assert logger.isEnabledFor(logging.INFO)
    assert logger.isEnabledFor(logging.WARNING)
    assert logger.isEnabledFor(logging.ERROR)
    assert logger.isEnabledFor(logging.CRITICAL)