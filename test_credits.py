import requests, os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('ODDS_API_KEY')
url = 'https://api.the-odds-api.com/v4/sports/soccer_epl/odds'
params = {
    'apiKey': key,
    'regions': 'eu',
    'markets': 'h2h,totals,spreads',
    'dateFormat': 'iso',
    'oddsFormat': 'decimal'
}

print("Haciendo 1 petición con 3 mercados...")
r = requests.get(url, params=params)
print("Status:", r.status_code)
print("Headers relevantes:")
for h in ['x-requests-used', 'x-requests-remaining', 'x-requests-limit']:
    print(f"  {h}: {r.headers.get(h, 'NO PRESENTE')}")
print("Fin.")