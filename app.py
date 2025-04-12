from fetchers.ticketmaster import TicketmasterFetcher

# Add the cities you want to fetch from
cities = ["New York", "Los Angeles", "Chicago", "Austin", "San Francisco"]

if __name__ == "__main__":
    max_events = int(input("Enter number of events to fetch per city: "))

    total_fetched = 0

    for city in cities:
        print(f"\n🌆 Fetching from: {city}")
        fetcher = TicketmasterFetcher(city=city)  # supports custom city
        fetcher.fetch_events(max_events)
        total_fetched += max_events

    print(f"\n✅ Done! Attempted to fetch up to {total_fetched} events across {len(cities)} cities.")
