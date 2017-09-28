import os
import json
import requests
from peewee import *
import click

import database
from asset import *
from exchanges.exchange import Exchange
from exchanges.bitrex import Bitrex

# Used to get path of this script
__location__ = os.path.realpath(
	os.path.join(os.getcwd(), os.path.dirname(__file__)))

def initdb():

	# Create tables
	if not Asset.table_exists():
		db.create_tables([Asset])
		db.create_tables([Symbol])
		db.create_tables([AssetSymbol])
		db.create_tables([Market])
		db.create_tables([ExchangeInfo])

	# Create fiat assets
	usd = Asset(name='USD', fiat=True)
	usd.save()

	bitrexMarketsUrl = "https://bittrex.com/api/v1.1/public/getmarkets"
	response = requests.get(bitrexMarketsUrl)
	result = response.json()["result"]

	# Loop over markets
	for market in result:

		# See if base asset with name already exists
		try: 
			Asset.select().where(Asset.name == market['BaseCurrencyLong']).get()
		except DoesNotExist:
			baseAsset = Asset(name=market['BaseCurrencyLong'])
			baseAsset.save()

			# Look for symbol
			try:
				Symbol.select().where(Symbol.name == market['BaseCurrency']).get()
			except DoesNotExist:
				baseSymbol = Symbol(name=market['BaseCurrency'])
				baseSymbol.save()

				symbolLink = AssetSymbol(asset=baseAsset, symbol=baseSymbol)
				symbolLink.save()


		# See if market asset with name already exists
		try: 
			Asset.select().where(Asset.name == market['MarketCurrencyLong']).get()
		except DoesNotExist:
			marketAsset = Asset(name=market['MarketCurrencyLong'])
			marketAsset.save()

			# Look for symbol
			try:
				Symbol.select().where(Symbol.name == market['MarketCurrency']).get()
			except DoesNotExist:
				marketSymbol = Symbol(name=market['MarketCurrency'])
				marketSymbol.save()

				symbolLink = AssetSymbol(asset=marketAsset, symbol=marketSymbol)
				symbolLink.save()

		#click.secho(market['MarketCurrency'] + '-' + market['BaseCurrency'], bold=False)



	"""
	# Bitcoin
	bitcoin = Asset(name='Bitcoin')
	bitcoin.save()

	btcSymbol = Symbol(name='BTC')
	btcSymbol.save()

	bitcoinSymbol = AssetSymbol(coin=bitcoin, symbol=btcSymbol)
	bitcoinSymbol.save()

	# Bitrex exchange
	bitrex = Bitrex()
	bitrex.save()

	btcusdBitrex = Market(exchange=bitrex.info, marketAsset=bitcoin, baseAsset=usd)
	btcusdBitrex.save()
	"""







