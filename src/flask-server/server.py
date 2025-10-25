import os
import urllib.parse, requests
from datetime import datetime
from flask import Flask, redirect, request, jsonify, session

# Flask app initialization
app = Flask(__name__)

# Constants
# - REDIRECT_URI = 'https://localhost:3000/callback'
REDIRECT_URI = 'http://127.0.0.1:5000/callback'
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1'

@app.route('/')
def lander():
    return "<div><h1>API lander<h1><div>"

# Login route
@app.route('/login')
def login(): 
    '''Redirect the user to Spotify's authorization URL to authorize the app.'''

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
        # Return error message
        return jsonify({'error': str(e)})

# Callback route 
@app.route('/callback')
def callback():
    '''Handle the callback from Spotify's authorization server and exchange temporary code for access token.'''

    # Check if there is an error
    if 'error' in request.args:
        # Return error message
        return jsonify({'error': request.args['error']})
    
    try:
        # If there is no error, get the temporary authorization code
        # - When successful, auth server returns a temporary code in URL parameters
        # - Need to exchange temp code for access token 
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
            
            # Return success message
            return jsonify({'message': 'User authorized successfully'})
    except Exception as e:
        # Return error message
        return jsonify({'error': str(e)})

# Dashboard route
@app.route('/api-get-user-info')
def api_get_user_info():
    '''Get the user's information from the Spotify API using the access token.'''

    # Check if user is logged in
    if 'access_token' not in session:
        # If not logged in, redirect to login page
        return redirect('/login')
    
    # Check if access token is expired
    if datetime.now().timestamp() > session['expires_at']:
        # If access token is expired, refresh token
        return redirect('/refresh-token')
    
    try:
        # Send GET request to Spotify API to get user information
        req_headers = { 
            "Authorization": f"Bearer {session['access_token']}"
        }

        # Send GET request to Spotify API to get user information
        response = requests.get(f'{API_BASE_URL}/me', headers=req_headers)
        # Extract JSON from response
        user_info = response.json()
        
        # Return the user_info
        return jsonify({'message': 'User information retrieved', 'user_info': user_info})
    except Exception as e:
        # Return error message
        return jsonify({'error': str(e)})

# Refresh token route
@app.route('/refresh-token')
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
        return jsonify({'message': 'Access token refreshed'})
    except Exception as e:
        # Return error message
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)