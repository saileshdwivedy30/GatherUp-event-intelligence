# from ai_ml.recommender import MLRecommender
from recommender import MLRecommender

# Simulate a user who likes these categories
user_categories = ["Music", "Sports"]  # <- change as needed

# Initialize and get recommendations
recommender = MLRecommender()
results = recommender.recommend(preferred_categories=user_categories, top_n=30, return_ids_only=False)

# Print results
print("📌 Recommended Events:\n")
for event in results:
    print(f"🆔 {event['_id']}")
    print(f"🎫 Name     : {event['name']}")
    print(f"📍 Venue    : {event['venue']['name']} ({event['venue']['city']}, {event['venue']['state']})")
    print(f"🕒 DateTime : {event['date_time']}")
    print(f"🏷️ Category : {event['category']}")
    print("-" * 50)