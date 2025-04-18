# tfidf_trainer.py
import pandas as pd
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "event_data"
COLLECTION_NAME = "events"
OUTPUT_DIR = "new_models"
os.makedirs(OUTPUT_DIR, exist_ok=True)

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def train_tfidf_model():
    events = list(collection.find({}))
    df = pd.DataFrame(events)

    print(f"📦 Fetched {len(df)} events from MongoDB.")
    print("📝 Sample events:")
    # Safely extract segment from nested classifications
    df["category"] = df["classifications"].apply(
        lambda c: c.get("segment") if isinstance(c, dict) else "Uncategorized"
    )
    print(df[["name", "description", "category", "date_time"]].head(5))

    proceed = input("\n⚠️ Proceed with training the TF-IDF model? (yes/no): ").strip().lower()
    if proceed != "yes":
        print("❌ Training cancelled.")
        return

    # df["category"] = df["category"].fillna("Uncategorized")
    df["text"] = df["name"].fillna("") + " " + df["description"].fillna("")

    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    #tfidf_matrix = vectorizer.fit_transform(df["text"])

    joblib.dump(vectorizer, os.path.join(OUTPUT_DIR, "tfidf_vectorizer.pkl"))
    #joblib.dump(tfidf_matrix, os.path.join(OUTPUT_DIR, "tfidf_matrix.pkl"))
    df.to_pickle(os.path.join(OUTPUT_DIR, "event_df.pkl"))

    print("✅ TF-IDF model and matrix saved.")

if __name__ == "__main__":
    train_tfidf_model()
