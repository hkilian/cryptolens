import urwid
import time
import itertools

class Header(urwid.WidgetWrap):

	def __init__(self):

		self.title = "Cryptolens"

		# Header
		self.header_left = urwid.Text(u"\n" + self.title + "\n")
		self.header_left = urwid.AttrWrap(self.header_left, 'titlebar')

		self.header_right = urwid.Text(u"\nBitcoin USD/BTC (Bitfinex)", align='right')
		self.header_right = urwid.AttrWrap(self.header_right, 'titlebar')

		columns = urwid.Columns([self.header_left, self.header_right])

		self.__super.__init__(urwid.AttrWrap(columns, 'header'))

class Footer(urwid.WidgetWrap):

	def __init__(self):

		# Footer
		self.reloadText = urwid.Text(u" Press q to exit \n")
		self.reloadText = urwid.AttrWrap(self.reloadText, 'titlebar')

		columns = urwid.Columns([self.reloadText])

		self.__super.__init__(urwid.AttrWrap(columns, 'footer'))

class Table(urwid.WidgetWrap):

	def __init__(self, columns, rows, column_names=[], column_widths=[], fillbottom=False):

		# Create columns based on the passed in column names
		self.col_list = []

		# Fill values from the bottom
		self.fillbottom = fillbottom

		# Header row for table
		self.head_row = []

		# Total rows in table
		self.row_count = rows

		# Widths for each column
		self.column_widths = column_widths

		# If column names have been provided
		if len(column_names) > 0:
			j = 0
			for name in column_names:
				if self.column_widths and self.column_widths[j] != 0:
					self.head_row.append((self.column_widths[j], urwid.Text(('table header', str(name)))))
				else:
					self.head_row.append(urwid.Text(('table header', str(name))))

		self.columnCount = columns
		self.listwalker = urwid.SimpleListWalker([])

	def update_data(self, data):

		# If head row has data then add as first row
		index_start = 0
		if len(self.head_row) > 0:
			self.listboxBody.body[0] = urwid.Columns(self.head_row)
			index_start = 1

		# About if no data
		if len(data) < 1:
			return

		if self.fillbottom == True:
			data.reverse()

		for i in range(0, self.row_count):

			# End loop if out of data
			if i >= len(data):
				break

			colRowList = []
			for j in range(len(data[0])):
				if self.column_widths and self.column_widths[j] != 0:
					colRowList.append((self.column_widths[j], urwid.Text(str(data[i][j]))))
				else:
					colRowList.append(urwid.Text(str(data[i][j])))

			row = urwid.Columns(colRowList)

			if self.fillbottom == False:
				self.listboxBody.body[index_start + i] = row
			else:
				self.listboxBody.body[self.row_count - 1 - (i)] = row


	def create_table(self):

		# List of all rows
		rows = []

		# If has a header row then add 1 to end index
		if len(self.head_row) > 0:
			# Add header row
			rows.append(urwid.Columns(self.head_row))

		# Loop over rows
		for i in range(0, self.row_count):

			colRowList = []
			for j in range(self.columnCount):
				colRowList.append(urwid.Text(str("-")))

			col = urwid.Columns(colRowList)
			rows.append(col)

		# Hold onto walker so we can modify list later
		self.listwalker = urwid.SimpleListWalker(rows)
		self.listboxBody = urwid.ListBox(self.listwalker)
		self.listboxBody = urwid.AttrWrap(self.listboxBody, 'listbox')

		self.__super.__init__(self.listboxBody)




