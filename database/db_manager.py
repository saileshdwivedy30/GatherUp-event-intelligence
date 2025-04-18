import pymongo
import os
from dotenv import load_dotenv

class DatabaseManager:
    """Handles MongoDB connections and event storage with multi-source merging."""

    dotenv_path = os.path.join(os.path.dirname(__file__), '/Users/saileshdwivedy/PycharmProjects/GatherUp/.env')  # Adjust path if needed
    load_dotenv(dotenv_path)

    def __init__(self, db_name="event_data", collection_name="events"):
        MONGO_URI = os.getenv("MONGO_URI")  # Fetch from .env file

        #print(f"DEBUG: Loaded MONGO_URI = {MONGO_URI}")

        if not MONGO_URI or "localhost" in MONGO_URI:
            print("Warning: Connecting to LOCAL MongoDB!")
        else:
            print(f"Connecting to MongoDB Atlas!")

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
        """Merge only source URLs from the new event into the existing event."""

        # Ensure both have sources dicts
        existing_event.setdefault("sources", {})
        new_event.setdefault("sources", {})

        # Merge sources (e.g., add 'eventbrite' if it’s not already there)
        existing_event["sources"].update(new_event["sources"])

        return existing_event


db_manager = DatabaseManager()
