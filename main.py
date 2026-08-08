import argparse
import sys
from src.config_loader import ConfigLoader
from src.logger import setup_logging
from src.connectors.factory import ProviderFactory
from src.core.arbitrage import ArbitrageEngine
from src.storage.database import Database
from src.storage.repository import Repository
from src.notifications.telegram_notifier import TelegramNotifier
import logging

logger = logging.getLogger(__name__)

def run_pipeline(source='oddsapi', save=True, simple=False):
    config = ConfigLoader()
    # Configurar logging (si simple, solo WARNING en consola)
    log_level = logging.WARNING if simple else logging.INFO
    setup_logging(level=log_level)

    engine = ArbitrageEngine()
    db = Database()
    repo = Repository(db)

    provider = ProviderFactory.create(source)
    snapshots = provider.get_events()

    all_opportunities = []
    for snap in snapshots:
        opps = engine.find_opportunities(snap)
        all_opportunities.extend(opps)

    # Filtrar por umbral mínimo
    min_profit = config['arbitrage']['min_profit_percent']
    valid_opps = [o for o in all_opportunities if o.profit_percent >= min_profit]

    if valid_opps and save:
        opp_dicts = [{
            'event_name': o.event_name,
            'sport': o.sport,
            'market': o.market,
            'strategy': 'arbitrage',
            'details': o.details,
            'profit': o.profit,
            'profit_percent': o.profit_percent
        } for o in valid_opps]
        repo.save_opportunities(opp_dicts)

    # Imprimir resumen
    print_summary(valid_opps, simple)

    # Notificaciones Telegram
    if valid_opps:
        try:
            notifier = TelegramNotifier(config.telegram_token, config.telegram_chat_id)
            notifier.send_opportunities(valid_opps)
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")

def print_summary(opportunities, simple):
    if not opportunities:
        print("\n🔍 No se encontraron oportunidades de arbitraje.\n")
        return

    print(f"\n🎯 {len(opportunities)} OPORTUNIDADES DE ARBITRAJE DETECTADAS\n")
    for opp in opportunities:
        print(f"⚽ {opp.event_name} ({opp.sport}) – {opp.market}")
        if simple:
            for outcome in opp.details['outcomes']:
                print(f"   {outcome['outcome']}: {outcome['bookmaker']} @ {outcome['odds']} (Stake: {outcome['stake']:.2f}€)")
            print(f"   Inversión total: {opp.details['total_investment']:.2f}€ → Retorno: {opp.details['guaranteed_return']:.2f}€ (+{opp.profit_percent:.2f}%)\n")
        else:
            # Versión detallada con JSON (ya no se usa mucho pero se mantiene)
            import json
            print(json.dumps(opp.__dict__, indent=2))

def main():
    parser = argparse.ArgumentParser(description='QuantBet - Sistema de Arbitraje')
    parser.add_argument('--source', default='oddsapi', choices=['csv', 'oddsapi'],
                        help='Fuente de datos (default: oddsapi)')
    parser.add_argument('--mode', default='all',
                        help='Modo de ejecución (actualmente solo "all")')
    parser.add_argument('--simple', action='store_true',
                        help='Salida limpia, sin logs técnicos')
    parser.add_argument('--no-save', action='store_false', dest='save',
                        help='No guardar en base de datos')
    args = parser.parse_args()
    run_pipeline(source=args.source, save=args.save, simple=args.simple)

if __name__ == '__main__':
    main()