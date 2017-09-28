import urwid


class Header(urwid.WidgetWrap):

	def __init__(self):

		self.title = "Cryptolens"

		# Header
		self.header = urwid.Text(u"\n" + self.title + " (q to exit)")
		self.header = urwid.AttrWrap(self.header, 'titlebar')

		columns = urwid.Columns([self.header])

		self.__super.__init__(urwid.AttrWrap(columns, 'header'))

class Footer(urwid.WidgetWrap):

	def __init__(self):

		# Footer
		self.reloadText = urwid.Text(u" Press r to pull in data \n")
		self.reloadText = urwid.AttrWrap(self.reloadText, 'titlebar')

		columns = urwid.Columns([self.reloadText])

		self.__super.__init__(urwid.AttrWrap(columns, 'footer'))

class Table(urwid.WidgetWrap):

	def __init__(self):

		self.tableHeader = urwid.Text(('table header', "Top 10 coins by marketcap (Bitfinex):"))

		prices = []
		colList = [(3, urwid.Text(('table header', str("-")))),
									 (urwid.Text(('table header', str("Symbol")))),
									 (urwid.Text(('table header', str("Price")))),
									 (urwid.Text(('table header', str("Market Cap")))),
									 (urwid.Text(('table header', str("Volume")))),
									 (urwid.Text(('table header', str("24hr Change")))),
									 (urwid.Text(('table header', str("Last Update"))))]

		col = urwid.Columns(colList)
		prices.append(col)

		for i in range(10):

				colList = [(3, urwid.Text(str(i + 1))),
									 (urwid.Text(str("-"))),
									 (urwid.Text(str("-"))),
									 (urwid.Text(str("-"))),
									 (urwid.Text(str("-"))),
									 (urwid.Text(str("-"))),
									 (urwid.Text(str("-")))]

				col = urwid.Columns(colList)

				prices.append(col)

		lw = urwid.SimpleListWalker(prices)
		listboxBody = urwid.ListBox(lw)

		listboxBody = urwid.AttrWrap(listboxBody, 'listbox')
		self.body = urwid.Frame(listboxBody, self.tableHeader)

		self.__super.__init__(urwid.AttrWrap(self.body, 'footer'))

class Display:

	def __init__(self):
		self.mainPileList = []
		self.header = Header()
		self.footer = Footer()

	def ShowLoading(self, loadingText):

		self.text = urwid.Text(loadingText)
		padding = urwid.Padding(self.text, align='center', width='pack')
		filler = urwid.Filler(padding, valign='middle')
		self.mainPileList.append(filler)

	def Update(self, text):
		self.text.set_text(text)

	def ShowTable(self):

		table = Table()
		self.mainPileList.append(table)

	def Show(self):

		self.body = urwid.Pile(self.mainPileList)
		self.body = urwid.Padding(self.body, left=2, right=2)
		self.body = urwid.LineBox(self.body)

		self.view = urwid.Frame(self.body, header=self.header, footer=self.footer)
		self.view = urwid.Padding(self.view, left=2, right=2)



def input_filter(keys, raw):

		if 'q' in keys or 'Q' in keys:
				raise urwid.ExitMainLoop

		if 'r' in keys or 'R' in keys:
				footer.set_text(u" PRESSED \n")


