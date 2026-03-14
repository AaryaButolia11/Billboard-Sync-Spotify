
#importing modules 
from bs4 import BeautifulSoup  #Parse HTML from Billboard website
import requests #Send HTTP request to Billboard
import spotipy #Python wrapper for Spotify API
from spotipy.oauth2 import SpotifyOAuth #Handle Spotify authentication
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
response = requests.get(url=billboard_url, headers=header) #Billboard Hot 100 chart page for that date.
soup = BeautifulSoup(response.text, 'html.parser')
song_names_spans = soup.select("li ul li h3") #This extracts song titles from the webpage. soup.select() uses CSS selectors.
This targets the song title elements on Billboard page.
song_names = [song.getText().strip() for song in song_names_spans]

# Spotify Authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(  # This logs you into Spotify using OAuth.
        redirect_uri=REDIRECT_URI,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scope=SCOPE,
        cache_path=r"C:\Users\Arya\100 Days of Python Programming\billboard-spotify\.cache-spotify",  #This stores the authentication token locally so you don't need to login every time.
        show_dialog=False
    )
)

user_id = sp.current_user()["id"]  #This fetches your Spotify account ID.
print(f"Logged in as: {user_id}")

# Search for songs
song_uris = []
year = date.split("-")[0]   #Extracts the year from the input date.
for song in song_names:
    result = sp.search(q=f"track:{song} year:{year}", type="track")  #searcheed as -> track:song:year -> improved accuracy
    try: 
        uri = result["tracks"]["items"][0]["uri"]  #Spotify tracks are identified by URI.
        song_uris.append(uri)  #These URIs will be added to the playlist.
    except IndexError:
        print(f"{song} not found on Spotify. Skipping.")   #If Spotify can't find the song, it skips it.

# Create playlist
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False) #This creates a new Spotify playlist.
# public=False means private playlist.
print(f"Created playlist: {playlist['name']}") 

# Add tracks
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris) #This adds all the songs to the playlist.
print("Playlist populated with songs.")
