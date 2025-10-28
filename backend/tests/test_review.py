import json
from datetime import datetime
from pathlib import Path

# Example movie folder and user
movie_folder_name = "Thor Ragnarok"
user_id = "6b3a2d50-73f9-4d52-8a3a-2c3f4c9091e2"

# Path to the movie folder
movie_folder = Path(f"data/movies/{movie_folder_name}")

# Path to user_reviews.json inside the movie folder
user_reviews_file = movie_folder / "user_reviews.json"

# Load existing reviews or create empty dict (python cant parse empty json files so it doesn't error if it is 1st reveiw)
if user_reviews_file.exists() and user_reviews_file.stat().st_size > 0:
    with open(user_reviews_file, "r") as f:
        reviews = json.load(f)
else:
    reviews = {}

# Create a new review for the user
new_review = {
    "rating": 9,
    "review_text": "Amazing movie with epic moments!",
    "upvotes": 0,
    "downvotes": 0,
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat()
}

# Append / overwrite user's review
reviews[user_id] = new_review

# Ensure folder exists (should already exist) and save JSON
movie_folder.mkdir(parents=True, exist_ok=True)
with open(user_reviews_file, "w") as f:
    json.dump(reviews, f, indent=4)

print(f"✅ Review for user {user_id} added/updated in {user_reviews_file}")
