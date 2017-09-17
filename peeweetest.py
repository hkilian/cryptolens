import os
from peewee import *

# Used to get path of this script
__location__ = os.path.realpath(
	os.path.join(os.getcwd(), os.path.dirname(__file__)))

db = SqliteDatabase(__location__ + '/people.db')

class Coin(Model):
    name = CharField()
    symbol = CharField()
    creation = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        database = db # This model uses the "people.db" database.

db.connect()
db.create_tables([Coin])

bitcoin = Coin(name='Bitcoin', symbol="BTC")
bitcoin.save()