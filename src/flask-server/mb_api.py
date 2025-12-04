# Prologue
# Name: mb_api.py
# Description: Handle MusicBrainz API logic
# Programmer: Logan Smith
# Dates: 11/25/25
# Revisions: 1.0
# Pre/post conditions
#   - Pre: Spotify API must have returned empty genre list on request
#   - Post: MusicBrainz returns a list of genres or it remains empty
# Errors: All known errors should be handled gracefully.

import requests
import time
import os

# Header required per MusicBrainz API Documentation
USER_AGENT = f"Scorify/1.0 ({os.getenv('USER_AGENT_EMAIL')})"
HEADERS = {"User-Agent": USER_AGENT}

def mb_search_artist(artist_name: str):
    """
     Searches for an artist by name using MusicBrainz.
     Returns the MBID or None.
    """

    # Rate limit - 1 second per API request
    time.sleep(1) 

    # Construct URL for fetching tags via MBID
    url = f"https://musicbrainz.org/ws/2/artist/?query={artist_name}&fmt=json"

    # Issue GET request to MusicBrainz with required User-Agent
    r = requests.get(url, headers=HEADERS)

    # Abort if request fails or API returns non-200 status
    if r.status_code != 200:
        return None
    
    # Parse response into Python dict
    data = r.json()

    # If no artists found in the result set → return None
    if "artists" not in data or len(data["artists"]) == 0:
        return None
    
    # Take the top result (MusicBrainz sorts by score)
    return data["artists"][0]["id"]

def mb_get_genres(mbid: str):
    """
    Uses the MBID to fetch tags/genres.
    Returns a list of genres.
    """

    # Rate limit - 1 second per API request
    time.sleep(1)

    # Construct URL for fetching tags via MBID
    url = f"https://musicbrainz.org/ws/2/artist/{mbid}?inc=tags&fmt=json"

    # Issue GET request to MusicBrainz with required User-Agent
    r = requests.get(url, headers=HEADERS)

    # Abort early if API returns any non-200 status code
    if r.status_code != 200:
        return []

    # Parse the JSON response
    data = r.json()

    # Extract the "tags" array — may be missing or empty
    tags = data.get("tags", [])

    # Only take meaningful tags -> Convert to genre list
    genres = []
    for t in tags:
        # Only accept tags that have a "count" field and occur at least 3 times
        if "count" in t and t["count"] >= 3:
            genres.append(t["name"])

    return genres

def mb_lookup_by_spotify_id(spotify_artist_id):
    """
    Searches MusicBrainz using the artist's Spotify ID.
    Returns the MBID (MusicBrainz ID) or None.
    """

    # Respect 1-second rate limit
    time.sleep(1)

    # Query MusicBrainz for artists linked to this Spotify ID
    url = (
        "https://musicbrainz.org/ws/2/artist/"
        "?query=artistaccent:spotify:" + spotify_artist_id + "&fmt=json"
    )

    response = requests.get(url, headers=HEADERS)

    # Abort on request failure
    if response.status_code != 200:
        return None

    data = response.json()

    # No artists found
    if "artists" not in data or len(data["artists"]) == 0:
        return None

    # Return the MBID of the first match
    first_artist = data["artists"][0]
    mbid = first_artist.get("id", None)

    return mbid

def mb_lookup_by_name(artist_name):
    """
        Searches by artist name
        Returns tags from first matching artist
    """
    try:
        # Build MusicBrainz search query using artist name
        url = f"https://musicbrainz.org/ws/2/artist/?query=artist:{artist_name}&fmt=json"

        # Perform the search request
        response = requests.get(url, headers=HEADERS)

        # If API fails or returns a non-200 status code → empty list
        if response.status_code != 200:
            return []

        # Parse the JSON response
        data = response.json()

        # If no artists found in the result set → return empty list
        if "artists" not in data or len(data["artists"]) == 0:
            return []

        # Take the highest scoring result (index 0)
        first = data["artists"][0]

        # Extract tags (may be missing)
        tags = first.get("tags", [])

        # Convert tag list into simple genre names
        genres = []
        for t in tags:
            # Only add tag entries that actually contain a "name" field
            if "name" in t:
                genres.append(t["name"])

        return genres

    except Exception:
        return []