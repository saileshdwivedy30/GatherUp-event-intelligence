import hashlib
from datetime import datetime

class BaseFetcher:
    """Abstract class for event fetching from different sources."""

    def __init__(self, source_name):
        self.source_name = source_name

    def generate_event_id(self, event):
        """Generate a unique MD5 hash based on name, date, and venue."""
        unique_string = event["name"].strip().lower() + event["date_time"] + event["venue"]["name"].strip().lower()
        return hashlib.md5(unique_string.encode()).hexdigest()

    def fetch_events(self, max_events):
        """Fetch events (must be implemented by subclasses)."""
        raise NotImplementedError("fetch_events() must be implemented in subclasses.")
