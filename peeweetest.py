import os
from peewee import *
import database
from coin import *
from exchanges.exchange import Exchange
from exchanges.bitrex import Bitrex

# Used to get path of this script
__location__ = os.path.realpath(
	os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Create tables if they dont exist
if not Coin.table_exists():
	db.create_tables([Coin])
	db.create_tables([Symbol])
	db.create_tables([CoinSymbol])
	db.create_tables([Market])
	db.create_tables([Exchange])

# Fiat
usd = Coin(name='USD', fiat=True)
usd.save()

# Bitcoin
bitcoin = Coin(name='Bitcoin')
bitcoin.save()

btcSymbol = Symbol(name='BTC')
btcSymbol.save()

bitcoinSymbol = CoinSymbol(coin=bitcoin, symbol=btcSymbol)
bitcoinSymbol.save()

# Bitrex exchange
bitrex = Bitrex()
bitrex.save()

btcusdBitrex = Market(exchange=bitrex, coin1=bitcoin, coin2=usd)
btcusdBitrex.save()








