import json
import requests
from .exchange import Exchange

class Bitrex(Exchange):

	def __init__(self):
		 Exchange.__init__(self, "Bitrex")

	def PullData(self):
		url = "https://bittrex.com/api/v1.1/public/getticker?market=USDT-BTC"
		response = requests.get(url)
		ticker = response.json()["result"]

		data = {}
		data['price'] = ticker['Last']
		data['change'] = 0
		data['percentChange'] = 0
		data['volume'] = 0

		return data
