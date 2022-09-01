import datetime
from decimal import Decimal
import hmac
import string
from symtable import Symbol
import time
from tokenize import String
from unittest import result
from flask import Flask,jsonify,request
import hashlib,json,threading,hmac,requests,time, websocket
import ssl
from operator import itemgetter
import logging
from datetime import datetime
import pytz
from datetime import datetime
from kafka import KafkaProducer,KafkaConsumer
from DataController.binance import createBinanceTradeOrder, createCryptoOrder, getActiveOrders, getBinanceTradeOrder, updateBinanceTradeOrder, updateCryptoOrder
from DataModel.binance import BinanceTradeOrderStatus, CryptoOrderStatus
from colorama import Fore
import types

class BinanceAPIException(Exception):
    
    def __init__(self, response):
        self.code = 0
        try:
            json_res = response.json()
        except ValueError:
            self.message = 'Invalid JSON error message from Binance: {}'.format(response.text)
        else:
            self.code = json_res['code']
            self.message = json_res['msg']
        self.status_code = response.status_code
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):  # pragma: no cover
        return 'APIError(code=%s): %s' % (self.code, self.message)


class BinanceRequestException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'BinanceRequestException: %s' % self.message
    
class Binance:
    #API_URL = 'https://api.binance.{}/api'
    API_URL = 'https://testnet.binance.vision/api'
    
    STREAM_URL = 'wss://stream.binance.com:9443/ws/'
    #STREAM_URL = "wss://testnet.binance.vision/stream?streams="

    
    PUBLIC_API_VERSION = 'v1'
    PRIVATE_API_VERSION = 'v3'
    
    spot_test_api_key = 'Zv026lRmGX4zssYLjbTfB9M4yjLygb24XclGkt0WJjbRglgMxlaIeV2FcBNiBrlt'
    spot_test_secret = 'kIJW1EsbNHhy5NmFc2luysabxjdY0lrbR96Js4lhM8ggytosegaKnbeh0WTmRdPU'
    
    api_key_live='E84bxVugUex2gvz1Uke9yUWj5nZqvzGqyuisslTsywgxS9lQK6E8A8ZWR6ws2ReI'
    api_secret_live='GTo2GjpbeiGPEpxhaQ1mzbZacZsmaqf9BJx6TW0o6zPAm2CULPsrnRiKp507cPhe'
    
    def __init__(self, api_key='Zv026lRmGX4zssYLjbTfB9M4yjLygb24XclGkt0WJjbRglgMxlaIeV2FcBNiBrlt',
                 api_secret='kIJW1EsbNHhy5NmFc2luysabxjdY0lrbR96Js4lhM8ggytosegaKnbeh0WTmRdPU', requests_params=None,
                 tld='com'):
    # def __init__(self, api_key='E84bxVugUex2gvz1Uke9yUWj5nZqvzGqyuisslTsywgxS9lQK6E8A8ZWR6ws2ReI',
    #              api_secret='GTo2GjpbeiGPEpxhaQ1mzbZacZsmaqf9BJx6TW0o6zPAm2CULPsrnRiKp507cPhe', requests_params=None,
    #              tld='com'):
        
        self.API_URL = self.API_URL.format(tld)
    
        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.session = self._init_session()
        self._requests_params = requests_params
        self.response = None
        
    
    def _init_session(self):
    
        session = requests.session()
        session.headers.update({'Accept': 'application/json',
                                'User-Agent': 'binance/jainaveen',
                                'X-MBX-APIKEY': self.API_KEY})
        print(session)
        return session
    

    def stream_close(self, listenKey):
        """Close out a user data stream.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#close-user-data-stream-user_stream

        :param listenKey: required
        :type listenKey: str

        :returns: API response

        .. code-block:: python

            {}

        :raises: BinanceRequestException, BinanceAPIException

        """
        params = {
            'listenKey': listenKey
        }
        return self._delete('userDataStream', False, data=params)

    def stream_get_listen_key(self):
        """Start a new user data stream and return the listen key
        If a stream already exists it should return the same key.
        If the stream becomes invalid a new key is returned.

        Can be used to keep the user stream alive.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#start-user-data-stream-user_stream

        :returns: API response

        .. code-block:: python

            {
                "listenKey": "pqia91ma19a5s61cv6a81va65sdf19v8a65a1a5s61cv6a81va65sdf19v8a65a1"
            }

        :raises: BinanceRequestException, BinanceAPIException

        """
        res = self._post('userDataStream', False, data={})
        return res['listenKey']
    

    def createSocket(self,path,onmessage=None,data=[]):
        try:
            websocket.enableTrace(True)
            if onmessage == None:
                onmessage = self.on_message
            url = self.STREAM_URL + path
            print(f"socker url : {url}")
            ws = websocket.WebSocketApp(url=url,on_message=onmessage,header=data)
            print("Socket Created")
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            print( "Socket Closed Automatically")
        except Exception as e:
            print(str(e))
            
    def createSocketThread(self,path,onmessage=None,data=[]):
        t = threading.Thread(target=self.createSocket,args=(path,onmessage,data))
        t.daemon = True
        t.start()
        
    def createUserSocketThread(self,path,onmessage=None):
        t = threading.Thread(target=self.createUserDataStreamSocket,args=(path,onmessage))
        t.daemon = True
        t.start()
        t2 = threading.Thread(target=self.refreshListenkey)
        t2.daemon = True
        t2.start()
        
    def createUserSocket(self,path,onmessage=None):
        while True:
            try:
                # print( "Created new Socket" )
                # print("Getting old listen key")
                listentoken = self.stream_get_listen_key()
                # print("Closing old listen key")
                self.stream_close(listenKey=listentoken)
                # print("Getting new listen key")
                listentoken = self.stream_get_listen_key()
                websocket.enableTrace(True)
                if onmessage==None:
                    onmessage = self.on_message
                print(str(self.STREAM_URL +listentoken+"/"+ path ))
                ws = websocket.WebSocketApp(self.STREAM_URL +listentoken+"/"+ path,on_message=onmessage)
                print("Socket Created")
                ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
                print( "Socket Closed Automatically" )
                time.sleep(5)
            except Exception as e:
                print(str(e))
           
    def on_message_binance_order(self,message):
        print("WebSocket: ",str(message))
        
    def createUserDataStreamSocket(self,path,onmessage=None):
        while True:
            try:
                # print( "Created new Socket" )
                # print("Getting old listen key")
                listentoken = self.stream_get_listen_key()
                # print("Closing old listen key")
                self.stream_close(listenKey=listentoken)
                # print("Getting new listen key")
                listentoken = self.stream_get_listen_key()
                websocket.enableTrace(True)
                if onmessage==None:
                    onmessage = self.on_message_binance_order
                #url = "wss://stream.binance.com:9443/stream?streams="+ listentoken
                url = "wss://testnet.binance.vision/stream?streams=" + listentoken
                # print(str(url))
                ws = websocket.WebSocketApp(url,on_message=onmessage)
                print("Socket Created")
                ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
                print( "Socket Closed Automatically" )
                time.sleep(5)
            except Exception as e:
                print(str(e))
                 
    def refreshListenkey(self):
        while True:
            try:
                self.stream_get_listen_key()
                time.sleep(59)
                logging.info("Refreshing listen key")
            except:
                pass

        
    def on_message(self,message):
        print("WebSocket: ",str(message))
        
    
    def _generate_signature(self, data):
        
        ordered_data = self._order_params(data)
        query_string = '&'.join(["{}={}".format(d[0], d[1]) for d in ordered_data])
        m = hmac.new(self.API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        return m.hexdigest()
    
    def _order_params(self, data):
        """Convert params to list with signature as last element

        :param data:
        :return:

        """
        has_signature = False
        params = []
        for key, value in data.items():
            if key == 'signature':
                has_signature = True
            else:
                params.append((key, value))
        # sort parameters by key
        params.sort(key=itemgetter(0))
        if has_signature:
            params.append(('signature', data['signature']))
        return params
        
    def _request(self, method, uri, signed, force_params=False, **kwargs):
    
        # set default requests timeout
        kwargs['timeout'] = 10

        # add our global requests params
        if self._requests_params:
            kwargs.update(self._requests_params)

        data = kwargs.get('data', None)
        print(f"data in request -> {data}")
        if data and isinstance(data, dict):
            kwargs['data'] = data
            
            # find any requests params passed and apply them
            if 'requests_params' in kwargs['data']:
                # merge requests params into kwargs
                kwargs.update(kwargs['data']['requests_params'])
                del(kwargs['data']['requests_params'])
                
        if signed:
            # generate signature
            kwargs['data']['timestamp'] = int(time.time() * 1000)
            kwargs['data']['signature'] = self._generate_signature(kwargs['data'])
            print(f"kwargs data   -----    {kwargs['data']}")

        # sort get and post params to match signature order
        if data:
            # sort post params
            kwargs['data'] = self._order_params(kwargs['data'])
            # Remove any arguments with values of None.
            print(f"ordered params -> {kwargs['data']}")
            null_args = [i for i, (key, value) in enumerate(kwargs['data']) if value is None]
            for i in reversed(null_args):
                del kwargs['data'][i]

            print(f"after None removed ordered params -> {kwargs['data']}")


        # if get request assign data array to params value for requests lib
        if data and (method == 'get' or force_params):
            kwargs['params'] = '&'.join('%s=%s' % (data[0], data[1]) for data in kwargs['data'])
            print(f"get params -> {kwargs['params']}")
            del(kwargs['data'])

        response = getattr(self.session, method)(uri, **kwargs)
        # print(f"response -> {response}")
        return self._handle_response(response,uri, **kwargs)

    def _handle_response(self,response,uri, **kwargs):
        """Internal helper for handling API responses from the Binance server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.
        """
        #logging.info(str(["_handle_response", response.text, uri, kwargs]))
        if not str(response.status_code).startswith('2'):
            raise BinanceAPIException(response)
        try:
            return response.json()
        except ValueError:
            raise BinanceRequestException('Invalid Response: %s' % response.text)
        
        
    #Create api url       
    def _create_api_uri(self, path, signed=True, version=PUBLIC_API_VERSION):
        v = self.PRIVATE_API_VERSION if signed else version
        return self.API_URL + '/' + v + '/' + path
    
    def _create_withdraw_api_uri(self, path):
        return self.WITHDRAW_API_URL + '/' + self.WITHDRAW_API_VERSION + '/' + path
        


    #Make request
    def _request_api(self, method, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        uri = self._create_api_uri(path, signed, version)
        return self._request(method, uri, signed, **kwargs)
    
    def _request_withdraw_api(self, method, path, signed=False, **kwargs):
        uri = self._create_withdraw_api_uri(path)
        return self._request(method, uri, signed, True, **kwargs)        
        
    
    #Http calls
    def _get(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        return self._request_api('get', path, signed, version, **kwargs)

    def _post(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        return self._request_api('post', path, signed, version, **kwargs)

    def _put(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        return self._request_api('put', path, signed, version, **kwargs)

    def _delete(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        return self._request_api('delete', path, signed, version, **kwargs)
    
    
    
    def get_recent_trades(self, **params):
        """Get recent trades (up to last 500).

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#recent-trades-list

        :param symbol: required
        :type symbol: str
        :param limit:  Default 500; max 500.
        :type limit: int

        :returns: API response

        .. code-block:: python

            [
                {
                    "id": 28457,
                    "price": "4.00000100",
                    "qty": "12.00000000",
                    "time": 1499865549590,
                    "isBuyerMaker": true,
                    "isBestMatch": true
                }
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('trades', data=params)
    
    def get_account(self, **params):
        """Get current account information.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#account-information-user_data

        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            {
                "makerCommission": 15,
                "takerCommission": 15,
                "buyerCommission": 0,
                "sellerCommission": 0,
                "canTrade": true,
                "canWithdraw": true,
                "canDeposit": true,
                "balances": [
                    {
                        "asset": "BTC",
                        "free": "4723846.89208129",
                        "locked": "0.00000000"
                    },
                    {
                        "asset": "LTC",
                        "free": "4763368.68006011",
                        "locked": "0.00000000"
                    }
                ]
            }

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('account', True, data=params)
    
    # General Endpoints

    def ping(self):
        """Test connectivity to the Rest API.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#test-connectivity

        :returns: Empty array

        .. code-block:: python

            {}

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('ping')

    def get_server_time(self):
        """Test connectivity to the Rest API and get the current server time.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#check-server-time

        :returns: Current server time

        .. code-block:: python

            {
                "serverTime": 1499827319559
            }

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('time')
    
    # Exchange Endpoints

    def get_products(self):
        """Return list of products currently listed on Binance

        Use get_exchange_info() call instead

        :returns: list - List of product dictionaries

        :raises: BinanceRequestException, BinanceAPIException

        """

        products = self._request_website('get', 'exchange/public/product')
        return products
    
    def get_exchange_info(self):
        """Return rate limits and list of symbols

        :returns: list - List of product dictionaries

        .. code-block:: python

            {
                "timezone": "UTC",
                "serverTime": 1508631584636,
                "rateLimits": [
                    {
                        "rateLimitType": "REQUESTS",
                        "interval": "MINUTE",
                        "limit": 1200
                    },
                    {
                        "rateLimitType": "ORDERS",
                        "interval": "SECOND",
                        "limit": 10
                    },
                    {
                        "rateLimitType": "ORDERS",
                        "interval": "DAY",
                        "limit": 100000
                    }
                ],
                "exchangeFilters": [],
                "symbols": [
                    {
                        "symbol": "ETHBTC",
                        "status": "TRADING",
                        "baseAsset": "ETH",
                        "baseAssetPrecision": 8,
                        "quoteAsset": "BTC",
                        "quotePrecision": 8,
                        "orderTypes": ["LIMIT", "MARKET"],
                        "icebergAllowed": false,
                        "filters": [
                            {
                                "filterType": "PRICE_FILTER",
                                "minPrice": "0.00000100",
                                "maxPrice": "100000.00000000",
                                "tickSize": "0.00000100"
                            }, {
                                "filterType": "LOT_SIZE",
                                "minQty": "0.00100000",
                                "maxQty": "100000.00000000",
                                "stepSize": "0.00100000"
                            }, {
                                "filterType": "MIN_NOTIONAL",
                                "minNotional": "0.00100000"
                            }
                        ]
                    }
                ]
            }

        :raises: BinanceRequestException, BinanceAPIException

        """

        return self._get('exchangeInfo')
    
    def get_all_orders(self, **params):
        """Get all account orders; active, canceled, or filled.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#all-orders-user_data

        :param symbol: required
        :type symbol: str
        :param orderId: The unique order id
        :type orderId: int
        :param limit: Default 500; max 500.
        :type limit: int
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            [
                {
                    "symbol": "LTCBTC",
                    "orderId": 1,
                    "clientOrderId": "myOrder1",
                    "price": "0.1",
                    "origQty": "1.0",
                    "executedQty": "0.0",
                    "status": "NEW",
                    "timeInForce": "GTC",
                    "type": "LIMIT",
                    "side": "BUY",
                    "stopPrice": "0.0",
                    "icebergQty": "0.0",
                    "time": 1499827319559
                }
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('allOrders', True, data=params)
   
    def get_my_trades(self, **params):
        """Get trades for a specific symbol.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#account-trade-list-user_data

        :param symbol: required
        :type symbol: str
        :param limit: Default 500; max 500.
        :type limit: int
        :param fromId: TradeId to fetch from. Default gets most recent trades.
        :type fromId: int
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            [
                {
                    "id": 28457,
                    "price": "4.00000100",
                    "qty": "12.00000000",
                    "commission": "10.10000000",
                    "commissionAsset": "BNB",
                    "time": 1499865549590,
                    "isBuyer": true,
                    "isMaker": false,
                    "isBestMatch": true
                }
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('myTrades', True, data=params)
    
    def get_historical_trades(self, **params):
        """Get older trades.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#recent-trades-list

        :param symbol: required
        :type symbol: str
        :param limit:  Default 500; max 500.
        :type limit: int
        :param fromId:  TradeId to fetch from. Default gets most recent trades.
        :type fromId: str

        :returns: API response

        .. code-block:: python

            [
                {
                    "id": 28457,
                    "price": "4.00000100",
                    "qty": "12.00000000",
                    "time": 1499865549590,
                    "isBuyerMaker": true,
                    "isBestMatch": true
                }
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('historicalTrades', data=params)

    def create_order(self, **params):
            """Send in a new order

            Any order with an icebergQty MUST have timeInForce set to GTC.

            https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#new-order--trade

            :param symbol: required
            :type symbol: str
            :param side: required
            :type side: str
            :param type: required
            :type type: str
            :param timeInForce: required if limit order
            :type timeInForce: str
            :param quantity: required
            :type quantity: decimal
            :param quoteOrderQty: amount the user wants to spend (when buying) or receive (when selling)
                of the quote asset, applicable to MARKET orders
            :type quoteOrderQty: decimal
            :param price: required
            :type price: str
            :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
            :type newClientOrderId: str
            :param icebergQty: Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
            :type icebergQty: decimal
            :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
            :type newOrderRespType: str
            :param recvWindow: the number of milliseconds the request is valid for
            :type recvWindow: int

            :returns: API response

            Response ACK:

            .. code-block:: python

                {
                    "symbol":"LTCBTC",
                    "orderId": 1,
                    "clientOrderId": "myOrder1" # Will be newClientOrderId
                    "transactTime": 1499827319559
                }

            Response RESULT:

            .. code-block:: python

                {
                    "symbol": "BTCUSDT",
                    "orderId": 28,
                    "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
                    "transactTime": 1507725176595,
                    "price": "0.00000000",
                    "origQty": "10.00000000",
                    "executedQty": "10.00000000",
                    "status": "FILLED",
                    "timeInForce": "GTC",
                    "type": "MARKET",
                    "side": "SELL"
                }

            Response FULL:

            .. code-block:: python

                {
                    "symbol": "BTCUSDT",
                    "orderId": 28,
                    "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
                    "transactTime": 1507725176595,
                    "price": "0.00000000",
                    "origQty": "10.00000000",
                    "executedQty": "10.00000000",
                    "status": "FILLED",
                    "timeInForce": "GTC",
                    "type": "MARKET",
                    "side": "SELL",
                    "fills": [
                        {
                            "price": "4000.00000000",
                            "qty": "1.00000000",
                            "commission": "4.00000000",
                            "commissionAsset": "USDT"
                        },
                        {
                            "price": "3999.00000000",
                            "qty": "5.00000000",
                            "commission": "19.99500000",
                            "commissionAsset": "USDT"
                        },
                        {
                            "price": "3998.00000000",
                            "qty": "2.00000000",
                            "commission": "7.99600000",
                            "commissionAsset": "USDT"
                        },
                        {
                            "price": "3997.00000000",
                            "qty": "1.00000000",
                            "commission": "3.99700000",
                            "commissionAsset": "USDT"
                        },
                        {
                            "price": "3995.00000000",
                            "qty": "1.00000000",
                            "commission": "3.99500000",
                            "commissionAsset": "USDT"
                        }
                    ]
                }

            :raises: BinanceRequestException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

            """
            return self._post('order', True, data=params)

    def get_open_orders(self, **params):
        """Get all open orders on a symbol.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#current-open-orders-user_data

        :param symbol: optional
        :type symbol: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            [
                {
                    "symbol": "LTCBTC",
                    "orderId": 1,
                    "clientOrderId": "myOrder1",
                    "price": "0.1",
                    "origQty": "1.0",
                    "executedQty": "0.0",
                    "status": "NEW",
                    "timeInForce": "GTC",
                    "type": "LIMIT",
                    "side": "BUY",
                    "stopPrice": "0.0",
                    "icebergQty": "0.0",
                    "time": 1499827319559
                }
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('openOrders', True, data=params)
        

    def get_order_book(self, **params):
        """Get the Order Book for the market

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#order-book

        :param symbol: required
        :type symbol: str
        :param limit:  Default 100; max 1000
        :type limit: int

        :returns: API response

        .. code-block:: python

            {
                "lastUpdateId": 1027024,
                "bids": [
                    [
                        "4.00000000",     # PRICE
                        "431.00000000",   # QTY
                        []                # Can be ignored
                    ]
                ],
                "asks": [
                    [
                        "4.00000200",
                        "12.00000000",
                        []
                    ]
                ]
            }

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('depth', data=params)

    def cancel_order(self, **params):
        """Cancel an active order. Either orderId or origClientOrderId must be sent.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#cancel-order-trade

        :param symbol: required
        :type symbol: str
        :param orderId: The unique order id
        :type orderId: int
        :param origClientOrderId: optional
        :type origClientOrderId: str
        :param newClientOrderId: Used to uniquely identify this cancel. Automatically generated by default.
        :type newClientOrderId: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            {
                "symbol": "LTCBTC",
                "origClientOrderId": "myOrder1",
                "orderId": 1,
                "clientOrderId": "cancelMyOrder1"
            }

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._delete('order', True, data=params)

    def get_user_assets(self,**params):
        return self._request_withdraw_api('post','asset/getUserAsset', True, data=params,)

    def cancel_all_open_orders(self, **params):
        return self._delete('openOrders', True, data=params)
    
 
app = Flask(__name__)

app_name = "Binance_demo"

@app.route("/",methods=["GET"])   
def basic():
    binance = Binance()
    result = binance.get_exchange_info()
    # initsocket()
    return jsonify({"status":"success","message":result})


@app.route("/getassets",methods=["GET"]) 
def get_assets():
    binance = Binance()
    result = binance.get_recent_trades(symbol="TRXUSDT",limit=10)
    return jsonify({"status":"success","message":result})


@app.route("/getaccount",methods=["GET"])   
def get_account():
    binance = Binance()
    result = binance.get_account(recvWindow=5000)
    return jsonify({"status":"success","message":result})


@app.route("/getallorders/<symbol>",methods=["GET"])   
def getallorders(symbol):
    binance = Binance()
    result = binance.get_all_orders(symbol=symbol)
    return jsonify({"status":"success","message":result})

@app.route("/getopenorders",methods=["GET"])    
def getOpenorders(symbol=None):
    binance = Binance()
    result = binance.get_open_orders()
    return jsonify({"status":"success","message":result})

@app.route("/gettradehistory",methods=["GET"])   
def gettradehistory():
    binance = Binance()
    result = binance.get_all_orders(symbol="TRXUSDT")
    return jsonify({"status":"success","message":result})


@app.route("/getmytrades/<symbol>",methods=["POST"])   
def getmytrades(symbol):
    binance = Binance()
    result = binance.get_my_trades(symbol=symbol) # we can mention the fromid to get the trade history
    return jsonify({"status":"success","message":result})

# work only in live api
@app.route("/getuserassets",methods=["GET"])   
def getuserassets():
    binance = Binance()
    result = binance.get_user_assets() # return positive assets  
    return jsonify({"status":"success","message":result})

@app.route("/createorder/market",methods=["POST"])   
def createMarketOrder():
    binance = Binance()
    request_data = request.get_json()
    result = None
    #need to pass quantity or quoteOrderQty
    if request_data.get("quantity") is not None:
        result = binance.create_order(
            symbol=request_data.get("symbol"),
            side =  request_data.get("side"),
            type = "MARKET",
            quantity =  request_data.get("quantity")
       )
    if request_data.get("quoteOrderQty") is not None:
        result = binance.create_order(
            symbol=request_data.get("symbol"),
            side =  request_data.get("side"),
            type = "MARKET",
            quoteOrderQty =  request_data.get("quoteOrderQty")
       )
    return jsonify({"status":"success","message":result})

@app.route("/createorder/limit",methods=["POST"])   
def createLimitOrder():
    request_data = request.get_json()
    binance = Binance()
    result = binance.create_order(
        symbol=request_data.get("symbol"),
        side = request_data.get("side"),
        type = "LIMIT",
        timeInForce = "GTC",
        quantity = request_data.get("qty"),
        price = request_data.get("price")
        )
    #        quoteOrderQty = 400.0,
    return jsonify({"status":"success","message":result})


@app.route("/getorderbook",methods=["POST"])   
def getorderbook():
    request_data = request.get_json()
    binance = Binance()
    result = binance.get_order_book(symbol=request_data.get("symbol"),limit=10)
    return jsonify({"status":"success","message":result})  


@app.route("/cancelorder",methods=["POST"])   
def cancelorder():
    request_data = request.get_json()
    binance = Binance()
    result = binance.cancel_order(symbol=request_data.get("symbol"),orderId = request_data.get("orderId"))
    return jsonify({"status":"success","message":result})


@app.route('/delete/allopenorders',methods=['POST'])
def deleteAllOpenOrder():
    binance = Binance()
    request_data = request.get_json()
    result = binance.cancel_all_open_orders(symbol=request_data['symbol'])
    return jsonify({"status":"success","message":result})
    
    

# need to be moved
def cryptoOrderBookRefresh(*argv):
    try:
        data = json.loads(list(argv)[1])
        coinpair = list(argv)[0].header['coinpair']
        try:
            #data = binance.get_order_book(symbol=coinpair.replace("/", ""), limit=20)
            paircoin, basecoin = coinpair.split("/")
            topbids = []
            topasks = []
            for item in data['bids']:
                s = str(Decimal(item[0]) * Decimal(item[1]))
                topbids.append(
                    {"price": "{} {}".format(item[0][:item[0].find(".")], basecoin),
                     "amount": "{} {}".format(item[1][:item[1].find(".")], paircoin),
                     "total": "{} {}".format(s[:s.find(".") + 1 + 8], basecoin), "sum": "", "flash": "0"})
            for item in data['asks']:
                s = str(Decimal(item[0]) * Decimal(item[1]))
                topasks.append(
                    {"price": "{} {}".format(item[0][:item[0].find(".")], basecoin),
                     "amount": "{} {}".format(item[1][:item[1].find(".")], paircoin),
                     "total": "{} {}".format(s[:s.find(".") + 8], basecoin), "sum": "", "flash": "0"})
            '''print json.dumps(
                {"topbids": topbids, "topasks": topasks,
                 "coinpair": coinpair})'''
            # time.sleep(int(serviceMgmt.app_config['cryptopairrefresh']))
            print(f"Top Bid {topbids}")
            print(f"Top Ask {topasks}")
        except:
            print("sefdvcse")
    except Exception as e:
        print(f'watch {str(e)}')

# need to be moved        


def marketData():
    binance = Binance()
    coinpair = "TRX/USDT"
    binance.createSocketThread(path="{}@depth10@1000ms".format(coinpair.replace("/", "").lower()),
                                onmessage=cryptoOrderBookRefresh, data={"coinpair": coinpair})
    
def initsocket():
    binance = Binance()
    # marketData()
    try:
        print("Came here")
        # binance.createUserDataStreamSocket(path="btcusdt@kline_1m")
        #binance.createUserSocket(path="btcusdt@kline_1m")
        binance.createUserSocketThread(path="",onmessage=watchBinanceCyptoOrders)
        # marketData()
    except Exception as e:
        print(str(e))

def serializer(message):
    return json.dumps(message).encode('utf-8') 
def deserializer(message):
    return json.loads(message).decode('utf-8') 

# def watchBinanceCyptoOrders(*argv):
#     try:
#         message = json.loads(list(argv)[1])
#         message = message['data']
#         print(f"Message -> {str(message)}")
#         if message['e']=='outboundAccountPosition':
#             logging.info(str(["watchCyptoOrders", list(argv)]))
#         elif message['e']=='executionReport':
            
#             orderId = message['i']
#             partitionId = orderId % partitionCount
            
#             Kafka.producer.send('trade', message,partition=partitionId)
#             print("event produced")
#             if  message['X']=='PARTIALLY_FILLED':
#                 print("PARTIALLY_FILLED")
#             if message['X'] == 'FILLED':
#                 print("FILLED")
#             print(str(message))
#             logging.info(str(["watchCyptoOrders:",message,message['i'],message['X'],message['x']]))
#     except:
#         print("")

class Kafka():       
    producer = KafkaProducer(
        bootstrap_servers=['localhost:29092'],
        value_serializer=serializer
    )
    def getPartitionCount():
        consumer = KafkaConsumer(
            "trade",
            bootstrap_servers='localhost:29092',
        )
        partitions = consumer.partitions_for_topic("trade")
        print(len(partitions))
        return len(partitions)

partitionCount = None


#################################################---NEW JOBS------############################################################################################################################################

# this will create a row in crypto order table with status 1(NEW)
@app.route("/create/order",methods=["POST"])   
def createOrder():
    request_data = request.get_json()
    order = None
    try:
        order = createCryptoOrder(
            price=request_data.get("price"),
            qty=request_data.get("qty"),
            status= CryptoOrderStatus.NEW,
            ordertype=1, # 1 - LIMIT order  0 - Market order
            trantype= 0 if request_data.get("trantype") == "BUY" else 1, # 0 - buy 1 - sell
            coinpair=request_data.get("coinpair"),
            exchgid=1,
        )
        print(f"Order create successfully order - {order}")
    except Exception as e:
        print(str(e))
        return jsonify({"status":"error","message":str(e)})
    return jsonify({"status":"order created successfully","message":order})


# this will cancel the order and send the response to kafka producer

@app.route("/cancel/order/<orderId>",methods=["POST"])
def cancelOrder(orderId):
    binanceOrder = None
    try:
        order = getBinanceTradeOrder(crypto_order_id=orderId)
        print(f"Cancel Order -> {order}")
        binanceOrder = binance.cancel_order(
            orderId = order[0]['exchgorderid'],
            symbol = order[0]['coinpair']
        )
        orderId = binanceOrder['orderId']
        binanceOrder['eventType'] = 'httpEvent'
        binanceOrder['action'] = "CANCELED"
        partitionId = orderId % partitionCount
        print(Fore.YELLOW+f"Producer cancel order -> {binanceOrder}"+Fore.RESET)
        Kafka.producer.send('trade',binanceOrder,partition = partitionId,key = b"httpEvent")
    except Exception as e:
        print(str(e))
    return jsonify({"status":"order cancelled successfully","message":binanceOrder})


#This will take order from cryptoorders and place order in binance and make the order as processed
@app.route("/process/order",methods=["GET"])
def process_order():
    result = []
    try:
        activeOrders = getActiveOrders(status=1)
        for order in activeOrders:
            binanceOrder = binance.create_order(
                symbol=order['coinpair'],
                side = "BUY" if order['trantype'] == 0 else "SELL",
                type = "LIMIT",
                timeInForce = "GTC",
                quantity = order['qty'],
                price = order['price']
            )            
            createBinanceTradeOrder(
                clientid = binanceOrder['clientOrderId'],
                price = binanceOrder['price'], 
                qty = binanceOrder['origQty'], 
                status = BinanceTradeOrderStatus.FULLY_FILLED if binanceOrder['status'] == "FILLED" else BinanceTradeOrderStatus.ORDER_PLACED, 
                ordertype = 1 if binanceOrder['type'] == "LIMIT" else 0, 
                trantype = 0 if binanceOrder['side'] == "BUY" else 1, 
                coinpair = binanceOrder['symbol'], 
                exchgid = 1, 
                exchgorderid = binanceOrder['orderId'], 
                trandata = str(binanceOrder['fills']),
                crypto_order_id = order['id']
            )
            updateCryptoOrder(
                id = order['id'],
                status = CryptoOrderStatus.PROCESSED
            )
            orderId = binanceOrder['orderId']
            partitionId = orderId % partitionCount
            binanceOrder['eventType'] = 'httpEvent'
            binanceOrder['action'] = "NEW"
            print(Fore.YELLOW+f"Producer process order -> {binanceOrder}"+Fore.RESET)
            Kafka.producer.send('trade',binanceOrder,partition = partitionId,key = b"httpEvent")
            print("event produced")
            if  binanceOrder['status'] == 'PARTIALLY_FILLED':
                print("PARTIALLY_FILLED")
            if binanceOrder['status'] == 'FILLED':
                print("FILLED")
            result.append(binanceOrder)
    except Exception as e:
        return jsonify({"status":"error","message":str(e)})
    return jsonify({"status":"order created successfully","message":result})


def watchBinanceCyptoOrders(*argv):
    try:
        message = json.loads(list(argv)[1])
        message = message['data']
        print(f"Message -> {str(message)}")
        if message['e']=='outboundAccountPosition':
           print(str(["watchCyptoOrders", list(argv)]))
           print(Fore.YELLOW+f"Producer websocker -> {message}"+Fore.RESET)
        elif message['e']=='executionReport':
            orderId = message['i']
            partitionId = orderId % partitionCount
            message['eventType'] = 'wsocketEvent'
            message['action'] = message['x']
            print(f"watchBinanceCyptoOrderstype - {type(message)}")
            Kafka.producer.send('trade',message,partition=partitionId,key=b"wsocketEvent")
            print("event produced")
            if  message['X']=='PARTIALLY_FILLED':
                print("PARTIALLY_FILLED")
            if message['X'] == 'FILLED':
                print("FILLED")
            print(str(message))
    except Exception as e:
        print(str(e))
        


def consumer():
    print("Consumer Started")
    while True:
        consumer = KafkaConsumer(
            "trade",
            bootstrap_servers='localhost:29092',
            group_id = 'trade-group1',
            auto_offset_reset='latest',
            auto_commit_interval_ms=1000,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        for message in consumer:
            print(f"Message - {message.value}   type - {type(message.value)}")
            print(Fore.GREEN+f"consumer {message.value}"+Fore.RESET)
            data = message.value
            if type(data) == str:
                print("Came here")
                data = json.loads(data)
            print(f"Json event type -> {data['eventType']}")
            if data['eventType'] == "wsocketEvent":
                orderID = data['i']
                if data['action'] == "CANCELED":
                    updateBinanceTradeOrder(exchgorderid=orderID,status = BinanceTradeOrderStatus.CANCELLED_BY_CT,)
                else:
                    order = getBinanceTradeOrder(orderId=orderID)
                    print(Fore.GREEN+f"Order data ws -> {orderID}    order -> {order}"+Fore.RESET)
                    trandata = None
                    if order[0]['trandata'] is not None:
                        trandata = json.loads(order[0]['trandata'].replace("\'", "\""))
                        print(f"Json for trandata -> {trandata}")
                    print(Fore.RED+f"Trandata inside WS -> {type(trandata)}   data -> {trandata}"+Fore.RESET)
                    print(f"Tran data -> {order[0]['trandata']}")
                    new_tran_data = {
                                "price":data['p'],
                                "qty":data['l'],
                                "commission":data['n'],
                                "commissionAsset":data['N'],
                                "tradeId":data['t']
                            }
                    if new_tran_data not in trandata:
                        print(Fore.RED+"NOT Same trandata"+Fore.RESET)
                        trandata.append(new_tran_data)
                    print(Fore.YELLOW+f"New Tran data - {trandata}"+Fore.RESET)
                    updateBinanceTradeOrder(exchgorderid=orderID,trandata=str(trandata))
                    
            elif data['eventType'] == "httpEvent":
                orderID = data['orderId']
                if data['action'] == "CANCELED":
                    updateBinanceTradeOrder(exchgorderid=orderID,status = BinanceTradeOrderStatus.CANCELLED_BY_CT,)
                else:
                    order = getBinanceTradeOrder(orderId=orderID) 
                    print(Fore.GREEN+f"Order data http -> {orderID}   order -> {order}"+Fore.RESET)
                    # trandata =json.loads(order[0]['trandata'])
                    # updateBinanceTradeOrder()
                    print(f"Tran data -> {order[0]['trandata']}")
                    # print(Fore.RED+f"Tran data -> {trandata}")
                
            
def init_thread(func):
    t = threading.Thread(target=func)
    t.start()

binance = None

if __name__ == "__main__":
    # initsocket()
    binance = Binance()
    partitionCount = Kafka.getPartitionCount()
    init_thread(func=consumer)
    binance.createUserSocketThread(path="",onmessage=watchBinanceCyptoOrders)
    app.run(host="0.0.0.0", port=6091, threaded=True, debug=False)

# yellow - producer
# green - consumer