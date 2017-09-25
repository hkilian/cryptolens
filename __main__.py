import time
import json
import click

# For testing, remove db
import os
if os.path.exists('test.db'):
	#os.remove('test.db')
	True

from initdb import *
from exchanges.bitfinex import Bitfinex
from exchanges.gdax import GDAX
from exchanges.bitrex import Bitrex
from exchanges.poloniex import Poloniex
from exchanges.bitmex import Bitmex

# Main entry point for CLI
@click.command()
@click.option('--exchange', default="Bitfinex", help='Exchange in which to pull prices')
@click.argument('symbol')
def main(exchange, symbol):

	# Run initdb if missing db
	if not Asset.table_exists():
		click.secho('No database found, pulling in coin information from exchanges...', bold=True)
		initdb()


	bitrex = Bitrex()
	data = bitrex .PullData(symbol.upper())
	outputPrice("Bitrex", data)
	
	"""
	bitfinex = Bitfinex()
	data = bitfinex.PullData()
	outputPrice("Bitfinex", data)

	gdax = GDAX()
	data = gdax.PullData()
	outputPrice("GDAX", data)

	bitmex = Bitmex()
	data = bitmex.PullData()
	outputPrice("Bitmex", data)

	poloniex = Poloniex()
	data = poloniex.PullData()
	outputPrice("Poloniex", data)
	"""
def outputPrice(exchangeName, data):
	if not data:
		click.secho('Could not connect', fg="red")
		return

	# Echo price
	click.secho('%s ' %exchangeName, bold=False, nl=False)
	click.secho('%s/USD at '%data['marketAsset'], bold=True, nl=False)
	click.echo(click.style('$%s' %data['price'], bold=True), nl=False)

	# Echo daily change
	dailyChangeColor = "green"
	if data['percentChange'] < 0:
		dailyChangeColor = "red"

	click.secho(' (%%%s)' %data['percentChange'], fg=dailyChangeColor)


if __name__ == '__main__':
    main()
