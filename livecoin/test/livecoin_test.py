import pprint
import unittest
import json
from livecoin.livecoin import Livecoin


def test_basic_response(unit_test, result, method_name):

    unit_test.assertTrue(result is not None, "result not present in response")


def test_auth_basic_failures(unit_test, result, test_type):
    unit_test.assertFalse(result['success'], "{0:s} failed".format(test_type))
    unit_test.assertTrue('invalid' in str(result['message']).lower(), "{0:s} failed response message".format(test_type))
    unit_test.assertIsNone(result['result'], "{0:s} failed response result not None".format(test_type))


class TestBittrexPublicAPI(unittest.TestCase):
    """
    Integration tests for the Bittrex public API.
    These will fail in the absence of an internet connection or if bittrex API goes down
    """
    market = 'ADZ/BTC'

    def setUp(self):
        self.livecoin = Livecoin(None, None)

    def test_handles_none_key_or_secret(self):
        self.livecoin = Livecoin(None, None)
        # could call any public method here
        actual = self.livecoin.get_markets()
        self.assertTrue(actual['success'], "failed with None key and None secret")

        self.livecoin = Livecoin("123", None)
        actual = self.livecoin.get_markets()
        self.assertTrue(actual['success'], "failed with None secret")

        self.livecoin = Livecoin(None, "123")
        self.assertTrue(actual['success'], "failed with None key")

    def test_get_ticker(self):
        actual = self.livecoin.get_ticker(self.market)
        test_basic_response(self, actual, "get_ticker")
        self.assertTrue(
            isinstance(actual, dict), "result is not a dict")

    def test_get_all_tickers(self):
        actual = self.livecoin.get_all_tickers()
        test_basic_response(self, actual, "get_all_tickers")
        self.assertTrue(
            isinstance(actual, list), "result is not a list")
        self.assertTrue(
            len(actual) > 0, "result list is 0-length")

    def test_get_last_trades(self):
        actual = self.livecoin.get_last_trades(self.market)
        test_basic_response(self, actual, "get_last_trades")
        self.assertTrue(
            isinstance(actual, list), "result is not a list")
        self.assertTrue(
            len(actual) > 0, "result list is 0-length")

    def test_get_orderbook(self):
        actual = self.livecoin.get_orderbook(self.market)
        test_basic_response(self, actual, "get_orderbook")
        self.assertTrue(
            isinstance(actual, dict), "result is not a dict")

    def test_get_all_orderbooks(self):
        actual = self.livecoin.get_all_orderbooks()
        test_basic_response(self, actual, "get_all_orderbooks")
        self.assertTrue(
            isinstance(actual, dict), "result is not a dict")

    def test_get_maxbid_minask(self):
        actual = self.livecoin.get_maxbid_minask()
        test_basic_response(self, actual, "get_maxbid_minask")

        actual = self.livecoin.get_maxbid_minask(market=self.market)
        test_basic_response(self, actual, "get_maxbid_minask")



class TestLivecoinAccountAPI(unittest.TestCase):
    """
    Integration tests for the Livecoin Account API.
      * These will fail in the absence of an internet connection or if livecoin
        API goes down.
      * They require a valid API key and secret issued by Livecoin.
      * They also require the presence of a JSON file called secrets.json.
      It is structured as such:
    {
      "key": "12341253456345",
      "secret": "3345745634234534"
    }
    """
    def setUp(self):
        with open("secrets.json") as secrets_file:
            self.secrets = json.load(secrets_file)
            secrets_file.close()
        self.livecoin = Livecoin(self.secrets['key'], self.secrets['secret'])

    def test_handles_invalid_key_or_secret(self):
        self.livecoin = Livecoin('invalidkey', self.secrets['secret'])
        actual = self.livecoin.get_balance('BTC')
        test_auth_basic_failures(self, actual, 'Invalid key, valid secret')

        self.livecoin = Livecoin(None, self.secrets['secret'])
        actual = self.livecoin.get_balance('BTC')
        test_auth_basic_failures(self, actual, 'None key, valid secret')

        self.livecoin = Livecoin(self.secrets['key'], 'invalidsecret')
        actual = self.livecoin.get_balance('BTC')
        test_auth_basic_failures(self, actual, 'valid key, invalid secret')

        self.livecoin = Livecoin(self.secrets['key'], None)
        actual = self.livecoin.get_balance('BTC')
        test_auth_basic_failures(self, actual, 'valid key, None secret')

        self.livecoin = Livecoin('invalidkey', 'invalidsecret')
        actual = self.livecoin.get_balance('BTC')
        test_auth_basic_failures(self, actual, 'invalid key, invalid secret')
        pass

    def test_get_balance(self):
        actual = self.livecoin.get_balance('BTC')
        test_basic_response(self, actual, "getbalance")
        self.assertTrue(
            isinstance(actual['result'], dict), "result is not a dict")
        self.assertEqual(
            actual['result']['Currency'],
            "BTC",
            "requested currency {0:s} does not match returned currency {1:s}"
            .format("BTC", actual['result']['Currency']))

if __name__ == '__main__':
    unittest.main()
