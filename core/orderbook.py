import os
from sortedcontainers import SortedDict

class Orderbook:

	buyOrders = SortedDict()
	sellOrders = SortedDict()

	def __init__(self):
		True

	def add_order(self, price, amount):

		print("PRICE = " + str(price))

		if price > 0.0:
			# Buy orders
			if price in self.buyOrders:
				updatedAmount = self.buyOrders[price] + amount
				self.buyOrders[price] = updatedAmount
			else:
				self.buyOrders[price] = amount
		else:
			# Sell orders
			if price in self.sellOrders:
				updatedAmount = self.sellOrders[price] + amount
				self.sellOrders[price] = updatedAmount
			else:
				self.sellOrders[price] = amount

"""
orderbook = Orderbook()
orderbook.add_order(2000.0, 5.0)
orderbook.add_order(3000.0, 5.0)
orderbook.add_order(1000.0, 5.0)
orderbook.add_order(2000.0, 5.0)

for key in orderbook.buyOrders:
	print(key)

print(len(orderbook.buyOrders))
"""