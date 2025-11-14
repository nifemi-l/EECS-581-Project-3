# Prologue
# Name: server.py
# Description: Create and manage a flask server backend for our application
# Programmer: Nifemi Lawal
# Creation date: 10/23/25
# Last revision date: 11/05/25
# Revisions: 1.2
# Pre/post conditions
#   - Pre: None. 
#   - Post: None.
# Errors: None. 

import os
from flask.typing import ErrorHandlerCallable
import urllib.parse, requests
from datetime import datetime
from flask import Flask, redirect, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from typing import Optional
import werkzeug
from helpers.simplify_json import SimplifyJSON
from DBConnection import DBConnection
from werkzeug.exceptions import HTTPException, InternalServerError

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
    SESSION_COOKIE_SAMESITE='Lax',  # This means the cookie is only accessible on the same site
    SESSION_COOKIE_SECURE=False,    # This means the cookie is not secure --> not HTTPS
    SESSION_COOKIE_HTTPONLY=True,   # This means the cookie is not accessible by JavaScript
    SESSION_COOKIE_DOMAIN='127.0.0.1' # This means the cookie is only accessible on the local host (127.0.0.1)
)

# Constants
# - REDIRECT_URI = 'https://localhost:3000/callback'
REDIRECT_URI = 'http://127.0.0.1:5000/callback'
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1'
ERROR_MESSAGE = 'Authentication failed: {error}'

# Initialize our connection to the Scorify database
dbConn : Optional[DBConnection] = None
try:
    temp = DBConnection()
    if not temp.connected:
        raise ConnectionError("Database connection failed: could not connect to Scorify database.")
    else:
        dbConn = temp
except Exception as e:
    import sys
    print(f"[ERROR] {e}", file=sys.stderr)

def handle_error(error):
    '''Handle an error by redirecting to the login page with the error parameter.'''

    try:
        # URL-encode the error message
        encoded_error_message = urllib.parse.quote(ERROR_MESSAGE.format(error=error))
        # Redirect to login page with error parameter
        return redirect(f'http://127.0.0.1:3000/login?error={encoded_error_message}')
    except Exception as e:
        # URL-encode the error message
        encoded_error_message = urllib.parse.quote(ERROR_MESSAGE.format(error=e))
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
        assert(dbConn.connected)
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
            session['expires_at'] = datetime.now().timestamp() + int(token_info['expires_in'])
            
            # Return success message and redirect to the dashboard page
            return redirect('http://127.0.0.1:3000/dashboard')
    except Exception as e:
        # Handle error and redirect to login page with error parameter
        return handle_error(e)

# User profile information endpoint
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
        # Extract JSON from response
        user_info = response.json()
        spotify_id = user_info['id']
        session['spotify_id'] = spotify_id
        
        dbConn.add_user(response.text, session["access_token"], session["refresh_token"])
        # Return the user_info
        return jsonify({
            'message': 'User information retrieved', 
            'user_info': user_info,
            'logged_in': True,
            'needs_refresh': False
        }), 200

    except Exception as e:
        # Return error message
        return jsonify({'error': str(e)}), 400

# User listening history endpoint
@app.route('/get-user-listening-history')
def get_user_listening_history():
    '''Get the user's listening history from the Spotify API, using the access token.'''

    # Check if user is logged in
    if 'access_token' not in session: 
        return jsonify({ 
            'error': 'Not authenticated: access token not in session',
            'logged_in': False
        }), 401

    # Check if we've stored user's spotify_id locally
    spotify_id : Optional[str] = None
    spotify_id = session['spotify_id']
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
        user_info = response.json()

        try:
            dbConn.update_user_history(session['spotify_id'], response.text)
        except Exception as e:
            print(f"Database could not update user history: {e}")
            raise Exception(f"Database could not update user history: {e}")

        
        # Clean/Simplify the JSON data (create instance first)
        simplifier = SimplifyJSON()
        cleaned_user_info = simplifier.simplify_listening_history(user_info)

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
        session['expires_at'] = datetime.now().timestamp() + int(new_token_info['expires_in'])

        # Return success message
        return jsonify({'message': 'Access token refreshed'}), 200
    except Exception as e:
        # Return error message
        return jsonify({'error': str(e)}), 400

@app.before_request
def check_db_connection():
    if dbConn is None or not dbConn.connected:
        return jsonify({
            "error": "Database connection failed. Please try again later."
        }), 501


# Run the application
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
