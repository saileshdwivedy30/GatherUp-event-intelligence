# from fetchers.ticketmaster import TicketmasterFetcher
#
# # Add the cities you want to fetch from
# cities = ["New York", "Los Angeles", "Chicago", "Austin", "San Francisco"]
#
# if __name__ == "__main__":
#     max_events = int(input("Enter number of events to fetch per city: "))
#
#     total_fetched = 0
#
#     for city in cities:
#         print(f"\n🌆 Fetching from: {city}")
#         fetcher = TicketmasterFetcher(city=city)  # supports custom city
#         fetcher.fetch_events(max_events)
#         total_fetched += max_events
#
#     print(f"\n✅ Done! Attempted to fetch up to {total_fetched} events across {len(cities)} cities.")

from datetime import datetime, timedelta, timezone
from fetchers.ticketmaster import TicketmasterFetcher

# List of target cities
cities = ["New York", "Los Angeles", "Chicago", "Austin", "San Francisco", "Seattle", "Miami", "Denver", "Boston", "Atlanta"]

if __name__ == "__main__":
    max_events_per_day = 50
    total_days = 10
    base_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    total_fetched = 0

    for city in cities:
        print(f"\n🌆 Fetching events for: {city}")

        for i in range(total_days):
            current_date = base_date + timedelta(days=i)
            start_date_str = current_date.strftime("%Y-%m-%dT00:00:00Z")
            end_date_str = current_date.strftime("%Y-%m-%dT23:59:59Z")

            print(f"\n📅 Fetching events for {current_date.strftime('%Y-%m-%d')}")

            fetcher = TicketmasterFetcher(
                city=city,
                start_date=start_date_str,
                end_date=end_date_str
            )
            fetcher.fetch_events(max_events_per_day)
            total_fetched += max_events_per_day

    print(f"\n✅ Done! Attempted to fetch up to {total_fetched} events across {len(cities)} cities over {total_days} days.")