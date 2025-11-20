# Prologue
# Name: oBConnction.py
# Description: Open a connection to our application's PostgreSQL database
# Programmer: Dellie Wright
# Dates: 11/17/25
# Revisions: 1.2
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
import time

import psycopg2
from psycopg2 import Error, sql
from psycopg2.extras import execute_values


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
        self.HOSTNAME = "581db.d3llie.tech"
        self.LOCAL_HOST = "127.0.0.1"
        self.LOCAL_PORT = 54321
        self.DB_NAME = "spotifydb"

        # Set a timeout value for external connections
        self.STARTUP_TIMEOUT = 20

        # The command that will be used to connect to the database through the cloudflare tunnel
        self.cloudflared_cmd = [
            "cloudflared", "access", "tcp",
            "--hostname", self.HOSTNAME,
            "--url", f"{self.LOCAL_HOST}:{self.LOCAL_PORT}",
            "--service-token-id", self.SERVICE_TOKEN_ID,
            "--service-token-secret", self.SERVICE_TOKEN_SECRET,
        ]

        # Output status information
        print(f"Starting Cloudflare proxy on {self.LOCAL_HOST}:{self.LOCAL_PORT} → {self.HOSTNAME} ...")

        # Make the actual subprocess to handle our connection
        self.proc = subprocess.Popen(
            self.cloudflared_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Wait briefly for the tunnel to come up
        time.sleep(0.5)

        if self.proc.poll() is not None:
            stderr = self.proc.stderr.read()
            raise RuntimeError(f"cloudflared exited early:\n{stderr}")

        # The main connection initialization block
        try:

            # Establish a connection to the PostgreSQL database
            self.conn = psycopg2.connect(
                host=self.LOCAL_HOST, port=self.LOCAL_PORT,
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
                    ic(result)
                self.conn.commit()
                # print(f"successfully executed command:\n\t{command}\nWith result:\n\t{result}")
                return result
        except psycopg2.ProgrammingError as e:
            self.conn.commit()
            # print(f"Failed to execute command:\n\t{command}\nWith error:\n\t{e}")
            raise e

    def add_user(self, user_info_json: str, access_token: str, refresh_token: str):
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
        cmd = f"""SELECT t.spotify_id, t.user_name, t.profile_image_url
        FROM users us
        WHERE us.user_id = %s
        ;"""
        params = (user_id)
        return self.execute_cmd(cmd, params)

    def get_user_history(self, user_id, limit=25):
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
        cmd = """
            SELECT a.genres
            FROM listening_history lh
            JOIN tracks t ON lh.track_id = t.spotify_track_id
            JOIN artists a ON t.spotify_artist_id = a.spotify_artist_id
            WHERE lh.spotify_id = %s
        """
        params = (spotify_id,)
        return self.execute_cmd(cmd, params, fetch=True)
    
    def get_artists_missing_genres(self):
        cmd = """
            SELECT spotify_artist_id
            FROM artists
            WHERE genres IS NULL OR array_length(genres, 1) = 0
        """
        return [row[0] for row in self.execute_cmd(cmd, (), fetch=True)]
    
    def refresh_missing_genres(self, access_token: str):
        missing_ids = self.get_artists_missing_genres()

        if not missing_ids:
            print("No missing genres to refresh.")
            return

        print(f"Refreshing genres for {len(missing_ids)} artists")

        headers = {"Authorization": f"Bearer {access_token}"}

        rows = []
        for a_id in missing_ids:
            url = f"https://api.spotify.com/v1/artists/{a_id}"
            try:
                r = requests.get(url, headers=headers)
                if r.status_code == 200:
                    genres = r.json().get("genres", [])
                else:
                    genres = []
            except:
                genres = []

            rows.append((a_id, genres))

        # batch update
        artist_genre_cmd = """
            UPDATE artists 
            SET genres = data.genres
            FROM (VALUES %s) AS data(spotify_artist_id, genres)
            WHERE artists.spotify_artist_id = data.spotify_artist_id
            AND (
                    artists.genres IS NULL 
                    OR array_length(artists.genres, 1) = 0
                );
        """

        self.execute_vals(artist_genre_cmd, rows)
        print("Finished refreshing missing genres.")
    
    def get_many_user_profiles(self, limit=25):
        cmd = """SELECT user_name, profile_image_url 
                FROM users
                LIMIT %s;"""
        params = [limit]
        return self.execute_cmd(cmd, params, fetch=True)

    def update_user_history(self, spotify_id, spotify_json: str, access_token: str):
        # based on endpoint: https://developer.spotify.com/documentation/web-api/reference/get-recently-played
        print("upating history")
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
            ON CONFLICT (track_id) DO NOTHING;
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
            

        unique_artist_ids = {artist_id for (artist_id, _) in artist_rows}
        artist_genre_rows = []

        headers = {"Authorization": f"Bearer {access_token}"}

        for a_id in unique_artist_ids:
            url = f"https://api.spotify.com/v1/artists/{a_id}"

            try:
                r = requests.get(url, headers=headers)
                if r.status_code == 200:
                    genres = r.json().get("genres", [])
                else:
                    genres = []
            except:
                genres = []

            artist_genre_rows.append((a_id, genres))

            # Add variables for batch artists_tracks update

        ic(self.execute_vals(artists_cmd, artist_rows))
        ic(self.execute_vals(tracks_cmd, tracks_rows))
        ic(self.execute_vals(listening_history_cmd, listening_history_rows))
        ic(self.execute_vals(artists_tracks_cmd, artists_tracks_rows))
        ic(self.execute_vals(artist_genre_cmd, artist_genre_rows))

    def killCloudflare(self):
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

    def get_all_listening_history(self):
        get_listening_history = "SELECT context, tracks.name FROM listening_history JOIN tracks ON listening_history.track_id = tracks.track_id"
        return self.execute_cmd(get_listening_history, ())

    def get_user_id_from_spotify_id(self, spotify_id):
        cmd = "SELECT user_id FROM users WHERE spotify_id = %s"
        params = (spotify_id)
        user_id = self.execute_cmd(cmd, params)
        if user_id == []:
            raise Error("User is not present in database")
        else:
            return user_id

    def update_track_artists(self):
        cmd = """
        SELECT
    lh.track_id AS track_id,
    t.spotify_artist_id AS artist_id
FROM listening_history lh
JOIN tracks t
    ON lh.track_id = t.spotify_track_id;"""
        print(cmd)

        res = ic(self.execute_cmd(cmd, (), True))
        print(res)

        cmd2 = """
            INSERT INTO artist_tracks (track_id, artist_id)
            VALUES %s;
        """

        self.execute_vals(cmd2, res)

    def debug_full_genre_listing(self, spotify_id):
        cmd = """
            SELECT 
                t.name AS track_name,
                a.name AS artist_name,
                a.genres
            FROM listening_history lh
            JOIN tracks t ON lh.track_id = t.spotify_track_id
            JOIN artists a ON t.spotify_artist_id = a.spotify_artist_id
            WHERE lh.spotify_id = %s
            ORDER BY lh.played_at DESC;
        """
        rows = self.execute_cmd(cmd, (spotify_id,), fetch=True)
        count = 0

        output = "=== USER GENRE DEBUG ===\n"
        for track_name, artist_name, genres in rows:
            output += f"{count}. {artist_name} - {track_name} → {genres}\n"
            count += 1

        return output
