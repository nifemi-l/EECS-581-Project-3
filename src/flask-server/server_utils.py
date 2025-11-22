# Prologue
# Name: server_utils.py
# Description: Helper utilities for the Flask server, including genre flattening, diversity scoring,
#              taste alignment scoring, Spotify date normalization, and track URL generation.
# Programmer: Logan Smith
# Dates: 11/20/25
# Revisions: 1.0
# Pre/post conditions
#   - Pre: Functions expect valid input formats (e.g., lists of genre lists, Spotify date strings).
#   - Post: Returns normalized values, computed scores, or formatted outputs.
# Errors: All known errors should be handled gracefully.

import math
import os
import json

# --- LOAD BUCKET DEFINITIONS ---

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENRE_PATH = os.path.join(BASE_DIR, "genres_dict.json")

with open(GENRE_PATH, "r", encoding="utf-8") as f:
    GENRES = json.load(f)

ROOTS = GENRES["genres"]
GENRE_MAP = GENRES["genres_map"]

# Build reverse lookup table:
# "dance pop" → "Pop", "edm" → "Electronic", etc.
REVERSE = {}

for root, subs in GENRE_MAP.items():
    for s in subs:
        REVERSE[s.lower()] = root


# --- GENRE CLASSIFICATION ---

def classify_genre(genre: str):
    g = genre.strip().lower()

    # If genre matches a root exactly
    for root in ROOTS:
        if g == root.lower():
            return root

    # If genre is mapped inside genres_map
    if g in REVERSE:
        return REVERSE[g]

    return None

def bucketize_genre_lists(list_of_lists):
    """
    Input:  [["djent", "progressive metal"], ["indie pop", "neo-synthpop"]]
    Output: [["metal"], ["pop"]]
    """

    # Define return list
    final = []

    # Classify each genre list
    for genre_list in list_of_lists:

        #Debug
        #print(genre_list, "\n")

        # Start with a set of genres for no duplicate genres per list
        buckets = set()

        for genre in genre_list:
            
            # If a genre is "None" -> don't process it
            if genre == None:
                continue

            # Run the bucketing algorithm on the genre
            bucket = classify_genre(genre)
            
            # If a root genre list is returned -> add it to the return list
            if bucket:
                buckets.add(bucket)

        # Add only non-empty sets as list
        if len(buckets) > 0:
            final.append(sorted(list(buckets)))
    
    #Debug
    #print("Final List:\n")
    #print(final)
    return final


# --- FLATTEN LIST ---

def flatten_list(genre_lists):
    """Converts a list of lists to a single list"""

    # Define the return list
    genres = []

    # Remove each genre from its genre list
    for genre_list in genre_lists:
        for genre in genre_list:
            genres.append(genre)

    return genres


# --- DIVERSITY SCORE ---

# Expecting genre lists to be a list of lists [[pop, dance], [punk], [rock, metal, prog metal]]
def calculate_diversity_score(genre_lists):
    """Uses Shannon's Entropy formula to calculate normalized diversity relative to the full genre set.
       Score closer to 1 = High Diversity | Score closer to 0 = Low Diversity
    """
    
    # Get a single list of genres the user listens to
    user_genres = flatten_list(genre_lists)
    
    # Check if the list is empty (rare edge case)
    if len(user_genres) == 0:
        return 0.00
    
    # Build frequency map (initialize all buckets with 0)
    genre_counts = {}
    for g in ROOTS:
        genre_counts[g] = 0

    # Count user listens (only for genres in our known set)
    for genre in user_genres:
        if genre in genre_counts:
            genre_counts[genre] += 1

    # Compute total listens
    total = 0
    for count in genre_counts.values():
        total = total + count

    if total == 0:
        return 0.0
    
    # Calculate Shannon entropy
    entropy = 0.0
    for count in genre_counts.values():
        if count > 0:
            p = count / total
            entropy = entropy - (p * math.log(p, 2))

    # Normalize entropy by the total number of genres
    max_entropy = math.log(len(ROOTS), 2)
    diversity = (entropy / max_entropy) * 100

    # Round to 2 places - (Can Be Adjusted)!
    return round(diversity, 2)


# --- TASTE SCORE ---

def calculate_taste_score(user_diversity, developer_diversities):
    """
    Compares user's diversity score to average developer diversity.
    Returns a float between 0.0 and 1.0 indicating taste alignment.
    """

    if len(developer_diversities) == 0:
        return 0.0
    
    # Compute average developer diversity
    total = 0
    for dev_score in developer_diversities:
        total = total + dev_score
    dev_average = total / len(developer_diversities)

    # Compute distance from the average
    difference = abs(user_diversity - dev_average)

    # Convert to taste alignment score
    taste_score = 1 - difference

    # Bound to [0, 1]
    if taste_score < 0:
        taste_score = 0.0
    if taste_score > 1:
        taste_score = 1.0

    return round(taste_score, 2)


# --- OTHER UTILITIES ---
  
def get_track_url_from_id(track_id):
    return f"http://open.spotify.com/track/{track_id}"

def normalize_spotify_date(date_str):
    if date_str is None:
        return None

    parts = date_str.split("-")

    if len(parts) == 1:
        # Only year → assume January 1
        return f"{parts[0]}-01-01"

    elif len(parts) == 2:
        # Year + month → assume day 1
        return f"{parts[0]}-{parts[1]}-01"

    else:
        # Already valid yyyy-mm-dd
        return date_str
