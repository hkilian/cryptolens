import time
import json

import requests
import click

# Main entry point for CLI
@click.command()
@click.option('--exchange', default="Bitfinex", help='Exchange in which to pull prices')
@click.argument('symbol')
def main(exchange, symbol):
			
	data = pullData()
	if not data:
		click.secho('Could not connect', fg="red")
		return

	# Echo price
	click.secho('Bitfinex: ', bold=False, nl=False)
	click.secho('BTC/USD at ', bold=True, nl=False)
	click.echo(click.style('$%s' %data['price'], bold=True), nl=False)

	# Echo daily change
	dailyChangeColor = "green"
	if data['percentChange'] < 0:
		dailyChangeColor = "red"

	click.secho(' (%%%s)' %data['percentChange'], fg=dailyChangeColor)



def pullData():

	url = "https://api.bitfinex.com/v2/ticker/tBTCUSD"
	response = requests.get(url)
	ticker = response.json()

	if len(ticker) != 10:
		click.echo(click.style('%s' %ticker, bold=True))
		return False

	data = {}
	data['price'] = ticker[6]
	data['change'] = ticker[4]
	data['percentChange'] = ticker[5]
	data['volume'] = ticker[7]

	return data

if __name__ == '__main__':
    main()
