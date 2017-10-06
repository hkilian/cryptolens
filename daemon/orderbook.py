import os
from sortedcontainers import SortedDict

class Orderbook:

	buyOrders = SortedDict()
	sellOrders = SortedDict()

	def __init__(self):

		self.bestBuy = 0
		self.bestSell = 0
		self.spread = 0

	def get_best_price(self):
		bestSell = self.sellOrders.keys()[0]
		return bestSell

	def add_order(self, price, amount):

		print("")

		if amount > 0:

			print("BUY ORDER: Price = " + str(price) + ", amount = " + str(amount))

			# Buy orders
			if price in self.buyOrders:
				updatedAmount = self.buyOrders[price] + amount
				self.buyOrders[price] = updatedAmount
			else:
				self.buyOrders[price] = amount
		else:

			print("SELL ORDER: Price = " + str(price) + ", amount = " + str(amount))

			# Sell orders
			if price in self.sellOrders:
				updatedAmount = self.sellOrders[price] + abs(amount)
				self.sellOrders[price] = updatedAmount
			else:
				self.sellOrders[price] = abs(amount)

		# Update best buys and sells
		if(len(self.buyOrders) > 0 and len(self.sellOrders) > 0):

			self.bestBuy = self.buyOrders.keys()[len(self.buyOrders)-1]
			self.bestSell = self.sellOrders.keys()[0]
			self.spread = self.bestSell - self.bestBuy

			print(" - Spread = " + str(self.spread))
			self.match_orders()

	def match_orders(self):

		print(" - MATCHING ORDERS:")

		# If negative spread then match order
		if self.spread < 0:

			print(" - - Spread is negative")

			# Get the best but order
			bestBuyPrice = self.buyOrders.keys()[len(self.buyOrders)-1]
			bestBuyVolume = self.buyOrders[bestBuyPrice]

			print(" - - bestBuyPrice = " + str(bestBuyPrice) + ", bestBuyVolume = " + str(bestBuyVolume))

			# Hold sells which get filled completely
			sellFilledList = []

			# Push sells into the buy orders
			# Loop over the sells in ascending order
			for key in self.sellOrders:

				sellOrderPrice = key
				sellOrderVolume = self.sellOrders[key]

				print(" - - - At sell price = " + str(sellOrderPrice) + ", amount = " + str(sellOrderVolume))

				# Subtract the buy order from the sell
				updatedSellOrderVolume = sellOrderVolume - bestBuyVolume

				print(" - - - - Sell order volume remaining = " + str(updatedSellOrderVolume))

				if(updatedSellOrderVolume < 0):
					print(" - - - - Sell order exhausted")
					sellFilledList.append(sellOrderPrice)


				# Amount of this buy than can be filled by the sell
				buyVolumeRemaining = bestBuyVolume - sellOrderVolume

				print(" - - - - Volume Remaining = " + str(buyVolumeRemaining))

				# Buy order has been filled
				if buyVolumeRemaining < 0:
					print(" - - - - ORDER FILLED COMPLETELY - " + str(bestBuyPrice))
					del self.buyOrders[bestBuyPrice]
					break

				
			# Remove filled sells
			for key in sellFilledList:
				del self.sellOrders[key]



orderbook = Orderbook()

# Buys
orderbook.add_order(120.0, 2.0)
orderbook.add_order(130.0, 2.0)

# Sells
orderbook.add_order(150.0, -3.0)
orderbook.add_order(100.0, -1.0)

print("")
print(" - - Sell Orders - - ")

for key in orderbook.sellOrders.islice(0, 5, reverse=True):
	print(str(key) + " - " +  str(orderbook.sellOrders[key]))

print(" - - Buy Orders - - ")

for key in orderbook.buyOrders.islice(0, 5, reverse=True):
	print(str(key) + " - " +  str(orderbook.buyOrders[key]))

print(" - - - - - - - - - ")
print("Best Price = " + " - " +  str(orderbook.get_best_price()))



