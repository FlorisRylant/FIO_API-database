import requests, json
from colorama import Fore as F

def get_order_book(ticker, market_identifier='NC1', logging=False):
    try:
        order_book = requests.get(f'https://rest.fnar.net/exchange/{ticker}.{market_identifier}')
        order_book.raise_for_status()
        order_book = order_book.json()
    except requests.HTTPError as e:
        print(f'URL ongeldig: {e}')
    except:
        print(f'Omzetten naar json mislukt, kijk de URL na.')
    if logging: print(f'Fetched {F.BLUE+ticker+F.RESET} from {F.BLUE+order_book["ExchangeName"]+F.RESET}.')
    return order_book

def get_ask(ticker, market_identifier='NC1', logging=False):
    """Deze functie gaat eerst naar de website via fetch_order_book
    => enkel gebruiken als je enkel de vraagprijs nodig hebt voor efficiëntie"""
    out = get_order_book(ticker, market_identifier, logging).get('Ask', 1_234_567_890)
    if out==None: return 1_234_567_890
    else: return out

def get_bid(ticker, market_identifier='NC1', logging=False):
    """Deze functie gaat eerst naar de website via fetch_order_book
    => enkel gebruiken als je enkel de aangeboden prijs nodig hebt voor efficiëntie"""
    out = get_order_book(ticker, market_identifier, logging).get('Bid', 0)
    if out==None: return 0
    else: return out

def get_currency(market_identifier):
    return {'NC1':'NCC', 'CI1':'CIS', 'IC1':'ICA', 'AI1':'AIC', 'NC2':'NCC', 'CI2':'CIS'}[market_identifier]

def get_order_books(tickers, market_identifier='NC1', logging=False): # voor meerdere dingen
    if not type(tickers)==set:
        try:
            tickers = set(tickers)
        except:
            print(f'Kan {tickers} niet omzetten naar een set')
            return None
    out = {}
    for ticker in tickers: out[ticker] = get_order_book(ticker, market_identifier, logging)
    return out

if __name__ == '__main__':
    print(get_order_books(['SF', 'FF']))