from fetchers.ticketmaster import TicketmasterFetcher
from fetchers.eventbrite import EventbriteFetcher

if __name__ == "__main__":
    max_events = int(input("Enter the number of events to fetch: "))
    ticketmaster_fetcher  = TicketmasterFetcher()
    ticketmaster_fetcher.fetch_events(max_events)
    eventbrite_fetcher = EventbriteFetcher()
    eventbrite_fetcher.fetch_events(max_events)
