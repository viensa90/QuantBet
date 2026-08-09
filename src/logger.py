"""
Configuración de logging para QuantBet.
- Filtra campos sensibles (API key, tokens) en los mensajes.
- Salida estructurada en consola y archivo.
"""
import os
import logging
from logging.handlers import RotatingFileHandler

# --- Filtro para ocultar secretos ---
class SensitiveFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        # Cargamos los secretos desde .env (si están disponibles)
        self.api_key = os.getenv('ODDS_API_KEY', '')
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')

    def filter(self, record):
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            # Oculta API key
            if self.api_key:
                record.msg = record.msg.replace(self.api_key, '***API_KEY***')
            # Oculta bot token
            if self.bot_token:
                record.msg = record.msg.replace(self.bot_token, '***BOT_TOKEN***')
        return True

# --- Configuración del logger global ---
def setup_logger(name='QuantBet', log_file='quantbet.log', level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evitar duplicados
    if logger.handlers:
        return logger

    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para consola
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.addFilter(SensitiveFilter())
    logger.addHandler(console)

    # Handler para archivo (rotación)
    try:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5*1024*1024, backupCount=3
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(SensitiveFilter())
        logger.addHandler(file_handler)
    except Exception:
        pass  # Si no se puede escribir el archivo, solo consola

    return logger

# Logger por defecto
logger = setup_logger()