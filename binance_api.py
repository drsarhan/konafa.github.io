from binance.client import Client
from binance.exceptions import BinanceAPIException

class BinanceClient:
    def __init__(self, api_key, secret_key):
        self.client = Client(api_key, secret_key)

    def get_balance(self):
        try:
            account_info = self.client.get_account()
            balances = {balance['asset']: balance['free'] for balance in account_info['balances'] if float(balance['free']) > 0}
            return {k: v.rstrip('0').rstrip('.') for k, v in balances.items()}
        except BinanceAPIException as e:
            return str(e)

    def get_available_symbols(self):
        try:
            exchange_info = self.client.get_exchange_info()
            symbols = [symbol['symbol'] for symbol in exchange_info['symbols']]
            return symbols
        except BinanceAPIException as e:
            return str(e)

    def buy(self, symbol, quantity):
        try:
            order = self.client.order_market_buy(symbol=symbol, quantity=quantity)
            return order
        except BinanceAPIException as e:
            return str(e)

    def sell(self, symbol, quantity):
        try:
            order = self.client.order_market_sell(symbol=symbol, quantity=quantity)
            return order
        except BinanceAPIException as e:
            return str(e)