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
def top_songs():
    top_100 = sp.playlist_tracks('0sDahzOkMWOmLXfTMf2N4N', limit=100)
    conn = sqlite3.connect('chart_entries.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Artists (
                        ArtistID INTEGER PRIMARY KEY,
                        ArtistName TEXT UNIQUE
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS TopSongs (
                        SongName TEXT,
                        ArtistIDs TEXT,
                        FOREIGN KEY (ArtistIDs) REFERENCES Artists(ArtistID)
                    )''')

    # Get the count of current entries in the database
    cursor.execute("SELECT COUNT(*) FROM TopSongs")
    current_count = cursor.fetchone()[0]

    # Determine the start and end indices for processing batches of 25
    start_index = current_count
    end_index = min(start_index + 25, len(top_100['items']))

    for i in range(start_index, end_index):
        track = top_100['items'][i]
        song_name = track['track']['name']
        #artists = ', '.join([artist['name'] for artist in track['track']['artists']])
        artists = [artist['name'] for artist in track['track']['artists']]
        
        #store artist IDs for each artist
        artist_ids= []
        for artist_name in artists:
            cursor.execute("SELECT ArtistID FROM Artists WHERE ArtistName= ?", (artist_name,))
            existing_artist=cursor.fetchone()
            if existing_artist:
                artist_id= existing_artist[0]
            else:
                cursor.execute("INSERT INTO Artists (ArtistName) VALUES (?)", (artist_name,))
                artist_id= cursor.lastrowid
            artist_ids.append(str(artist_id))
        artist_ids_str= ','.join(artist_ids)
        cursor.execute("SELECT * FROM TopSongs WHERE SongName = ?", (song_name,))
        existing_entry= cursor.fetchone()
        if existing_entry is None:
            cursor.execute("INSERT OR IGNORE INTO TopSongs (SongName, ArtistIDs) VALUES (?, ?)", (song_name, artist_ids_str))
    conn.commit()
    conn.close()  

    #     # Check if the entry already exists
    #     cursor.execute("SELECT * FROM TopSongs WHERE SongName = ? AND Artists = ?", (song_name, artists))
    #     existing_entry = cursor.fetchone()

    #     if existing_entry is None:
    #         cursor.execute("INSERT OR IGNORE INTO TopSongs (SongName, Artists) VALUES (?, ?)", (song_name, artists))

    
    
    
    # cursor.execute('''CREATE TABLE IF NOT EXISTS AritstID (
    #                     Arists TEXT,
    #                     ID INTEGER,
    #                     UNIQUE (Artists, ID)
    #                 )''')

# Retrieve data for artist appearances, and top performing artists from the database
def artist_appearances():
    conn = sqlite3.connect('chart_entries.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ArtistIDs, COUNT(*) AS Appearances FROM TopSongs GROUP BY ArtistIDs")
    artist_data = cursor.fetchall()
    artist_count = {}
    for artists_str in artist_data:
        artists = artists_str[0].split(',')
        for artist in artists:
            if artist in artist_count:
                artist_count[artist] += 1
            else:
                artist_count[artist] = 1
    top_artists = {artist: count for artist, count in artist_count.items() if count > 1}
    conn.close()
    print(artist_count)
    print(top_artists)
    return artist_count, top_artists

def top_artists_vis(top_artists):
    conn = sqlite3.connect('chart_entries.db')
    cursor = conn.cursor()
    artist_names = {}
    for artist_id in top_artists.keys():
        cursor.execute("SELECT ArtistName FROM Artists WHERE ArtistID = ?", (artist_id,))
        artist_name = cursor.fetchone()
        if artist_name:
            artist_names[artist_name[0]] = top_artists[artist_id]
    conn.close()
    
    plt.figure(figsize=(10, 6))
    plt.bar(artist_names.keys(), artist_names.values(), color='skyblue')
    plt.xlabel('Artists')
    plt.ylabel('Number of Appearances')
    plt.title('Top Performing Artists')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def text_file(artist_count, top_artists, file_name):
    conn = sqlite3.connect('chart_entries.db')
    cursor = conn.cursor()
    top_artist_names = {}
    artist_names = {}
    for artist_id in top_artists.keys():
        cursor.execute("SELECT ArtistName FROM Artists WHERE ArtistID = ?", (artist_id,))
        artist_name = cursor.fetchone()
        if artist_name:
            top_artist_names[artist_name[0]] = top_artists[artist_id]
    for artist_id in artist_count.keys():
        cursor.execute("SELECT ArtistName FROM Artists WHERE ArtistID = ?", (artist_id,))
        artist_name = cursor.fetchone()
        if artist_name:
            artist_names[artist_name[0]] = artist_count[artist_id]
    conn.close()
    
    with open(file_name, 'w') as file:
        file.write("Artist Count:\n")
        for artist, count in artist_names.items():
            file.write(f"{artist}: {count}\n")
        
        file.write("\nTop Performing Artists:\n")
        for artist, count in top_artist_names.items():
            file.write(f"{artist}: {count}\n")


def main():
    top_songs()
    artist_count, top_artists = artist_appearances()
    top_artists_vis(top_artists)
    text_file(artist_count, top_artists, 'artist_counts.txt')
    
    

if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)