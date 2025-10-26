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

config = dotenv_values(".env")
HOSTNAME = "581db.d3llie.tech"        

print(config)
SERVICE_TOKEN_ID = config["SERVICE_TOKEN_ID"]
SERVICE_TOKEN_SECRET = config["SERVICE_TOKEN_SECRET"]


HOSTNAME = "581db.d3llie.tech" 
LOCAL_HOST = "127.0.0.1"
LOCAL_PORT = 5432             
DB_USER = "dellie"
DB_NAME = "spotifydb"
DB_PASSWORD = config["DB_PASSWORD"]

STARTUP_TIMEOUT = 20

cmd = [
    "cloudflared", "access", "tcp",
    "--hostname", HOSTNAME,
    "--url", f"{LOCAL_HOST}:{LOCAL_PORT}",
    "--service-token-id", SERVICE_TOKEN_ID,
    "--service-token-secret", SERVICE_TOKEN_SECRET,
]

def wait_for_port(host, port, timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket() as s:
            s.settimeout(1.0)
            try:
                s.connect((host, port))
                return True
            except OSError:
                time.sleep(0.3)
    return False

print(f"Starting Cloudflare proxy on {LOCAL_HOST}:{LOCAL_PORT} → {HOSTNAME} ...")
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

try:
    start = time.time()
    while time.time() - start < 2:
        line = proc.stdout.readline()
        if not line:
            break
        print("[cloudflared]", line.rstrip(), file=sys.stderr)

    if proc.poll() is not None:
        raise RuntimeError("cloudflared exited early. Check token, hostname, and Access policy.")

    if not wait_for_port(LOCAL_HOST, LOCAL_PORT, timeout=20):
        raise RuntimeError(f"Timed out waiting for {LOCAL_HOST}:{LOCAL_PORT} to open.")

    conn = psycopg2.connect(
        host=LOCAL_HOST, port=LOCAL_PORT,
        user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME,
        connect_timeout=10,
    )
    with conn, conn.cursor() as cur:
        cur.execute("SELECT now();")
        print("DB Time:", cur.fetchone()[0])

finally:
    print("Stopping Cloudflare proxy...")
    if proc.poll() is None:
        proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
