from fetchers.ticketmaster import TicketmasterFetcher
from fetchers.eventbrite import EventbriteFetcher
from datetime import datetime, timedelta, timezone
import re

# List of target cities
cities = ["New York", "Los Angeles", "Chicago", "Austin", "San Francisco", "Seattle", "Miami", "Denver", "Boston", "Atlanta"]

city_to_slug = {
    "New York": "ny--new-york",
    "Los Angeles": "ca--los-angeles",
    "Chicago": "il--chicago",
    "Austin": "tx--austin",
    "San Francisco": "ca--san-francisco",
    "Seattle": "wa--seattle",
    "Miami": "fl--miami",
    "Denver": "co--denver",
    "Boston": "ma--boston",
    "Atlanta": "ga--atlanta"
}


def format_for_eventbrite(city_name):
    """Converts city name to Eventbrite-compatible slug like 'co--boulder'."""
    city_parts = city_name.lower().replace(",", "").split()
    return "--".join(city_parts)

if __name__ == "__main__":
    max_events_per_day = 50
    total_days = 10
    max_events_eventbrite = 50  # Max per city from Eventbrite
    base_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    total_fetched = 0

    for city in cities:
        print(f"\nFetching events for: {city}")

        # Eventbrite fetching
        eventbrite_city = city_to_slug.get(city)
        print(f"Looking up Eventbrite slug for '{city}' -> Found: {eventbrite_city}")
        if not eventbrite_city:
            print(f"No Eventbrite slug found for {city}. Skipping...")
            continue

        print(f"\nEventbrite: Fetching events for {city} -> {eventbrite_city}")
        eventbrite_fetcher = EventbriteFetcher(city=eventbrite_city)
        eventbrite_fetcher.fetch_events(max_events_eventbrite)
        
        # Ticketmaster fetching per day
        for i in range(total_days):
            current_date = base_date + timedelta(days=i)
            start_date_str = current_date.strftime("%Y-%m-%dT00:00:00Z")
            end_date_str = current_date.strftime("%Y-%m-%dT23:59:59Z")

            print(f"\nTicketmaster: {current_date.strftime('%Y-%m-%d')}")

            fetcher = TicketmasterFetcher(
                city=city,
                start_date=start_date_str,
                end_date=end_date_str
            )
            fetcher.fetch_events(max_events_per_day)
            total_fetched += max_events_per_day
        

    print(f"\nDone! Attempted to fetch up to {total_fetched} Ticketmaster events across {len(cities)} cities over {total_days} days.")
