import hashlib
from datetime import datetime
import re

class BaseFetcher:
    """Abstract class for event fetching from different sources."""

    def __init__(self, source_name):
        self.source_name = source_name

    @staticmethod
    def normalize_name(name):
        name = name.lower().strip()
        name = re.sub(r'[^\w\s]', '', name)  # remove punctuation
        name = re.sub(r'\s+', ' ', name)  # collapse multiple spaces
        return name

    def generate_event_id(self, event):
        """Generate a unique MD5 hash based on name, date, and venue."""
        unique_string = self.normalize_name(event["name"]) + event["date_time"] + event["venue"]["name"].strip().lower()
        return hashlib.md5(unique_string.encode()).hexdigest()

    def fetch_events(self, max_events):
        """Fetch events (must be implemented by subclasses)."""
        raise NotImplementedError("fetch_events() must be implemented in subclasses.")
