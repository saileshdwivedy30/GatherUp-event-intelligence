from pymongo import MongoClient
from dotenv import load_dotenv
import os
import pprint

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["event_data"]
collection = db["events"]

print("Showing 20 sample events:\n")
for event in collection.find().limit(20):
    pprint.pprint(event)
    print("\n" + "-"*50 + "\n")
