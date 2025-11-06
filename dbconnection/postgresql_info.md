# postgresql info

## setup info - on the server
created a postgres user
initialized db in /var/lib/postgres/data

systemd service to open port for db connection:


## using db - inside server
`sudo -iu postgres` - switch to correct user
`psql` - initialized psqk

## using db - remotely
1. run `db_listener.py` to start listening for db connection
   - starts a local listener, connected to cloudflare tunnel
   - ensure .env is in the right directory!
2. in another terminal: `psql -h http://127.0.0.1:5432 --username=defaultuser --dbname=spotifydb`                                                                                
    - connects local listener to instance of db at end of cloudflare tunnel
    - default password is `eecs581project3`

## DB - setup

### Table: Users
users (
    user_id SERIAL primary key, 
    spotify_id text unique not null,
    user_name text,
    profile_image_url text,
    access_token text,
    refresh_token text,
    diversity_score decimal
) 

### Table: Artists
artists (
    artist_id SERIAL PRIMARY KEY,
    spotify_artist_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    genres TEXT[] DEFAULT '{}'
);


### Table: Tracks
tracks (
    track_id SERIAL PRIMARY KEY,
    spotify_track_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    artist_id INT REFERENCES artists(artist_id) ON DELETE CASCADE,
    duration_ms INT,
    album_name TEXT,
    release_date DATE,
    song_img_url TEXT,
    
);

### Table: Listening History
listening_history (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    track_id INT REFERENCES tracks(track_id) ON DELETE CASCADE,
    played_at TIMESTAMP NOT NULL,
    context TEXT,
    UNIQUE (user_id, track_id, played_at)
);

### Table: User Metrics
user_metrics (
    user_id INT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    diversity_score FLOAT CHECK (diversity_score BETWEEN 0 AND 1),
    taste_score FLOAT CHECK (taste_score BETWEEN 0 AND 1),
    last_updated TIMESTAMP DEFAULT NOW()
);

