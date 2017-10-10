import urwid
from .displaycommon import *

class DisplayMarket:

	def __init__(self):
		self.mainPileList = []

		self.leftColumn = urwid.Pile([])
		self.rightColumn = urwid.Pile([])

		self.header = Header()
		self.footer = Footer()

	def ShowLoading(self, loadingText):

		self.text = urwid.Text(loadingText)
		padding = urwid.Padding(self.text, align='center', width='pack')
		filler = urwid.Filler(padding, valign='middle')
		self.mainPileList.append(filler)

	def Update(self, text):
		True

	def ShowOrderBook(self):

		colList = [(10, urwid.Text(('table header', str("Timestamp")))),
					(urwid.Text(('table header', str("Price"))))]

		table = Table("Order Book", colList)
		table.createTable()
		self.rightColumn = table

	def ShowTable(self):

		table = Table()
		self.mainPileList.append(table)

	def PrepareBody(self):

		# Sort left and right columns
		columnList = [(100, self.leftColumn), self.rightColumn]

		self.body = urwid.Columns(columnList)
		self.body = urwid.Padding(self.body, left=2, right=2)
		self.body = urwid.LineBox(self.body)


