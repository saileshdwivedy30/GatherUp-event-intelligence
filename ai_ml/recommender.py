import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timezone
import numpy as np

class MLRecommender:
    def __init__(self, model_path="new_models"):
        self.vectorizer = joblib.load(f"{model_path}/tfidf_vectorizer.pkl")
        #self.tfidf_matrix = joblib.load(f"{model_path}/tfidf_matrix.pkl")
        self.event_df = pd.read_pickle(f"{model_path}/event_df.pkl")


    def recommend(self, preferred_categories, preferred_locations=None, top_n=30, return_ids_only=False):
        # Parse & normalize input
        preferred_categories = preferred_categories or []
        preferred_locations = [loc.lower() for loc in (preferred_locations or [])]

        # Prepare event dataframe
        self.event_df["date_time"] = pd.to_datetime(self.event_df["date_time"], errors="coerce")
        self.event_df["category"] = self.event_df["category"].fillna("Uncategorized")

        # Filter to future events only
        now_utc = datetime.now(timezone.utc)
        future_df = self.event_df[self.event_df["date_time"] >= now_utc].copy()

        # Normalize city names
        future_df["venue_city"] = future_df["venue"].apply(
            lambda v: v.get("city", "").lower() if isinstance(v, dict) else ""
        )

        # Strict location filtering
        if preferred_locations:
            future_df = future_df[future_df["venue_city"].isin(preferred_locations)]

        if future_df.empty:
            return []

        # Loose category filtering:
        # Build user profile only from events in preferred categories (within the location-filtered pool)
        filtered_df = future_df[future_df["category"].isin(preferred_categories)]

        if filtered_df.empty:
            return []

        # Build user profile vector
        user_interest_matrix = self.vectorizer.transform(filtered_df["text"])
        user_profile_vector = np.asarray(user_interest_matrix.mean(axis=0)).reshape(1, -1)

        # Compute similarity with "all" location-filtered events (any category)
        full_event_matrix = self.vectorizer.transform(future_df["text"])
        similarities = cosine_similarity(user_profile_vector, full_event_matrix).flatten()

        # Rank events by similarity
        top_indices = similarities.argsort()[::-1]
        top_events = future_df.iloc[top_indices]

        # Deduplicate by event name — keep earliest
        from collections import defaultdict
        grouped = defaultdict(list)
        for _, event in top_events.iterrows():
            grouped[event["name"]].append(event)

        unique_recommendations = []
        for same_named_events in grouped.values():
            same_named_events.sort(key=lambda e: e["date_time"])
            unique_recommendations.append(same_named_events[0])  # Pick earliest
            if len(unique_recommendations) >= top_n:
                break

        return [e["_id"] for e in unique_recommendations] if return_ids_only else [e.to_dict() for e in
                                                                                   unique_recommendations]
