import requests, json, market_fetcher
from colorama import Fore as F

class Building:
    def __init__(self, ticker, logging=False):
        self.__ticker = ticker
        try:
            self.__data = requests.get(f'https://rest.fnar.net/building/{ticker}')
            self.__data.raise_for_status()
            self.__data = self.__data.json()
        except requests.HTTPError as e:
            print(f'{F.RED}Ongeldige URL: {F.RESET+e}')
        except:
            print(f'{F.RED}Omzetten naar json onmogelijk.{F.RESET}')
        else:
            self.__build_costs = {}
            for material in self.__data['BuildingCosts']: self.__build_costs[material['CommodityTicker']] = material['Amount']
            self.__area = self.__data['AreaCost']

            self.__workforce = {}
            for work_type in {'pioneers'}

            if logging: print(f'Succesfully fetched {F.BLUE+ticker+F.RESET}')

