import json
import requests
from .exchange import Exchange

class Bitmex(Exchange):

	def __init__(self):
		 Exchange.__init__(self, "Bitmex")

	def PullData(self):
		url = "https://www.bitmex.com/api/v1/instrument?symbol=XBTUSD&count=1&reverse=false"
		response = requests.get(url)
		ticker = response.json()[0]

		data = {}
		data['price'] = ticker['lastPrice']
		data['percentChange'] = 0
		data['volume'] = ticker['volume24h']

		return data
