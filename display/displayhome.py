import time
import asyncio
import urwid
import websockets
import json
from .displaycommon import *
from exchanges.bitfinex import Bitfinex
from core.orderbook import Orderbook
from daemon.processor import BitfinexProcessor

class HomeModel:
	def __init__(self):

		self.latest_price = 0
		#asyncio.Task(self.get_orders())

		# Bitfinex processor
		self.bitfinex_processor = BitfinexProcessor()

	def get_orderbook(self):
		return self.bitfinex_processor.orderbook

	def get_market_info(self):
		return self.bitfinex_processor.market_info

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
		self.prepare_market_info_pane()
		self.prepare_stats_pane()
		self.prepare_left_pane()

		self.__super.__init__(self.main_window())

	def update(self):

		# Get the orderbook
		orderbook = self.controller.get_orderbook()
		market_info = self.controller.market_info

		# Get the best price
		self.best_price.set_text(str(orderbook.best_sell))

		# Update the sell table
		sell_data = []
		for key in orderbook.sellOrders.islice(0, 18, reverse=True):
			amount = "{:.10f}".format(orderbook.sellOrders[key])
			sell_data.append([key, amount, 0])

		self.sellTable.update_data(sell_data)

		# Update the buy table
		buy_data = []
		for key in itertools.islice(reversed(orderbook.buyOrders), 0, 18):
			amount = "{:.10f}".format(orderbook.buyOrders[key])
			buy_data.append([key, amount, 0])

		self.buyTable.update_data(buy_data)

		# Update info pane
		info_data = []
		info_data.append(['Total Orders Processed', orderbook.total_orders_processed])
		info_data.append(['Buy Orders Received', orderbook.total_buy_orders_processed])
		info_data.append(['Sell Orders Received', orderbook.total_sell_orders_processed])
		info_data.append(['Orders Removed', orderbook.total_orders_removed])
		info_data.append(['Orders In System', len(orderbook.order_list)])
		info_data.append(['Volume Of Modified Orders', orderbook.order_change_volume])
		self.stats_table.update_data(info_data)

		# Update market pane
		market_data = []
		market_data.append(['Total volume', market_info['volume']])

		self.market_info_table.update_data(market_data)

	def main_window(self):
		price = str(self.controller.get_price_data())

		# Prepare body
		columnList = [self.leftColumn, (40, self.rightColumn)]
		body = urwid.Columns(columnList)
		body = urwid.Padding(body, left=2, right=2)

		return body

	def prepare_left_pane(self):
		self.leftColumn = urwid.Pile([(8, self.market_info_table), self.stats_table])

	def prepare_market_info_pane(self):

		columnList = ['Market Info']
		self.market_info_table = Table(2, 6, column_names=columnList)
		self.market_info_table.create_table()

	def prepare_stats_pane(self):

		columnList = ['Stats']
		self.stats_table = Table(2, 6, column_names=columnList)
		self.stats_table.create_table()

	def prepare_order_book(self):

		column_list = [(12, urwid.Text(('table header', "Price"))), urwid.Text(('table header', "Volume")), (6, urwid.Text(('table header', "Orders")))]
		column_headers = urwid.Columns(column_list)
		column_headers = urwid.Filler(column_headers, valign='middle', top=1, bottom=1)

		self.sellTable = Table(3, 30, fillbottom=True, column_widths=[12,0,6])
		self.sellTable.create_table()

		self.sellTable._w.set_focus(self.sellTable.row_count - 1)

		self.buyTable = Table(3, 30, column_widths=[12,0,6])
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

	def get_market_info(self):
		return self.model.get_market_info();


