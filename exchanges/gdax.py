import json
import requests
from .exchange import Exchange

class GDAX(Exchange):

	def __init__(self):
		 Exchange.__init__(self, "GDAX")

	def PullData(self):
		url = "https://api.gdax.com/products/BTC-USD/ticker"
		response = requests.get(url)
		ticker = response.json()

		data = {}
		data['price'] = ticker['price']
		data['percentChange'] = 0
		data['volume'] = ticker['volume']

		return data
