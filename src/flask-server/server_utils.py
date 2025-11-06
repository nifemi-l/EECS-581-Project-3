import math

# TEMPORARY LIST OF GENRES (Needs Expansion / Bucketing Algorithm)
ALL_GENRES = [
    'pop', 'dance', 'edm', 'rock', 'metal', 'hip hop', 'rnb',
    'country', 'folk', 'jazz', 'blues', 'classical', 'indie',
    'punk', 'reggae', 'soul', 'house', 'techno', 'latin', 'k-pop'
]

def flatten_list(genre_lists):
    """Converts a list of lists to a single list"""
    genres = []
    for genre_list in genre_lists:
        for genre in genre_list:
            genres.append(genre)

    return genres


# Expecting genre lists to be a list of lists [[pop, dance], [punk], [rock, metal, prog metal]]
def calculate_diversity_score(genre_lists):
    """Uses Shannon's Entropy formula to calculate normalized diversity relative to the full genre set.
       Score closer to 1 = High Diversity | Score closer to 0 = Low Diversity
    """
    
    # Get a single list of genres the user listens to
    user_genres = flatten_list(genre_lists)
    
    # Check if the list is empty (rare edge case)
    if len(user_genres) == 0:
        return 0.0
    
    # Build frequency map (initialize all genres with 0)
    genre_counts = {}
    for genre in ALL_GENRES:
        genre_counts[genre] = 0

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
    max_entropy = math.log(len(ALL_GENRES), 2)
    diversity = entropy / max_entropy

    # Round to 2 places - Can Be Adjusted!
    return round(diversity, 2)


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
  
def get_track_url_from_id(track_id):
    return f"http://open.spotify.com/track/{track_id}"