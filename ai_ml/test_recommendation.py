from recommender import MLRecommender

# Simulate a user who likes these categories
user_categories = ["Music"]
user_cities = ["Los Angeles", "San Francisco", "New York"]

# Initialize and get recommendations
recommender = MLRecommender()
results = recommender.recommend(
    preferred_categories=user_categories,
    preferred_locations=user_cities,
    top_n=20
)

# Print results
print("Recommended Events:\n")
for event in results:
    print(f"ID: {event['_id']}")
    print(f"Name     : {event['name']}")
    print(f"Venue    : {event['venue']['name']} ({event['venue']['city']}, {event['venue']['state']})")
    print(f"DateTime : {event['date_time']}")
    print(f"Category : {event['category']}")
    print("-" * 50)