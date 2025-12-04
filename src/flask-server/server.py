# Prologue
# Name: server.py
# Description: Create and manage a flask server backend for our application
# Programmer: Nifemi Lawal, Jack Bauer, Logan Smith, Dellie Wright, Blake Carlson
# Creation date: 10/23/25
# Last revision date: 12/02/25
# Revisions: 2.0
# Pre/post conditions
#   - Pre: None.
#   - Post: None.
# Errors: None.

import os
from flask.typing import ErrorHandlerCallable
import urllib.parse
import requests
from datetime import datetime
from flask import Flask, redirect, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from typing import Optional
import werkzeug
import random
from helpers.simplify_json import SimplifyJSON
import threading
from DBConnection import DBConnection
from server_utils import *
from werkzeug.exceptions import HTTPException, InternalServerError
from server_utils import calculate_diversity_score, bucketize_genre_lists, calculate_taste_score

# Load env variables
load_dotenv()

# Flask app initialization
app = Flask(__name__)
CORS(app,
     origins=['http://127.0.0.1:3000'],
     supports_credentials=True
     )

# Load secret key from environment variable and bind to app instance
app.secret_key = os.getenv('APP_SECRET_KEY')

# Configure session cookie settings
app.config.update(
    # This means the cookie is only accessible on the same site
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,    # This means the cookie is not secure --> not HTTPS
    # This means the cookie is not accessible by JavaScript
    SESSION_COOKIE_HTTPONLY=True,
    # This means the cookie is only accessible on the local host (127.0.0.1)
    SESSION_COOKIE_DOMAIN='127.0.0.1'
)

# Constants
# - REDIRECT_URI = 'https://localhost:3000/callback'
REDIRECT_URI = 'http://127.0.0.1:5000/callback'
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# Developer Spotify IDs for taste score baseline
DEV1_SPOTIFY_ID = os.getenv('DEV1_SPOTIFY_ID')
DEV2_SPOTIFY_ID = os.getenv('DEV2_SPOTIFY_ID')
DEV3_SPOTIFY_ID = os.getenv('DEV3_SPOTIFY_ID')
DEV4_SPOTIFY_ID = os.getenv('DEV4_SPOTIFY_ID')
DEV5_SPOTIFY_ID = os.getenv('DEV5_SPOTIFY_ID')

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1'
ERROR_MESSAGE = 'Authentication failed: {error}'

# Initialize our connection to the Scorify database
dbConn: Optional[DBConnection] = None
try:
    temp = DBConnection()
    if not temp.connected:
        raise ConnectionError(
            "Database connection failed: could not connect to Scorify database.")
    else:
        dbConn = temp
except Exception as e:
    import sys
    print(f"[ERROR] {e}", file=sys.stderr)


def handle_error(error):
    '''Handle an error by redirecting to the login page with the error parameter.'''

    try:
        # URL-encode the error message
        encoded_error_message = urllib.parse.quote(
            ERROR_MESSAGE.format(error=error))
        # Redirect to login page with error parameter
        return redirect(f'http://127.0.0.1:3000/login?error={encoded_error_message}')
    except Exception as e:
        # URL-encode the error message
        encoded_error_message = urllib.parse.quote(
            ERROR_MESSAGE.format(error=e))
        # Redirect to login page with error parameter
        return redirect(f'http://127.0.0.1:3000/login?error={encoded_error_message}')


@app.route('/')
def lander():
    return "<div><h1>API lander<h1><div>"

# Login route


@app.route('/login')
def login():
    '''Redirect the user to Spotify's authorization URL to authorize the app.'''

    # Check if user is already logged in
    if 'access_token' in session:
        # If already logged in, redirect to dashboard
        # add data population here!
        print("access token in session")
        print(session)
        return jsonify({'message': 'User already logged in', 'logged_in': True}) and redirect('http://127.0.0.1:3000/dashboard')

    try:
        # Spotify scopes
        # - user-read-recently-played: Read access to user's recently played tracks
        # - user-read-private: Read access to user's private information
        # - user-read-email: Read access to user's email address
        # Note: To get a user's display name, will use user-read-private and user-read-email
        scope = 'user-read-recently-played user-read-private user-read-email'

        # Declare the parameters for the authorization URL
        params = {
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'scope': scope,
            'redirect_uri': REDIRECT_URI
        }

        # Create the authorization URL and encode the parameters
        auth_url = f'{AUTH_URL}?{urllib.parse.urlencode(params)}'

        # Redirect the user to Spotify's authorization URL
        return redirect(auth_url)
    except Exception as e:
        # Handle error and redirect to login page with error parameter
        return handle_error(e)

# Callback route


@app.route('/callback')
def callback():
    '''Handle the callback from Spotify's authorization server and exchange temporary code for access token.'''

    try:
        # Check if there is an error from Spotify (e.g., user denied access)
        if 'error' in request.args:
            # Throw an error
            raise Exception(request.args['error'])

        # If there is no error, get the temporary authorization code
        # - When successful, auth server returns a temporary code in URL parameters
        # - Need to exchange temp code for access token
        assert (dbConn.connected)
        if 'code' in request.args:
            req_body = {
                'code': request.args['code'],
                'grant_type': 'authorization_code',
                'redirect_uri': REDIRECT_URI,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET
            }

            # Send the response body to get an access token
            response = requests.post(TOKEN_URL, data=req_body)
            # Extract JSON from response
            token_info = response.json()

            # Store access token
            session['access_token'] = token_info['access_token']
            # Store refresh token
            session['refresh_token'] = token_info['refresh_token']
            # Store expiry as an absolute timestamp
            session['expires_at'] = datetime.now().timestamp() + \
                int(token_info['expires_in'])

            # Return success message and redirect to the dashboard page
            return redirect('http://127.0.0.1:3000/dashboard')
    except Exception as e:
        # Handle error and redirect to login page with error parameter
        return handle_error(e)

# User profile information endpoint


@app.route('/get-user-info-by-id/<int:user_id>')
def get_user_info_by_id(user_id):
    '''Returns user info for a given user ID.'''
    
    # Check if user is logged in
    if 'access_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get the user's information from the database
    out = dbConn.get_user_info_by_id(user_id)

    # Clean the output
    cleaned = []
    row = out[0]
    cleaned.append({
            "user_id": row[0],
            "spotify_id": row[1],
            "user_name": row[2],
            "profile_image_url": row[3],
            "diversity_score": row[6]
        })

    return jsonify({ "user_info": cleaned }), 200

@app.route('/get-user-info')
def api_get_user_info():
    '''Get the user's information from the Spotify API, using the access token.'''

    # Check if user is logged in
    if 'access_token' not in session:
        # If not logged in, return error
        return jsonify({
            'error': 'Not authenticated',
            'logged_in': False
        }), 401

    # Check if access token is expired
    if datetime.now().timestamp() > session['expires_at']:
        # If access token is expired, refresh token
        return jsonify({
            'error': 'Access token expired',
            'logged_in': False,
            'needs_refresh': True
        }), 401

    try:
        # Construct header
        req_headers = {
            "Authorization": f"Bearer {session['access_token']}"
        }

        # Send GET request to Spotify API to get user information
        response = requests.get(f'{API_BASE_URL}/me', headers=req_headers)
        print("User info response status code:", response.status_code)
        # Extract JSON from response
        user_info = response.json()
        spotify_id = user_info['id']
        session['spotify_id'] = spotify_id
        # Get user_id from database
        print("Fetching user ID for Spotify ID:", spotify_id)
        user_id = dbConn.get_user_id_by_spotify_id(spotify_id)
        print("Fetched user ID:", user_id)
        # Store/Update the user in the database
        dbConn.add_user(
            response.text, session["access_token"], session["refresh_token"])
        # Prepare user_info with user_id
        print("Preparing user info with user ID")
        user_info_with_id = {
            'user_id': user_id,
            'spotify_id': user_info.get('id'),
            'user_name': user_info.get('display_name'),
            'profile_image_url': user_info.get('images')[0]['url'] if user_info.get('images') else None,
            'email': user_info.get('email')
        }
        # Return the user_info
        return jsonify({
            'message': 'User information retrieved',
            'user_info': user_info_with_id,
            'logged_in': True,
            'needs_refresh': False,
        }), 200

    except Exception as e:
        # Return error message
        return jsonify({'error': str(e)}), 400


@app.route('/get-leaderboard-data')
def get_leaderboard_data():
    '''Get profile pictures, usernames, diversity scores, and music taste ratings for all users.'''

    # Steps:
    # 0 - Ensure we're logged in and have a valid token
    # 1 - Check if we have a DB connection. Error if not.
    # 2 - Fetch data from database. Error on failure.
    # 3 - Format data from database if necessary. Error on failure.
    # 4 - Return data to requestee.

    # Check if user is logged in
    if 'access_token' not in session:
        # If not logged in, return error
        return jsonify({
            'error': 'Not authenticated',
            'logged_in': False
        }), 401

    # Check if access token is expired
    if datetime.now().timestamp() > session['expires_at']:
        # If access token is expired, refresh token
        return jsonify({
            'error': 'Access token expired',
            'logged_in': False,
            'needs_refresh': True
        }), 401

    try:
        # Step 1 - Check DB connection
        assert (dbConn.connected)

        # Step 2 - Fetch needed data from database
        # Will raise any errors we hit
        result = dbConn.get_many_user_profiles()

        # Get user scores
        # Note: if we ever have more than 25 users, we'll need to specifically fetch user scores
        # instead of just requesting all scores we have
        scores = dbConn.get_many_user_scores()

        # Step 3 - No need to format yet

        # Step 4 - Return (as a dictionary of both the user profiles and user scores)
        return {
            "profiles": result,
            "scores": scores
        }

    except Exception as e:
        # Return error message
        return jsonify({'error': str(e)}), 500


@app.route('/get-user-diversity-score-by-id/<int:user_id>')
def get_user_diversity_score_by_user_id(user_id):
    if 'access_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get the users diversity score from the database
    diversity_score = dbConn.get_user_diversity_score_by_id(user_id)
    if diversity_score is None:
        return jsonify({'error': 'Diversity score not found for user'}), 404
    return jsonify({'diversity_score': diversity_score}), 200

@app.route('/get-user-diversity-score')
def get_user_diversity_score():
    # Check if user is logged in
    if 'access_token' not in session:
        # If not logged in, return error
        return jsonify({
            'error': 'Not authenticated',
            'logged_in': False
        }), 401

    # We need the user's Spotify ID to look up their songs/artists.
    spotify_id = session['spotify_id']

    try:
        # Get genres from DB | Return Form: [( ['rock','metal'], ), ( ['pop'], ), ... ]
        genres_rows = dbConn.get_user_genres(spotify_id)

        # Convert SQL rows --> list of lists
        # Ex: [( ['rock','metal'], ), ( ['pop'], )] --> [ ['rock','metal'], ['pop'] ]
        genre_lists = []
        for (genre_array,) in genres_rows:
            if genre_array:
                genre_lists.append(genre_array)

        # Convert raw genres → bucketed genres
        bucketed_genres = bucketize_genre_lists(genre_lists)

        # Calculate score by calling the helper function
        div_score = calculate_diversity_score(bucketed_genres)

        # Commit user scores to db (if user exists).
        user_id = dbConn.get_user_id_by_spotify_id(spotify_id)
        dbConn.update_user_diversity_score(user_id, spotify_id, div_score)

        # Return score to the frontend
        return jsonify({
            "diversity_score": div_score
        }), 200

    except Exception as e:
        # Return error message
        return jsonify({'error': str(e)}), 500


@app.route('/get-user-taste-score')
def get_user_taste_score():
    '''Get the user's taste score based on developer diversity scores stored in the database.'''

    # Check if user is logged in
    if 'access_token' not in session:
        # If not logged in, return error
        return jsonify({
            'error': 'Not authenticated',
            'logged_in': False
        }), 401
    
    # We need the user's Spotify ID to compare to developer scores
    user_spotify_id = session.get('spotify_id')
    print("user spotify id:", user_spotify_id)
    if user_spotify_id is None:
        return jsonify({
            'error': 'User Spotify ID not found in session',
            'logged_in': False
        }), 401

    try:
        # Ensure DB connection is valid
        assert (dbConn.connected)

        # Collect developer Spotify IDs from constants
        dev_ids = [
            DEV1_SPOTIFY_ID,
            DEV2_SPOTIFY_ID,
            DEV3_SPOTIFY_ID,
            DEV4_SPOTIFY_ID,
            DEV5_SPOTIFY_ID
        ]

        # Ensure all 5 IDs exist in the environment
        if any(dev_id is None for dev_id in dev_ids):
            return jsonify({
                "error": "Developer Spotify IDs are not fully configured in environment."
            }), 500
        
        # Get the user's diversity score and normalize to 0–100 scale
        raw_user_div = dbConn.get_diversity_score_by_spotify_id(user_spotify_id)
        print("raw_user_div:", raw_user_div)
        if raw_user_div is None:
            return jsonify({
                'error': 'No diversity score found for user. Please generate a diversity score first.',
            }), 404

        # Normalize the diversity score
        user_div = raw_user_div * 100
        print("user_div:", user_div)
        # Fetch developer diversity scores (0–100)
        developer_diversities = []
        for dev_spotify_id in dev_ids:
            score = dbConn.get_diversity_score_by_spotify_id(dev_spotify_id)
            if score is not None:
                # Normalize from 0–1 to 0–100
                developer_diversities.append(score * 100)
        
        # If none of the developers have diversity scores stored
        if len(developer_diversities) == 0:
            return jsonify({
                'error': 'No developer diversity scores found in database.'
            }), 500

        # Calculate the taste score (0–100)
        taste_score = calculate_taste_score(user_div, developer_diversities)
        
        # Commit user scores to db (if user exists).
        user_id = dbConn.get_user_id_by_spotify_id(user_spotify_id)
        dbConn.update_user_taste_score(user_id, user_spotify_id, taste_score)

        # Return taste score to the frontend
        return jsonify({
            "taste_score": taste_score
        }), 200

    except Exception as e:
        # Return error message
        return jsonify({'error': str(e)}), 500

@app.route('/get-user-taste-score-by-id/<int:user_id>')
def get_user_taste_score_by_user_id(user_id):
    '''Returns the taste score for a given user ID.'''

    # Check if user is logged in
    if 'access_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get the users taste score from the database
    taste_score = dbConn.get_user_taste_score_by_id(user_id)

    # Return error if taste score not found
    if taste_score is None:
        return jsonify({'error': 'Taste score not found for user'}), 404
    return jsonify({'taste_score': taste_score}), 200

@app.route('/get-user-listening-history-by-id/<int:user_id>')
def get_user_listening_history_id(user_id):
    '''Retrieve a user's listening history by their user ID.'''

    # Check if user is logged in
    if 'access_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    # Verify that the user exists
    print("user id", user_id, "checking rows")
    user_rows = dbConn.get_user_info_by_id(user_id)
    print("user rows", user_rows)

    # If no such user exists, return error
    if not user_rows:
        return jsonify({'error': 'User not found'}), 404

    # Directly fetch history by user_id
    rows = dbConn.get_listening_history_by_user_id(user_id)

    # Return the listening history
    return jsonify({
        'message': 'User listening history retrieved',
        'user_listening_history': rows,
        'logged_in': True,
        'needs_refresh': False
    }), 200

def clean_user_info_by_username(out):
    '''Cleans the user info from the database.'''

    # Convert DB output to list of dicts
    cleaned_info = []
    for row in out:
        user_dict = {
            'spotify_id': row[1],
            'user_name': row[2],
            'profile_image_url': row[3],
            'diversity_score': row[4]
        }
        cleaned_info.append(user_dict)
    return cleaned_info

@app.route('/is-user-history-updating') # Will also have the spotify id as a query parameter
def is_user_history_updating():
    '''Returns whether the user's listening history is currently being updated.'''

    # Check if user is logged in
    if 'access_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get spotify_id from query parameters
    spotify_id = request.args.get('spotify_id')

    # If no spotify_id provided, return error
    if spotify_id is None:
        return jsonify({
            'error': 'No spotify_id provided in request',
        }), 400

    # No synchronization issues because we never write to this variable on thread 1!
    return {"status":dbConn.is_user_history_updating(spotify_id)}

@app.route('/get-user-listening-history')
def get_user_listening_history():
    '''Get the user's listening history from the SpotifyDB Database, using existing dbconnection'''

    # Check if we've stored user's spotify_id locally
    spotify_id: Optional[str] = None
    try:
        spotify_id = session['spotify_id']
    except:
        print("spotify_id not in session")
    print("Fetch listening history spotify_id:", spotify_id)
    if spotify_id is None:
        return jsonify({
            'error': 'Not authenticated: spotify id not in session',
            'logged_in': False
        }), 401

    # Fetch and clean the user's listening history from the database
    cleaned_user_info = dbConn.get_user_listening_history(
        session['spotify_id'])
    
    # Return the user_info
    try:
        return jsonify({
            'message': 'User listening history retrieved',
            'user_listening_history': cleaned_user_info,
            'logged_in': True,
            'needs_refresh': False
        }), 200
    except Exception as e:
        # Return error message
        return jsonify({'error': str(e)}), 400

# User listening history endpoint


@app.route('/fetch-user-listening-history-by-id/<int:user_id>')
def fetch_user_listening_history(user_id):
    '''Fetch the user's listening history from the Spotify API, using the access token.'''

    # Check if user is logged in
    if 'access_token' not in session:
        return jsonify({
            'error': 'Not authenticated: access token not in session',
            'logged_in': False
        }), 401
    
    # Check if current user matches requsted user_id
    current_user_id = dbConn.get_user_id_by_spotify_id(session.get('spotify_id'))
    if current_user_id != user_id:
        return jsonify({
            'error': 'Not authorized to fetch this user\'s listening history',
            'logged_in': False
        }), 403

    # Check if we've stored user's spotify_id locally
    spotify_id = dbConn.get_spotify_id_by_user_id(user_id)
    print("Fetch listening history spotify_id:", spotify_id)
    if spotify_id is None:
        return jsonify({
            'error': 'Not authenticated: spotify id not in session',
            'logged_in': False
        }), 401

    # Check if access token is expired
    if datetime.now().timestamp() > session['expires_at']:
        # If access token is expired, refresh token
        return jsonify({
            'error': 'Access token expired',
            'logged_in': False,
            'needs_refresh': True
        }), 401

    try:
        # Construct header
        req_headers = {
            "Authorization": f"Bearer {session['access_token']}"
        }

        req_params = {
            "limit": 50
        }

        # Send GET request to Spotify API to get user information
        response = requests.get(
            f'{API_BASE_URL}/me/player/recently-played',
            headers=req_headers,
            params=req_params)

        # Extract JSON from response
        user_history = response.json()

        # Clean/Simplify the JSON data (create instance first)
        simplifier = SimplifyJSON()
        cleaned_user_info = simplifier.simplify_listening_history(user_history)

        # Return the user_info
        return jsonify({
            'message': 'User listening history retrieved',
            'user_listening_history': cleaned_user_info,
            'logged_in': True,
            'needs_refresh': False
        }), 200

    except Exception as e:
        # Return error message
        return jsonify({'error': str(e)}), 400
    finally:
        threading.Thread(
            target=dbConn.update_user_history,
            args=(session['spotify_id'], response.text,
                  session['access_token'])
        ).start()


# Refresh token route
@app.route('/refresh-user-token')
def refresh_token():
    '''Refresh the access token using the refresh token.'''

    # Check if refresh token is available
    if 'refresh_token' not in session:
        # Return error message
        return jsonify({'error': 'Refresh token not found'})

    try:
        # Send refresh token to get a new access token
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        # Send POST request to Spotify API to refresh access token
        response = requests.post(TOKEN_URL, data=req_body)
        # Extract JSON from response
        new_token_info = response.json()

        # Store new access token and expiry time in session
        session['access_token'] = new_token_info['access_token']
        # Store expiry as an absolute timestamp
        session['expires_at'] = datetime.now().timestamp() + \
            int(new_token_info['expires_in'])

        # Return success message
        return jsonify({'message': 'Access token refreshed'}), 200
    except Exception as e:
        # Return error message
        return jsonify({'error': str(e)}), 400


@app.route('/get-song-of-the-day')
def get_song_of_the_day():
    '''Get the song of the day. Refreshes it if it's older than 24 hours.'''

    # Check if user is logged in
    if 'access_token' not in session:
        return jsonify({
            'error': 'Not authenticated',
            'logged_in': False
        }), 401

    # Check if access token is expired
    if datetime.now().timestamp() > session['expires_at']:
        return jsonify({
            'error': 'Access token expired',
            'logged_in': False,
            'needs_refresh': True
        }), 401

    try:
        # Check if we need to refresh the song of the day
        should_refresh = dbConn.should_refresh_song_of_the_day()

        if should_refresh:
            # Get all unique tracks from all users' listening histories
            all_tracks = dbConn.get_all_unique_tracks()
            
            if not all_tracks or len(all_tracks) == 0:
                # No tracks available
                return jsonify({
                    'error': 'No listening history available',
                    'song_of_the_day': None
                }), 200

            # Get all previously selected track IDs
            previously_selected = dbConn.get_all_previously_selected_track_ids()

            # Filter out previously selected tracks
            available_tracks = [
                track for track in all_tracks
                if track[0] not in previously_selected  # track[0] is track_id
            ]

            # If no tracks remain, clear history and restart
            if len(available_tracks) == 0:
                dbConn.clear_song_of_the_day_history()
                available_tracks = all_tracks

            # Randomly select one track from available tracks
            if len(available_tracks) > 0:
                selected_track = random.choice(available_tracks)
                track_id = selected_track[0]
                
                # Update the song of the day
                dbConn.update_song_of_the_day(track_id)

        # Get the current song of the day (either existing or newly selected)
        current_song = dbConn.get_current_song_of_the_day()

        if current_song is None:
            return jsonify({
                'error': 'No song of the day available',
                'song_of_the_day': None
            }), 200

        # Format the response to match frontend expectations
        # * current_song format: (track_id, track_name, song_img_url, album_name, artist_names, artist_ids, selected_at)
        track_id = current_song[0]
        track_name = current_song[1]
        song_img_url = current_song[2]
        album_name = current_song[3] if len(current_song) > 3 else None
        artist_names = current_song[4] if len(current_song) > 4 else []
        artist_ids = current_song[5] if len(current_song) > 5 else []

        # Format artist names as a string (comma-separated)
        artists_str = ", ".join(artist_names) if artist_names else "Unknown Artist"

        # Generate Spotify URL
        from server_utils import get_track_url_from_id
        spotify_url = get_track_url_from_id(track_id)

        # Return formatted response
        return jsonify({
            'message': 'Song of the day retrieved',
            'song_of_the_day': {
                'id': track_id,
                'track_name': track_name,
                'artists': artists_str,
                'artist_ids': artist_ids,
                'album_image': song_img_url,
                'spotify_url': spotify_url,
                'album_name': album_name
            },
            'logged_in': True,
            'needs_refresh': False
        }), 200

    except Exception as e:
        # Return error message
        return jsonify({'error': str(e)}), 500


@app.before_request
def check_db_connection():
    if dbConn is None or not dbConn.connected:
        return jsonify({
            "error": "Database connection failed. Please try again later."
        }), 501


# Run the application
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
