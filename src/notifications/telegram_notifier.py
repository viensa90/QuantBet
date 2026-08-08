import requests
from src.logger import get_logger

logger = get_logger(__name__)

class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, text):
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {'chat_id': self.chat_id, 'text': text, 'parse_mode': 'Markdown'}
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            logger.error(f"Error enviando Telegram: {e}")

    def send_opportunities(self, opportunities):
        if not opportunities:
            return
        best = opportunities[0]
        text = f"🚨 *QuantBet: {len(opportunities)} oportunidades*\n\n"
        text += f"🏆 Mejor: {best.event_name} – {best.market}\n"
        for out in best.details['outcomes']:
            text += f"  {out['outcome']}: {out['bookmaker']} @ {out['odds']}\n"
        text += f"Profit: {best.profit_percent:.2f}%\n"
        text += f"Dashboard: http://localhost:5000"
        self.send_message(text)