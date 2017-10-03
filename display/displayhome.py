import asyncio
import urwid
import websockets
import json
from .displaycommon import *
from exchanges.bitfinex import Bitfinex

class HomeModel:
	def __init__(self):
		self.latest_price = 0
		#asyncio.Task(self.get_price())
		asyncio.Task(self.get_orders())

	@asyncio.coroutine
	def get_price(self):
		while True:
			bitfinex = Bitfinex()
			data = bitfinex.PullData()
			self.latest_price = data['price']
			yield from asyncio.sleep(1)

	@asyncio.coroutine
	def get_orders(self):
		websocket = yield from websockets.connect('wss://api.bitfinex.com/ws/2')
		sendData = json.dumps({ "event":"subscribe", "channel": "book", "pair": "BTCUSD", "prec": "p0", "freq": "f0", "len": "25"})
		
		try:
			yield from websocket.send(sendData)

			while True:

				result = yield from websocket.recv()

				if result is not None:

					json_string = '{"first_name": "Guido", "last_name":"Rossum"}'
					parsed_json = json.loads(json_string)

					try:
						result = json.loads(result)
						self.latest_price = result[1][0]
					except:
						pass

		finally:
			yield from websocket.close()

			

class HomeView(urwid.WidgetWrap):
	def __init__(self, controller):
		self.controller = controller
		self.main_text = urwid.Text("empty")

		self.__super.__init__(self.main_window())

	def update(self):
		price = "Bitcoin = " + str(self.controller.get_price_data())
		self.main_text.set_text(price)

	def main_window(self):
		price = str(self.controller.get_price_data())
		w = urwid.Filler(self.main_text)
		return w

class HomeController:
	def __init__(self):
		self.model = HomeModel()
		self.view = HomeView(self)

	def set_loop(self, loop):
		self.loop = loop
		self.update_price()

	def update_price(self, loop=None, user_data=None):
		self.view.update()
		self.update_alarm = self.loop.set_alarm_in(0.05, self.update_price)

	def get_price_data(self):
		return self.model.latest_price;

	





class DisplayHome:

	def __init__(self):
		self.mainPileList = []

		self.topCoins = urwid.Pile([])

	def ShowLoading(self, loadingText):

		self.text = urwid.Text(loadingText)
		padding = urwid.Padding(self.text, align='center', width='pack')
		filler = urwid.Filler(padding, valign='middle')
		self.mainPileList.append(filler)

	def Update(self, text):
		self.text.set_text(text)

	def ShowTopCoins(self):

		colList = [(3, urwid.Text(('table header', str("-")))),
									 (urwid.Text(('table header', str("Symbol")))),
									 (urwid.Text(('table header', str("Price")))),
									 (urwid.Text(('table header', str("Market Cap")))),
									 (urwid.Text(('table header', str("Volume")))),
									 (urwid.Text(('table header', str("24hr Change")))),
									 (urwid.Text(('table header', str("Last Update"))))]

		table = Table("Top coins by marketcap (Bitfinex):", colList)
		table.createTable()
		self.topCoins = table

	def PrepareBody(self):

		# Sort left and right columns
		mainList = [self.topCoins]

		self.body = urwid.Pile(mainList)
		self.body = urwid.Padding(self.body, left=2, right=2)
		self.body = urwid.LineBox(self.body)





