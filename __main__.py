import time
import json
import urwid
import asyncio
from random import randint

# For testing, remove db
import os
if os.path.exists('test.db'):
	#os.remove('test.db')
	True

from display import Display
from initdb import *
from exchanges.bitfinex import Bitfinex
from exchanges.gdax import GDAX
from exchanges.bitrex import Bitrex
from exchanges.poloniex import Poloniex
from exchanges.bitmex import Bitmex

palette = [
	('titlebar', 'dark red, bold', ''),
	('table header', 'light gray, bold', ''),
	('refresh button', 'dark green,bold', ''),
	('quit button', 'dark red', ''),
	('getting quote', 'dark blue', ''),
	('headers', 'white,bold', ''),
	('change ', 'dark green', ''),
	('change negative', 'dark red', '')]

loop = asyncio.get_event_loop()
display = Display()

# Entry point
def main():

	display.ShowLoading("Loading latest market data to database...")
	display.Show()

	loop.call_later(0.1, constantUpdate)

	# Run initdb if missing db
	if not Asset.table_exists():
		initdb()
		display.Update("Database Updated")
	else:
		display.Update("Database already updated")



	# Main urwid loop
	urwid_loop = urwid.MainLoop(display.view, palette,
	 						input_filter=input_filter,
	 						event_loop=urwid.AsyncioEventLoop(loop=loop))
	urwid_loop.run()

def rPressed():
	display.Update("UPDATED")

def constantUpdate():

	bitfinex = Bitfinex()
	data = bitfinex.PullData()

	display.Update("Bitcoin price is " + str(data['price']))
	loop.call_later(1, constantUpdate)
	
def input_filter(keys, raw):
	if 'q' in keys or 'Q' in keys:
			raise urwid.ExitMainLoop

	if 'r' in keys or 'R' in keys:
		rPressed()
if __name__ == '__main__':
    main()
