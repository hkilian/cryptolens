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

class Symbol(Model):
    name = CharField()

    class Meta:
        database = db # This model uses the "people.db" database.

class CoinSymbols(Model):
    coin = ForeignKeyField(Coin)
    symbol = ForeignKeyField(Symbol)

db.connect()

# Create tables if they dont exist
if not Coin.table_exists():
	db.create_tables([Coin])

bitcoin = Coin(name='Bitcoin', symbol="BTC")
bitcoin.save()