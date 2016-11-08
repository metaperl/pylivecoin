import logging
import urllib
import time
import requests
import hmac
import hashlib
import pprint

logger = logging.getLogger(__name__)


BUY_ORDERBOOK = 'buy'
SELL_ORDERBOOK = 'sell'
BOTH_ORDERBOOK = 'both'

PUBLIC_SET = [
    'ticker', 'last_trades', 'order_book', 'all/order_book',
    'maxbid_minask', 'restrictions'
]

MARKET_SET = ['getopenorders', 'cancel', 'sellmarket', 'selllimit', 'buymarket', 'buylimit']

ACCOUNT_SET = ['getbalances', 'getbalance', 'getdepositaddress', 'withdraw', 'getorder', 'getorderhistory', 'getwithdrawalhistory', 'getdeposithistory']


class Livecoin(object):
    """
    Used for requesting Bittrex with API key and API secret
    """
    def __init__(self, api_key, api_secret):
        self.api_key = str(api_key) if api_key is not None else ''
        self.api_secret = str(api_secret) if api_secret is not None else ''
        self.public_set = set(PUBLIC_SET)
        self.market_set = set(MARKET_SET)
        self.account_set = set(ACCOUNT_SET)

    def api_query(self, method, options=None):
        """
        Queries Bittrex with given method and options

        :param method: Query method for getting info
        :type method: str

        :param options: Extra options for query
        :type options: dict

        :return: JSON response from Bittrex
        :rtype : dict
        """
        if not options:
            options = {}
        nonce = str(int(time.time() * 1000))
        base_url = 'https://api.livecoin.net/'
        request_url = ''

        if method in self.public_set:
            request_url = base_url + 'exchange/' + method
            if options:
                request_url += '?' + urllib.urlencode(options)
            print "request_url = {0}".format(request_url)
        elif method in self.market_set:
            request_url = (base_url % 'market') + method + '?apikey=' + self.api_key + "&nonce=" + nonce + '&'
        elif method in self.account_set:
            request_url = (base_url % 'account') + method + '?apikey=' + self.api_key + "&nonce=" + nonce + '&'

        signature = hmac.new(self.api_secret.encode(), request_url.encode(), hashlib.sha512).hexdigest()

        headers = {"apisign": signature}

        ret = requests.get(request_url, headers=headers)
        print "Result of {0} via {1} = {2}".format(
            method, request_url, pprint.pformat(ret.json()))
        # logger.info("Result of {0}={1}".format(method, ret))
        return ret.json()

    def get_markets(self):
        """
        Used to get the open and available trading markets
        at Bittrex along with other meta data.

        :return: Available market info in JSON
        :rtype : dict
        """
        return self.api_query('getmarkets')

    def get_currencies(self):
        """
        Used to get all supported currencies at Bittrex
        along with other meta data.

        :return: Supported currencies info in JSON
        :rtype : dict
        """
        return self.api_query('getcurrencies')

    def get_ticker(self, market):
        """
        Used to get the current tick values for a market.

        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str

        :return: Current values for given market in JSON
        :rtype : dict
        """
        return self.api_query('ticker', {
            'currencyPair': market
            }
        )

        return self.api_query('getticker', {'market': market})

    def get_all_tickers(self):
        """
        Summarize all markets.

        :return: Current values for all markets in JSON
        :rtype : list of dict
        """
        return self.api_query('ticker')

    def get_last_trades(self, market, in_minutes='false', type='false'):
        """
        Retrieve information on the latest transactions for a currency pair.

        :param str market: Which currency pair. E.g. LTC/BTC
        :param bool in_minutes: if false (the default), then supply in hours.
        :param str type: defaults to false. But can be BUY or SELL.

        :return: Summaries of active exchanges in JSON
        :rtype : list of dict
        """
        return self.api_query('last_trades', {
            'currencyPair': market,
            'minutesOrHour': in_minutes,
            'type': type
        })

    def get_orderbook(self, market, group_by_price=False, depth=20):
        """
        Used to get retrieve the orderbook for a given market

        :param market: String literal for the market (ex: LTC/BTC)
        :type market: str

        :param group_by_price: group by price.
        :type depth_type: bool

        :param depth: how deep of an order book to retrieve.
        :type depth: int


        :return: Orderbook of market in JSON
        :rtype : dict
        """
        return self.api_query('order_book', {
            'currencyPair': market,
            'groupByPrice': group_by_price,
            'depth': depth})

    def get_all_orderbooks(self, group_by_price=False, depth=1):
        """
        Used to get retrieve all orderbooks. for a given market

        :param group_by_price bool: group order book by price. Default=False.
        :param depth  int: Max orders to retrive. Default=all.

        :return: Orderbook of market in JSON
        :rtype : list of dict
        """
        options = {
            'groupByPrice': group_by_price,
            'depth': depth
        }
        return self.api_query(
            'all/order_book', options
        )

    def get_maxbid_minask(self, market=None):
        """
        Returns maximum bid and minimum ask optionally
        in a specific orderbook.

        :param market: String literal for the market (ex: LTC/BTC)
        :type market: str

        :return: Market history in JSON
        :rtype : dict
        """
        if market:
            options = dict(currencyPair=market)
            return self.api_query('maxbid_minask', options)

        return self.api_query('maxbid_minask')

    def buy_market(self, market, quantity):
        """
        Used to place a buy order in a specific market. Use buymarket to
        place market orders. Make sure you have the proper permissions
        set on your API keys for this call to work

        /market/buymarket

        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str

        :param quantity: The amount to purchase
        :type quantity: float

        :param rate: The rate at which to place the order.
            This is not needed for market orders
        :type rate: float

        :return:
        :rtype : dict
        """
        return self.api_query('buymarket', {'market': market, 'quantity': quantity})

    def buy_limit(self, market, quantity, rate):
        """
        Used to place a buy order in a specific market. Use buylimit to place
        limit orders Make sure you have the proper permissions set on your
        API keys for this call to work

        /market/buylimit

        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str

        :param quantity: The amount to purchase
        :type quantity: float

        :param rate: The rate at which to place the order.
            This is not needed for market orders
        :type rate: float

        :return:
        :rtype : dict
        """
        return self.api_query('buylimit', {'market': market, 'quantity': quantity, 'rate': rate})

    def sell_market(self, market, quantity, rate):
        """
        Used to place a sell order in a specific market. Use sellmarket to place
        market orders. Make sure you have the proper permissions set on your
        API keys for this call to work

        /market/sellmarket

        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str

        :param quantity: The amount to purchase
        :type quantity: float

        :param rate: The rate at which to place the order.
            This is not needed for market orders
        :type rate: float

        :return:
        :rtype : dict
        """
        return self.api_query('sellmarket', {'market': market, 'quantity': quantity, 'rate': rate})

    def sell_limit(self, market, quantity, rate):
        """
        Used to place a sell order in a specific market. Use selllimit to place
        limit orders Make sure you have the proper permissions set on your
        API keys for this call to work

        /market/selllimit

        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str

        :param quantity: The amount to purchase
        :type quantity: float

        :param rate: The rate at which to place the order.
            This is not needed for market orders
        :type rate: float

        :return:
        :rtype : dict
        """
        return self.api_query('selllimit', {'market': market, 'quantity': quantity, 'rate': rate})

    def cancel(self, uuid):
        """
        Used to cancel a buy or sell order

        /market/cancel

        :param uuid: uuid of buy or sell order
        :type uuid: str

        :return:
        :rtype : dict
        """
        return self.api_query('cancel', {'uuid': uuid})

    def get_open_orders(self, market):
        """
        Get all orders that you currently have opened. A specific market can be requested

        /market/getopenorders

        :param market: String literal for the market (ie. BTC-LTC)
        :type market: str

        :return: Open orders info in JSON
        :rtype : dict
        """
        return self.api_query('getopenorders', {'market': market})

    def get_balances(self):
        """
        Used to retrieve all balances from your account

        /account/getbalances

        :return: Balances info in JSON
        :rtype : dict
        """
        return self.api_query('getbalances', {})

    def get_balance(self, currency):
        """
        Used to retrieve the balance from your account for a specific currency

        /account/getbalance

        :param currency: String literal for the currency (ex: LTC)
        :type currency: str

        :return: Balance info in JSON
        :rtype : dict
        """
        return self.api_query('getbalance', {'currency': currency})

    def get_deposit_address(self, currency):
        """
        Used to generate or retrieve an address for a specific currency

        /account/getdepositaddress

        :param currency: String literal for the currency (ie. BTC)
        :type currency: str

        :return: Address info in JSON
        :rtype : dict
        """
        return self.api_query('getdepositaddress', {'currency': currency})

    def withdraw(self, currency, quantity, address):
        """
        Used to withdraw funds from your account

        /account/withdraw

        :param currency: String literal for the currency (ie. BTC)
        :type currency: str

        :param quantity: The quantity of coins to withdraw
        :type quantity: float

        :param address: The address where to send the funds.
        :type address: str

        :return:
        :rtype : dict
        """
        return self.api_query('withdraw', {'currency': currency, 'quantity': quantity, 'address': address})

    def get_order(self, uuid):
        """
        Used to get an order from your account

        /account/getorder

        :param uuid: The order UUID to look for
        :type uuid: str

        :return:
        :rtype : dict
        """
        return self.api_query('getorder', {'uuid': uuid})

    def get_order_history(self, market = ""):
        """
        Used to retrieve your order history

        /account/getorderhistory

        :param market: Bittrex market identifier (i.e BTC-DOGE)
        :type market: str

        :return:
        :rtype : dict
        """
        return self.api_query('getorderhistory', {"market": market})

    def get_withdrawal_history(self, currency = ""):
        """
        Used to retrieve your withdrawal history

        /account/getwithdrawalhistory

        :param currency: String literal for the currency (ie. BTC) (defaults to all)
        :type currency: str

        :return:
        :rtype : dict
        """
        return self.api_query('getwithdrawalhistory', {"currency": currency})

    def get_deposit_history(self, currency = ""):
        """
        Used to retrieve your deposit history

        /account/getdeposithistory

        :param currency: String literal for the currency (ie. BTC) (defaults to all)
        :type currency: str

        :return:
        :rtype : dict
        """
        return self.api_query('getdeposithistory', {"currency": currency})
