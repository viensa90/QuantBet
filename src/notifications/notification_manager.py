"""
src/notifications/notification_manager.py
Gestor de notificaciones para QuantBet
Versión: 0.3.1
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from src.config_loader import config
from src.storage.repository import Repository
from src.notifications.email_notifier import EmailNotifier
from src.notifications.telegram_notifier import TelegramNotifier

logger = logging.getLogger(__name__)

class NotificationManager:
    """Gestor de notificaciones para oportunidades detectadas"""
    
    def __init__(self):
        self.repo = Repository()
        self.email = EmailNotifier()
        self.telegram = TelegramNotifier()
        
        # Configuración
        self.enabled = config.get('notifications', {}).get('enabled', True)
        self.min_score = config.get('notifications', {}).get('min_score', 70.0)
        self.notify_interval = config.get('notifications', {}).get('interval_minutes', 15)
        self.max_notifications = config.get('notifications', {}).get('max_per_interval', 10)
        
        # Estado para rate limiting
        self._last_notification = datetime.now() - timedelta(minutes=self.notify_interval)
        self._sent_count = 0
    
    def check_and_notify(self, force: bool = False) -> int:
        """Verifica nuevas oportunidades y envía notificaciones"""
        if not self.enabled:
            logger.debug("Notificaciones deshabilitadas")
            return 0
        
        # Rate limiting
        if not force:
            time_since_last = datetime.now() - self._last_notification
            if time_since_last.total_seconds() < self.notify_interval * 60:
                logger.debug(f"Rate limiting: esperar {self.notify_interval} minutos entre notificaciones")
                return 0
        
        # Obtener nuevas oportunidades (no notificadas)
        decisions = self._get_new_decisions()
        
        if not decisions:
            logger.debug("No hay nuevas decisiones para notificar")
            return 0
        
        # Filtrar por score mínimo
        decisions = [d for d in decisions if d.get('score', 0) >= self.min_score]
        
        if not decisions:
            logger.debug(f"No hay decisiones con score >= {self.min_score}")
            return 0
        
        # Limitar cantidad
        if len(decisions) > self.max_notifications:
            logger.info(f"Limitando notificaciones: {len(decisions)} -> {self.max_notifications}")
            decisions = decisions[:self.max_notifications]
        
        # Enviar notificaciones
        sent = 0
        
        if self.email.enabled:
            sent += self.email.send_bulk_notification(decisions)
        
        if self.telegram.enabled:
            sent += self.telegram.send_bulk_notification(decisions)
        
        # Actualizar estado
        self._last_notification = datetime.now()
        self._sent_count += sent
        
        # Marcar decisiones como notificadas
        self._mark_as_notified(decisions)
        
        logger.info(f"Notificaciones enviadas: {sent} (total acumulado: {self._sent_count})")
        return sent
    
    def send_manual_notification(self, event_id: str, strategy: str) -> bool:
        """Envía notificación manual para un evento específico"""
        # Obtener decisiones del evento
        decisions = self.repo.get_decisions_by_event(event_id, limit=10)
        
        if not decisions:
            logger.warning(f"No se encontraron decisiones para evento {event_id}")
            return False
        
        # Convertir a dict
        decisions_dict = [
            {
                'event_id': d.event_id,
                'strategy': d.strategy,
                'score': d.opportunity_score,
                'data': d.opportunity_data,
                'timestamp': d.timestamp.isoformat()
            }
            for d in decisions
        ]
        
        # Filtrar por estrategia
        if strategy != 'all':
            decisions_dict = [d for d in decisions_dict if d['strategy'] == strategy]
        
        if not decisions_dict:
            logger.warning(f"No se encontraron decisiones para evento {event_id} estrategia {strategy}")
            return False
        
        # Enviar notificación forzada
        sent = 0
        if self.email.enabled:
            sent += self.email.send_bulk_notification(decisions_dict)
        if self.telegram.enabled:
            sent += self.telegram.send_bulk_notification(decisions_dict)
        
        return sent > 0
    
    def _get_new_decisions(self) -> List[Dict[str, Any]]:
        """Obtiene decisiones no notificadas"""
        # Usar timestamp de última notificación
        since = self._last_notification - timedelta(minutes=5)
        
        # Buscar decisiones con score alto
        decisions = self.repo.get_top_opportunities(limit=50, min_score=self.min_score)
        
        # Filtrar por timestamp (solo nuevas)
        new_decisions = []
        for d in decisions:
            timestamp = datetime.fromisoformat(d['timestamp'])
            if timestamp > since:
                new_decisions.append(d)
        
        return new_decisions
    
    def _mark_as_notified(self, decisions: List[Dict[str, Any]]):
        """Marca decisiones como notificadas (implementación futura)"""
        # Por ahora solo log
        logger.debug(f"Marcadas {len(decisions)} decisiones como notificadas")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de notificaciones"""
        return {
            'enabled': self.enabled,
            'email': self.email.enabled,
            'telegram': self.telegram.enabled,
            'total_sent': self._sent_count,
            'last_notification': self._last_notification.isoformat(),
            'min_score': self.min_score,
            'interval_minutes': self.notify_interval,
            'max_per_interval': self.max_notifications
        }