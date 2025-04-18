import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import os

# Database imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from database.db_manager import db_manager
from database.duplicate_handler import duplicate_handler
from fetchers.base_fetcher import BaseFetcher

from dateutil.parser import parse

class EventbriteFetcher(BaseFetcher):
    def __init__(self, city="co--boulder"):
        self.city = city
        self.url = f"https://www.eventbrite.com/d/{self.city}/events/"
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def fetch_html(self):
        """Fetches the Eventbrite events page for the specified city."""
        response = requests.get(self.url, headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None
        return response.text

    def extract_json_script(self, html):
        """Extracts JSON data from the <script> tag in the Eventbrite page."""
        soup = BeautifulSoup(html, "html.parser")
        script_tag = soup.find("script", type="application/ld+json")
        return script_tag.string.strip() if script_tag else None

    def parse_event_data(self, json_string):
        """Parses the JSON data and returns a list of event items."""
        try:
            json_data = json.loads(json_string)
            return json_data.get('itemListElement', [])
        except json.JSONDecodeError:
            print("Error parsing JSON data")
            return []

    def process_event_data(self, event_items, max_events=None):
        """Processes event data, validates it, and inserts it into the database."""
        count = 0

        #If location is Unknown:
        state_name = self.city.split("--")[0].upper()
        city_name = self.city.split("--")[1]

        for event_item in event_items:
            if max_events and count >= max_events:
                break  # Stop processing if max_events limit is reached

            event = event_item.get("item", {})

            if not event:
                continue  # Skip empty events

            # Extract event details with safe defaults
            event_data = {
                "name": event.get("name"),
                "date_time": event.get("startDate"),
                "dto_date_time": parse(event.get("startDate")),
                "venue": {
                    "name": event.get("location", {}).get("name", "Unknown Venue"),
                    "city": event.get("location", {}).get("address", {}).get("addressLocality", city_name),
                    "state": event.get("location", {}).get("address", {}).get("addressRegion", state_name),
                    "country": event.get("location", {}).get("address", {}).get("addressCountry", "US")
                },
                "image_url": event.get("image", ""),
                "description": event.get("description", ""),
                "sources": {
                    "eventbrite": {
                        "url": event.get("url", ""),
                        "ticket_availability": "Available"
                    }
                },
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            # Validate required fields
            if not event_data["name"] or not event_data["date_time"] or not event_data["sources"]["eventbrite"]["url"]:
                print(f"Skipping event due to missing fields: {event_data}")
                continue

            # Handle duplicates and insert into DB
            if duplicate_handler.handle_duplicate(event_data):
                db_manager.insert_event(event_data)
                count += 1

        duplicate_handler.log_duplicate_summary()
        print(f"Processed {count} events successfully!")

    def fetch_events(self, max_events=None):
        """Main method to fetch and process events."""
        html = self.fetch_html()
        if not html:
            return

        json_string = self.extract_json_script(html)
        if not json_string:
            print("No JSON data found in the HTML.")
            return

        event_items = self.parse_event_data(json_string)
        self.process_event_data(event_items, max_events)
