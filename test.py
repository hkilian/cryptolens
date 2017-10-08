import time
import logging
import decimal

from daemon.orderbook import *
import config


logging.info("")
orderbook = Orderbook()

# Buys
orderbook.add_order(0, 300.0, Decimal(9.33219292))
orderbook.add_order(1, 300.0, Decimal(0.10766))

orderbook.add_order(2, 300.0, Decimal(0.00000320))

orderbook.add_order(2, 320.0, Decimal(12.33219292))

# Sells
orderbook.remove_order(0)
orderbook.remove_order(1)

logging.info("")

logging.info(" - - Sell Orders - - ")

for key in orderbook.sellOrders.islice(0, 5, reverse=True):
	logging.info(str(key) + " - " +  str(orderbook.sellOrders[key]))

logging.info(" - - Buy Orders - - ")

for key in orderbook.buyOrders.islice(0, 5, reverse=True):
	logging.info(str(key) + " - " +  str(orderbook.buyOrders[key]))

logging.info(" - - - - - - - - - ")
logging.info("Best Price = " + " - " +  str(orderbook.get_best_price()))