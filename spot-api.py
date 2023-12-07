#import spotipy API to access Spotify content
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#othe imports
import sys
import sqlite3
import json
import os
import matplotlib.pyplot as plt
import unittest

#STEP 1: access spotify using credentials below

client_id="bca2c2e8e6d94866aff803ac08baf51f"
client_secret="c8e5cf89332e4040b2ab70c1b47d9ded"
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


#STEP 2: Create Database in local environment
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

#STEP 3: Create table for top songs with song and artist information
def top_songs():
    top_100 = sp.playlist_tracks('0sDahzOkMWOmLXfTMf2N4N', limit=100)
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS TopSongs (
                        SongName TEXT,
                        Artists TEXT,
                        UNIQUE (SongName, Artists)
                    )''')
    for track in top_100['items']:
        song_name = track['track']['name']
        artists = ', '.join([artist['name'] for artist in track['track']['artists']])

        # Check if the entry already exists
        cursor.execute("SELECT * FROM TopSongs WHERE SongName = ? AND Artists = ?", (song_name, artists))
        existing_entry = cursor.fetchone()

        if existing_entry is None:
            cursor.execute("INSERT INTO TopSongs (SongName, Artists) VALUES (?, ?)", (song_name, artists))

    conn.commit()
    conn.close()

# Retrieve data for artist appearances, and top performing artists from the database
def artist_appearances():
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Artists, COUNT(*) AS Appearances FROM TopSongs GROUP BY Artists")
    artist_data = cursor.fetchall()
    artist_count = {}
    for artists_str in artist_data:
        artists = artists_str[0].split(', ')
        for artist in artists:
            if artist in artist_count:
                artist_count[artist] += 1
            else:
                artist_count[artist] = 1
    top_artists = {artist: count for artist, count in artist_count.items() if count > 1}
    conn.close()
    print(artist_count)
    print(top_artists)
    plt.figure(figsize=(10, 6))
    plt.bar(top_artists.keys(), top_artists.values(), color='skyblue')
    plt.xlabel('Artists')
    plt.ylabel('Number of Appearances')
    plt.title('Top Performing Artists')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()  # Adjusts subplot parameters to give specified padding
    plt.show()
    return artist_count, top_artists



def main():
    top_songs()
    artist_appearances()
    
    

if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)