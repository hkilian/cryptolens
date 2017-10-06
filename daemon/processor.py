import os
import json
import requests
import websockets
import asyncio
import time
from orderbook import *
from sortedcontainers import SortedDict

class Processor:

	def __init__(self):

		self.close = False
		self.latest_price = 0

		self.transactionsProcessed = 0
		self.totalLatency = 0
		self.averageTransactionTime = 0

		self.orderbook = Orderbook()

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
		#sendData = json.dumps({ "event":"subscribe", "channel": "book", "pair": "BTCUSD", "prec": "p0", "freq": "f0", "len": "25"})
		sendData = json.dumps({ "event":"subscribe", "channel": "trades", "pair": "BTCUSD"})
		try:
			yield from websocket.send(sendData)
			print("Sending request over wss")

			while True:

				result = yield from websocket.recv()

				try:

					result = json.loads(result)
					code = result[1]

					#print(result)

					if code == "te" or code == "tu":

						data = result[2]
						timestamp = data[1]
						price = data[3]
						amount = data[2]

						ourTimestamp = int(time.time() * 1000)
						timeSinceTransaction = (ourTimestamp - timestamp) / 100.0

						#print("ourTimestamp = " + str(ourTimestamp) + " - trade time = " + str(timestamp))
						timestampOut = "(transTime = " + str(timestamp) + ", outTime = " + str(ourTimestamp) + ")"
						#print("Price = " + str(price) + " (" + str(timeSinceTransaction) + "ms) ")

						self.totalLatency += timeSinceTransaction
						self.transactionsProcessed += 1
						self.averageTransactionTime = self.totalLatency / self.transactionsProcessed

						os.system('clear')

						self.orderbook.add_order(price, amount)

						print(result)

						print("Last order price: " + str(price))
						print("Last order amount: " + str(amount))
						print("Total orders processed: " + str(self.transactionsProcessed))
						print("Orderbook size: " + str(len(self.orderbook.buyOrders)))

						print("")
						print(" - - Sell Orders - - ")

						for key in self.orderbook.sellOrders.islice(0, 5, reverse=True):
							print(str(key) + " - " +  str(self.orderbook.sellOrders[key]))

						print(" - - Buy Orders - - ")

						for key in self.orderbook.buyOrders.islice(0, 5, reverse=True):
							print(str(key) + " - " +  str(self.orderbook.buyOrders[key]))

						print(" - - - - - - - - - ")
						print("Best Price = " + " - " +  str(self.orderbook.get_best_price()))

						#print("Transactions: " + str(self.transactionsProcessed))
						#print("Avg latancy: " + str(self.averageTransactionTime) + " ms")

				except:
					pass

		finally:
			yield from websocket.close()

# Runs until processor signal exit
async def main():
	processor = Processor()

	print("Running now...")

	while processor.close == False:
		await asyncio.sleep(1)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()


