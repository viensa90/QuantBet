import argparse
import sys
from src.config_loader import ConfigLoader
from src.logger import get_logger
from src.connectors.factory import ConnectorFactory
from src.core.arbitrage import ArbitrageEngine
from src.storage.database import Database
from src.storage.repository import Repository
from src.notifications.telegram_notifier import maybe_notify
import logging as _logging

logger = get_logger(__name__)

def run_pipeline(source='oddsapi', save=True, simple=False):
    config = ConfigLoader()
    log_level = _logging.WARNING if simple else _logging.INFO
    _logging.getLogger().setLevel(log_level)

    engine = ArbitrageEngine()
    db = Database()
    repo = Repository(db)

    provider = ConnectorFactory.create(source, config._config)
    snapshots = provider.get_events()

    all_opportunities = []
    for snap in snapshots:
        opps = engine.find_opportunities(snap)
        all_opportunities.extend(opps)

    min_profit = config['arbitrage']['min_profit_percent']
    valid_opps = [o for o in all_opportunities if o.profit_percent >= min_profit]

    # Deduplicación
    dedup_window = config['pipeline'].get('dedup_window_hours', 1)
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
        # Guardar y obtener solo las nuevas
        new_opps = repo.save_opportunities(opp_dicts, dedup_window_hours=dedup_window)
        # Convertir de dict a objetos para la notificación y el resumen
        final_opps = [o for o in valid_opps if any(
            o.event_name == no['event_name'] and o.market == no['market'] and o.profit_percent == no['profit_percent']
            for no in new_opps
        )]
        valid_opps = final_opps
    else:
        dedup_window = None

    print_summary(valid_opps, simple)

    if valid_opps:
        try:
            maybe_notify(valid_opps)
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