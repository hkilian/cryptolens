import sys
import os
import time
import json
import urwid
import asyncio
from random import randint
from cryptolens.mvc.displaycommon import *
from cryptolens.mvc.displayhome import *
from cryptolens.mvc.displaymarket import DisplayMarket

palette = [
	('titlebar', 'dark red, bold', ''),
	('table header', 'light gray, bold', ''),
	('refresh button', 'dark green,bold', ''),
	('quit button', 'dark red', ''),
	('getting quote', 'dark blue', ''),
	('headers', 'white,bold', ''),
	('change ', 'dark green', ''),
	('change negative', 'dark red', '')]

def main():
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

if __name__ == "__main__":
    main()

