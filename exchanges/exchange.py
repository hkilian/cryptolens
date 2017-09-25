from peewee import *
from database import *

class ExchangeInfo(Model):

	name = CharField()

	class Meta:
		database = db

class Exchange():

	info = ExchangeInfo()

	def __init__(self, name):
		self.info.name = name

	class Meta:
		database = db

	def Name(self):
		return self.name

	def save(self):
		self.info.save()