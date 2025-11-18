# Prologue
# Name: DBConnction.py
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
import signal
import subprocess
import time
from contextlib import closing
import os
from icecream import ic
from server_utils import normalize_spotify_date
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
        print(f"Starting Cloudflare proxy on {self.LOCAL_HOST}:{
              self.LOCAL_PORT} → {self.HOSTNAME} ...")

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

    def update_user_history(self, spotify_id, spotify_json: str):
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

        tracks_cmd = """
            INSERT INTO tracks (spotify_track_id, name, spotify_artist_id, duration_ms, album_name, release_date, song_img_url)
            VALUES %s
            ON CONFLICT (spotify_track_id) DO NOTHING;"""

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

            # Add variables for batch artists_tracks update
            for artist in artists:
                artist_id = artist["id"]
                artists_tracks_rows.append((artist_id, track_id))

        self.execute_vals(artists_cmd, artist_rows)
        self.execute_vals(tracks_cmd, tracks_rows)
        self.execute_vals(listening_history_cmd, listening_history_rows)
        self.execute_vals(artists_tracks_cmd, artists_tracks_rows)

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
        get_listening_history = """
        SELECT 
            listening_history.*,
            tracks.*,
            artist_tracks.*,
            artists.*
        FROM listening_history
        JOIN tracks 
            ON listening_history.track_id = tracks.spotify_track_id
        JOIN artist_tracks 
            ON tracks.spotify_track_id = artist_tracks.track_id
        JOIN artists 
            ON artist_tracks.artist_id = artists.spotify_artist_id
        WHERE listening_history.spotify_id = %s;
        """
        params = (spotify_id)
        return self.execute_cmd(get_listening_history, params)

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
