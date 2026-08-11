import argparse
import sys
import traceback
import re
from pathlib import Path
from src.config_loader import ConfigLoader
from src.logger import get_logger
from src.connectors.factory import ConnectorFactory
from src.core.arbitrage import ArbitrageEngine
from src.storage.database import Database
from src.storage.repository import Repository
from src.notifications.telegram_notifier import maybe_notify
import logging as _logging

logger = get_logger(__name__)

class ApiKeyMaskingFilter(_logging.Filter):
    """Filtro que reemplaza la API key por '***' en los mensajes de log."""
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

    def filter(self, record):
        if self.api_key and hasattr(record, 'msg'):
            record.msg = str(record.msg).replace(self.api_key, '***')
        return True

def run_pipeline(source='oddsapi', save=True, simple=False, log_file=None):
    config = ConfigLoader()
    log_level = _logging.WARNING if simple else _logging.INFO
    _logging.getLogger().setLevel(log_level)

    # Añadir FileHandler con nivel INFO fijo (para guardar todos los detalles)
    file_handler = None
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = _logging.FileHandler(log_path, mode='w', encoding='utf-8')
        file_handler.setLevel(_logging.INFO)  # siempre INFO, sin importar --simple
        root_logger = _logging.getLogger()
        # Usar el mismo formateador JSON que la consola
        if root_logger.handlers:
            file_handler.setFormatter(root_logger.handlers[0].formatter)
        # Añadir filtro para enmascarar API key
        api_key = config.odds_api_key
        if api_key:
            mask_filter = ApiKeyMaskingFilter(api_key)
            file_handler.addFilter(mask_filter)
        root_logger.addHandler(file_handler)

    try:
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
            new_opps = repo.save_opportunities(opp_dicts, dedup_window_hours=dedup_window)
            final_opps = [o for o in valid_opps if any(
                o.event_name == no['event_name'] and o.market == no['market'] and o.profit_percent == no['profit_percent']
                for no in new_opps
            )]
            valid_opps = final_opps

        # Construir resumen
        summary_lines = []
        if not valid_opps:
            summary_lines.append("\n🔍 No se encontraron oportunidades de arbitraje.\n")
        else:
            summary_lines.append(f"\n🎯 {len(valid_opps)} OPORTUNIDADES DE ARBITRAJE DETECTADAS\n")
            for opp in valid_opps:
                summary_lines.append(f"⚽ {opp.event_name} ({opp.sport}) – {opp.market}")
                if simple:
                    for outcome in opp.details['outcomes']:
                        summary_lines.append(f"   {outcome['outcome']}: {outcome['bookmaker']} @ {outcome['odds']} (Stake: {outcome['stake']:.2f}€)")
                    summary_lines.append(f"   Inversión total: {opp.details['total_investment']:.2f}€ → Retorno: {opp.details['guaranteed_return']:.2f}€ (+{opp.profit_percent:.2f}%)\n")
                else:
                    import json
                    summary_lines.append(json.dumps(opp.__dict__, indent=2))

        # Escribir resumen en el archivo de log (además de lo que ya capturó el FileHandler)
        if file_handler:
            file_handler.stream.write('\n'.join(summary_lines) + '\n')

        # Imprimir en consola
        for line in summary_lines:
            print(line)

        if valid_opps:
            try:
                maybe_notify(valid_opps)
            except Exception as e:
                logger.error(f"Error enviando notificación: {e}")

    except Exception as e:
        error_msg = f"\n❌ Error en pipeline: {e}\n{traceback.format_exc()}\n"
        print(error_msg)
        if file_handler:
            file_handler.stream.write(error_msg)
    finally:
        if file_handler:
            root_logger = _logging.getLogger()
            root_logger.removeHandler(file_handler)
            file_handler.close()

def main():
    parser = argparse.ArgumentParser(description='QuantBet - Sistema de Arbitraje')
    parser.add_argument('--source', default='oddsapi', choices=['csv', 'oddsapi'],
                        help='Fuente de datos (default: oddsapi)')
    parser.add_argument('--mode', default='all',
                        help='Modo de ejecución (actualmente solo "all")')
    parser.add_argument('--simple', action='store_true',
                        help='Salida limpia en consola (logs técnicos solo en archivo)')
    parser.add_argument('--no-save', action='store_false', dest='save',
                        help='No guardar en base de datos')
    parser.add_argument('--log-file', type=str, default=None,
                        help='Archivo donde guardar el registro COMPLETO (con API key enmascarada)')
    args = parser.parse_args()
    run_pipeline(source=args.source, save=args.save, simple=args.simple, log_file=args.log_file)

if __name__ == '__main__':
    main()