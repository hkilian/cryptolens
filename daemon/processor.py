import os
import json
import requests
import websockets
import asyncio
import time

class Processor:
	def __init__(self):
		self.close = False
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
						price = data[2]

						ourTimestamp = int(time.time())
						timeSinceTransaction = int(str(ourTimestamp) + "000") - timestamp
						timeSinceTransaction = timeSinceTransaction / 1000

						#print("ourTimestamp = " + str(ourTimestamp) + " - trade time = " + str(timestamp))

						print("Price = " + str(price) + " (" + str(timeSinceTransaction) + "ms)")

					self.latest_price = result[1][0]

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


