import requests, json

# supplies needed / 100 workers:
supplies = {
    'pioneers'   :{'base':{'DW':4, 'RAT':4, 'OVE':0.5},                         'luxury':{'COF':0.5, 'PWO':0.2}},
    'settlers'   :{'base':{'DW':5, 'RAT':6, 'EXO':0.5, 'PT':0.5},               'luxury':{'KOM':1, 'REP':0.2}  },
    'technicians':{'base':{'DW':7.5, 'RAT':7, 'MED':0.5, 'HMS':0.5, 'SCN':0.1}, 'luxury':{'ALE':1, 'SC':0.1}   },
    'engineers'  :{'base':{'DW':10, 'FIM':7, 'MED':0.5, 'HSS':0.2, 'PDA':0.1},  'luxury':{'GIN':1, 'VG':0.2}   },
    'scientists' :{'base':{'DW':10, 'MEA':7, 'MED':0.5, 'LC':0.2, 'WS':0.1},    'luxury':{'WIN':1, 'NST':0.1}  }
}

def get_market_info(ticker, market_identifier='NC1'):
    try:
        order_book = requests.get(f"https://rest.fnar.net/exchange/{ticker}.{market_identifier}")
        order_book.raise_for_status()
    except requests.HTTPError as e:
        print(f'Ongeldige url (regel 14): {e}')
        return None
    order_book = order_book.json()
    return order_book['Bid']

# deze functie is redelijk efficiënt door nul extra info te geven buiten de onderhoudskost
def calculate_upkeep(workers, luxury={'pioneers':False, 'settlers':False, 'technicians':False, 'engineers':False, 'scientists':False}):
    needed_items = {}
    for work_type in workers:
        for item in supplies[work_type]['base']:
            needed_items[item] = needed_items.get(item, 0) + supplies[work_type]['base'][item] * workers[work_type]/100
        if luxury.get(work_type, False):
            for item in supplies[work_type]['luxury']:
                needed_items[item] = needed_items.get(item, 0) + supplies[work_type]['luxury'][item] * workers[work_type]/100
    cost = 0
    for item in needed_items:
        cost += needed_items[item]*get_market_info(item)
    return round(cost)

print(calculate_upkeep({'pioneers':70}))