from setlist_client import SetlistFMClient
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Replace 'YOUR_API_KEY' with your actual setlist.fm API key or set it as an environment variable
API_KEY = os.environ.get("SETLISTFM_API_KEY", "YOUR_API_KEY")

if API_KEY == "YOUR_API_KEY":
    print("Warning: Please set your setlist.fm API key in the SETLISTFM_API_KEY environment variable or replace 'YOUR_API_KEY'.")

client = SetlistFMClient(api_key=API_KEY)



# Example: Search for setlists for 'Muse'
setlists = client.search_setlists(artist_name="Muse")
print(json.dumps(setlists, indent=2))

artists=client.search_artists(artist_name="Muse")
print(json.dumps(artists, indent=2))
artist = artists['artist'][0]
print(json.dumps(artist, indent=2))
mbid=artist['mbid']
#mdib="9c9f1380-2516-4fc9-a3e6-f9f61941d090"
setlists=client.get_artist_setlists(mbid)
first=setlists['setlist'][0]
print(json.dumps(first, indent=2))
