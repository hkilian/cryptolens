from peewee import *
from database import *
from exchanges.exchange import ExchangeInfo

class Asset(Model):

    name = CharField()
    fiat = BooleanField(default=False)
    creation = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        database = db

class Symbol(Model):
    name = CharField()

    class Meta:
        database = db

class AssetSymbol(Model):
    asset = ForeignKeyField(Asset)
    symbol = ForeignKeyField(Symbol)

    class Meta:
        database = db

class Market(Model):

    exchange = ForeignKeyField(ExchangeInfo)
    marketAsset = ForeignKeyField(Asset, related_name='market_asset')
    baseAsset = ForeignKeyField(Asset, related_name='base_asset')

    creation = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        database = db









