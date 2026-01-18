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
    if logging: print(f'Fetched {F.BLUE+ticker+F.RESET} from {F.BLUE+market_identifier+F.RESET}.')
    return order_book

def get_price_chart(ticker, market_identifier='NC1', logging=False):
    try:
        chart = requests.get(f'https://rest.fnar.net/exchange/cxpc/{ticker}.{market_identifier}')
        chart.raise_for_status()
        chart = chart.json()
    except requests.HTTPError as e:
        print(f'URL ongeldig: {e}')
    except:
        print(f'Omzetten naar json mislukt, kijk de URL na.')
    if logging: print(f'Fetched {F.BLUE+ticker+F.RESET} charts from {F.BLUE+market_identifier+F.RESET}.')
    return chart

def filter_chart(chart, interval="DAY_ONE", n=100):
    # enkel laatste n datapunten: achterstevoren door de (al gesorteerde) datalijst gaan
    data_points = []
    i = len(chart)-1
    while len(data_points) < n and i >= 0:
        if chart[i]['Interval'] == interval: data_points.append(chart[i])
        i -= 1
    return data_points[::-1] # terug van oud naar recent

def plot_chart(data, logging=False): # omdat matplotlib uitzoeken offline een hel is programmeer ik nog liever zelf een plotter
    if len(data) > 150:
        if logging: print(f'Te veel datapunten ({len(data)} gegeven, max 150)')
        plot_chart(data[len(data)-150:], logging)
        return None
    height = (int(len(data)/6)//3)*3 # om een ongeveer mooie aspect ratio te hebben van de grafiek: elke drie regels een tick
    high_bound, low_bound = 0, 1_234_567_890
    for datapoint in data:
        if datapoint['Low'] < low_bound: low_bound = datapoint['Low']
        if datapoint['High'] > high_bound: high_bound = datapoint['High']
    line_increment = round((high_bound-low_bound)/(height*0.8), 2)
    line_zero = low_bound-line_increment
    for line in range(height, -1, -1):
        line_val = (line_zero + line*line_increment) # de waarde van die lijn
        out = ''
        if line%3==0: out += f'{F.RESET}{line_val:8.2f} |'
        else: out += ' '*8 + ' |'
        for datapoint in data:
            color = F.RED if datapoint['Close'] < datapoint['Open'] else F.GREEN
            if min(datapoint['Close'], datapoint['Open']) <= line_val <= max(datapoint['Close'], datapoint['Open'])+line_increment/2:
                out += f'{color}#'
            elif datapoint['Low'] <= line_val <= datapoint['High']:
                out += f'{color}|'
            else: out += ' '
        out += f'{F.RESET}|'
        print(out)
    print()
        

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
    print(get_order_books(['SF', 'FF']), '\n')
    plot_chart(filter_chart(get_price_chart('ALO'), interval='DAY_THREE', n=180))