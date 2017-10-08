import os
import json
import requests
import websockets
import asyncio
import time
import itertools
import logging
from .orderbook import *
from sortedcontainers import SortedDict

logging.basicConfig(filename='example.log',level=logging.INFO)
#logging.getLogger().setLevel(logging.INFO)

class BitfinexProcessor:

	def __init__(self):

		self.close = False
		self.latest_price = 0

		self.transactionsProcessed = 0
		self.totalLatency = 0
		self.averageTransactionTime = 0

		self.orderbook = Orderbook()

		#asyncio.Task(self.get_price())
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
			    price = float(bid["price"])
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
	def get_orders(self):

		websocket = yield from websockets.connect('wss://api.bitfinex.com/ws/2')
		sendData = json.dumps({ "event":"subscribe", "channel": "book", "pair": "tBTCUSD", "prec": "R0", "len":"100"})

		eventPayloadReceived = False
		subscribedPayloadReceived = False
		snapshotPayloadReceived = False

		# Pull in the complete orderbook
		#self.process_full_order_book()

		try:
			yield from websocket.send(sendData)
			logging.info("Sending request over wss")

			while True:

				result = yield from websocket.recv()
				result = json.loads(result)

				logging.info(result)

				# Look for first event payload
				if len(result) == 2 and eventPayloadReceived == False:
					eventPayloadReceived = True
					logging.info("Got event payload")
					continue

				# Look for subscribed payload
				if len(result) == 8 and subscribedPayloadReceived == False:
					subscribedPayloadReceived = True
					logging.info("Got subscribed")
					continue

				# Look for subscribed payload
				if len(result) == 2 and snapshotPayloadReceived == False:
					snapshotPayloadReceived = True
					logging.info("Got snapshot")
					self.process_snapshot(result)
					continue

				# Look for heatbeat
				if result[1] == 'hb':
					logging.info("Got heartbeat")
					continue

				data = result[1]
				timestamp = data[0]
				price = data[1]
				amount = data[2]
				order_id = int(data[0])

				if price == 0:
					self.orderbook.remove_order(order_id)
					continue

				ourTimestamp = int(time.time() * 1000)
				timeSinceTransaction = (ourTimestamp - timestamp) / 100.0

				#logging.info("ourTimestamp = " + str(ourTimestamp) + " - trade time = " + str(timestamp))
				timestampOut = "(transTime = " + str(timestamp) + ", outTime = " + str(ourTimestamp) + ")"
				#logging.info("Price = " + str(price) + " (" + str(timeSinceTransaction) + "ms) ")

				self.totalLatency += timeSinceTransaction
				self.transactionsProcessed += 1
				self.averageTransactionTime = self.totalLatency / self.transactionsProcessed

				#os.system('clear')

				# Disable logging.info
				sys.stdout = open(os.devnull, 'w')

				# Place order
				self.orderbook.add_order(order_id, price, amount)

				# Enable logging.info
				sys.stdout = sys.__stdout__

				logging.info(result)

		finally:
			yield from websocket.close()

	def process_snapshot(self, result):

		data = result[1]

		logging.info("LOOK HERE")
		logging.info(data)

		for order in data:
			order_id = order[0]
			price = order[1]
			amount = order[2]
			self.orderbook.add_order(order_id, price, amount)
				

"""
# Runs until processor signal exit
async def main():
	processor = BitfinexProcessor()

	logging.info("Running now...")

	while processor.close == False:
		await asyncio.sleep(1)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
"""

