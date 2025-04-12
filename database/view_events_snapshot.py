# from pymongo import MongoClient
# from dotenv import load_dotenv
# import os
# import pprint
#
# load_dotenv()
#
# client = MongoClient(os.getenv("MONGO_URI"))
# db = client["event_data"]
# collection = db["events"]
#
# print("📦 Showing 10 sample events:\n")
# for event in collection.find().limit(10):
#     pprint.pprint({
#         "_id": event.get("_id"),
#         "name": event.get("name"),
#         "category": event.get("category"),
#         "date_time": event.get("date_time"),
#         "venue": event.get("venue", {}).get("city"),
#     })
#     print("-" * 50)
#
# print("\n📊 Total events in DB:", collection.count_documents({}))

from pymongo import MongoClient
from dotenv import load_dotenv
import os
import pprint

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["event_data"]
collection = db["events"]

print("📦 Showing 20 sample events:\n")
for event in collection.find().limit(20):
    pprint.pprint(event)
    print("\n" + "-"*50 + "\n")

