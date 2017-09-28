import asyncio
import websockets
import json
import click

currentPrice = 0

async def hello():
	async with websockets.connect('wss://api.bitfinex.com/ws/2') as websocket:

		sendData = json.dumps({ "event":"subscribe", "channel": "trades", "pair": "BTCUSD" })
		#print(sendData)
		await websocket.send(sendData )
		
		result = await websocket.recv()
		#print(result)

		result = await websocket.recv()
		#print(result)

		while True:
			result = await websocket.recv()
			result = json.loads(result)

			code = result[1]

			#print(result)

			if(code == 'te' or code == 'tu'):
				price = result[2][3]
				click.secho('price = %s' %price, bold=False)

				currentPrice = price

		#result = json.loads(result)

		#print("< {}".format(result))

asyncio.get_event_loop().run_until_complete(hello())