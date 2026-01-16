import requests, json

# supplies nodig / 100 arbeiders:
supplies = {
    'pioneers'   :{'base':{'DW':4, 'RAT':4, 'OVE':0.5},                         'luxury':{'COF':0.5, 'PWO':0.2}},
    'settlers'   :{'base':{'DW':5, 'RAT':6, 'EXO':0.5, 'PT':0.5},               'luxury':{'KOM':1, 'REP':0.2}  },
    'technicians':{'base':{'DW':7.5, 'RAT':7, 'MED':0.5, 'HMS':0.5, 'SCN':0.1}, 'luxury':{'ALE':1, 'SC':0.1}   },
    'engineers'  :{'base':{'DW':10, 'FIM':7, 'MED':0.5, 'HSS':0.2, 'PDA':0.1},  'luxury':{'GIN':1, 'VG':0.2}   },
    'scientists' :{'base':{'DW':10, 'MEA':7, 'MED':0.5, 'LC':0.2, 'WS':0.1},    'luxury':{'WIN':1, 'NST':0.1}  }
}

def get_market_info(ticker, market_identifier='NC1', logging=False):
    try:
        order_book = requests.get(f"https://rest.fnar.net/exchange/{ticker}.{market_identifier}")
        order_book.raise_for_status()
    except requests.HTTPError as e:
        print(f'Ongeldige url (regel 14): {e}')
        return None
    order_book = order_book.json()
    if logging: print(f'{ticker:3} fetched: selling @{order_book["Ask"]:.2f} {order_book["Currency"]}')
    return order_book['Ask']

# deze functie is redelijk efficiënt door nul extra info te geven buiten de onderhoudskost
def calculate_upkeep(workers, luxury={}, market_identifier='NC1', logging=False):
    needed_items = {}
    for work_type in workers:
        for item in supplies[work_type]['base']:
            needed_items[item] = needed_items.get(item, 0) + supplies[work_type]['base'][item] * workers[work_type]/100
        if luxury.get(work_type, False): # als een class niet opgegeven is in 'luxury' wordt die niet meegeteld
            for item in supplies[work_type]['luxury']:
                needed_items[item] = needed_items.get(item, 0) + supplies[work_type]['luxury'][item] * workers[work_type]/100
    if logging: print(f'Fetch-list made: {needed_items}\n')
    cost = 0
    for item in needed_items:
        cost += needed_items[item]*get_market_info(item, market_identifier, logging)
    return round(cost)

# minder efficiënt, meer info
def upkeep_rapport(workers, luxury={}, market_identifier='NC1', logging=False):
    items_needed = set()
    for work_type in workers:
        for item in supplies[work_type]['base']: items_needed.add(item)
        if luxury.get(work_type, False): # als een class niet opgegeven is in 'luxury' wordt die niet meegeteld
            for item in supplies[work_type]['luxury']: items_needed.add(item)
    if logging: print(f'Fetch-list made: {items_needed}\n')
    supply_prices = {}
    for item in items_needed: supply_prices[item] = get_market_info(item, market_identifier, logging)
    if logging: print()
    total = 0
    for work_type in workers:
        cost = calculate_upkeep({work_type:workers[work_type]}, luxury, market_identifier)
        total += cost
        print(f'{work_type:12}|{workers[work_type]:4} | {cost:.2f}')
    print('-'*30, f'\ntotal:', ' '*12, f'{total:.2f}\n')


upkeep_rapport({'pioneers':160, 'settlers':50}, luxury={'pioneers':True})