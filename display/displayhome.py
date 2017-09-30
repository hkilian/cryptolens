import urwid
from .displaycommon import *

class DisplayHome:

	def __init__(self):
		self.mainPileList = []

		self.topCoins = urwid.Pile([])

	def ShowLoading(self, loadingText):

		self.text = urwid.Text(loadingText)
		padding = urwid.Padding(self.text, align='center', width='pack')
		filler = urwid.Filler(padding, valign='middle')
		self.mainPileList.append(filler)

	def Update(self, text):
		self.text.set_text(text)

	def ShowTopCoins(self):

		colList = [(3, urwid.Text(('table header', str("-")))),
									 (urwid.Text(('table header', str("Symbol")))),
									 (urwid.Text(('table header', str("Price")))),
									 (urwid.Text(('table header', str("Market Cap")))),
									 (urwid.Text(('table header', str("Volume")))),
									 (urwid.Text(('table header', str("24hr Change")))),
									 (urwid.Text(('table header', str("Last Update"))))]

		table = Table("Top coins by marketcap (Bitfinex):", colList)
		table.createTable()
		self.topCoins = table

	def PrepareBody(self):

		# Sort left and right columns
		mainList = [self.topCoins]

		self.body = urwid.Pile(mainList)
		self.body = urwid.Padding(self.body, left=2, right=2)
		self.body = urwid.LineBox(self.body)





