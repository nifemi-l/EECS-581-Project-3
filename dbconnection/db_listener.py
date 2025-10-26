# Prologue
# Name: db_listener.py
# Description: Open a connection to our application's PostgreSQL database
# Programmer: Dellie Wright
# Dates: 10/24/25
# Revisions: 1.0
# Pre/post conditions
#   - Pre: None. 
#   - Post: After execution, the connection to the database will be closed.
# Errors: All known errors should be handled gracefully. 

# Import needed libraries
import os
from dotenv import dotenv_values
import re
import shlex
import signal
import subprocess
import sys
import time
from contextlib import closing
import os, signal, socket, subprocess, sys, time

import psycopg2
from psycopg2 import sql

# Read secure config keys / values from a .env file that is not included with git
config = dotenv_values(".env")
print(config) # Display which config we're using
SERVICE_TOKEN_ID = config["SERVICE_TOKEN_ID"]
SERVICE_TOKEN_SECRET = config["SERVICE_TOKEN_SECRET"]
DB_PASSWORD = config["DB_PASSWORD"]

# Set other needed config parameters
HOSTNAME = "581db.d3llie.tech" 
LOCAL_HOST = "127.0.0.1"
LOCAL_PORT = 5432             
DB_USER = "dellie"
DB_NAME = "spotifydb"

# Set a timeout value for external connections
STARTUP_TIMEOUT = 20

# The command that will be used to connect to the database through the cloudflare tunnel
cmd = [
    "cloudflared", "access", "tcp",
    "--hostname", HOSTNAME,
    "--url", f"{LOCAL_HOST}:{LOCAL_PORT}",
    "--service-token-id", SERVICE_TOKEN_ID,
    "--service-token-secret", SERVICE_TOKEN_SECRET,
]

def wait_for_port(host, port, timeout=20):
    """Open a socket connection to a host on a specific port. Timeout on set timeout value."""
    start = time.time() # Retrieve start time
    while time.time() - start < timeout: # Until we timeout
        with socket.socket() as s: # Open the socket
            s.settimeout(1.0) # For this attempt, set a 1s timeout (note that this is different than the timeout parameter)
            try:
                # Attempt a connection. If we succeed, return true
                s.connect((host, port)) 
                return True
            except OSError:
                time.sleep(0.3) # If an OSError occurs (i.e. a resource is in use), try again after 300 ms
    return False # On failure, return false

# Output status information
print(f"Starting Cloudflare proxy on {LOCAL_HOST}:{LOCAL_PORT} → {HOSTNAME} ...")

# Make the actual subprocess to handle our connection
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# The main connection initialization block
try:
    start = time.time()
    while time.time() - start < 2:
        # Get cloudflared process info and print output to stdout with an identifying tag
        line = proc.stdout.readline()
        if not line:
            break
        print("[cloudflared]", line.rstrip(), file=sys.stderr)

    # If the cloudflared process is not running (has exited), raise an error
    if proc.poll() is not None:
        raise RuntimeError("cloudflared exited early. Check token, hostname, and Access policy.")

    # Attempt to open a socket to the host and port for the database. If the socket fails, raise an error
    if not wait_for_port(LOCAL_HOST, LOCAL_PORT, timeout=20):
        raise RuntimeError(f"Timed out waiting for {LOCAL_HOST}:{LOCAL_PORT} to open.")

    # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(
        host=LOCAL_HOST, port=LOCAL_PORT,
        user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME,
        connect_timeout=10,
    )
    with conn, conn.cursor() as cur: 
        cur.execute("SELECT now();") # Execute a SQL command to return the current time
        print("DB Time:", cur.fetchone()[0]) # Output that time, proving the connection is established

# Regardless of success or failure in making the connection...
finally:
    print("Stopping Cloudflare proxy...")
    # If the cloudflared process is running, shut it down.
    if proc.poll() is None:
        proc.send_signal(signal.SIGINT) # Tell it to close
        try:
            proc.wait(timeout=3) # Give it the chance to exit gracefully
        except subprocess.TimeoutExpired:
            proc.kill() # Kill it if it takes too long
    # This ensures that we will never leave a process running (ensuring the post-condition)