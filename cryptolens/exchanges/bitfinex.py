import json
import requests
from .exchange import Exchange

class Bitfinex(Exchange):

	def __init__(self):
		 Exchange.__init__(self, "Bitfinex")

	def PullData(self):
		url = "https://api.bitfinex.com/v2/ticker/tBTCUSD"
		response = requests.get(url)
		ticker = response.json()

		if len(ticker) != 10:
			return False

		data = {}
		data['price'] = ticker[6]
		data['change'] = ticker[4]
		data['percentChange'] = ticker[5]
		data['volume'] = ticker[7]

		return data
