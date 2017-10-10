import os
import sqlite3

# Used to get path of this script
__location__ = os.path.realpath(
	os.path.join(os.getcwd(), os.path.dirname(__file__)))

class DBManager:

	def __init__(self):
		self.databasePath = ""

		# See if db exists
		if os.path.exists(__location__ + "/crypto.db"):
			self.db = sqlite3.connect(__location__  + '/crypto.db')
		else:
			self.CreateDatabase()

	def CreateDatabase(self):

		# Connect to db (file created when not found)
		self.db = sqlite3.connect(__location__  + '/crypto.db')

		# Read sql used to create database schema
		sqlSchema = open(__location__  + "/Coins.sql", "r").read()

		cursor = self.db.cursor()
		cursor.executescript(sqlSchema)
		self.db.commit()
		self.db.close()

	def AddCoin(self, name, symbol):

		cursor = self.db.cursor()
		cursor.execute('''INSERT INTO Coins(Name, Symbol)
                  VALUES(?,?)''', (name, symbol))

db = DBManager()
db.AddCoin("Bitcoin", "BTC")