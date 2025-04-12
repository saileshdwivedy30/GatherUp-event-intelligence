import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timezone
import numpy as np
from collections import defaultdict

class MLRecommender:
    def __init__(self, model_path="new_models"):
        self.vectorizer = joblib.load(f"{model_path}/tfidf_vectorizer.pkl")
        self.tfidf_matrix = joblib.load(f"{model_path}/tfidf_matrix.pkl")
        self.event_df = pd.read_pickle(f"{model_path}/event_df.pkl")

    def recommend(self, preferred_categories, top_n=30, return_ids_only=False):
        # Filter future events only
        self.event_df["date_time"] = pd.to_datetime(self.event_df["date_time"], errors="coerce")
        self.event_df["category"] = self.event_df["category"].fillna("Uncategorized")
        now_utc = datetime.now(timezone.utc)
        future_df = self.event_df[self.event_df["date_time"] >= now_utc]

        # Filter by user’s selected categories
        filtered_df = future_df[future_df["category"].isin(preferred_categories)]

        if filtered_df.empty:
            return []

        # Build user profile vector (mean of TF-IDFs of selected categories)
        user_interest_matrix = self.vectorizer.transform(filtered_df["text"])
        user_profile_vector = np.asarray(user_interest_matrix.mean(axis=0)).reshape(1, -1)

        # Compute cosine similarity with all future events
        full_event_matrix = self.vectorizer.transform(future_df["text"])
        similarities = cosine_similarity(user_profile_vector, full_event_matrix).flatten()
        #
        # # Get top-N most similar
        # top_indices = similarities.argsort()[::-1][:top_n]
        # recommended = future_df.iloc[top_indices]
        #
        # return recommended["_id"].tolist() if return_ids_only else recommended.to_dict(orient="records")

        # Get top-N most similar
        top_indices = similarities.argsort()[::-1]
        top_events = future_df.iloc[top_indices]

        # Deduplicate by event name — keep earliest
        grouped = defaultdict(list)
        for _, event in top_events.iterrows():
            grouped[event["name"]].append(event)

        unique_recommendations = []
        for same_named_events in grouped.values():
            same_named_events.sort(key=lambda e: e["date_time"])
            unique_recommendations.append(same_named_events[0])  # pick earliest per name
            if len(unique_recommendations) >= top_n:
                break  # Only keep top-N unique names

        # Convert to output format
        if return_ids_only:
            return [e["_id"] for e in unique_recommendations]
        else:
            return [e.to_dict() for e in unique_recommendations]

