import hashlib
import json
import csv
import torch
from sentence_transformers import SentenceTransformer, util
from database.db_manager import db_manager
from datetime import datetime
from copy import deepcopy
from dateutil.parser import isoparse

def stringify_date(event):
    if isinstance(event.get("date_time"), datetime):
        event["date_time"] = event["date_time"].isoformat()
    return event

def stringify_event(event):
    event = deepcopy(event)
    event.pop("dto_date_time", None)
    event.pop("_embedding", None)  # Remove embedding for cleaner output
    return event

def ensure_datetime(dt):
    if isinstance(dt, str):
        return isoparse(dt)
    return dt

class DuplicateHandler:
    """Handles intelligent duplicate detection using embeddings and logs method used."""

    def __init__(self, enable_logging):
        self.enable_logging = enable_logging
        self.duplicate_count = 0
        self.duplicate_via_id = 0
        self.duplicate_via_embedding = 0
        self.merged_examples = []
        self.duplicate_logs = []
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def get_event_text(self, event):
        return f"{event['name']} at {event['venue']['name']}"

    def embed_event(self, event):
        return self.model.encode(self.get_event_text(event), convert_to_tensor=True).to("cpu")

    def generate_event_id(self, event):
        """Generate a stable _id using name + venue + date_time."""
        name = event["name"].strip().lower()
        venue = event["venue"]["name"].strip().lower()
        date = event["date_time"]
        raw = f"{name}|{venue}|{date}"
        return hashlib.md5(raw.encode()).hexdigest()

    def is_duplicate_embedding(self, new_embedding, existing_event, threshold=0.90):

        #stringify_date(existing_event)

        if existing_event["date_time"] != self.current_event["date_time"]:
            return False

        existing_embedding = torch.tensor(existing_event["_embedding"]).to("cpu")
        score = util.pytorch_cos_sim(new_embedding, existing_embedding).item()

        if score >= threshold:
            self.duplicate_via_embedding += 1
            self.log_classification_diff("embedding", existing_event, self.current_event)
            return True
        return False

    def handle_duplicate(self, event_data):
        """Check if an event is a duplicate using ID first, then semantic similarity."""
        event_data["_id"] = self.generate_event_id(event_data)

        # Check for ID match
        existing_event = db_manager.find_event(event_data["_id"])
        if existing_event:
            #stringify_date(existing_event)
            self.duplicate_count += 1
            self.duplicate_via_id += 1
            self.log_classification_diff("id", existing_event, event_data)

            self.merged_examples.append((existing_event, event_data))
            db_manager.insert_event(event_data)
            return False

        # No ID match proceed with embedding
        self.current_event = event_data
        embedding = self.embed_event(event_data)
       #candidates = db_manager.collection.find({"date_time": event_data["date_time"]})

        # Normalize date to YYYY-MM-DD for fuzzy same-day matching
        target_date_str = event_data["date_time"][:10]  # works for both "2025-04-17" and "2025-04-17T20:00:00Z"

        # Match any event that starts with that date (Eventbrite or Ticketmaster style)
        candidates = db_manager.collection.find({"date_time": {"$regex": f"^{target_date_str}"}})

        for existing_event in candidates:

            #stringify_date(existing_event)

            if "_embedding" not in existing_event:
                old_emb = self.embed_event(existing_event).tolist()
                db_manager.collection.update_one(
                    {"_id": existing_event["_id"]},
                    {"$set": {"_embedding": old_emb}}
                )
                existing_event["_embedding"] = old_emb

            if self.is_duplicate_embedding(embedding, existing_event):
                self.duplicate_count += 1

                self.merged_examples.append((existing_event, event_data))
                db_manager.insert_event(event_data)
                return False

        # Store as new event
        event_data["_embedding"] = embedding.tolist()
        db_manager.insert_event(event_data)
        return True

    def log_classification_diff(self, match_type, existing_event, duplicate_event):
        seg = existing_event.get("classifications", {}).get("segment", "")
        genre_o = existing_event.get("classifications", {}).get("genre", "")
        genre_d = duplicate_event.get("classifications", {}).get("genre", "")
        sub_o = existing_event.get("classifications", {}).get("subGenre", "")
        sub_d = duplicate_event.get("classifications", {}).get("subGenre", "")

        url_o = existing_event.get("sources", {}).get("ticketmaster", {}).get("url", "")
        url_d = duplicate_event.get("sources", {}).get("ticketmaster", {}).get("url", "")

        self.duplicate_logs.append({
            "match_type": match_type,
            "name": duplicate_event.get("name", ""),
            "venue": duplicate_event.get("venue", {}).get("name", ""),
            "date_time": duplicate_event.get("date_time", ""),
            "segment": seg,
            "genre_original": genre_o,
            "genre_duplicate": genre_d,
            "sub_genre_original": sub_o,
            "sub_genre_duplicate": sub_d,
            "genre_differs": genre_o != genre_d,
            "sub_genre_differs": sub_o != sub_d,
            "ticket_url_original": url_o,
            "ticket_url_duplicate": url_d,
            "ticket_url_differs": url_o != url_d
        })

    def log_duplicate_summary(self):
        print(f"Detected {self.duplicate_count} duplicate events merged.")
        print(f"   • Via ID match       : {self.duplicate_via_id}")
        print(f"   • Via Embeddings     : {self.duplicate_via_embedding}")

        if self.enable_logging and self.merged_examples:
            print(f"Logging {len(self.merged_examples)} merged examples...")

            merged_log = []
            for original, duplicate in self.merged_examples:
                merged_event = db_manager.find_event(original["_id"])
                match_type = "id" if original["_id"] == duplicate["_id"] else "embedding"

                merged_log.append({
                    "original": stringify_event(original),
                    "duplicate": stringify_event(duplicate),
                    "merged": stringify_event(merged_event),
                    "merged_via": match_type,
                    "original_sources": list(original.get("sources", {}).keys()),
                    "duplicate_sources": list(duplicate.get("sources", {}).keys())
                })

            with open("ticketmaster_eventbrite_merged.json", "w") as f:
                json.dump(merged_log, f, indent=4)

            print("Full merged dump saved to: ticketmaster_eventbrite_merged.json")

        if self.enable_logging and self.duplicate_logs:
            with open("duplicate_events_log.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "match_type", "name", "venue", "date_time",
                    "segment", "genre_original", "genre_duplicate",
                    "sub_genre_original", "sub_genre_duplicate",
                    "genre_differs", "sub_genre_differs",
                    "ticket_url_original", "ticket_url_duplicate", "ticket_url_differs"
                ])
                writer.writeheader()
                writer.writerows(self.duplicate_logs)
                print("CSV log saved to: duplicate_events_log.csv")

duplicate_handler = DuplicateHandler(enable_logging=False)
