import json
import requests
from .exchange import Exchange

class Poloniex(Exchange):

	def __init__(self):
		 Exchange.__init__(self, "GDAX")

	def PullData(self):
		url = "https://poloniex.com/public?command=returnTicker&currencyPair=USDT_BTC"
		response = requests.get(url)
		ticker = response.json()['USDT_BTC']

		data = {}
		data['price'] = ticker['last']
		data['percentChange'] = 0
		data['volume'] = ticker['baseVolume']

		return data
