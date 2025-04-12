import hashlib
from fuzzywuzzy import fuzz
from database.db_manager import db_manager


class DuplicateHandler:
    """Handles duplicate event detection before insertion."""

    def __init__(self):
        self.duplicate_count = 0
        self.merged_examples = []  # Stores examples of merged duplicates

    def generate_event_id(self, event):
        """Generate a unique MD5 hash for the event based on name, date, and venue."""
        unique_string = event["name"].strip().lower() + event["date_time"] + event["venue"]["name"].strip().lower()
        return hashlib.md5(unique_string.encode()).hexdigest()

    def is_duplicate(self, event1, event2):
        """Check if two events are near-duplicates using fuzzy matching."""
        if event1["date_time"] == event2["date_time"] and event1["venue"]["name"] == event2["venue"]["name"]:
            name_similarity = fuzz.ratio(event1["name"].lower(), event2["name"].lower())
            return name_similarity > 85  # Consider as duplicate if similarity > 85%
        return False

    def handle_duplicate(self, event_data):
        """Check if an event is a duplicate before passing it to db_manager for merging."""
        event_data["_id"] = self.generate_event_id(event_data)
        existing_event = db_manager.find_event(event_data["_id"])

        if existing_event:
            if self.is_duplicate(existing_event, event_data):
                self.duplicate_count += 1
                if len(self.merged_examples) < 2:
                    self.merged_examples.append({
                        "original": {
                            "name": existing_event["name"],
                            "date_time": existing_event["date_time"],
                            "venue": existing_event["venue"]["name"]
                        },
                        "duplicate": {
                            "name": event_data["name"],
                            "date_time": event_data["date_time"],
                            "venue": event_data["venue"]["name"]
                        }
                    })

                # Pass both events to `db_manager` for merging
                db_manager.insert_event(event_data)
                return False  # Indicates a duplicate was found

        return True  # Indicates event is unique and should be inserted

    def log_duplicate_summary(self):
        """Log duplicate handling summary at the end."""
        print(f"🔄 Detected {self.duplicate_count} duplicate events merged into {self.duplicate_count // 2}.")
        if self.merged_examples:
            print("Here are two examples of merged duplicate events:")
            for pair in self.merged_examples:
                print("📌 Original Event:")
                print(f"   🏷️  {pair['original']['name']}")
                print(f"   📅  {pair['original']['date_time']} | 📍 {pair['original']['venue']}")
                print("🔁 Merged With:")
                print(f"   🏷️  {pair['duplicate']['name']}")
                print(f"   📅  {pair['duplicate']['date_time']} | 📍 {pair['duplicate']['venue']}")
                print("—" * 40)


duplicate_handler = DuplicateHandler()
