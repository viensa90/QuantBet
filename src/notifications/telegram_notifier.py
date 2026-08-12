import requests
from datetime import datetime
from src.config_loader import ConfigLoader
from src.logger import get_logger

logger = get_logger(__name__)

BOOKMAKER_EMOJI = {
    'pinnacle': '🟠',
    '1xbet': '🔵',
    'betonline.ag': '🔴',
    'betfair': '🟡',
    'marathonbet': '🟢',
}
FALLBACK_EMOJI = '⚪'

def _format_event_time(event_time):
    if not event_time:
        return "Fecha desconocida"
    try:
        dt = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return event_time

def _format_opportunity(opp) -> str:
    lines = [f"⚽ *{opp.event_name}*"]
    lines.append(f"   Mercado: {opp.market} | Profit: *{opp.profit_percent:.2f}%*")
    event_time_str = _format_event_time(opp.event_time)
    live_info = ""
    if getattr(opp, 'is_live', False):
        minute = opp.match_time if opp.match_time is not None else '?'
        live_info = f" 🔴 EN VIVO {minute}'"
    lines.append(f"   🕒 {event_time_str}{live_info}")
    for outcome in opp.details['outcomes']:
        bookmaker = outcome['bookmaker']
        emoji = BOOKMAKER_EMOJI.get(bookmaker.lower(), FALLBACK_EMOJI)
        lines.append(f"   {emoji} {outcome['outcome']} @ {outcome['odds']} ({bookmaker}) → {outcome['stake']:.2f} €")
    total = opp.details['total_investment']
    retorno = opp.details['guaranteed_return']
    lines.append(f"   💰 Inv: {total:.2f} € | Ret: {retorno:.2f} € | Gan: {opp.profit:.2f} €")
    return "\n".join(lines)

def maybe_notify(opportunities):
    cfg = ConfigLoader()
    token = cfg.telegram_token
    chat_id = cfg.telegram_chat_id
    if not token or not chat_id:
        logger.warning("Telegram no configurado – no se enviarán notificaciones.")
        return

    if not opportunities:
        logger.info("Sin oportunidades, no se envía notificación.")
        return

    header = f"🚀 *QuantBet – {len(opportunities)} oportunidad(es) de arbitraje*"
    parts = [header]
    for opp in opportunities[:10]:
        parts.append(_format_opportunity(opp))
    message = "\n\n".join(parts)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Notificación de Telegram enviada correctamente.")
    except Exception as e:
        logger.error(f"Error al enviar notificación Telegram: {e}")