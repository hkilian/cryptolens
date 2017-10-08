import time
import logging
import decimal
import asyncio

from daemon.processor import *
import config

# Runs until processor signal exit
async def main():

	logging.info("Running now...")

	processor = BitfinexProcessor()

	while True:
		await asyncio.sleep(1)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
