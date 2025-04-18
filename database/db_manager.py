import pymongo
import os
from dotenv import load_dotenv
import sys

# Database imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

class DatabaseManager:
    """Handles MongoDB connections and event storage with multi-source merging."""
    load_dotenv()

    def __init__(self, db_name="event_data", collection_name="events"):
        MONGO_URI = os.getenv("MONGO_URI")  # Fetch from .env file

        print(f"DEBUG: Loaded MONGO_URI = {MONGO_URI}")

        if not MONGO_URI or "localhost" in MONGO_URI:
            print("Warning: Connecting to LOCAL MongoDB!")
        else:
            print(f"Connecting to MongoDB Atlas: {MONGO_URI}")

        self.client = pymongo.MongoClient(MONGO_URI)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_event(self, event):
        """Insert a new event or merge it if a duplicate exists."""

        existing_event = self.collection.find_one({"_id": event["_id"]})

        if existing_event:
            # Merge existing event with new event data
            merged_event = self.merge_event_data(existing_event, event)
            self.collection.update_one({"_id": event["_id"]}, {"$set": merged_event})
        else:
            self.collection.insert_one(event)  # Insert new unique event

    def find_event(self, event_id):
        """Find an event by its unique ID."""
        return self.collection.find_one({"_id": event_id})

    def count_events(self):
        """Count unique events in the database."""
        return self.collection.count_documents({})

    def merge_event_data(self, existing_event, new_event):
        """Merge details from a duplicate event into the existing event."""

        # Merge platform_ids
        existing_event.setdefault("platform_ids", {})
        new_event.setdefault("platform_ids", {})
        existing_event["platform_ids"].update(new_event["platform_ids"])

        # Merge tags (combine unique tags)
        existing_event.setdefault("tags", [])
        new_event.setdefault("tags", [])
        existing_event["tags"] = list(set(existing_event["tags"]) | set(new_event["tags"]))

        # Merge ticket types (only add new ones)
        existing_event.setdefault("ticket_types", [])
        new_event.setdefault("ticket_types", [])
        existing_ticket_types = {t["type"]: t for t in existing_event["ticket_types"]}
        for ticket in new_event["ticket_types"]:
            if ticket["type"] not in existing_ticket_types:
                existing_event["ticket_types"].append(ticket)

        # Fix: Handle `NoneType` for `price_range`
        existing_event.setdefault("price_range", {"min": None, "max": None, "currency": "USD"})
        new_event.setdefault("price_range", {"min": None, "max": None, "currency": "USD"})

        existing_min = existing_event["price_range"]["min"]
        new_min = new_event["price_range"]["min"]
        existing_max = existing_event["price_range"]["max"]
        new_max = new_event["price_range"]["max"]

        # Ensure values are not None before comparing
        if existing_min is None:
            existing_event["price_range"]["min"] = new_min
        elif new_min is not None:
            existing_event["price_range"]["min"] = min(existing_min, new_min)

        if existing_max is None:
            existing_event["price_range"]["max"] = new_max
        elif new_max is not None:
            existing_event["price_range"]["max"] = max(existing_max, new_max)

        existing_event["price_range"]["currency"] = new_event["price_range"].get("currency", "USD")

        return existing_event

db_manager = DatabaseManager()
