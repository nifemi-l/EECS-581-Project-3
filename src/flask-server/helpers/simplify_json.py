import json 

class SimplifyJSON:
    def __init__(self):
        self.simplified = []
    
    def simplify_listening_history(self, json_data): 
        '''Extract and return relevant information from user listening history JSON data'''
        
        # Obtain song items
        song_items = json_data["user_info"]["items"]

        # Extract relevant elements
        for item in song_items:
            track = item["track"]
            artists = [
                artist["name"] for artist in track["artists"]
            ]
            album_img = track["album"]["images"][0]["url"] if track["album"]["images"] else None

            # Append simplified dict
            self.simplified.append({ 
                "track_name": track["name"],
                "artists": ", ".join(artists),
                "played_at": item["played_at"],
                "album_image": album_img, 
                "spotify_url": track["external_urls"]["spotify"]
            })
        
        # Convert dict to json, indent for pretty print
        self.simplified = json.dumps(self.simplified, indent=3)
        return self.simplified