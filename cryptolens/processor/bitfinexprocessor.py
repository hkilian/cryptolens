import os
import json
import requests
import websockets
import asyncio
import time
import itertools
import logging
from sortedcontainers import SortedDict

import cryptolens.config
from cryptolens.core.orderbook import *

logging.basicConfig(filename='output.log',level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)

class BitfinexProcessor:

	def __init__(self):

		# Expected api version number for websockets
		self.expected_ws2_version = 2.0

		# Orderbook
		self.orderbook = Orderbook()

		# Flag if we are connected or in process of connecting to websocket
		self.connected = False
		self.connecting = False

		# ID numbers for channels
		self.channel_id_ticker = -1
		self.channel_id_raw_books = -1

		# Market info
		self.market_info = {}
		self.market_info['bid'] = 0
		self.market_info['bid_size'] = 0
		self.market_info['ask'] = 0
		self.market_info['ask_size']= 0
		self.market_info['daily_change'] = 0
		self.market_info['daily_perc_change'] = 0
		self.market_info['last_price'] = 0
		self.market_info['volume'] = 0
		self.market_info['high'] = 0
		self.market_info['low'] = 0

		# Connect to websocket and subscribe to channels
		asyncio.Task(self.connect_and_subscribe())

	@asyncio.coroutine
	def connect_and_subscribe(self):

		logging.info("Connecting to websocket and subscribing...")

		# Connect to websocket
		yield from asyncio.Task(self.connect_to_websocket())

		# Send subscriptions
		subscribe_ticker = json.dumps({ "event": "subscribe", "channel": "ticker","symbol": "tBTCUSD" })
		subscribe_raw_books = json.dumps({ "event":"subscribe", "channel": "book", "pair": "tBTCUSD", "prec": "R0", "len":"100"})

		try:

			yield from self.websocket.send(subscribe_ticker)
			yield from self.websocket.send(subscribe_raw_books)

			logging.info("Sending channel subscribe requests...")

			while True:

				result = yield from self.websocket.recv()
				result = json.loads(result)

				logging.info(result)

				# Look for subscriptions events
				if self.channel_id_ticker == -1:
					if 'event' in result and result['event'] == 'subscribed' and result['channel'] == 'ticker':
						self.channel_id_ticker = result['chanId']
						logging.info('Subscribed to ticker channel, id (' + str(self.channel_id_ticker) + ')')
						ticker_subscribed = True
						continue

				if self.channel_id_raw_books == -1:
					if 'event' in result and result['event'] == 'subscribed' and result['channel'] == 'book':
						self.channel_id_raw_books = result['chanId']
						logging.info('Subscribed to raw books channel, id (' + str(self.channel_id_raw_books) + ')')
						raw_books_subscribed = True
						continue

				# Direct data in to the right handler
				channel_id = result[0]
				logging.info('Got data for channel with id (' + str(channel_id) + ')')

				if self.channel_id_ticker == channel_id:
					self.handle_ticker_data(result)
				elif self.channel_id_raw_books == channel_id:
					self.handle_raw_books(result)
					pass

				#logging.info(result)

		finally:
			logging.info("Done")
			pass


		# Subscribe to raw books channel
		asyncio.Task(self.get_orderbook())

		# Subscribe to ticker channel
		#asyncio.Task(self.get_ticker_data())

		# Send subscription events
		subscribe_ticker = json.dumps({ "event":"subscribe", "channel": "book", "pair": "tBTCUSD", "prec": "R0", "len":"100"})
		self.websocket.send(subscribe_ticker)

	def process_full_order_book(self):

		logging.info('Processing full order book from bitfinex')

		url = "https://api.bitfinex.com/v1/book/BTCUSD"
		response = requests.get(url)
		bookdata = response.json()

		bids = bookdata["bids"]
		asks = bookdata["asks"]

		for bid in bids:
			
			try:
			    price = Decimal(bid["price"])
			except ValueError:
			    logging.info("Price is invalid")
			    continue

			# Ignore scientifically formatted floats(extremely low price buy orders)
			if "e" in bid["price"]:
				continue

			amount = float(bid["amount"])
			timestamp = float(bid["timestamp"])

			logging.info("BID")
			logging.info(bid)
			logging.info("price = " + str(price))
			logging.info("amount = " + str(amount))

			self.orderbook.add_order(0, price, amount)

		for ask in asks:

			try:
			    price = float(ask["price"])
			except ValueError:
			    logging.info("Price is invalid")

			if "e" in ask["price"]:
				continue

			amount = float(ask["amount"])
			amount = -amount
			timestamp = float(ask["timestamp"])

			logging.info("ASK")
			logging.info(ask)
			logging.info("price = " + str(price))
			logging.info("amount = " + str(amount))

			self.orderbook.add_order(price, amount)

	@asyncio.coroutine
	def connect_to_websocket(self):

		# Flag that we are attempting connection
		self.connecting = True

		# Connect to bitfinex websocket
		self.websocket = yield from websockets.connect('wss://api.bitfinex.com/ws/2')

		# Wait for a confirmation of connection from bitfinex
		# Should look like this:
		# {"event":"info","version":2}
		try:

			logging.info("Attempting connection to websocket...")

			received_event_payload = False
			while received_event_payload == False:

				result = yield from self.websocket.recv()
				result = json.loads(result)

				# If event payload not received then do nothing
				if received_event_payload == False:
					if self.handle_event_payload(result):
						received_event_payload = True
						logging.info("Connection successfully established!")
						return True
					else:
						logging.critical("Problem connecting to bitfinex, look at logs.")
						return False

		finally:
			pass

	def handle_event_payload(self, data):

		# Look for event payload
		if 'event' in data:

			version = data['version']
			if version != self.expected_ws2_version:
				logging.error('Unexpected version number ' + str(version) + ' received from bitfinex, expected version ' + str(self.expected_ws2_version))
				self.connected = False
				self.connecting = False
				return False

			logging.info("Received event payload: " + str(data))

			self.connecting = False
			self.connected = True

			return True

	def handle_ticker_data(self, data):
			
		logging.info('Handling ticker data...')

		if len(data[1]) > 9:
			ticker_data = data[1]
			self.market_info['bid'] = ticker_data[0]
			self.market_info['bid_size'] = ticker_data[1]
			self.market_info['ask'] = ticker_data[2]
			self.market_info['ask_size']= ticker_data[3]
			self.market_info['daily_change'] = ticker_data[4]
			self.market_info['daily_perc_change'] = ticker_data[5]
			self.market_info['last_price'] = ticker_data[6]
			self.market_info['volume'] = ticker_data[7]
			self.market_info['high'] = ticker_data[8]
			self.market_info['low'] = ticker_data[9]

	def handle_raw_books(self, data):
			
		# Flags used on waiting for websocket responses
		got_snapshot_payload = False
		result = data

		logging.info(result)

		# Look for snapshot payload
		if len(result) == 2 and len(result[1]) >= 20:
			logging.info("Received snapshot data!")
			self.process_snapshot(result)
			return

		# Look for heatbeat
		if result[1] == 'hb':
			logging.info("Got heartbeat")
			return

		data = result[1]
		timestamp = data[0]
		price = data[1]
		amount = Decimal(data[2])
		order_id = int(data[0])

		if price == 0:
			self.orderbook.remove_order(order_id)
			return

		# Meassure time since transaction took place
		ourTimestamp = int(time.time() * 1000)
		timeSinceTransaction = (ourTimestamp - timestamp) / 100.0
		#logging.info("ourTimestamp = " + str(ourTimestamp) + " - trade time = " + str(timestamp))
		timestampOut = "(transTime = " + str(timestamp) + ", outTime = " + str(ourTimestamp) + ")"
		#logging.info("Price = " + str(price) + " (" + str(timeSinceTransaction) + "ms) "

		# Disable logging.info
		sys.stdout = open(os.devnull, 'w')

		# Place order
		self.orderbook.add_order(order_id, price, amount)

		# Enable logging.info
		sys.stdout = sys.__stdout__

	def process_snapshot(self, result):

		btotal_volume = 0;
		for order in self.orderbook.buyOrders.keys():
			btotal_volume += self.orderbook.buyOrders[order]

		data = result[1]

		logging.info("Processing snapshot data...")

		total_volume = 0
		for order in data:
			order_id = order[0]
			price = order[1]

			amount = Decimal(order[2])

			total_volume += amount

			self.orderbook.add_order(order_id, price, amount)

		logging.info("Finished processing snapshot data. Total volume (" + str(total_volume) + ")")

		rtotal_volume = 0;
		for order in self.orderbook.buyOrders.keys():
			rtotal_volume += self.orderbook.buyOrders[order]

		logging.info("Total volume (" + str(rtotal_volume) + ")")
				


