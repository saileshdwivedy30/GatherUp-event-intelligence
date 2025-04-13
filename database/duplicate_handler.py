import hashlib
import json
import re
import torch
from sentence_transformers import SentenceTransformer, util
from database.db_manager import db_manager


class DuplicateHandler:
    """Handles intelligent duplicate detection using embeddings and logs method used."""

    def __init__(self):
        self.duplicate_count = 0
        self.duplicate_via_id = 0
        self.duplicate_via_embedding = 0
        self.merged_examples = []
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

    def is_duplicate_embedding(self, new_embedding, existing_event, threshold=0.92):
        if existing_event["date_time"] != self.current_event["date_time"]:
            return False

        existing_embedding = torch.tensor(existing_event["_embedding"]).to("cpu")
        score = util.pytorch_cos_sim(new_embedding, existing_embedding).item()

        if score >= threshold:
            self.duplicate_via_embedding += 1
            return True
        return False

    def handle_duplicate(self, event_data):
        """Check if an event is a duplicate using ID first, then semantic similarity."""
        event_data["_id"] = self.generate_event_id(event_data)

        # Step 1: Check for ID match
        existing_event = db_manager.find_event(event_data["_id"])
        if existing_event:
            self.duplicate_count += 1
            self.duplicate_via_id += 1
            if len(self.merged_examples) < 2:
                self.merged_examples.append((existing_event, event_data))
            db_manager.insert_event(event_data)
            return False

        # Step 2: No ID match, proceed with embedding
        self.current_event = event_data
        embedding = self.embed_event(event_data)
        candidates = db_manager.collection.find({"date_time": event_data["date_time"]})

        for existing_event in candidates:
            if "_embedding" not in existing_event:
                old_emb = self.embed_event(existing_event).tolist()
                db_manager.collection.update_one(
                    {"_id": existing_event["_id"]},
                    {"$set": {"_embedding": old_emb}}
                )
                existing_event["_embedding"] = old_emb

            if self.is_duplicate_embedding(embedding, existing_event):
                self.duplicate_count += 1
                if len(self.merged_examples) < 2:
                    self.merged_examples.append((existing_event, event_data))
                db_manager.insert_event(event_data)
                return False

        # Step 3: Store as new event
        event_data["_embedding"] = embedding.tolist()
        db_manager.insert_event(event_data)
        return True

    def log_duplicate_summary(self):
        print(f"🔄 Detected {self.duplicate_count} duplicate events merged.")
        print(f"   • ✅ Via ID match       : {self.duplicate_via_id}")
        print(f"   • 🤖 Via Embeddings     : {self.duplicate_via_embedding}")

        if self.merged_examples:
            print("Here are two examples of merged duplicate events:")
            for original, duplicate in self.merged_examples:
                print(f"📌 Original: {original['name']} | {original['date_time']} | {original['venue']['name']}")
                print(f"🔁 Merged : {duplicate['name']} | {duplicate['date_time']} | {duplicate['venue']['name']}")
                print("————————————————————————————————————————")

            with open("new_dup_event_dump.json", "w") as f:
                json.dump(
                    [{"original": o, "duplicate": d} for o, d in self.merged_examples],
                    f, indent=4
                )
                print("📄 Dump saved to: new_dup_event_dump.json")


duplicate_handler = DuplicateHandler()
