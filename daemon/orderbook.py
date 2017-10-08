import sys, os
import logging
from sortedcontainers import SortedDict

class Orderbook:

	buyOrders = SortedDict()
	sellOrders = SortedDict()
	order_list = {}

	def __init__(self):

		self.best_buy = 0
		self.best_sell = 0
		self.spread = 0

		# Stats
		self.total_orders_processed = 0
		self.total_buy_orders_processed = 0
		self.total_sell_orders_processed = 0
		self.total_orders_removed = 0

	def get_best_price(self):
		bestBuy = self.buyOrders.keys()[len(self.buyOrders)-1]
		return bestBuy

	def remove_order(self, order_id):

		logging.info("REMOVING ORDER: " + str(order_id))

		if order_id in self.order_list:

			price = self.order_list[order_id][0]
			amount = self.order_list[order_id][1]

			if amount > 0:
				logging.info("Subtracting buy from book at price = " + str(price))

				# Look for order baked into orderbook
				if price in self.buyOrders:
					self.buyOrders[price] -= amount

					# Delete this order level if its below 0
					if self.buyOrders[price] <= 0:
						logging.info("Removing price level " + str(price) + " from the buy book")
						del self.buyOrders[price]

				else:
					logging.error("Could not find order at price given by remove order")

			else:

				logging.info("Subtracting sell from book at price = " + str(price))

				# Look for order baked into orderbook
				if price in self.sellOrders:
					self.sellOrders[price] -= amount

					# Delete this order level if its below 0
					if self.sellOrders[price] <= 0:
						logging.info("Removing price level " + str(price) + " from the sell book")
						del self.sellOrders[price]

				else:
					logging.error("Could not find order at price given by remove order")

			del self.order_list[order_id]
			self.total_orders_removed += 1

		else:
			logging.error("COULD NOT FIND ORDER TO REMOVE: " + str(order_id))

	def add_order(self, order_id, price, amount):

		self.total_orders_processed += 1

		# Look for existing order with id
		if order_id in self.order_list:
			logging.info("Found already existing order")
			self.order_list[order_id] = [price, amount]
		else:
			self.order_list[order_id] = [price, amount]

		if amount > 0:

			logging.info("BUY ORDER: order_id = " + str(order_id) + ", price = " + str(price) + ", amount = " + str(amount))

			self.total_buy_orders_processed += 1

			# Buy orders
			if price in self.buyOrders:
				updatedAmount = self.buyOrders[price] + amount
				self.buyOrders[price] = updatedAmount
			else:
				self.buyOrders[price] = amount
		else:

			logging.info("SELL ORDER: order_id = " + str(order_id) + ", price = " + str(price) + ", amount = " + str(amount))

			self.total_sell_orders_processed += 1

			# Sell orders
			if price in self.sellOrders:
				updatedAmount = self.sellOrders[price] + abs(amount)
				self.sellOrders[price] = updatedAmount
			else:
				self.sellOrders[price] = abs(amount)

		# Update best buys and sells
		if(len(self.buyOrders) > 0 and len(self.sellOrders) > 0):

			self.best_buy = self.buyOrders.keys()[len(self.buyOrders)-1]
			self.best_sell = self.sellOrders.keys()[0]
			self.spread = self.best_sell - self.best_buy

			logging.info(" - Spread = " + str(self.spread))
			#self.match_orders()

		logging.info("")

	def match_orders(self):

		logging.info(" - MATCHING ORDERS:")

		# If negative spread then match order
		if self.spread <= 0:

			logging.info(" - - Spread is negative")

			# Get the best but order
			bestBuyPrice = self.buyOrders.keys()[len(self.buyOrders)-1]
			bestBuyVolume = self.buyOrders[bestBuyPrice]

			logging.info(" - - bestBuyPrice = " + str(bestBuyPrice) + ", bestBuyVolume = " + str(bestBuyVolume))

			# Hold sells which get filled completely
			sellFilledList = []

			# Push sells into the buy orders
			# Loop over the sells in ascending order
			for key in self.sellOrders:

				sellOrderPrice = key
				sellOrderVolume = self.sellOrders[key]

				logging.info(" - - - At sell price = " + str(sellOrderPrice) + ", amount = " + str(sellOrderVolume))

				if bestBuyPrice < sellOrderPrice:
					logging.info(" - - - - NO MORE SELLERS TO FILL BUY ORDER")
					break

				# Subtract the buy order from the sell
				updatedSellOrderVolume = sellOrderVolume - bestBuyVolume

				logging.info(" - - - - Sell order volume remaining = " + str(updatedSellOrderVolume))

				if(updatedSellOrderVolume < 0):
					logging.info(" - - - - Sell order exhausted")
					sellFilledList.append(sellOrderPrice)


				# Amount of this buy than can be filled by the sell
				buyVolumeRemaining = bestBuyVolume - sellOrderVolume

				logging.info(" - - - -Buy Volume Remaining = " + str(buyVolumeRemaining))

				# Buy order has been filled
				if buyVolumeRemaining < 0:
					logging.info(" - - - - ORDER FILLED COMPLETELY - " + str(bestBuyPrice))
					del self.buyOrders[bestBuyPrice]
					break

				
			# Remove filled sells
			for key in sellFilledList:
				del self.sellOrders[key]


""""
orderbook = Orderbook()

# Buys
orderbook.add_order(120.0, 1.0)

# Sells
orderbook.add_order(120.0, -1.0)

logging.info("")
logging.info(" - - Sell Orders - - ")

for key in orderbook.sellOrders.islice(0, 5, reverse=True):
	logging.info(str(key) + " - " +  str(orderbook.sellOrders[key]))

logging.info(" - - Buy Orders - - ")

for key in orderbook.buyOrders.islice(0, 5, reverse=True):
	logging.info(str(key) + " - " +  str(orderbook.buyOrders[key]))

logging.info(" - - - - - - - - - ")
logging.info("Best Price = " + " - " +  str(orderbook.get_best_price()))
"""


