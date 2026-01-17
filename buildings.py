import requests, json, market_fetcher, workforce_calculator
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
            self.__build_costs, self.__workforce = {}, {}
            for material in self.__data['BuildingCosts']: self.__build_costs[material['CommodityTicker']] = material['Amount']
            for work_type in {'Pioneers', 'Settlers', 'Technicians', 'Engineers', 'Scientists'}:
                if self.__data[work_type]!=0: self.__workforce[work_type] = self.__data[work_type]
            self.__area = self.__data['AreaCost']
            self.__expertise = self.__data['Expertise']
            if logging: print(f'Succesfully fetched {F.BLUE+ticker+F.RESET}')

    def get_build_cost(self, market_identifier='NC1', logging=False):
        price_books = market_fetcher.get_order_books(self.__build_costs, market_identifier, logging)
        cost = 0
        for material in price_books:
            book = price_books[material]
            cost_new = book['Ask'] * self.__build_costs[material]
            if logging: print(f'{self.__build_costs[material]:2} x {material:3}: {cost_new:.2f}')
            cost += cost_new
        if logging: print(f'Total   : {cost:.2f}\n')
        return cost
    
    def get_workforce_cost(self, luxury=set(), market_identifier='NC1', logging=False): # in luxury zitten de types die luxegoederen verdienen
        if logging: print(self.__workforce)
        return workforce_calculator.calculate_upkeep(self.__workforce, luxury, market_identifier, logging)
    
    def get_workforce(self):
        return self.__workforce

    
if __name__=='__main__':
    sme = Building('WEL')
    sme.get_build_cost(logging=True)
    print(sme.get_workforce_cost(logging=True))