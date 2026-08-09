import itertools
from typing import List, Dict, Tuple, Union
from src.domain.entities import Outcome
from src.logger import log


# Colores ANSI para cada bookmaker (puedes ajustarlos a tu gusto)
BOOKMAKER_COLORS = {
    'pinnacle': '\033[34m',      # azul
    'onexbet': '\033[38;5;208m', # naranja
    'betonlineag': '\033[32m',   # verde
    'betfair': '\033[33m',       # amarillo
}
RESET_COLOR = '\033[0m'


class ArbitrageOpportunity:
    def __init__(self, event_name: str, market: str, outcomes: List[Union[Dict, Tuple]], profit_percent: float):
        self.event_name = event_name
        self.market = market
        self.outcomes = outcomes
        self.profit_percent = profit_percent

    def _parse_outcome(self, outcome):
        """Convierte cualquier formato de outcome a (bookmaker, name, price)."""
        if isinstance(outcome, dict):
            return outcome['bookmaker'], outcome['name'], outcome['price']
        # tuple: (bookmaker, name, price, point?)
        return outcome[0], outcome[1], outcome[2]

    def _calculate_stakes(self, total_stake=100.0):
        """Calcula la distribución de apuestas para garantizar el mismo retorno."""
        inverse_sum = 0.0
        prices = []
        for outcome in self.outcomes:
            _, _, price = self._parse_outcome(outcome)
            inverse_sum += 1.0 / price
            prices.append(price)
        stakes = []
        for price in prices:
            stake = total_stake * (1.0 / price) / inverse_sum
            stakes.append(stake)
        retorno = total_stake / inverse_sum
        return stakes, retorno

    def _colorize(self, bookmaker: str) -> str:
        color = BOOKMAKER_COLORS.get(bookmaker.lower(), '')
        return f"{color}{bookmaker}{RESET_COLOR}"

    def summary(self):
        lines = [f"⚽ {self.event_name}"]
        lines.append(f"   Mercado {self.market} | Profit {self.profit_percent:.2f}%")
        stakes, retorno = self._calculate_stakes(100.0)
        for i, outcome in enumerate(self.outcomes):
            bookmaker, name, price = self._parse_outcome(outcome)
            stake = stakes[i]
            bm_display = self._colorize(bookmaker)
            lines.append(f"   {name:<20} @{price:.2f} ({bm_display:<40}) -> ${stake:.2f}")
        lines.append(f"   Inversión total: $100.00 | Retorno: ${retorno:.2f} | Ganancia: ${retorno - 100:.2f}")
        return "\n".join(lines)

    def detail(self):
        return self.summary()


class ArbitrageEngine:
    def __init__(self):
        pass

    def find_opportunities(self, outcomes: List[Outcome], min_profit: float = 0.015) -> List[ArbitrageOpportunity]:
        """
        Agrupa outcomes por (event_name, market, point) y busca combinaciones de bookmakers
        que cubran todos los resultados (arbitraje).
        """
        # Agrupar por clave: (event_name, market, point)
        grouped = {}
        for o in outcomes:
            key = (o.event_name, o.market, o.point)
            grouped.setdefault(key, []).append(o)

        opportunities = []
        for (event, market, point), group in grouped.items():
            # Ignorar mercados con _lay (ya filtrados aguas arriba)
            # Separar por nombre de resultado (equipo 1, empate, equipo 2, Over, Under...)
            by_name = {}
            for o in group:
                name = o.name
                by_name.setdefault(name, []).append(o)

            # Si no hay suficientes nombres diferentes, no hay oportunidad
            if len(by_name) < 2:
                continue

            # Obtener todas las combinaciones de bookmakers que cubren todos los nombres
            names = list(by_name.keys())
            # Para cada nombre tenemos una lista de outcomes (con sus bookmakers)
            # Queremos elegir un outcome por nombre, de distinto bookmaker, pero el motor actual
            # permite que una casa aparezca en varios nombres? El arbitraje clásico requiere una apuesta por nombre,
            # y no hay problema si el mismo bookmaker ofrece dos cuotas para el mismo evento, pero normalmente no se puede.
            # Por simplicidad tomamos la mejor cuota disponible para cada nombre (la más alta).
            best_odds = {}
            for name, lst in by_name.items():
                best = max(lst, key=lambda x: x.price)
                best_odds[name] = best

            # Verificar si existe arbitraje: sum(1/price) < 1
            inverse_sum = sum(1.0 / best_odds[name].price for name in names)
            if inverse_sum < 1:
                profit = (1.0 / inverse_sum) - 1.0
                if profit >= min_profit:
                    # Construir lista de outcomes seleccionados (tupla: bookmaker, name, price, point)
                    arb_outcomes = []
                    for name in names:
                        o = best_odds[name]
                        arb_outcomes.append((o.bookmaker, o.name, o.price, o.point))
                    opportunities.append(
                        ArbitrageOpportunity(event, market, arb_outcomes, profit * 100)
                    )

        return opportunities