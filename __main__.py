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

from display.displaycommon import *
from display.displayhome import *
from display.displaymarket import DisplayMarket
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

# Main loop
loop = asyncio.get_event_loop()

display = DisplayHome()
display.ShowLoading("Loading latest market data to database...")
display.ShowTopCoins()
display.PrepareBody()

header = Header()
footer = Footer()

# MVC test
controller = HomeController()

# Create the view
view = urwid.Frame(header=header, body=controller.view, footer=footer)
view = urwid.Padding(view, left=2, right=2)

# Run initdb if missing db
if not Asset.table_exists():
	initdb()
	display.Update("Database Updated")
else:
	display.Update("Database already updated")

@asyncio.coroutine
def slow_operation():
	while True:
		bitfinex = Bitfinex()
		data = bitfinex.PullData()

		view.original_widget.body = urwid.Filler(urwid.Text(str(data['price'])))

		yield from asyncio.sleep(1)

#asyncio.Task(slow_operation())

def rPressed():
	display = DisplayMarket()
	display.ShowOrderBook()
	display.PrepareBody()
	view.original_widget.body = display.body
	
def input_filter(keys, raw):
	if 'q' in keys or 'Q' in keys:
			raise urwid.ExitMainLoop

	if 'r' in keys or 'R' in keys:
		rPressed()

# Main urwid loop
urwid_loop = urwid.MainLoop(view, palette,
 						input_filter=input_filter,
 						event_loop=urwid.AsyncioEventLoop(loop=loop))

controller.set_loop(urwid_loop)

urwid_loop.run()

