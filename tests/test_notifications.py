"""
tests/test_notifications.py
Pruebas para el sistema de notificaciones
Versión: 0.3.1
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.notifications import EmailNotifier, TelegramNotifier, NotificationManager
from src.storage.repository import Repository
from src.domain.entities import Decision

class TestEmailNotifier:
    """Pruebas para EmailNotifier"""
    
    def test_init_disabled(self):
        """Verifica que se deshabilita si faltan credenciales"""
        with patch('src.config_loader.config.get') as mock_get:
            mock_get.return_value = {'enabled': True}
            notifier = EmailNotifier()
            assert not notifier.enabled
    
    def test_init_enabled(self):
        """Verifica que se habilita con credenciales"""
        with patch('src.config_loader.config.get') as mock_get:
            mock_get.return_value = {
                'enabled': True,
                'username': 'test',
                'password': 'test',
                'from_email': 'test@test.com',
                'to_emails': ['to@test.com']
            }
            notifier = EmailNotifier()
            assert notifier.enabled
    
    def test_send_notification_low_score(self):
        """Verifica que no envía notificaciones con score bajo"""
        notifier = EmailNotifier()
        notifier.enabled = True
        notifier.min_score = 70.0
        
        decision = {'score': 50.0, 'event_id': 'test'}
        result = notifier.send_notification(decision)
        assert not result
    
    @patch('smtplib.SMTP')
    def test_send_notification_success(self, mock_smtp):
        """Verifica envío exitoso de email"""
        with patch('src.config_loader.config.get') as mock_get:
            mock_get.return_value = {
                'enabled': True,
                'username': 'test',
                'password': 'test',
                'from_email': 'test@test.com',
                'to_emails': ['to@test.com'],
                'min_score': 70.0
            }
            
            notifier = EmailNotifier()
            notifier.enabled = True
            
            decision = {
                'event_id': 'test',
                'strategy': 'arbitrage',
                'score': 85.0,
                'data': {'profit_percent': 2.5, 'market_type': '1X2'},
                'timestamp': datetime.now().isoformat()
            }
            
            result = notifier.send_notification(decision)
            assert result

class TestTelegramNotifier:
    """Pruebas para TelegramNotifier"""
    
    def test_init_disabled(self):
        """Verifica que se deshabilita si faltan credenciales"""
        with patch('src.config_loader.config.get') as mock_get:
            mock_get.return_value = {'enabled': True}
            notifier = TelegramNotifier()
            assert not notifier.enabled
    
    def test_init_enabled(self):
        """Verifica que se habilita con credenciales"""
        with patch('src.config_loader.config.get') as mock_get:
            mock_get.return_value = {
                'enabled': True,
                'bot_token': 'token123',
                'chat_ids': ['123456']
            }
            notifier = TelegramNotifier()
            assert notifier.enabled
    
    def test_send_notification_low_score(self):
        """Verifica que no envía notificaciones con score bajo"""
        notifier = TelegramNotifier()
        notifier.enabled = True
        notifier.min_score = 70.0
        
        decision = {'score': 50.0, 'event_id': 'test'}
        result = notifier.send_notification(decision)
        assert not result

class TestNotificationManager:
    """Pruebas para NotificationManager"""
    
    @pytest.fixture
    def temp_db(self):
        """Crea una base de datos temporal para los tests"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        yield db_path
        Path(db_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def repo(self, temp_db):
        """Repositorio con base de datos temporal"""
        return Repository(temp_db)
    
    def test_init(self):
        """Verifica inicialización del manager"""
        with patch('src.config_loader.config.get') as mock_get:
            mock_get.return_value = {
                'enabled': True,
                'min_score': 70.0,
                'interval_minutes': 15,
                'max_per_interval': 10
            }
            manager = NotificationManager()
            assert manager.enabled
            assert manager.min_score == 70.0
    
    def test_check_and_notify_disabled(self):
        """Verifica que no envía notificaciones si está deshabilitado"""
        with patch('src.config_loader.config.get') as mock_get:
            mock_get.return_value = {'enabled': False}
            manager = NotificationManager()
            result = manager.check_and_notify()
            assert result == 0