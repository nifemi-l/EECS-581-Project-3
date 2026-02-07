# Prologue
# Name: oBConnction.py
# Description: Open a connection to our application's PostgreSQL database
# Programmer: Dellie Wright, Jack Bauer, Logan Smith, Blake Carlson
# Last revision date: 12/02/25
# Revisions: 2.0
# Pre/post conditions
#   - Pre: Port 54321 must not be in use by any other processes.
#   - Post: After execution, the connection to the database will be accessible via the DBConnection.sql_cursor object.
# Errors: All known errors should be handled gracefully.

# Import needed libraries
import atexit
import os
from flask import Flask, redirect, request, jsonify, session
import json
from dotenv import dotenv_values
import requests
import signal
import subprocess
import time
from contextlib import closing
import os
from icecream import ic
from server_utils import clean_db_listening_history, normalize_spotify_date
import signal
import socket
import subprocess
import sys

import psycopg2
from psycopg2 import Error, sql
from psycopg2.extras import execute_values
from mb_api import mb_lookup_by_name, mb_lookup_by_spotify_id, mb_get_genres


def exit_handler():
    subprocess.call("killall cloudflared")


class DBConnection:
    def __init__(self):

        # Read secure config keys / values from a .env file that is not included with git
        config = dotenv_values(".env")
        self.connected = False
        self.SERVICE_TOKEN_ID = config["SERVICE_TOKEN_ID"]
        self.SERVICE_TOKEN_SECRET = config["SERVICE_TOKEN_SECRET"]
        self.DB_PASSWORD = config["DB_PASSWORD"]
        self.DB_USER = config["DB_USER"]

        # Set other needed config parameters
        self.DB_PORT = config["DB_PORT"]
        self.LOCAL_HOST = "127.0.0.1"
        self.DB_NAME = "spotifydb"

        # List of updates currently being made to user histories
        # Should be a list of spotify_ids
        self.history_update_list = []

        # Set a timeout value for external connections
        self.STARTUP_TIMEOUT = 20

        # The command that will be used to connect to the database through the cloudflare tunnel
        # self.cloudflared_cmd = [
        #     "cloudflared", "access", "tcp",
        #     "--hostname", self.HOSTNAME,
        #     "--url", f"{self.LOCAL_HOST}:{self.LOCAL_PORT}",
        #     "--service-token-id", self.SERVICE_TOKEN_ID,
        #     "--service-token-secret", self.SERVICE_TOKEN_SECRET,
        # ]
        #
        # # Output status information
        # print(f"Starting Cloudflare proxy on {self.LOCAL_HOST}:{self.LOCAL_PORT} → {self.HOSTNAME} ...")
        #
        # Make the actual subprocess to handle our connection
        # self.proc = subprocess.Popen(
        #     self.cloudflared_cmd,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     text=True,
        # )
        # Wait briefly for the tunnel to come up
        # time.sleep(0.5)

        # if self.proc.poll() is not None:
        #     stderr = self.proc.stderr.read()
        #     raise RuntimeError(f"cloudflared exited early:\n{stderr}")
        #
        # The main connection initialization block
        try:

            # Establish a connection to the PostgreSQL database
            self.conn = psycopg2.connect(
                host=self.LOCAL_HOST, port=self.DB_PORT,
                user=self.DB_USER, password=self.DB_PASSWORD, dbname=self.DB_NAME,
                connect_timeout=10,
            )
            self.connected = True
            print(f"Established connection! {self.conn}")
        except Exception as e:
            self.connected = False
            print(
                f"Failed to establish SQL connection!\nFailed with exception: {e}")
            if self.proc.poll() is None:
                self.proc.send_signal(signal.SIGINT)  # Tell it to close
                try:
                    # Give it the chance to exit gracefully
                    self.proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.proc.kill()  # Kill it if it takes too long

    def execute_vals(self, cmd, rows, fetch=False):
        """Executes a batch SQL command using execute_values for efficiency."""
        try:
            with self.conn.cursor() as cur:
                execute_values(cur, cmd, rows)
                result = []
                if fetch:
                    try:
                        result = cur.fetchall()
                    except psycopg2.ProgrammingError:
                        pass
                self.conn.commit()
                # print(f"successfully executed command:\n\t{command}\nWith result:\n\t{result}")
                return result
        except psycopg2.ProgrammingError as e:
            self.conn.commit()
            # print(f"Failed to execute command:\n\t{command}\nWith error:\n\t{e}")
            raise e

    def execute_cmd(self, command, params, fetch=False):
        """Execute an arbitrary SQL command with parameters."""
        # function that executes an arbitrary SQL command
        # fetch flag - if false, we do not expect any results to be returned by SQL - used insert, update, or delete
        try:
            with self.conn.cursor() as cur:
                cur.execute(command, params)
                result = []
                if fetch == True:
                    try:
                        result = cur.fetchall()
                    except psycopg2.ProgrammingError:
                        pass
                self.conn.commit()
                # print(f"successfully executed command:\n\t{command}\nWith result:\n\t{result}")
                return result
        except psycopg2.ProgrammingError as e:
            self.conn.commit()
            # print(f"Failed to execute command:\n\t{command}\nWith error:\n\t{e}")
            raise e

    def add_user(self, user_info_json: str, access_token: str, refresh_token: str):
        """Add a new user to the database"""

        # based on endpoint: https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile
        print("running add user")
        user_info = json.loads(user_info_json)
        spotify_id = user_info['id']
        user_name = user_info['display_name']
        diversity_score = 0.0
        try:
            profile_image_url = user_info['images'][0]['url']
        except Error as _:
            print("user does not have profilepicture, defaulting")
            profile_image_url = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.pinimg.com%2F736x%2Ff6%2Fbc%2F9a%2Ff6bc9a75409c4db0acf3683bab1fab9c.jpg&f=1&nofb=1&ipt=c48e5082d31a5e88acc29db27870ce17134db62d49a799dd7a7d41fd938c0a98"
        cmd = """
            INSERT INTO users (spotify_id, user_name, access_token, refresh_token, profile_image_url, diversity_score)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (spotify_id)
            DO UPDATE SET
                access_token = EXCLUDED.access_token,
                refresh_token = EXCLUDED.refresh_token;
            """
        params = (spotify_id, user_name, access_token,
                  refresh_token, profile_image_url, diversity_score)

        self.execute_cmd(cmd, params, fetch=False)

    def get_user_profile(self, user_id):
        """Return username and profile image for the user with parameter user_id"""

        cmd = f"""SELECT t.spotify_id, t.user_name, t.profile_image_url
        FROM users us
        WHERE us.user_id = %s
        ;"""
        params = (user_id,)
        return self.execute_cmd(cmd, params)

    def get_user_diversity_score_by_id(self, user_id):
        """Return diversity score for the user with parameter user_id"""

        cmd = f"""SELECT um.diversity_score
        FROM user_metrics um
        JOIN users u ON um.user_id = u.user_id
        WHERE u.user_id = %s
        ;"""
        params = (user_id,)
        return self.execute_cmd(cmd, params, fetch=True)
    
    def get_user_taste_score_by_id(self, user_id):
        """Return taste score for the user with parameter user_id"""

        cmd = f"""SELECT um.taste_score
        FROM user_metrics um
        JOIN users u ON um.user_id = u.user_id
        WHERE u.user_id = %s
        ;"""
        params = (user_id,)
        return self.execute_cmd(cmd, params, fetch=True)
    
    def get_user_history(self, user_id, limit=25):
        """Return recently played tracks for the user with parameter user_id"""

        cmd = f"""SELECT t.name, a.name AS artist, t.track_id
        FROM listening_history lh
        JOIN tracks t ON lh.track_id = t.track_id
        JOIN artists a ON t.artist_id = a.artist_id
        WHERE lh.user_id = %s
        ORDER BY lh.played_at DESC
        LIMIT %s;
        """
        params = (user_id, limit)
        return self.execute_cmd(cmd, params)
    
    def get_user_genres(self, spotify_id):
        """Return genres for the user with parameter spotify_id"""

        cmd = """
            SELECT a.genres
            FROM listening_history lh
            JOIN tracks t ON lh.track_id = t.spotify_track_id
            JOIN artists a ON t.spotify_artist_id = a.spotify_artist_id
            WHERE lh.spotify_id = %s
        """
        params = (spotify_id,)
        return self.execute_cmd(cmd, params, fetch=True)
    
    def get_many_user_profiles(self, limit=25):
        """Return usernames and profile images per each user."""
        cmd = """SELECT spotify_id, user_name, profile_image_url, user_id
                FROM users
                LIMIT %s;"""
        params = [limit]
        return self.execute_cmd(cmd, params, fetch=True)
    
    def get_many_user_scores(self, limit=25):
        """Return metrics calculated for each user."""
        cmd = """SELECT spotify_id, diversity_score, taste_score 
                FROM user_metrics
                LIMIT %s;"""
        params = [limit]
        return self.execute_cmd(cmd, params, fetch=True)
    
    def update_user_diversity_score(self, user_id, spotify_id, div_score):
        """Update diversity score for the user with parameter user_id"""
        # Check if user has entries in the metrics table (this is necessary since add_user does not
        # initialize these records by default)
        check_cmd = """SELECT 1 
                       FROM user_metrics 
                       WHERE user_id=%s
                       AND spotify_id=%s;
                    """
        check_params = [user_id, spotify_id]
        check_result = self.execute_cmd(check_cmd, check_params, fetch=True)

        # Diversity score must be between 0 and 1 for the database:
        div_score /= 100
        div_score = round(div_score, 4) # Round to four decimal places

        # If we don't have a user_metrics entry for this user, we need to insert a new record.
        # Otherwise, we run an update query. 
        cmd = """"""
        params = []
        if len(list(check_result)) <= 0:
            # We need to insert a new record. We'll initialize the taste score to zero.
            # We don't need to worry about updating last_updated because it is automatically set to now by default
            cmd = """INSERT INTO user_metrics (user_id, spotify_id, diversity_score, taste_score)
                     VALUES (%s, %s, %s, %s);
                  """
            # Setup our parameters (remember: defaulting taste score to zero for now since we're inserting a new record)
            params = [user_id, spotify_id, div_score, 0]
        else:
            # We can just update an old record
            cmd = """UPDATE user_metrics
                     SET diversity_score = %s, last_updated = DEFAULT
                     WHERE spotify_id = %s
                     AND user_id = %s;"""
            # Set the params. Note the different order than previously
            params = [div_score, spotify_id, user_id]

        # Raise an error if we haven't set the command or parameters correctly
        if len(cmd) <= 0 or len(params) <= 0:
            # This should be impossible to hit but is left for redundancy
            raise ValueError("Cannot run an empty command or run a command with no parameters.")

        return self.execute_cmd(cmd, params)

    def update_user_taste_score(self, user_id, spotify_id, taste_score):
        """Update taste score for the user with parameter user_id"""
        # Check if user has entries in the metrics table (this is necessary since add_user does not
        # initialize these records by default)
        check_cmd = """SELECT 1 
                       FROM user_metrics 
                       WHERE user_id=%s
                       AND spotify_id=%s;
                    """
        check_params = [user_id, spotify_id]
        check_result = self.execute_cmd(check_cmd, check_params, fetch=True)

        # Taste score must be between 0 and 1 for the database:
        taste_score /= 100
        taste_score = round(taste_score, 4) # Round to four decimal places

        # If we don't have a user_metrics entry for this user, we need to insert a new record.
        # Otherwise, we run an update query. 
        cmd = """"""
        params = []
        if len(list(check_result)) <= 0:
            # We need to insert a new record. We'll initialize the taste score to zero.
            # We don't need to worry about updating last_updated because it is automatically set to now by default
            cmd = """INSERT INTO user_metrics (user_id, spotify_id, diversity_score, taste_score)
                     VALUES (%s, %s, %s, %s);
                  """
            # Setup our parameters (remember: defaulting taste score to zero for now since we're inserting a new record)
            params = [user_id, spotify_id, 0, taste_score]
        else:
            # We can just update an old record
            cmd = """UPDATE user_metrics
                     SET taste_score = %s, last_updated = DEFAULT
                     WHERE spotify_id = %s
                     AND user_id = %s;"""
            # Set the params. Note the different order than previously
            params = [taste_score, spotify_id, user_id]

        # Raise an error if we haven't set the command or parameters correctly
        if len(cmd) <= 0 or len(params) <= 0:
            # This should be impossible to hit but is left for redundancy
            raise ValueError("Cannot run an empty command or run a command with no parameters.")
        return self.execute_cmd(cmd, params)
    
    def get_user_listening_history(self, spotify_id):
        """Returns the entire listening history of the user with parameter spotify_id"""

        get_listening_history = f"SELECT * FROM listening_history JOIN tracks ON listening_history.track_id = tracks.track_id WHERE listening_history.spotify_id = %s ORDER BY played_at DESC;"
        params = (spotify_id,)
        return self.execute_cmd(get_listening_history, params)
    
    def get_user_listening_history_id(self, spotify_id):
        """Returns the entire listening history of the user with parameter spotify_id (Non-Ordered)"""

        get_listening_history = f"SELECT * FROM listening_history JOIN tracks ON listening_history.track_id = tracks.track_id WHERE listening_history.spotify_id = %s"
        params = (spotify_id,)
        return self.execute_cmd(get_listening_history, params)
    

    def get_user_info_by_id(self, user_id: int):
        """Returns user info for the user with the given user_id"""

        print("getting user info by id:", user_id)
        query = """
            SELECT user_id, spotify_id, user_name, profile_image_url,
                access_token, refresh_token, diversity_score
            FROM users
            WHERE user_id = %s;
        """
        return self.execute_cmd(query, (user_id,), fetch=True)
    
    def get_all_listening_history(self):
        """Returns the entire listening history of all users (Non-Ordered)"""\
        
        get_listening_history = "SELECT context, tracks.name FROM listening_history JOIN tracks ON listening_history.track_id = tracks.track_id"
        return self.execute_cmd(get_listening_history, ())

    def get_spotify_id_by_user_id(self, user_id):
        """Returns spotify_id for the user with parameter user_id"""

        cmd = "SELECT spotify_id FROM users WHERE user_id = %s;"
        params = [user_id]
        user_id = self.execute_cmd(cmd, params, fetch=True)
        if user_id == []:
            raise Error("User is not present in database")
        else:
            return user_id

    def get_listening_history_by_user_id(self, user_id: int):
        """Returns the entire listening history of the user with parameter user_id"""

        spotify_id = self.get_spotify_id_by_user_id(user_id)
        spotify_id = spotify_id[0][0]

        # Same listening history command as non-user_id path
        get_listening_history = """
            SELECT
                lh.played_at,
                lh.context,
                t.spotify_track_id AS track_id,
                t.name AS track_name,
                t.song_img_url,
                ARRAY_AGG(a.name ORDER BY a.name) AS artist_names,
                ARRAY_AGG(a.spotify_artist_id ORDER BY a.name) AS artist_ids
            FROM listening_history lh
            JOIN tracks t
                ON lh.track_id = t.spotify_track_id
            JOIN artist_tracks at
                ON t.spotify_track_id = at.track_id
            JOIN artists a
                ON at.artist_id = a.spotify_artist_id
            WHERE lh.spotify_id = %s
            GROUP BY
                lh.played_at,
                lh.context,
                t.spotify_track_id,
                t.name,
                t.song_img_url
            ORDER BY lh.played_at DESC;
        """
        params = [spotify_id]
        return clean_db_listening_history(self.execute_cmd(get_listening_history, params, fetch=True))

    def get_user_id_by_spotify_id(self, spotify_id):
        """Returns user_id for the user with parameter spotify_id"""

        cmd = "SELECT user_id FROM users WHERE spotify_id = %s;"
        params = [spotify_id]
        user_id = self.execute_cmd(cmd, params, fetch=True)
        if user_id == []:
            raise Error("User is not present in database")
        else:
            return user_id[0][0]
        
    def get_diversity_score_by_spotify_id(self, spotify_id):
        """Returns diversity_score for the user with parameter spotify_id"""

        cmd = "SELECT diversity_score FROM user_metrics WHERE spotify_id = %s;"
        params = [spotify_id]
        diversity_score = self.execute_cmd(cmd, params, fetch=True)
        if diversity_score == []:
            raise Error("User is not present in database")
        else:
            return diversity_score[0][0]
        
    def is_user_history_updating(self, spotify_id):
        """Returns True if the user's history is currently being updated, False otherwise"""
        return spotify_id in self.history_update_list

    def update_user_history(self, spotify_id, spotify_json: str, access_token: str):
        """Update the user's listening history in the database"""

        # based on endpoint: https://developer.spotify.com/documentation/web-api/reference/get-recently-played
        print("updating history for:", spotify_id)
        self.history_update_list.append(spotify_id)
        artist_rows = []
        tracks_rows = []
        listening_history_rows = []
        artists_tracks_rows = []

        artists_cmd = """
            INSERT INTO artists (spotify_artist_id, name)
            VALUES %s
            ON CONFLICT (spotify_artist_id) DO NOTHING;
        """

        artist_genre_cmd = """
            UPDATE artists
            SET genres = data.genres
            FROM (VALUES %s) AS data(spotify_artist_id, genres)
            WHERE artists.spotify_artist_id = data.spotify_artist_id;
        """

        tracks_cmd = """
            INSERT INTO tracks (spotify_track_id, name, spotify_artist_id, duration_ms, album_name, release_date, song_img_url)
            VALUES %s
            ON CONFLICT (spotify_track_id) DO NOTHING;
        """

        listening_history_cmd = """
            INSERT INTO listening_history (spotify_id, track_id,  played_at, context)
            VALUES %s
            ON CONFLICT (track_id) 
            DO UPDATE SET played_at = EXCLUDED.played_at;
        """

        artists_tracks_cmd = """
            INSERT INTO artist_tracks (artist_id, track_id)
            VALUES %s ON CONFLICT (artist_id, track_id) DO NOTHING;
            """

        spotify_data = json.loads(spotify_json)

        for item in spotify_data["items"]:
            track = item["track"]
            track_id = track["id"]
            played_at = item["played_at"]
            album = track["album"]
            artists = track["artists"]  # just the first artist for now

            artist = track["artists"][0]
            artist_id = artist["id"]

            track_name = track["name"]
            song_img_url = track["album"]["images"][0]["url"]
            album_name = album["name"]
            release_date_raw = album.get("release_date", None)
            release_date = normalize_spotify_date(release_date_raw)

            duration_ms = track.get("duration_ms", "NULL")

            context = item["context"]["type"] if item.get("context") else None

            # Add variables for batch tracks update
            artist_rows.append((artist_id,
                                artist["name"]))

            # Add variables for batch tracks update
            tracks_rows.append((track_id, track_name, artist_id, duration_ms if duration_ms else "NULL", album_name, release_date if release_date else "NULL",
                                song_img_url))

            # Add variables for batch listening_history update
            listening_history_rows.append(
                (spotify_id, track_id,  played_at, context if context else "NULL"))

            for artist in artists:
                artist_id = artist["id"]
                artists_tracks_rows.append((artist_id, track_id))
                artist_rows.append((artist_id, artist["name"]))
            

        # Deduplicate rows by track_id — newest played_at wins
        dedup = {}
        for row in listening_history_rows:
            spotify_id, track_id, played_at, context = row

            # keep the row with the latest played_at
            if track_id not in dedup or played_at > dedup[track_id][2]:
                dedup[track_id] = row

        # only unique rows go to Postgres
        listening_history_rows = list(dedup.values())

        # Now fetch genres for all unique artists
        unique_artist_ids = {artist_id for (artist_id, _) in artist_rows}
        artist_genre_rows = []

        headers = {"Authorization": f"Bearer {access_token}"}

        for a_id in unique_artist_ids:
            # Define Spotify API URL with artist ID
            url = f"https://api.spotify.com/v1/artists/{a_id}"

            try:
                # Try the Spotify API request
                r = requests.get(url, headers=headers)

                # If API working -> get the genre list
                if r.status_code == 200:
                    genres = r.json().get("genres", [])

                    # If Spotify returns genres from API request -> Append genre list
                    if len(genres) > 0:
                        artist_genre_rows.append((a_id, genres))

                    else:
                        # Spotify returned empty genre list → do NOT call MusicBrainz.
                        # Instead preserve existing genres if they exist.
                        existing = self.execute_cmd(
                            "SELECT genres FROM artists WHERE spotify_artist_id = %s",
                            (a_id,),
                            fetch=True,
                        )
                        # If genre list exists, do not overwrite it, otherwise set to NO_GENRE_DATA
                        if existing and len(existing[0][0]) > 0 and existing[0][0] != ["NO_GENRE_DATA"]:
                            artist_genre_rows.append((a_id, existing[0][0]))
                        else:
                            artist_genre_rows.append((a_id, ["NO_GENRE_DATA"]))

            except Exception as e:
                print("Spotify error:", e)

                # Spotify failed → DO NOT call MusicBrainz here either.
                # Just preserve whatever genre data already exists.
                existing = self.execute_cmd(
                    "SELECT genres FROM artists WHERE spotify_artist_id = %s",
                    (a_id,),
                    fetch=True
                )

                # If genre list exists, do not overwrite it
                if existing and len(existing[0][0]) > 0 and existing[0][0] != ["NO_GENRE_DATA"]:
                    artist_genre_rows.append((a_id, existing[0][0]))
                else:
                    artist_genre_rows.append((a_id, ["NO_GENRE_DATA"]))

            # Add variables for batch artists_tracks update
        # Insert any new artists, tracks, genre lists & listening history enteries
        try: 
            self.repair_missing_genres()
        except Exception as e:
            print("Error while repairing missing genres:", e)
        self.execute_vals(artists_cmd, artist_rows)
        self.execute_vals(tracks_cmd, tracks_rows)
        self.execute_vals(artist_genre_cmd, artist_genre_rows)
        self.execute_vals(listening_history_cmd, listening_history_rows)
        self.execute_vals(artists_tracks_cmd, artists_tracks_rows)
        if spotify_id in self.history_update_list:
            self.history_update_list.remove(spotify_id)
        else:
            print("Error: user should be in update list")
        print("Done updating user listening history on the DB")

    def killCloudflare(self):
        """Kills the cloudflare process if it is running"""

        # Regardless of success or failure in making the connection...
        print("Stopping Cloudflare proxy...")
        if self.proc.poll() is None:
            self.proc.send_signal(signal.SIGINT)  # Tell it to close
            try:
                # Give it the chance to exit gracefully
                self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.proc.kill()  # Kill it if it takes too long
            # If the cloudflared process is running, shut it down.

    def get_user_listening_history(self, spotify_id):
        """Returns the entire listening history of the user with parameter spotify_id"""
        
        print(f"running get history from db {spotify_id}")
        get_listening_history = """
            SELECT
                lh.played_at,
                lh.context,
                t.spotify_track_id AS track_id,
                t.name AS track_name,
                t.song_img_url,
                ARRAY_AGG(a.name ORDER BY a.name) AS artist_names,
                ARRAY_AGG(a.spotify_artist_id ORDER BY a.name) AS artist_ids
            FROM listening_history lh
            JOIN tracks t
                ON lh.track_id = t.spotify_track_id
            JOIN artist_tracks at
                ON t.spotify_track_id = at.track_id
            JOIN artists a
                ON at.artist_id = a.spotify_artist_id
            WHERE lh.spotify_id = %s
            GROUP BY
                lh.played_at,
                lh.context,
                t.spotify_track_id,
                t.name,
                t.song_img_url
            ORDER BY lh.played_at DESC;
        """
        params = (spotify_id,)
        return clean_db_listening_history(self.execute_cmd(get_listening_history, params, fetch=True))

# --- GENRE STUFF ---

    def update_artist_genres(self, spotify_artist_id, genres_list):
        """
        Update the genres array for a specific artist.
        Used by MusicBrainz repair pipeline.
        """

        cmd = """
            UPDATE artists
            SET genres = %s
            WHERE spotify_artist_id = %s;
        """
        params = (genres_list, spotify_artist_id)
        self.execute_cmd(cmd, params, fetch=False)


    def get_artists_missing_genres(self):
        """
        Return all artists whose genres are missing, empty,
        or placeholder ('NO_GENRE_DATA').
        """
        
        cmd = """
            select spotify_artist_id, name
            from artists
            where genres is null
            or genres = '{}'
        """
        return self.execute_cmd(cmd, (), fetch=True)

    def repair_missing_genres(self):
        """
        Finds all artists with empty or placeholder genre lists
        and fills them using MusicBrainz. Warning - Slow
        """

        update_artist_cmd = """
            select spotify_artist_id, name
            from artists
            where genres is null
            or genres = '{}'
        """
        update_artist_rows = []

        # Fetch all artists missing genre data
        artists = self.get_artists_missing_genres()

        # Loop through the artists and attempt MusicBrainz repair
        for spotify_artist_id, artist_name in artists:

            # First try MBID lookup using Spotify ID (most reliable)
            mbid = mb_lookup_by_spotify_id(spotify_artist_id)

            if mbid is not None:
                # Fetch tags using MBID
                genres_by_mbid = mb_get_genres(mbid)

                if len(genres_by_mbid) > 0:
                    update_artist_rows.append((spotify_artist_id, genres_by_mbid))
                    continue

            # Fallback: lookup by artist name
            genres_by_name = mb_lookup_by_name(artist_name)

            if len(genres_by_name) > 0 and not any(obj[0] == spotify_artist_id for obj in update_artist_rows):
                update_artist_rows.append((spotify_artist_id, genres_by_name))

        self.execute_cmd(update_artist_cmd, update_artist_rows)


# --- SONG OF THE DAY FUNCTIONS ---

    def create_song_of_the_day_table(self):
        """
        Create the song_of_the_day table if it doesn't exist.
        This table stores the history of all previously selected songs of the day.
        """
        cmd = """
            CREATE TABLE IF NOT EXISTS song_of_the_day (
                track_id VARCHAR(255) PRIMARY KEY,
                selected_at TIMESTAMP NOT NULL DEFAULT NOW(),
                is_current BOOLEAN NOT NULL DEFAULT TRUE,
                last_updated TIMESTAMP NOT NULL DEFAULT NOW(),
                FOREIGN KEY (track_id) REFERENCES tracks(spotify_track_id)
            );
        """
        try:
            self.execute_cmd(cmd, (), fetch=False)
        except Exception as e:
            print(f"Error creating song_of_the_day table: {e}")
            raise e

    def get_all_unique_tracks(self):
        """
        Get all unique tracks from all users' listening histories.
        Returns list of unique tracks with full track info.
        """
        # Use a CTE to first get unique (track, artist) pairs, then aggregate.
        cmd = """
            WITH unique_track_artists AS (
                SELECT DISTINCT
                    t.spotify_track_id,
                    t.name AS track_name,
                    t.song_img_url,
                    t.album_name,
                    a.name AS artist_name,
                    a.spotify_artist_id AS artist_id
                FROM listening_history lh
                JOIN tracks t ON lh.track_id = t.spotify_track_id
                JOIN artist_tracks at ON t.spotify_track_id = at.track_id
                JOIN artists a ON at.artist_id = a.spotify_artist_id
            )
            SELECT
                spotify_track_id AS track_id,
                track_name,
                song_img_url,
                album_name,
                ARRAY_AGG(artist_name ORDER BY artist_name) AS artist_names,
                ARRAY_AGG(artist_id ORDER BY artist_name) AS artist_ids
            FROM unique_track_artists
            GROUP BY
                spotify_track_id,
                track_name,
                song_img_url,
                album_name
            ORDER BY track_name;
        """
        return self.execute_cmd(cmd, (), fetch=True)

    def get_current_song_of_the_day(self):
        """
        Get the current song of the day with full track information.
        Returns None if no current song exists.
        """
        # Ensure table exists
        self.create_song_of_the_day_table()
        
        # Use CTE to deduplicate artists before aggregation
        cmd = """
            WITH current_track_artists AS (
                SELECT DISTINCT
                    t.spotify_track_id,
                    t.name AS track_name,
                    t.song_img_url,
                    t.album_name,
                    sotd.selected_at,
                    a.name AS artist_name,
                    a.spotify_artist_id AS artist_id
                FROM song_of_the_day sotd
                JOIN tracks t ON sotd.track_id = t.spotify_track_id
                JOIN artist_tracks at ON t.spotify_track_id = at.track_id
                JOIN artists a ON at.artist_id = a.spotify_artist_id
                WHERE sotd.is_current = TRUE
            )
            SELECT
                spotify_track_id AS track_id,
                track_name,
                song_img_url,
                album_name,
                ARRAY_AGG(artist_name ORDER BY artist_name) AS artist_names,
                ARRAY_AGG(artist_id ORDER BY artist_name) AS artist_ids,
                selected_at
            FROM current_track_artists
            GROUP BY
                spotify_track_id,
                track_name,
                song_img_url,
                album_name,
                selected_at
            LIMIT 1;
        """
        result = self.execute_cmd(cmd, (), fetch=True)
        if result and len(result) > 0:
            return result[0]
        return None

    def get_all_previously_selected_track_ids(self):
        """
        Get all track IDs that have been selected as song of the day before.
        Returns a set of track IDs.
        """
        # Ensure table exists
        self.create_song_of_the_day_table()
        
        cmd = """
            SELECT DISTINCT track_id
            FROM song_of_the_day;
        """
        result = self.execute_cmd(cmd, (), fetch=True)
        return {row[0] for row in result} if result else set()

    def update_song_of_the_day(self, track_id):
        """
        Update the song of the day table with a new track.
        Deactivates all previous current songs and sets the new one as current.
        """
        # Ensure table exists
        self.create_song_of_the_day_table()
        
        # First, deactivate all current songs
        deactivate_cmd = """
            UPDATE song_of_the_day
            SET is_current = FALSE
            WHERE is_current = TRUE;
        """
        self.execute_cmd(deactivate_cmd, (), fetch=False)
        
        # Then insert or update the new song
        insert_cmd = """
            INSERT INTO song_of_the_day (track_id, selected_at, is_current, last_updated)
            VALUES (%s, NOW(), TRUE, NOW())
            ON CONFLICT (track_id)
            DO UPDATE SET
                selected_at = NOW(),
                is_current = TRUE,
                last_updated = NOW();
        """
        self.execute_cmd(insert_cmd, (track_id,), fetch=False)

    def clear_song_of_the_day_history(self):
        """
        Clear all entries from the song_of_the_day table.
        Called when all unique songs have been selected to restart the cycle.
        """
        # Ensure table exists
        self.create_song_of_the_day_table()
        
        cmd = """
            DELETE FROM song_of_the_day;
        """
        self.execute_cmd(cmd, (), fetch=False)

    def should_refresh_song_of_the_day(self):
        """
        Check if the song of the day should be refreshed.
        Returns True if:
        - No current song exists, OR
        - Current song was selected more than 24 hours ago
        """
        # Ensure table exists
        self.create_song_of_the_day_table()
        
        current_song = self.get_current_song_of_the_day()
        
        # If no current song exists, we need to refresh
        if current_song is None:
            return True
        
        # Check if the current song is older than 24 hours
        cmd = """
            SELECT selected_at
            FROM song_of_the_day
            WHERE is_current = TRUE
            LIMIT 1;
        """
        result = self.execute_cmd(cmd, (), fetch=True)
        
        if result and len(result) > 0:
            selected_at = result[0][0]
            # Check if selected_at is more than 24 hours ago
            check_cmd = """
                SELECT selected_at < NOW() - INTERVAL '24 hours'
                FROM song_of_the_day
                WHERE is_current = TRUE
                LIMIT 1;
            """
            refresh_result = self.execute_cmd(check_cmd, (), fetch=True)
            if refresh_result and len(refresh_result) > 0:
                return refresh_result[0][0]
        
        return False


