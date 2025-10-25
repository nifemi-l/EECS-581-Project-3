# EECS 581 Project 3

## Setup

Before anything else, in the root directory, run:
```bash
npm install
```
This grabs all the npm packages you'll need for the frontend.

Also install Python dependencies:
```bash
pip install -r requirements.txt
```

**Note:** If you have a virtual environment set up (there's a `venv/` directory), activate it first:
```bash
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

## Environment Variables

You'll need to set up environment variables:

**For the Flask backend:**
- `SPOTIFY_CLIENT_ID` - Your Spotify app client ID
- `SPOTIFY_CLIENT_SECRET` - Your Spotify app client secret

Create a `.env` file in the root directory or set these as system environment variables.

## Running the App

### Backend (Flask Server)
1. `cd` into `src/flask-server`
2. Run the Flask app normally or with `python -m server`
3. Click on the host URL
4. Go to a route to see activity (e.g. `127.0.0.1:5000/login`) to see login stuff

### Frontend (React Client)
1. `cd` into `src/client`
2. Run `npm start`
3. Get taken to the localhost frontend

## Note
You can technically run frontend and backend simultaneously, but they're not actually reconciled on the same host, so nothing (good) will happen.
