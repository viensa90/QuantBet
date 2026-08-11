"""Diagnóstico: bookmakers y mercados reales en Premier League (1 petición)."""
import requests
import os
import json
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
key = os.getenv('ODDS_API_KEY')
url = 'https://api.the-odds-api.com/v4/sports/soccer_epl/odds'
params = {
    'apiKey': key,
    'regions': 'eu',
    'markets': 'h2h,totals,spreads',
    'oddsFormat': 'decimal'
}

r = requests.get(url, params=params)
if r.status_code != 200:
    print(f'Error {r.status_code}: {r.text}')
    exit()

data = r.json()
muestra = data[:2] if isinstance(data, list) else data
Path('epl_sample.json').write_text(json.dumps(muestra, indent=2, ensure_ascii=False), encoding='utf-8')
print('✅ Muestra guardada en epl_sample.json')
print(f'Total de eventos: {len(data)}')

bookmakers_set = set()
for game in data[:5]:
    for bk in game.get('bookmakers', []):
        bookmakers_set.add(bk['title'])
print('Bookmakers encontrados (muestra):', ', '.join(sorted(bookmakers_set)))