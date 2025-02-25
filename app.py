from fetchers.ticketmaster import TicketmasterFetcher

if __name__ == "__main__":
    max_events = int(input("Enter the number of events to fetch: "))
    fetcher = TicketmasterFetcher()
    fetcher.fetch_events(max_events)
