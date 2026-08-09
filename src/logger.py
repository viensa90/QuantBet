import logging
import sys
from pathlib import Path

# Logger global creado de inmediato (sin riesgo de fallo en importación)
log = logging.getLogger("quantbet")
log.setLevel(logging.DEBUG)

# Handler por defecto en consola para que siempre haya salida,
# incluso antes de llamar a setup_logger()
_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(
    logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')
)
log.addHandler(_console_handler)

def setup_logger(simple_mode=False):
    """
    Reconfigura el logger global:
    - simple_mode: solo muestra INFO en consola
    - siempre guarda DEBUG en archivo 'logs/quantbet.log'
    """
    # Limpiar handlers anteriores
    log.handlers.clear()

    # Formateador común
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Consola
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO if simple_mode else logging.DEBUG)
    console.setFormatter(formatter)
    log.addHandler(console)

    # Archivo (siempre DEBUG)
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / 'quantbet.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

    log.debug("Logger configurado.")