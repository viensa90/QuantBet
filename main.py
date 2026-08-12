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

def _format_event_time(event_time):
    if not event_time:
        return "Fecha desconocida"
    try:
        dt = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return event_time

def run_pipeline(source='oddsapi', save=True, simple=False, log_file=None):
    config = ConfigLoader()
    log_level = _logging.WARNING if simple else _logging.INFO
    _logging.getLogger().setLevel(log_level)

    file_handler = None
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = _logging.FileHandler(log_path, mode='w', encoding='utf-8')
        file_handler.setLevel(_logging.INFO)
        root_logger = _logging.getLogger()
        if root_logger.handlers:
            file_handler.setFormatter(root_logger.handlers[0].formatter)
        api_key = config.odds_api_key
        if api_key:
            mask_filter = _logging.Filter()
            # simple masking: no usamos formateador especial, solo filtramos en el mensaje
            def filter_record(record, key=api_key):
                record.msg = str(record.msg).replace(key, '***')
                return True
            file_handler.addFilter(filter_record)
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

        summary_lines = []
        if not valid_opps:
            summary_lines.append("\n🔍 No se encontraron oportunidades de arbitraje.\n")
        else:
            summary_lines.append(f"\n🎯 {len(valid_opps)} OPORTUNIDADES DE ARBITRAJE DETECTADAS\n")
            for opp in valid_opps:
                event_time_str = _format_event_time(opp.event_time)
                live_info = ""
                if getattr(opp, 'is_live', False):
                    minute = opp.match_time if opp.match_time is not None else '?'
                    live_info = f" 🔴 EN VIVO {minute}'"
                summary_lines.append(f"⚽ {opp.event_name} ({opp.sport}) – {opp.market}")
                summary_lines.append(f"   🕒 {event_time_str}{live_info}")
                for outcome in opp.details['outcomes']:
                    summary_lines.append(f"   {outcome['outcome']}: {outcome['bookmaker']} @ {outcome['odds']} (Stake: {outcome['stake']:.2f}€)")
                summary_lines.append(f"   Inversión total: {opp.details['total_investment']:.2f}€ → Retorno: {opp.details['guaranteed_return']:.2f}€ (+{opp.profit_percent:.2f}%)\n")

        # Escribir resumen en archivo
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
    parser.add_argument('--source', default='oddsapi', choices=['csv', 'oddsapi'], help='Fuente de datos')
    parser.add_argument('--mode', default='all', help='Modo de ejecución')
    parser.add_argument('--simple', action='store_true', help='Salida limpia en consola')
    parser.add_argument('--no-save', action='store_false', dest='save', help='No guardar en base de datos')
    parser.add_argument('--log-file', type=str, default=None, help='Archivo de log completo')
    args = parser.parse_args()
    run_pipeline(source=args.source, save=args.save, simple=args.simple, log_file=args.log_file)

if __name__ == '__main__':
    main()