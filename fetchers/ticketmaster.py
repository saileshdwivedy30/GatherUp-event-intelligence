import requests
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from fetchers.base_fetcher import BaseFetcher
from database.db_manager import db_manager
from database.duplicate_handler import duplicate_handler
from dateutil.parser import parse

# Load API keys from .env file
load_dotenv()
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")


class TicketmasterFetcher(BaseFetcher):
    """Fetch events from Ticketmaster API."""

    def __init__(self, city="New York", start_date="2025-04-07T00:00:00Z", end_date=None):
        super().__init__("Ticketmaster")
        self.url = "https://app.ticketmaster.com/discovery/v2/events.json"
        self.params = {
            "apikey": TICKETMASTER_API_KEY,
            "size": 199,
            "page": 0,
            "startDateTime": start_date,
            "city": city
        }
        if end_date:
            self.params["endDateTime"] = end_date

    def fetch_events(self, max_events):
        total_fetched = 0
        total_api_events = 0

        # Extract for logging (clean date only)
        city = self.params["city"]
        start_date = self.params["startDateTime"].split("T")[0]

        while total_fetched < max_events:
            print(f"📦 Fetching page {self.params['page']}... (Total Fetched: {total_fetched}/{max_events})")

            response = requests.get(self.url, params=self.params)
            if response.status_code != 200:
                print(f"⚠️ API Error: {response.status_code} - {response.text}")
                break

            data = response.json()
            if "_embedded" in data and "events" in data["_embedded"]:
                for event in data["_embedded"]["events"]:
                    if total_fetched >= max_events:
                        break

                    total_api_events += 1  # Every API event seen

                    event_data = {
                        "name": event["name"],
                        "date_time": event["dates"]["start"].get("dateTime", event["dates"]["start"]["localDate"]),
                        "dto_date_time": parse(event["dates"]["start"].get("dateTime", event["dates"]["start"]["localDate"])),

                        "venue": {
                            "name": event["_embedded"]["venues"][0]["name"],
                            "city": event["_embedded"]["venues"][0]["city"]["name"],
                            "state": event["_embedded"]["venues"][0].get("state", {}).get("stateCode"),
                            "country": event["_embedded"]["venues"][0]["country"]["countryCode"]
                        },
                        "classifications": {
                            "segment": event.get("classifications", [{}])[0].get("segment", {}).get("name", "Unknown"),
                            "genre": event.get("classifications", [{}])[0].get("genre", {}).get("name", "Unknown"),
                            "subGenre": event.get("classifications", [{}])[0].get("subGenre", {}).get("name", "Unknown")
                        },
                        "price_range": event.get("priceRanges", [{"min": None, "max": None, "currency": None}])[0],
                        "image_url": event["images"][0]["url"] if "images" in event else None,
                        "description": event.get("info", "No description available"),
                        "sources": {
                            "ticketmaster": {
                                "url": event.get("url", "No URL available"),
                                "ticket_availability": event["dates"]["status"]["code"]
                            }
                        },
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    }

                    if duplicate_handler.handle_duplicate(event_data):
                        db_manager.insert_event(event_data)
                        total_fetched += 1

                self.params["page"] += 1
                time.sleep(1.1)

            else:
                print("✅ No more events available.")
                break

        # Log duplicates and stats
        duplicate_handler.log_duplicate_summary()
        print(f"📊 Stats — {city} | {start_date} | Fetched: {total_api_events} | Stored: {total_fetched}")

        current_db_count = db_manager.count_events()
        print(f"📁 Total events in DB so far: {current_db_count}")

