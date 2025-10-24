# postgresql info

## setup info - on the server
created a postgres user
initialized db in /var/lib/postgres/data

systemd service to open port for db connection:
- cloudflared-db-tcp.service

## using db - inside server
`sudo iu postgres` - switch to correct user
`psql` - initialized psqk

## using db - remotely
1. run `db_listener.py` to start listening for db connection
   - starts a local listener, connected to cloudflare tunnel
   - ensure .env is in the right directory!
2. in another terminal: `psql -h http://127.0.0.1:5432 --username=defaultuser --dbname=spotifydb`                                                                                
    - connects local listener to instance of db at end of cloudflare tunnel
    - default password is `eecs581project3`
