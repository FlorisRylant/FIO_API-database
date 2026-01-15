import requests, json
from colorama import Fore as F

BUILDING_TO_CHECK = 'WEL' # geen COL, EXT of RIG want die hun receptenlijst hangt af van de planeet

try:
    recipes = requests.get('https://rest.fnar.net/recipes/allrecipes')
    recipes.raise_for_status()
    recipes = recipes.json()
except requests.HTTPError as e:
    print(f'URL werkt niet meer: {e}')

# brandstofkost per rit berekenen, 72 SF is een dag reizen dus prima (max 1 rit heen en 1 terug per dag)
try:
    fuel = requests.get('https://rest.fnar.net/exchange/SF.NC1')
    fuel.raise_for_status()
    fuel = fuel.json()
except requests.HTTPError as e:
    print(f'brandstof-URL werkt niet meer: {e}')
fuel = round(fuel['Ask'], 2) * 144 # berekent brandstofkost (heen en terug)
print(f'{F.MAGENTA}Fuel: {fuel:.2f}/trip{F.RESET}')

# vist enkel de nuttige recepten eruit
i = 0
while i < len(recipes):
    if recipes[i]['BuildingTicker']==BUILDING_TO_CHECK: i += 1
    else: del recipes[i]

# zoekt uit welke items er voorkomen in de recepten
items_to_request = set()
for recipe in recipes:
    for item in recipe['Inputs']: items_to_request.add(item['Ticker'])
    for item in recipe['Outputs']: items_to_request.add(item['Ticker'])
    print(f'{F.BLUE}{recipe["RecipeName"]}{F.RESET} opgeslagen')
print(f'\nRequesting {items_to_request}...\n')

# blok om alle prijzen te vinden
# dit deel kan nog uitgerust worden met voorspellingsdingen over de prijzen in de toekomst (maar dat is lastig)
item_info = {}
for item in items_to_request:
    item_info[item] = {'buying':-0.00, 'selling':1_234_567_890} # maakt normaal gezien alles waar geen koper / aanbieder is onmogelijk duur
    try:
        price_book = requests.get(f'https://rest.fnar.net/exchange/{item}.NC1')
        price_book.raise_for_status()
        price_book = price_book.json()
        material_info = requests.get(f'https://rest.fnar.net/material/{item}')
        material_info.raise_for_status()
        material_info = material_info.json()
    except requests.HTTPError as e:
        print(f'{item} kan niet opgezocht worden: {e}')

    for order in price_book['BuyingOrders']:
        item_info[item]['buying'] = max(round(order['ItemCost'], 2), item_info[item]['buying'])
    for order in price_book['SellingOrders']:
        item_info[item]['selling'] = min(round(order['ItemCost'], 2), item_info[item]['selling'])
    item_info[item]['mass'] = round(material_info['Weight'], 4)
    item_info[item]['volume'] = round(material_info['Volume'], 4)
    print(f'{F.BLUE}{item:3}{F.RESET} fetched, {item_info[item]}')
print()

# berekent de waardes van de recepten (hier komt de rangschikking uit, later moeten werkkosten enzo er nog af)
max_profit = 0.0 # per dag
best_recipe = None
for recipe in recipes:
    cost, gain, vol_in, mass_in, vol_out, mass_out = 0, 0, 0, 0, 0, 0
    cycles = 86_400_000/recipe['TimeMs'] # aantal cyclussen op een dag
    for item in recipe['Inputs']:
        cost += item_info[item['Ticker']]['selling'] * item['Amount']
        vol_in += item_info[item['Ticker']]['volume'] * item['Amount']
        mass_in += item_info[item['Ticker']]['mass'] * item['Amount']
    for item in recipe['Outputs']:
        gain += item_info[item['Ticker']]['buying'] * item['Amount']
        vol_out += item_info[item['Ticker']]['volume'] * item['Amount']
        mass_out += item_info[item['Ticker']]['mass'] * item['Amount']
    cost, gain, transport = cost * cycles, gain * cycles, max(vol_in, vol_out, mass_in, mass_out) * cycles # transport = tonnage / volume per dag te vervoeren
    cost += (transport/500)*fuel # telt brandstofkost erbij
    profit = round(gain-cost,0)
    color = F.GREEN if profit>0 else F.RED
    print(f'{F.BLUE}{recipe["RecipeName"]:30}{F.RESET} {F.MAGENTA}({transport:<3.0f}ton/m3 ={(transport/500)*fuel:4.0f}){F.RESET}: {gain:.2f} - {cost:.2f} = {color}{gain-cost:.2f}{F.RESET} / 24h ({cycles:.1f} cycles/24h)')
    if profit > max_profit:
        best_recipe = recipe
        max_profit = profit

print(json.dumps(best_recipe,indent=3), max_profit, sep='\n')