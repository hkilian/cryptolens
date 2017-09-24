from peewee import *
from database import *
from exchanges.exchange import Exchange

class Coin(Model):
    name = CharField()
    fiat = BooleanField(default=False)
    creation = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        database = db

class Symbol(Model):
    name = CharField()

    class Meta:
        database = db

class CoinSymbol(Model):
    coin = ForeignKeyField(Coin)
    symbol = ForeignKeyField(Symbol)

    class Meta:
        database = db

class Market(Model):

    exchange = ForeignKeyField(Exchange)
    coin1 = ForeignKeyField(Coin, related_name='coin1_coin')
    coin2 = ForeignKeyField(Coin, related_name='coin2_coin')

    creation = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        database = db









