from itertools import product
from typing import List, Any

class ArbitrageOpportunity:
    def __init__(self, event_name, sport, market, details, profit, profit_percent,
                 event_time=None, is_live=False, match_time=None):
        self.event_name = event_name
        self.sport = sport
        self.market = market
        self.details = details
        self.profit = profit
        self.profit_percent = profit_percent
        self.event_time = event_time
        self.is_live = is_live
        self.match_time = match_time

class ArbitrageEngine:
    def find_opportunities(self, event: Any) -> List[ArbitrageOpportunity]:
        outcomes_map = {}
        for oc in event.outcomes:
            key = (oc.name, oc.point)
            outcomes_map.setdefault(key, []).append((oc.bookmaker, oc.price))

        if len(outcomes_map) < 2:
            return []

        outcome_keys = list(outcomes_map.keys())
        outcome_bookmakers = [outcomes_map[key] for key in outcome_keys]

        best_profit = -float('inf')
        best_combination = None
        total_investment = 100.0

        for combo in product(*outcome_bookmakers):
            odds_list = [item[1] for item in combo]
            if any(o <= 1.0 for o in odds_list):
                continue
            inv_sum = sum(1/o for o in odds_list)
            if inv_sum < 1.0:
                profit_percent = (1 / inv_sum - 1) * 100
                stakes = []
                for odd in odds_list:
                    stake = (total_investment * (1/odd)) / inv_sum
                    stakes.append(round(stake, 2))
                combo_details = {
                    'outcomes': [],
                    'total_investment': round(sum(stakes), 2),
                    'guaranteed_return': round(total_investment / inv_sum, 2),
                    'event_time': getattr(event, 'timestamp', None),
                    'is_live': getattr(event, 'is_live', False),
                    'match_time': getattr(event, 'match_time', None)
                }
                for (name, point), (bookmaker, odd), stake in zip(outcome_keys, combo, stakes):
                    label = name
                    if point is not None:
                        label = f"{name} {point}"
                    combo_details['outcomes'].append({
                        'outcome': label,
                        'bookmaker': bookmaker,
                        'odds': odd,
                        'stake': stake
                    })

                if profit_percent > best_profit:
                    best_profit = profit_percent
                    best_combination = combo_details

        if best_combination is None:
            return []

        opp = ArbitrageOpportunity(
            event_name=event.event_name,
            sport=event.sport,
            market=event.market,
            details=best_combination,
            profit=round(best_combination['guaranteed_return'] - best_combination['total_investment'], 2),
            profit_percent=round(best_profit, 2),
            event_time=getattr(event, 'timestamp', None),
            is_live=getattr(event, 'is_live', False),
            match_time=getattr(event, 'match_time', None)
        )
        return [opp]