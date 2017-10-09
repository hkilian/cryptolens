from decimal import *
import sys, os
import logging
from sortedcontainers import SortedDict
import config

logging.basicConfig(filename='output.log',level=logging.INFO)

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

		self.volume_processed = 0
		self.order_change_volume = 0

	def get_best_price(self):
		bestBuy = self.buyOrders.keys()[len(self.buyOrders)-1]
		return bestBuy

	def remove_order(self, order_id):

		logging.info("REMOVING ORDER: " + str(order_id))

		# Look for order in our order list
		if order_id in self.order_list:

			# Get details
			price = self.order_list[order_id][0]
			amount = self.order_list[order_id][1]

			if amount > 0:

				# Handle buy orders
				logging.info('Subtracting amount (' + str(amount) + ') of (' + str(price) + ') from buy book at price (' + str(price) + ')')

				# Look for order baked into orderbook
				if price in self.buyOrders:
					self.buyOrders[price] -= amount

					logging.info("Remaining volume (" + str(self.buyOrders[price]) + ") at price (" + str(price) + ")")

					# Delete this order level if its below 0
					if self.buyOrders[price] <= 0:
						logging.info("Removing price level (" + str(price) + ") from the buy book")
						del self.buyOrders[price]
				else:
					logging.fatal('Could not find order at price (' + str(price) + ') given by remove order  (' + str(order_id) + ')')

			else:

				# Handle sell orders
				logging.info('Subtracting amount (' + str(amount) + ') from sell book at price (' + str(price) + ')')

				# Look for order baked into orderbook
				if price in self.sellOrders:
					self.sellOrders[price] -= abs(amount)

					# Delete this order level if its below 0
					if self.sellOrders[price] <= 0:
						logging.info("Removing price level " + str(price) + " from the sell book")
						del self.sellOrders[price]

				else:
					logging.fatal('Could not find order at price (' + str(price) + ') given by remove order  (' + str(order_id) + ')')

			del self.order_list[order_id]
			self.total_orders_removed += 1

		else:
			logging.error("COULD NOT FIND ORDER TO REMOVE: " + str(order_id))

	def add_order(self, order_id, price, amount):

		# Bring volume into 8 decimal places
		amount = amount.quantize(Decimal('.00000001'), rounding=ROUND_HALF_DOWN)

		# Stats
		self.volume_processed += abs(amount)
		self.total_orders_processed += 1

		logging.info('self.volume_processed = ' + str(self.volume_processed))

		# Look for existing order with id
		if order_id in self.order_list:
			logging.info("Found existing order with given id(" + str(order_id) + ")")
			self.order_change_volume += abs(amount)

			current_amount = self.order_list[order_id][1]
			self.order_list[order_id] = [price, current_amount + amount]
		else:
			# Add to order to order list
			logging.info("Creating new order with given id(" + str(order_id) + ")")
			abs_amount = abs(amount)
			self.order_list[order_id] = [price, amount]

		if amount > 0:

			logging.info("BUY ORDER: order_id = " + str(order_id) + ", price = " + str(price) + ", amount = " + str(amount))
			self.total_buy_orders_processed += 1

			# Buy orders
			if price in self.buyOrders:

				updatedAmount = self.buyOrders[price] + amount

				logging.info('Price level (' + str(price) + ') found in orderbook, updating volume from (' + str(self.buyOrders[price]) + ') to (' + str(updatedAmount) + ')')

				self.buyOrders[price] = updatedAmount

			else:

				logging.info('Price level (' + str(price) + ') NOT found in orderbook, adding volume of (' + str(amount) + ')')

				self.buyOrders[price] = amount

		else:

			logging.info("SELL ORDER: order_id = " + str(order_id) + ", price = " + str(price) + ", amount = " + str(amount))

			self.total_sell_orders_processed += 1

			# Sell orders
			if price in self.sellOrders:

				updatedAmount = self.sellOrders[price] + abs(amount)

				logging.info('Price level (' + str(price) + ') found in orderbook, updating volume from (' + str(self.sellOrders[price]) + ') to (' + str(updatedAmount) + ')')

				self.sellOrders[price] = updatedAmount

			else:

				logging.info('Price level (' + str(price) + ') NOT found in orderbook, adding volume of (' + str(amount) + ')')

				self.sellOrders[price] = abs(amount)

		# Update best buys and sells
		if(len(self.buyOrders) > 0 and len(self.sellOrders) > 0):

			self.best_buy = self.buyOrders.keys()[len(self.buyOrders)-1]
			self.best_sell = self.sellOrders.keys()[0]
			self.spread = self.best_sell - self.best_buy

			#self.match_orders()

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




