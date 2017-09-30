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

	def __init__(self, header, cols):

		self.tableHeader = urwid.Text((header))
		self.colList = cols
		self.columnCount = len(self.colList)

	def createTable(self):

		prices = []
		col = urwid.Columns(self.colList)
		prices.append(col)

		for i in range(20):

			colRowList = []
			for i in range(self.columnCount-1):
				colRowList.append(urwid.Text(str("-")))

			col = urwid.Columns(colRowList)

			prices.append(col)

		lw = urwid.SimpleListWalker(prices)
		listboxBody = urwid.ListBox(lw)

		listboxBody = urwid.AttrWrap(listboxBody, 'listbox')
		self.body = urwid.Frame(listboxBody, self.tableHeader)

		self.__super.__init__(urwid.AttrWrap(self.body, 'footer'))




