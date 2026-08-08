from itertools import product
from typing import List, Dict, Optional, Any
from src.domain.entities import Snapshot

class ArbitrageOpportunity:
    def __init__(self, event_name, sport, market, details, profit, profit_percent):
        self.event_name = event_name
        self.sport = sport
        self.market = market
        self.details = details
        self.profit = profit
        self.profit_percent = profit_percent

class ArbitrageEngine:
    def find_opportunities(self, snapshot: Snapshot) -> List[ArbitrageOpportunity]:
        """
        Encuentra oportunidades de arbitraje para cualquier mercado de 2 o más opciones.
        Devuelve una lista de ArbitrageOpportunity (normalmente una por snapshot).
        """
        outcomes_map = self._group_by_outcome(snapshot.outcomes)
        if len(outcomes_map) < 2:
            return []  # mercado inválido

        outcome_names = list(outcomes_map.keys())
        # Cada outcome tiene una lista de (bookmaker, odds)
        outcome_bookmakers = [outcomes_map[name] for name in outcome_names]

        best_profit = -float('inf')
        best_combination = None
        total_investment = 100.0  # base para calcular stakes proporcionales

        # Producto cartesiano de todos los bookmakers para cada outcome
        for combo in product(*outcome_bookmakers):
            odds_list = [item[1] for item in combo]
            if any(o <= 1.0 for o in odds_list):
                continue
            inv_sum = sum(1/o for o in odds_list)
            if inv_sum < 1.0:
                profit_percent = (1 - inv_sum) * 100
                # Calcular stakes individuales para una inversión total fija
                stakes = []
                for odd in odds_list:
                    stake = (total_investment * (1/odd)) / inv_sum
                    stakes.append(round(stake, 2))
                # Detalles de la combinación
                combo_details = {
                    'outcomes': [],
                    'stakes': [],
                    'total_investment': round(sum(stakes), 2),
                    'guaranteed_return': round(total_investment / inv_sum, 2)
                }
                for (name, (bookmaker, odd)), stake in zip(zip(outcome_names, combo), stakes):
                    combo_details['outcomes'].append({
                        'outcome': name,
                        'bookmaker': bookmaker,
                        'odds': odd,
                        'stake': stake
                    })
                    combo_details['stakes'].append(stake)

                if profit_percent > best_profit:
                    best_profit = profit_percent
                    best_combination = combo_details

        if best_combination is None:
            return []

        opp = ArbitrageOpportunity(
            event_name=snapshot.event_name,
            sport=snapshot.sport,
            market=snapshot.market,
            details=best_combination,
            profit=round(best_combination['guaranteed_return'] - best_combination['total_investment'], 2),
            profit_percent=round(best_profit, 2)
        )
        return [opp]

    def _group_by_outcome(self, outcomes):
        """
        Agrupa los objetos Odds por nombre de outcome.
        Retorna dict: { 'Home': [('Pinnacle', 2.1), ('1xBet', 2.05), ...], ... }
        """
        grouped = {}
        for odds in outcomes:
            if odds.price is None or odds.price <= 0:
                continue
            grouped.setdefault(odds.name, []).append((odds.bookmaker, odds.price))
        return grouped