"""
Notificador por Telegram.
Requiere bot_token y chat_id.
"""
import requests
from src.logger import logger

class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Envía un mensaje al chat configurado."""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info("Mensaje Telegram enviado correctamente")
            return True
        except Exception as e:
            logger.error("Error enviando mensaje Telegram: %s", e)
            return False