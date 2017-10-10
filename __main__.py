import time
import json
import urwid
import asyncio
from random import randint
from mvc.displaycommon import *
from mvc.displayhome import *
from mvc.displaymarket import DisplayMarket
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

# Get the header and footer widgets
header = Header()
footer = Footer()

# MVC
controller = HomeController()

# Create the view
view = urwid.Frame(header=header, body=controller.view, footer=footer)
view = urwid.Padding(view, left=2, right=2)

# Handles input
def input_filter(keys, raw):
	if 'q' in keys or 'Q' in keys:
		raise urwid.ExitMainLoop


# Main urwid loop
urwid_loop = urwid.MainLoop(view, palette,
 						input_filter=input_filter,
 						event_loop=urwid.AsyncioEventLoop(loop=loop))

controller.set_loop(urwid_loop)
urwid_loop.run()

