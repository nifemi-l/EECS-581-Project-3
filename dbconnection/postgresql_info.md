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

                                    Table "public.users"
      Column       |  Type   | Collation | Nullable |                Default
-------------------+---------+-----------+----------+----------------------------------------
 user_id           | integer |           | not null | nextval('users_user_id_seq'::regclass)
 spotify_id        | text    |           | not null |
 user_name         | text    |           |          |
 profile_image_url | text    |           |          |
 access_token      | text    |           |          |
 refresh_token     | text    |           |          |
 diversity_score   | numeric |           |          |
Indexes:
    "users_pkey" PRIMARY KEY, btree (user_id)
    "users_spotify_id_key" UNIQUE CONSTRAINT, btree (spotify_id)
Referenced by:
    TABLE "listening_history" CONSTRAINT "fk_listening_history_user" FOREIGN KEY (spotify_id) REFERENCES users(spotify_id) ON UPDATE CASCADE ON DELETE CASCADE
    TABLE "user_metrics" CONSTRAINT "user_metrics_spotify_id_fkey" FOREIGN KEY (spotify_id) REFERENCES users(spotify_id) ON DELETE CASCADE
    TABLE "user_metrics" CONSTRAINT "user_metrics_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE

### Table: Artists

                                     Table "public.artists"
      Column       |  Type   | Collation | Nullable |                  Default
-------------------+---------+-----------+----------+--------------------------------------------
 artist_id         | integer |           | not null | nextval('artists_artist_id_seq'::regclass)
 spotify_artist_id | text    |           | not null |
 name              | text    |           | not null |
 genres            | text[]  |           |          | '{}'::text[]
Indexes:
    "artists_pkey" PRIMARY KEY, btree (artist_id)
    "artists_spotify_artist_id_key" UNIQUE CONSTRAINT, btree (spotify_artist_id)
Referenced by:
    TABLE "tracks" CONSTRAINT "fk_artist_spotify_id" FOREIGN KEY (spotify_artist_id) REFERENCES artists(spotify_artist_id) ON DELETE CASCADE

### Table: Tracks

                                     Table "public.tracks"
      Column       |  Type   | Collation | Nullable |                 Default
-------------------+---------+-----------+----------+------------------------------------------
 track_id          | integer |           | not null | nextval('tracks_track_id_seq'::regclass)
 spotify_track_id  | text    |           | not null |
 name              | text    |           | not null |
 spotify_artist_id | text    |           |          |
 duration_ms       | integer |           |          |
 album_name        | text    |           |          |
 release_date      | date    |           |          |
 song_img_url      | text    |           |          |
Indexes:
    "tracks_pkey" PRIMARY KEY, btree (track_id)
    "tracks_spotify_track_id_key" UNIQUE CONSTRAINT, btree (spotify_track_id)
Foreign-key constraints:
    "fk_artist_spotify_id" FOREIGN KEY (spotify_artist_id) REFERENCES artists(spotify_artist_id) ON DELETE CASCADE
Referenced by:
    TABLE "listening_history" CONSTRAINT "fk_track_id" FOREIGN KEY (track_id) REFERENCES tracks(spotify_track_id) ON DELETE CASCADE

### Table: Listening History

                                        Table "public.listening_history"
   Column   |            Type             | Collation | Nullable |                    Default
------------+-----------------------------+-----------+----------+-----------------------------------------------
 id         | integer                     |           | not null | nextval('listening_history_id_seq'::regclass)
 spotify_id | text                        |           |          |
 played_at  | timestamp without time zone |           | not null |
 context    | text                        |           |          |
 track_id   | text                        |           |          |
Indexes:
    "listening_history_pkey" PRIMARY KEY, btree (id)
    "unique_track_id" UNIQUE CONSTRAINT, btree (track_id)
Foreign-key constraints:
    "fk_listening_history_user" FOREIGN KEY (spotify_id) REFERENCES users(spotify_id) ON UPDATE CASCADE ON DELETE CASCADE
    "fk_track_id" FOREIGN KEY (track_id) REFERENCES tracks(spotify_track_id) ON DELETE CASCADE

### Table: User Metrics

                          Table "public.user_metrics"
     Column      |            Type             | Collation | Nullable | Default
-----------------+-----------------------------+-----------+----------+---------
 user_id         | integer                     |           | not null |
 spotify_id      | text                        |           |          |
 diversity_score | double precision            |           |          |
 taste_score     | double precision            |           |          |
 last_updated    | timestamp without time zone |           |          | now()
Indexes:
    "user_metrics_pkey" PRIMARY KEY, btree (user_id)
    "user_metrics_spotify_id_key" UNIQUE CONSTRAINT, btree (spotify_id)
Check constraints:
    "user_metrics_diversity_score_check" CHECK (diversity_score >= 0::double precision AND diversity_score <= 1::double precision)
    "user_metrics_taste_score_check" CHECK (taste_score >= 0::double precision AND taste_score <= 1::double precision)
Foreign-key constraints:
    "user_metrics_spotify_id_fkey" FOREIGN KEY (spotify_id) REFERENCES users(spotify_id) ON DELETE CASCADE
    "user_metrics_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
