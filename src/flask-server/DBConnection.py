# Prologue
# Name: DBConnction.py
# Description: Open a connection to our application's PostgreSQL database
# Programmer: Dellie Wright
# Dates: 10/24/25
# Revisions: 1.0
# Pre/post conditions
#   - Pre: Port 54321 must not be in use by any other processes.
#   - Post: After execution, the connection to the database will be accessible via the DBConnection.sql_cursor object.
# Errors: All known errors should be handled gracefully.

# Import needed libraries
import os
from flask import Flask, redirect, request, jsonify, session
import json
from dotenv import dotenv_values
import signal
import subprocess
import time
from contextlib import closing
import os
import signal
import socket
import subprocess
import sys
import time

import psycopg2
from psycopg2 import sql


class DBConnection:
    def __init__(self):

        # Read secure config keys / values from a .env file that is not included with git
        config = dotenv_values(".env")
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
            print("Established connection!")
        except Exception as e:
            print(
                f"Failed to establish SQL connection!\nFailed with exception: {e}")
            if self.proc.poll() is None:
                self.proc.send_signal(signal.SIGINT)  # Tell it to close
                try:
                    # Give it the chance to exit gracefully
                    self.proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.proc.kill()  # Kill it if it takes too long

    def execute_cmd(self, command):
        with self.conn.cursor() as cur:
            cur.execute(command)
            try:
                result = cur.fetchall()
                self.conn.commit()
                return result
            except psycopg2.ProgrammingError:
                self.conn.commit()
                return []

    def add_user(self, user_info_json: str, access_token: str, refresh_token: str):
        # based on endpoint: https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile
        user_info = json.loads(user_info_json)
        spotify_id = user_info['id']
        user_name = user_info['display_name']
        profile_image_url = user_info['images'][0]['url']
        command = f'''INSERT INTO users ({spotify_id}, {user_name}, {access_token}, {refresh_token}) 
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (spotify_id)
            DO UPDATE SET access_token = EXCLUDED.access_token,
                refresh_token = EXCLUDED.refresh_token,
                token_expires_at = EXCLUDED.token_expires_at,
                updated_at = NOW();'''

        self.execute_cmd(command)

    def get_user_profile(self, user_id):
        cmd = f"""SELECT t.spotify_id, t.user_name, t.profile_image_url
        FROM users us
        WHERE us.user_id = {user_id}
        ;"""

    def get_user_history(self, user_id, limit=25):
        cmd = f"""SELECT t.name, a.name AS artist, lh.played_at
FROM listening_history lh
JOIN tracks t ON lh.track_id = t.track_id
JOIN artists a ON t.artist_id = a.artist_id
WHERE lh.user_id = {user_id}
ORDER BY lh.played_at DESC
LIMIT {limit};
"""

    def update_user_history(self, user_id, spotify_json: str):
        # based on endpoint: https://developer.spotify.com/documentation/web-api/reference/get-recently-played
        spotify_data = json.loads(spotify_json)
        for item in spotify_data["items"]:
            track = item["track"]
            played_at = item["played_at"]
            album = track["album"]
            artist = track["artists"][0]  # just the first artist for now

            artist_id = None
            track_id = None

            # Ensure artist exists
            self.execute_cmd(f"""
                INSERT INTO artists (spotify_artist_id, name)
                VALUES ('{artist["id"].replace("'", "''")}', '{artist["name"].replace("'", "''")}')
                ON CONFLICT (spotify_artist_id) DO NOTHING;
            """)

            artist_id_result = self.execute_cmd(
                f"SELECT artist_id FROM artists WHERE spotify_artist_id = '{artist['id'].replace("'", "''")}';"
            )
            artist_id = artist_id_result[0][0]

            # Insert into tracks

            track_name = track["name"].replace("'", "''")
            album_name = album["name"].replace("'", "''")
            release_date = album.get("release_date", None)
            duration_ms = track.get("duration_ms", "NULL")

            self.execute_cmd(f"""
                INSERT INTO tracks (spotify_track_id, name, artist_id, duration_ms, album_name, release_date)
                VALUES ('{track["id"].replace("'", "''")}', '{track_name}', {artist_id},
                        {duration_ms if duration_ms else "NULL"},
                        '{album_name}', {f"'{release_date}'" if release_date else "NULL"})
                ON CONFLICT (spotify_track_id) DO NOTHING;
            """)

            track_id_result = self.execute_cmd(
                f"SELECT track_id FROM tracks WHERE spotify_track_id = '{track['id'].replace("'", "''")}';"
            )
            track_id = track_id_result[0][0]

            # Insert into listening_history
            context = item["context"]["type"].replace("'", "''") if item.get("context") else None
            self.execute_cmd(f"""
                INSERT INTO listening_history (user_id, track_id, played_at, context)
                VALUES (
                    {user_id},
                    {track_id},
                    '{played_at}',
                    {f"'{context}'" if context else "NULL"}
                )
                ON CONFLICT DO NOTHING;
            """)


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


sql_Cursor = DBConnection()
