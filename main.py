import argparse
import sys
import traceback
from datetime import datetime
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

def run_pipeline(source='oddsapi', save=True, simple=False, log_file=None):
    config = ConfigLoader()
    log_level = _logging.WARNING if simple else _logging.INFO
    _logging.getLogger().setLevel(log_level)

    # Redirigir la salida estándar a un StringIO para capturarla
    import io
    captured_output = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = captured_output

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

        if valid_opps:
            try:
                maybe_notify(valid_opps)
            except Exception as e:
                logger.error(f"Error enviando notificación: {e}")

        # Escribir resumen al archivo de log (si se pidió)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(summary_lines) + '\n')

        # Imprimir en consola (para ejecuciones manuales)
        for line in summary_lines:
            print(line)

    except Exception as e:
        # Si algo falla, escribir el error en el log y en consola
        error_msg = f"\n❌ Error en pipeline: {e}\n{traceback.format_exc()}\n"
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(error_msg)
        print(error_msg)
    finally:
        sys.stdout = original_stdout

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
    parser.add_argument('--log-file', type=str, default=None,
                        help='Archivo donde guardar el resumen de la ejecución')
    args = parser.parse_args()
    run_pipeline(source=args.source, save=args.save, simple=args.simple, log_file=args.log_file)

if __name__ == '__main__':
    main()