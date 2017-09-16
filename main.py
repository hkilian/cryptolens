import requests
import json
import click

# Main entry point for CLI
@click.command()
@click.option('--exchange', default="Bitfinex", help='Exchange in which to pull prices')
@click.argument('symbol')
def main(exchange, symbol):

		url = "https://api.bitfinex.com/v2/ticker/tBTCUSD"
		response = requests.get(url)

		ticker = response.json()
		price = ticker[6]
		change = ticker[4]
		percentChange = ticker[5]
		volume = ticker[7]

		# Echo price
		click.secho('BTC/USD at ', bold=True, nl=False)
		click.echo(click.style('$%s' %price, bold=True,), nl=False)

		# Echo daily change
		dailyChangeColor = "green"
		if percentChange < 0:
			dailyChangeColor = "red"

		click.secho(' (%%%s)' %percentChange, fg=dailyChangeColor)

if __name__ == '__main__':
    main()