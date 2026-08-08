import sys
import json
sys.path.append('.')
from src.storage.database import Database
from src.storage.repository import Repository

def main():
    db = Database()
    repo = Repository(db)
    opportunities = repo.get_opportunities(limit=50)
    for opp in opportunities:
        print(f"ID: {opp['id']} | {opp['event_name']} | {opp['market']} | Profit: {opp['profit_percent']:.2f}%")
        details = json.loads(opp['details'])
        for outcome in details['outcomes']:
            print(f"   {outcome['outcome']}: {outcome['bookmaker']} @ {outcome['odds']} (Stake: {outcome['stake']})")
        print(f"   Total invest: {details['total_investment']} → Return: {details['guaranteed_return']}\n")

if __name__ == '__main__':
    main()