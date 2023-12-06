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

def top_songs():
    top_100 = sp.playlist_tracks('37i9dQZEVXbMDoHDwVN2tF', limit=50)
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS TopSongs (
                        SongName TEXT,
                        Artists TEXT,
                        UNIQUE (SongName, Artists)
                    )''')
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()
    for track in top_100['items']:
        song_name = track['track']['name']
        artists = ', '.join([artist['name'] for artist in track['track']['artists']])
        cursor.execute("INSERT INTO TopSongs (SongName, Artists) VALUES (?, ?)", (song_name, artists))
    conn.commit()
    conn.close()
        
        
    
def artist_appearances(connection, table_name):
    cursor = connection.cursor()

    # Retrieve data for artist appearances from the database
    cursor.execute(f"SELECT Artists, COUNT(*) AS Appearances FROM {table_name} GROUP BY Artists")
    artist_data = cursor.fetchall()

    return artist_data

def plot_artist_comparison(artist, spotify_appearances, apple_appearances):
    # Plotting comparison between Spotify and Apple Music appearances
    labels = ['Spotify', 'Apple Music']
    values = [spotify_appearances.get(artist, 0), apple_appearances.get(artist, 0)]

    plt.bar(labels, values, color=['green', 'blue'])
    plt.title(f"Artist Appearances: {artist}")
    plt.xlabel('Platform')
    plt.ylabel('Number of Appearances')
    plt.show()
    

def main():
    top_songs()

if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)