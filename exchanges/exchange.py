from peewee import *
from database import *

class Exchange(Model):

	name = CharField()

	class Meta:
		database = db

	def Name(self):
		return self.name