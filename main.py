
#importing modules 
from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os


#get secret keys from os
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "playlist-modify-private playlist-read-private"

# Ask for date
while True:
    date = input("Enter a date (YYYY-MM-DD) to create a Billboard 100 playlist: ").strip()
    if len(date) == 10 and date[4] == '-' and date[7] == '-':
        break
    print("Invalid format! Please use YYYY-MM-DD.")

# Scrape Billboard
header = {"User-Agent": "Mozilla/5.0"}
billboard_url = "https://www.billboard.com/charts/hot-100/" + date
response = requests.get(url=billboard_url, headers=header)
soup = BeautifulSoup(response.text, 'html.parser')
song_names_spans = soup.select("li ul li h3")
song_names = [song.getText().strip() for song in song_names_spans]

# Spotify Authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        redirect_uri=REDIRECT_URI,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scope=SCOPE,
        cache_path=r"C:\Users\Arya\100 Days of Python Programming\billboard-spotify\.cache-spotify",  # Updated cache
        show_dialog=False
    )
)

user_id = sp.current_user()["id"]
print(f"Logged in as: {user_id}")

# Search for songs
song_uris = []
year = date.split("-")[0]
for song in song_names:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} not found on Spotify. Skipping.")

# Create playlist
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
print(f"Created playlist: {playlist['name']}")

# Add tracks
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
print("Playlist populated with songs.")
