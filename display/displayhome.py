import time
import asyncio
import urwid
import websockets
import json
from .displaycommon import *
from exchanges.bitfinex import Bitfinex
from daemon.orderbook import Orderbook
from daemon.processor import BitfinexProcessor

class HomeModel:
	def __init__(self):

		self.latest_price = 0
		#asyncio.Task(self.get_orders())

		# Bitfinex processor
		self.bitfinex_processor = BitfinexProcessor()

	def get_orderbook(self):
		return self.bitfinex_processor.orderbook

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

		self.mainPileList = []
		self.leftColumn = urwid.Pile([])
		self.rightColumn = urwid.Pile([])

		self.best_price = urwid.Text("Connecting...")

		# Prepare orderbook
		self.prepare_order_book()

		# Prepare left pane
		self.prepare_stats_pane()
		self.prepare_left_pane()

		self.__super.__init__(self.main_window())

	def update(self):

		# Get the orderbook
		orderbook = self.controller.get_orderbook()

		# Get the best price
		self.best_price.set_text(str(orderbook.best_sell))

		# Update the sell table
		sell_data = []
		for key in orderbook.sellOrders.islice(0, 18, reverse=True):
			amount = "{:.10f}".format(orderbook.sellOrders[key])
			sell_data.append([key, amount])

		self.sellTable.update_data(sell_data)

		# Update the buy table
		buy_data = []
		for key in itertools.islice(reversed(orderbook.buyOrders), 0, 18):
			amount = "{:.10f}".format(orderbook.buyOrders[key])
			buy_data.append([key, amount])

		self.buyTable.update_data(buy_data)

		# Update info pane
		info_data = []
		info_data.append(['Total Orders Processed', orderbook.total_orders_processed])
		info_data.append(['Buy Orders Received', orderbook.total_buy_orders_processed])
		info_data.append(['Sell Orders Received', orderbook.total_sell_orders_processed])
		info_data.append(['Orders Removed', orderbook.total_orders_removed])
		info_data.append(['Orders Waiting', len(orderbook.order_list)])

		best_sell = 9999;
		for order_id in orderbook.order_list.keys():
			price = orderbook.order_list[order_id][0]
			amount = orderbook.order_list[order_id][1]

			if amount < 0 and price < best_sell:
				best_sell = price
		info_data.append(['Best sell', best_sell])

		info_data.append(['Order volume change', orderbook.order_change_volume])

		info_data.append(['-', '-'])

		total_volume_actual = 0;
		for order_id in orderbook.order_list.keys():
			if orderbook.order_list[order_id][1] > 0:
				total_volume_actual += orderbook.order_list[order_id][1]
		info_data.append(['Total Volume Actual', total_volume_actual])

		total_buy_volume = 0;
		for order in orderbook.buyOrders.keys():
			total_buy_volume += orderbook.buyOrders[order]
		info_data.append(['Total Buy Volume', total_buy_volume])

		info_data.append(['Buy Diff', total_buy_volume - total_volume_actual])

		info_data.append(['-', '-'])

		total_sell_volume_actual = 0;
		for order_id in orderbook.order_list.keys():
			if orderbook.order_list[order_id][1] < 0:
				total_sell_volume_actual += abs(orderbook.order_list[order_id][1])
		info_data.append(['Total Sell Volume Actual', total_sell_volume_actual])

		total_sell_volume = 0;
		for order in orderbook.sellOrders.keys():
			total_sell_volume += orderbook.sellOrders[order]
		info_data.append(['Total Sell Volume', total_sell_volume])

		info_data.append(['Sell Diff', total_sell_volume - total_sell_volume_actual])

		if total_sell_volume - total_sell_volume_actual > 0.0001:
			#sys.exit()
			pass

		self.stats_table.update_data(info_data)

	def main_window(self):
		price = str(self.controller.get_price_data())

		# Prepare body
		columnList = [self.leftColumn, (40, self.rightColumn)]
		body = urwid.Columns(columnList)
		body = urwid.Padding(body, left=2, right=2)

		return body

	def prepare_left_pane(self):

		best_price = urwid.Text("empty")

		self.leftColumn = urwid.Pile([self.stats_table])

	def prepare_stats_pane(self):

		columnList = ['Stats']
		self.stats_table = Table(2, 15, column_names=columnList)
		self.stats_table.create_table()

	def prepare_order_book(self):

		column_list = [urwid.Text(('table header', "Price")), urwid.Text(('table header', "Volume"))]
		column_headers = urwid.Columns(column_list)
		column_headers = urwid.Filler(column_headers, valign='middle', top=1, bottom=1)

		self.sellTable = Table(2, 30, fillbottom=True)
		self.sellTable.create_table()

		self.sellTable._w.set_focus(self.sellTable.row_count - 1)

		self.buyTable = Table(2, 30)
		self.buyTable.create_table()

		best_price_widget = urwid.Padding(self.best_price, align="center", width='pack')
		best_price_widget = urwid.Filler(best_price_widget, valign='middle', top=1, bottom=1)
		self.rightColumn = urwid.Pile([(1, column_headers), self.sellTable, (3, best_price_widget), self.buyTable])

class HomeController:
	def __init__(self):
		self.model = HomeModel()
		self.view = HomeView(self)

	def set_loop(self, loop):
		self.loop = loop
		self.update()

	def update(self, loop=None, user_data=None):
		self.view.update()
		self.update_alarm = self.loop.set_alarm_in(0.05, self.update)

	def get_price_data(self):
		return self.model.latest_price;

	def get_orderbook(self):
		return self.model.get_orderbook();

	





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
		table.create_table()
		self.topCoins = table

	def PrepareBody(self):

		# Sort left and right columns
		mainList = [self.topCoins]

		self.body = urwid.Pile(mainList)
		self.body = urwid.Padding(self.body, left=2, right=2)
		self.body = urwid.LineBox(self.body)





