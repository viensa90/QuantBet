"""
src/notifications/telegram_notifier.py
Notificador por Telegram usando Bot API
Versión: 0.3.1
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests

from src.config_loader import config

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Notificador de oportunidades por Telegram"""
    
    def __init__(self, config_section: str = 'telegram'):
        self.config = config.get(config_section, {})
        self.enabled = self.config.get('enabled', False)
        self.bot_token = self.config.get('bot_token', '')
        self.chat_ids = self.config.get('chat_ids', [])
        self.min_score = self.config.get('min_score', 70.0)
        
        if self.enabled and not all([self.bot_token, self.chat_ids]):
            logger.warning("TelegramNotifier habilitado pero faltan credenciales")
            self.enabled = False
    
    def send_notification(self, decision: Dict[str, Any]) -> bool:
        """Envía notificación de una decisión por Telegram"""
        if not self.enabled:
            return False
        
        if decision.get('score', 0) < self.min_score:
            logger.debug(f"Score {decision.get('score')} menor que mínimo {self.min_score}, no se envía Telegram")
            return False
        
        try:
            message = self._format_message(decision)
            
            for chat_id in self.chat_ids:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                payload = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                
                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()
                
                logger.info(f"Mensaje Telegram enviado a chat {chat_id} para evento {decision.get('event_id')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar mensaje Telegram: {e}")
            return False
    
    def send_bulk_notification(self, decisions: List[Dict[str, Any]]) -> int:
        """Envía notificaciones masivas por Telegram"""
        if not self.enabled or not decisions:
            return 0
        
        sent = 0
        for decision in decisions:
            if self.send_notification(decision):
                sent += 1
        
        logger.info(f"Enviados {sent} mensajes Telegram de {len(decisions)} decisiones")
        return sent
    
    def send_photo(self, chart_path: str, caption: str = "📊 Resumen de oportunidades") -> bool:
        """Envía una foto/gráfico por Telegram"""
        if not self.enabled:
            return False
        
        try:
            for chat_id in self.chat_ids:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
                with open(chart_path, 'rb') as photo:
                    files = {'photo': photo}
                    data = {'chat_id': chat_id, 'caption': caption}
                    response = requests.post(url, files=files, data=data, timeout=30)
                    response.raise_for_status()
            
            logger.info(f"Foto enviada a {len(self.chat_ids)} chats")
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar foto Telegram: {e}")
            return False
    
    def _format_message(self, decision: Dict[str, Any]) -> str:
        """Formatea el mensaje de Telegram"""
        strategy = decision.get('strategy', 'unknown')
        score = decision.get('score', 0)
        event_id = decision.get('event_id', 'unknown')
        data = decision.get('data', {})
        
        # Emojis según estrategia
        emoji = {
            'arbitrage': '💰',
            'value_betting': '🎯',
            'dutching': '🔄'
        }.get(strategy, '🔔')
        
        # Formatear datos según estrategia
        details = ""
        if strategy == 'arbitrage':
            profit = data.get('profit_percent', 0)
            market = data.get('market_type', 'unknown')
            details = f"📊 Mercado: {market}\n💵 Beneficio: {profit:.2f}%"
        elif strategy == 'value_betting':
            edge = data.get('edge_percent', 0)
            selection = data.get('selection', 'unknown')
            details = f"🎯 Selección: {selection}\n📈 Edge: {edge:.2f}%"
        elif strategy == 'dutching':
            return_ = data.get('guaranteed_return', 0)
            details = f"🔄 Retorno garantizado: {return_:.2f}"
        
        # Score con color
        score_emoji = '🟢' if score > 80 else '🟡' if score > 60 else '🔴'
        
        return f"""
{emoji} <b>Nueva Oportunidad - QuantBet</b>

🏷️ <b>Estrategia:</b> {strategy}
📋 <b>Evento:</b> {event_id}
{score_emoji} <b>Score:</b> {score:.1f}

{details}

🕐 <b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔗 <a href="https://github.com/viensa90/QuantBet">QuantBet v0.3.1</a>
        """.strip()