# EECS 581 Project 3

## Setup

**Prerequisites:** Make sure you have Node.js and npm installed (Node.js 16+ recommended for React 18).

Install frontend dependencies:
```bash
cd src/client
npm install
```
This grabs all the npm packages you'll need for the frontend.

Also install Python dependencies:
```bash
pip install -r requirements.txt
```
All the libraries needed for the backend

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
- `APP_SECRET_KEY` - A random secret key for session security

Create a `.env` file in the `src/flask-server` directory with these variables.

**For the React client:**
Create a `.env` file in the `src/client` directory with:
```
HOST=127.0.0.1
DANGEROUSLY_DISABLE_HOST_CHECK=true
```
Best for frontend & backend sync

## Running the App

### Backend (Flask Server)
1. `cd` into `src/flask-server`
2. Run the Flask app with `python3 server.py` or `python3 -m server`
3. The server will start on `http://127.0.0.1:5000`
4. You can test the login flow by visiting `http://127.0.0.1:5000/login`

### Frontend (React Client)
1. `cd` into `src/client`
2. Run `npm start`
3. The React app will start on `http://127.0.0.1:3000`

## Usage

To get a working system, you need to run both the frontend and backend at the same time:

1. **Start the Flask backend** (in one terminal):
   ```bash
   cd src/flask-server
   python3 server.py
   ```

2. **Start the React frontend** (in another terminal):
   ```bash
   cd src/client
   npm start
   ```

3. **Access the application**:
   - Frontend: `http://127.0.0.1:3000`
   - Backend: `http://127.0.0.1:5000`

**Note:** The frontend and backend are separate applications. The React frontend makes API calls to the Flask backend for Spotify authentication and user data.
