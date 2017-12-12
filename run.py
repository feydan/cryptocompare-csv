import click
import csv
import cryptocompare
import pprint

# Cryptocompare code
import sys
import requests
import time
import datetime

@click.command()
@click.option('--file', default='results.csv', help='File name to save to.')
def get(file):
    header_written = False

    coin_list = cryptocompare.get_coin_list(format=False)
    i = 0
    for symbol in coin_list:
        i += 1
        print('Processing ' + symbol + ' ' + str(i) + '/' + str(len(coin_list)))
        symbolTotal = 0
        try:
            histohour_price_data = get_histohour_price(symbol)['Data']

            while (True):
                # if one closing price is not 0, request more data
                more_data = False

                lastKey = len(histohour_price_data) - 1
                del histohour_price_data[lastKey]

                for row in histohour_price_data:
                    row['date_string'] = datetime.datetime.fromtimestamp(row['time']).strftime('%Y-%m-%d %H:%M:%S')
                    row['symbol'] = symbol
                    if float(row['close']) > 0:
                        more_data = True
                
                if (more_data == False):
                    break

                if not header_written:
                    save_csv(histohour_price_data, file)
                    header_written = True
                else:
                    append_csv(histohour_price_data, file)

                symbolTotal += len(histohour_price_data)

                ts = int(histohour_price_data[0]['time'])
                histohour_price_data = get_histohour_price(symbol, CURR, ts)['Data']
        except:
            print('Error with symbol ' + str(symbol))

        print('Wrote ' + str(symbolTotal) + ' lines for ' + symbol)
        print('')

def save_csv(data, file):
    pprint.pprint(data)
    pprint.pprint(file)
    with open(file, 'w') as csv_file:
        wr = csv.writer(csv_file, delimiter=',')
        # write header
        first = next (iter (data))
        wr.writerow(list(first.keys()))
        for row in data:
            wr.writerow(list(row.values()))

def append_csv(data, file):
    with open(file, 'a') as csv_file:
        wr = csv.writer(csv_file, delimiter=',')
        for row in data:
            wr.writerow(list(row.values()))


# Cryptocompare code

# API
URL_COIN_LIST = 'https://www.cryptocompare.com/api/data/coinlist/'
URL_PRICE = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms={}'
URL_PRICE_MULTI = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms={}'
URL_PRICE_MULTI_FULL = 'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms={}'
URL_HIST_PRICE = 'https://min-api.cryptocompare.com/data/pricehistorical?fsym={}&tsyms={}&ts={}'
URL_HISTODAY_PRICE = 'https://min-api.cryptocompare.com/data/histoday?fsym={}&tsym={}'
URL_HISTOHOUR_PRICE = 'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym={}&toTs={}&limit=2000'
URL_AVG = 'https://min-api.cryptocompare.com/data/generateAvg?fsym={}&tsym={}&markets={}'

# FIELDS
PRICE = 'PRICE'
HIGH = 'HIGH24HOUR'
LOW = 'LOW24HOUR'
VOLUME = 'VOLUME24HOUR'
CHANGE = 'CHANGE24HOUR'
CHANGE_PERCENT = 'CHANGEPCT24HOUR'
MARKETCAP = 'MKTCAP'

# DEFAULTS
CURR = 'USD'

###############################################################################

def query_cryptocompare(url,errorCheck=True):
    try:
        response = requests.get(url).json()
    except Exception as e:
        print('Error getting coin information. %s' % str(e))
        return None
    if errorCheck and 'Response' in response.keys() and response['Response'] != 'Success':
        print('[ERROR] %s' % response['Message'])
        return None
    return response

def format_parameter(parameter):
    if isinstance(parameter, list):
        return ','.join(parameter)
    else:
        return parameter

###############################################################################

def get_coin_list(format=False):
    response = query_cryptocompare(URL_COIN_LIST, False)['Data']
    if format:
        return list(response.keys())
    else:
        return response

# TODO: add option to filter json response according to a list of fields
def get_price(coin, curr=CURR, full=False):
    if full:
        return query_cryptocompare(URL_PRICE_MULTI_FULL.format(format_parameter(coin),
            format_parameter(curr)))
    if isinstance(coin, list):
        return query_cryptocompare(URL_PRICE_MULTI.format(format_parameter(coin),
            format_parameter(curr)))
    else:
        return query_cryptocompare(URL_PRICE.format(coin, format_parameter(curr)))

def get_historical_price(coin, curr=CURR, timestamp=time.time()):
    if isinstance(timestamp, datetime.datetime):
        timestamp = time.mktime(timestamp.timetuple())
    return query_cryptocompare(URL_HIST_PRICE.format(coin, format_parameter(curr), int(timestamp)))

def get_histoday_price(coin, curr=CURR):
    result = query_cryptocompare(URL_HISTODAY_PRICE.format(coin, format_parameter(curr)))
    return result

def get_histohour_price(coin, curr=CURR, timestamp=time.time()):
    url = URL_HISTOHOUR_PRICE.format(coin, format_parameter(curr), int(timestamp))
    pprint.pprint(url)
    result = query_cryptocompare(url)
    return result

def get_avg(coin, curr, markets):
    response = query_cryptocompare(URL_AVG.format(coin, curr, format_parameter(markets)))
    if response: 
        return response['RAW']

if __name__ == '__main__':
    get()