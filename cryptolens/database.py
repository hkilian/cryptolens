import os
from peewee import *

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Connect to db
db = SqliteDatabase(__location__ + '/test.db')
db.connect()








