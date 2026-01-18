import requests, json, market_fetcher
from colorama import Fore as F

class Recipe:
    def __init__(self, recipe_json):
        self.__data = recipe_json
        self.__inputs, self.__outputs = {}, {}
        for item in recipe_json['Inputs']: self.__inputs[item['CommodityTicker']] = item['Amount']
        for item in recipe_json['Outputs']: self.__outputs[item['CommodityTicker']] = item['Amount']
        self.__timeMs = recipe_json['DurationMs']
        self.__name = recipe_json['RecipeName']

    def get_cost(self, market_identifier='NC1', logging=False):
        out = 0
        for item in self.__inputs: out += market_fetcher.get_ask(item, market_identifier, logging) * self.__inputs[item]
        return out
    
    def get_profit_bruto(self, market_identifier='NC1', logging=False):
        out = 0
        for item in self.__outputs: out += market_fetcher.get_bid(item, market_identifier, logging) * self.__outputs[item]
        return out
    
    def get_profit_net(self, market_identifier='NC1', logging=False):
        return self.get_profit_bruto(market_identifier, logging) - self.get_cost(market_identifier, logging)
    
    def get_daily_profit(self, market_identifier='NC1', logging=False):
        return round(self.get_profit_net(market_identifier, logging) * 86_400_000/self.__timeMs, 2)
    
    def __str__(self):
        return self.__name
    
    def __repr__(self):
        return json.dumps(self.__data, indent=3)


def recipes_from_building(building, logging=False):
    try:
        building = requests.get(f'https://rest.fnar.net/building/{building}')
        building.raise_for_status()
        building = building.json()
    except requests.HTTPError as e:
        print(f'{F.RED}URL ongeldig: {F.RESET+e}')
    except:
        print('Niet omzetbaar naar json.')
    else:
        out = []
        for recipe in building['Recipes']:
            out.append(Recipe(recipe))
            if logging: print(f'Fetched {F.BLUE+recipe["RecipeName"]+F.RESET}')
        if logging: print()
        return out
    
def recipes_from_item(ticker, logging=False):
    try:
        item = requests.get(f'https://rest.fnar.net/recipes/{ticker}')
        item.raise_for_status()
        item = item.json()
    except requests.HTTPError as e:
        print(f'{F.RED}URL ongeldig: {F.RESET+e}')
    except:
        print('Niet omzetbaar naar json.')
    else:
        out = []
        for recipe in item:
            out.append(Recipe(recipe))
            if logging: print(f'Fetched {F.BLUE+recipe["RecipeName"]+F.RESET}')
        if logging: print()
        return out
    
if __name__=='__main__':
    rec = recipes_from_building('SME')
    for r in rec:
        print(r, r.get_daily_profit())