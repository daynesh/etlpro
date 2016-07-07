#!/usr/bin/python

import MySQLdb
from pymongo import MongoClient
from collections import defaultdict

client = MongoClient("localhost:27017")
db = client.etlpro
orders = db.orders

cnx = MySQLdb.connect(user='root', passwd='hello', db='etlpro')
#cnx.time_zone = 'UTC'
cursor = cnx.cursor()

items = defaultdict(list)
cursor.execute("""
        select id as item_id, order_id, qty, description, price  from items
    """)
prevlen = 0
for (item_id, order_id, qty, description, price) in cursor:
    items[order_id].append({ "item_id" : item_id,
                             "qty" : qty,
                             "description" : description,
                             "price" : price })

tracking = defaultdict(list)
cursor.execute("""
        select order_id, status, timestamp from tracking
    """ )
prevlen = 0
for (order_id, status, time_stamp) in cursor:
    tracking[order_id].append({ "status" : status,
                                "timestamp" : time_stamp })

cursor.execute("""
  select id as order_id, first_name, last_name, shipping_address from orders
""")

for (order_id, first_name, last_name, shipping_address) in cursor:
    doc = { "order_id" : order_id,
            "first_name" : first_name,
            "last_name" : last_name,
            "shipping_address" : shipping_address,
            "items" : items[order_id],
            "tracking" : tracking[order_id] }
    orders.insert_one(doc)


cursor.close()
cnx.close()

client.close()
