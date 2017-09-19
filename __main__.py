import time
import json

import click
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
	
	bitfinex = Bitfinex()
	data = bitfinex.PullData()
	outputPrice("Bitfinex", data)

	gdax = GDAX()
	data = gdax.PullData()
	outputPrice("GDAX", data)

	bitrex = Bitrex()
	data = bitrex .PullData()
	outputPrice("Bitrex", data)

	bitmex = Bitmex()
	data = bitmex.PullData()
	outputPrice("Bitmex", data)

	poloniex = Poloniex()
	data = poloniex.PullData()
	outputPrice("Poloniex", data)

def outputPrice(exchangeName, data):
	if not data:
		click.secho('Could not connect', fg="red")
		return

	# Echo price
	click.secho('%s ' %exchangeName, bold=False, nl=False)
	click.secho('BTC/USD at ', bold=True, nl=False)
	click.echo(click.style('$%s' %data['price'], bold=True), nl=False)

	# Echo daily change
	dailyChangeColor = "green"
	if data['percentChange'] < 0:
		dailyChangeColor = "red"

	click.secho(' (%%%s)' %data['percentChange'], fg=dailyChangeColor)


if __name__ == '__main__':
    main()
