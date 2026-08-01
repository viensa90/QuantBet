"""
src/notifications/email_notifier.py
Notificador por email usando SMTP
Versión: 0.3.1
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.config_loader import config

logger = logging.getLogger(__name__)

class EmailNotifier:
    """Notificador de oportunidades por email"""
    
    def __init__(self, config_section: str = 'email'):
        self.config = config.get(config_section, {})
        self.enabled = self.config.get('enabled', False)
        self.smtp_server = self.config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = self.config.get('smtp_port', 587)
        self.username = self.config.get('username', '')
        self.password = self.config.get('password', '')
        self.from_email = self.config.get('from_email', '')
        self.to_emails = self.config.get('to_emails', [])
        self.min_score = self.config.get('min_score', 70.0)
        
        if self.enabled and not all([self.username, self.password, self.from_email, self.to_emails]):
            logger.warning("EmailNotifier habilitado pero faltan credenciales")
            self.enabled = False
    
    def send_notification(self, decision: Dict[str, Any]) -> bool:
        """Envía notificación de una decisión por email"""
        if not self.enabled:
            return False
        
        if decision.get('score', 0) < self.min_score:
            logger.debug(f"Score {decision.get('score')} menor que mínimo {self.min_score}, no se envía email")
            return False
        
        try:
            subject = f"🔔 QuantBet - Oportunidad detectada: {decision.get('strategy', 'unknown')}"
            body = self._format_email_body(decision)
            
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email enviado a {', '.join(self.to_emails)} para evento {decision.get('event_id')}")
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar email: {e}")
            return False
    
    def send_bulk_notification(self, decisions: List[Dict[str, Any]]) -> int:
        """Envía notificaciones masivas por email"""
        if not self.enabled or not decisions:
            return 0
        
        sent = 0
        for decision in decisions:
            if self.send_notification(decision):
                sent += 1
        
        logger.info(f"Enviados {sent} emails de {len(decisions)} decisiones")
        return sent
    
    def _format_email_body(self, decision: Dict[str, Any]) -> str:
        """Formatea el cuerpo del email en HTML"""
        strategy = decision.get('strategy', 'unknown')
        score = decision.get('score', 0)
        event_id = decision.get('event_id', 'unknown')
        timestamp = decision.get('timestamp', datetime.now().isoformat())
        data = decision.get('data', {})
        
        # Formatear datos según estrategia
        details = ""
        if strategy == 'arbitrage':
            profit = data.get('profit_percent', 0)
            market = data.get('market_type', 'unknown')
            details = f"""
            <p><b>Mercado:</b> {market}</p>
            <p><b>Beneficio:</b> {profit:.2f}%</p>
            """
        elif strategy == 'value_betting':
            edge = data.get('edge_percent', 0)
            selection = data.get('selection', 'unknown')
            details = f"""
            <p><b>Selección:</b> {selection}</p>
            <p><b>Edge:</b> {edge:.2f}%</p>
            """
        elif strategy == 'dutching':
            return_ = data.get('guaranteed_return', 0)
            details = f"""
            <p><b>Retorno garantizado:</b> {return_:.2f}</p>
            """
        
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
                .header {{ background: #2c3e50; color: white; padding: 15px; border-radius: 8px 8px 0 0; }}
                .score {{ font-size: 24px; font-weight: bold; color: {'#27ae60' if score > 80 else '#f39c12'}; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #999; text-align: center; }}
                .details {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🔔 QuantBet - Nueva Oportunidad</h2>
                </div>
                <div class="details">
                    <p><b>Evento:</b> {event_id}</p>
                    <p><b>Estrategia:</b> {strategy}</p>
                    <p><b>Score:</b> <span class="score">{score:.1f}</span></p>
                    {details}
                    <p><b>Timestamp:</b> {timestamp}</p>
                </div>
                <div class="footer">
                    <p>QuantBet v0.3.1 - Sistema de Arbitraje Deportivo Automatizado</p>
                    <p><a href="https://github.com/viensa90/QuantBet">Repositorio</a></p>
                </div>
            </div>
        </body>
        </html>
        """