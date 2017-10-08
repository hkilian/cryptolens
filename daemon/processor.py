import os
import json
import requests
import websockets
import asyncio
import time
import itertools
import logging
from sortedcontainers import SortedDict

import config
from .orderbook import *

logging.basicConfig(filename='example.log',level=logging.INFO)
#logging.getLogger().setLevel(logging.INFO)

class BitfinexProcessor:

	def __init__(self):

		# Expected api version number for websockets
		self.expected_ws2_version = 2.0

		# Orderbook
		self.orderbook = Orderbook()

		# True if we are connected to the websocket
		self.connected = False
		self.connecting = False

		# Connect to websocket and subscribe to channels
		asyncio.Task(self.connect_and_subscribe())

	@asyncio.coroutine
	def connect_and_subscribe(self):

		logging.info("Connecting and subscribing")

		# Connect to websocket
		yield from asyncio.Task(self.connect_to_websocket())

		# Subscribe to raw books channel
		asyncio.Task(self.get_orders())


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
	def get_price(self):
		while True:
			bitfinex = Bitfinex()
			data = bitfinex.PullData()
			self.latest_price = data['price']
			yield from asyncio.sleep(1)

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

				# Look for event payload
				if 'event' in result:

					version = result['version']

					if version != self.expected_ws2_version:
						logging.error('Unexpected version number ' + str(version) + ' received from bitfinex, expected version ' + str(self.expected_ws2_version))
						self.connected = False
						self.connecting = False
						break

					received_event_payload = True
					logging.info("Received event payload: " + str(result))

					self.connecting = False
					self.connected = True

					continue

			if self.connected:
				logging.info("Connection successfully established!")
			else:
				logging.critical("Problem connecting to bitfinex, look at logs.")

		finally:
			self.connected = False

	@asyncio.coroutine
	def get_orders(self):

		# Wait for connection to establish
		if self.connected == False and self.connecting == True:

			logging.info("Waiting for websocket to connect before subscribing to raw books channel...")

			while self.connected == False:

				asyncio.sleep(1)

				if self.connecting == False and self.connected == False:
					logging.error("Could not subscribe to order channel as no websocket is connected!")
		else:

			logging.info("Websocket connection found, subscribing to channel...")
				

		# Subscribe to most raw books channel
		subscribe_raw = json.dumps({ "event":"subscribe", "channel": "book", "pair": "tBTCUSD", "prec": "R0", "len":"100"})

		# Flag waiting for websocket responses
		got_subscribed_payload = False
		got_snapshot_payload = False

		try:

			yield from self.websocket.send(subscribe_raw)

			logging.info("Sending channel subscribe request...")

			while True:

				result = yield from self.websocket.recv()
				result = json.loads(result)

				# Look for subscribed payload
				if got_subscribed_payload == False and 'event' in result and result['event'] == 'subscribed':
					got_subscribed_payload = True
					logging.info("Received subscribe event!")
					continue

				# Do not proceed if not subscribed
				if got_subscribed_payload == False:
					continue

				# Look for snapshot payload
				if got_snapshot_payload == False and len(result) == 2:
					got_snapshot_payload = True
					logging.info("Got snapshot")
					self.process_snapshot(result)
					continue

				# Do not proceed without snapshot
				if got_snapshot_payload == False:
					continue

				# Look for heatbeat
				if result[1] == 'hb':
					logging.info("Got heartbeat")
					continue

				data = result[1]
				timestamp = data[0]
				price = data[1]
				amount = Decimal(data[2])
				order_id = int(data[0])

				if price == 0:
					self.orderbook.remove_order(order_id)
					continue

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

		finally:
			yield from self.websocket.close()

	def process_snapshot(self, result):

		btotal_volume = 0;
		for order in self.orderbook.buyOrders.keys():
			btotal_volume += self.orderbook.buyOrders[order]

		logging.info("Total volume before (" + str(btotal_volume) + ")")

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
				


