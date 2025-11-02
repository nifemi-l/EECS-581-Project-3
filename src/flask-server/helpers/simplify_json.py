import json 

class SimplifyJSON:
    def __init__(self):
        '''Initialize the SimplifyJSON class'''
        self.simplified = [] # Initialize simplified list
    
    def simplify_listening_history(self, json_data): 
        '''Extract and return relevant information from user listening history JSON data'''
        
        # Reset simplified list for new call
        self.simplified = []
        
        # Obtain song items from Spotify API response
        song_items = json_data.get("items", [])

        # Extract relevant elements
        for item in song_items:
            track = item.get("track", {})

            # Check if the track is already in the simplified list
            # - If it is, skip it
            if track.get("id", "") in [track.get("id", "") for track in self.simplified]:
                continue

            # Extract artists
            artists = [
                artist["name"] for artist in track.get("artists", [])
            ]

            # Extract album image
            album_images = track.get("album", {}).get("images", [])
            album_img = album_images[0]["url"] if album_images else None

            # Append simplified dict
            self.simplified.append({ 
                "id": track.get("id", ""),  # Add ID for React key prop
                "track_name": track.get("name", ""),
                "artists": ", ".join(artists),
                "played_at": item.get("played_at", ""),
                "album_image": album_img, 
                "spotify_url": track.get("external_urls", {}).get("spotify", "")
            })
        
        # Return Python list (not JSON string) so Flask can serialize it properly
        return self.simplified