import time
import json
import urwid

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

# Entry point
def main():

	display = Display()
	display.ShowLoading("Loading latest market data to database...")
	display.Show()

	loop = urwid.MainLoop(display.view, palette, input_filter=input_filter)
	loop.run()

	# Run initdb if missing db
	if not Asset.table_exists():
		initdb()




	
def input_filter(keys, raw):
	if 'q' in keys or 'Q' in keys:
			raise urwid.ExitMainLoop

	if 'r' in keys or 'R' in keys:
			footer.set_text(u" PRESSED \n")

if __name__ == '__main__':
    main()
