from os import write
from pprint import pprint 
import time
import requests
from urllib.parse import urlencode, urlparse, parse_qs
from base64 import b64encode

token_url="https://accounts.spotify.com/api/token"
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "playlist-modify-public playlist-modify-private"

ACCESS_TOKEN = ""   


# Step 1: Generate authorization URL
def get_authorization_url():
    auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "state": "some_random_state",  
    }
    url = f"{auth_url}?{urlencode(params)}"
    print(f"Go to the following URL and authorize the app: {url}")


def get_access_token(authorization_code):
    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()}"
    }
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(token_url, headers=headers, data=data)
    token_data = response.json()

    if response.status_code == 200:
        access_token = token_data["access_token"]
        return access_token
    else:
        print(f"Error: Unable to get access token. {response.status_code}")
        print(f"Error details: {response.text}")
        return None


# Step 3: Retrieve access token after user authorization
def retrieve_access_token():
    get_authorization_url()
    redirect_response = input("Paste the full redirect URL here: ")
    parsed_url = urlparse(redirect_response)
    authorization_code = parse_qs(parsed_url.query).get('code')[0]
    access_token = get_access_token(authorization_code)
    return access_token


# Function to fetch all tracks from a playlist
def fetch_all_tracks(playlist_id):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    all_tracks = []
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"  # URL to fetch tracks

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            break

        data = response.json()
        all_tracks.extend(data.get("items", []))  # Add current page items to the list
        url = data.get("next")  # Update next_url for pagination

    return all_tracks


# Function to create a new playlist with a unique name (based on timestamp)
def create_playlist():
    create_playlist_url = "https://api.spotify.com/v1/users/31dpxgfk5vf5wbrqmed6cirbbpdy/playlists"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Create a unique playlist name based on the current timestamp
    unique_name = f"New Playlist {int(time.time())}"  # Timestamp-based name
    body = {
        "name": unique_name,
        "description": "New playlist description",
        "public": False
    }

    response = requests.post(create_playlist_url, headers=headers, json=body)

    if response.status_code == 201:
        print(f"Playlist '{unique_name}' created successfully!")
        playlist_data = response.json()
        return playlist_data["id"]  # Returning the new playlist ID
    else:
        print(f"Failed to create playlist. Status code: {response.status_code}")
        print(f"Error message: {response.text}")
        return None


# Function to add tracks to a playlist in batches of 95
def add_tracks_in_batches(playlist_id, tracks_uris):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    batch_size = 95  # Max allowed per batch

    for i in range(0, len(tracks_uris), batch_size):
        batch_uris = tracks_uris[i:i + batch_size]
        body = {
            "uris": batch_uris
        }
        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 201:
            print(f"Batch {i//batch_size + 1} added successfully!")
        else:
            print(f"Error in batch {i//batch_size + 1}: {response.status_code}")
            print(response.json())  # Print the error details for debugging

def create_playlists(track_uris, tracks_per_playlist):
    # Calculate the number of playlists needed based on the size of the track list
    num_playlists = (len(track_uris) + tracks_per_playlist - 1) // tracks_per_playlist

    for i in range(num_playlists):
        print(f"Creating Playlist {i + 1}...")
        new_playlist_id = create_playlist()  # Create a new playlist
        if new_playlist_id:
            start_index = i * tracks_per_playlist  # Start index for the current batch
            end_index = (i + 1) * tracks_per_playlist  # End index for the current batch
            batch_tracks = track_uris[start_index:end_index]  # Select tracks for this playlist
            add_tracks_in_batches(new_playlist_id, batch_tracks)  # Add tracks to the new playlist
        else:
            print(f"Failed to create playlist {i + 1}.")


def group_tracks_by_artist(playlist):
    artist_to_tracks = {}

    # Iterate through each song in the playlist
    for song in playlist:
        track_name = song['track']['name']  # Get the track name
        
        # Iterate through each artist in the song's 'artists' list
        for artist in song['track']['artists']:
            artist_name = artist['name']  # Extract the artist name from the dictionary
            
            # If the artist isn't in the dictionary, add them with an empty list
            if artist_name not in artist_to_tracks:
                artist_to_tracks[artist_name] = []
            
            # Add the track to the artist's list of tracks
            artist_to_tracks[artist_name].append(track_name)

    # Pretty print the artist_to_tracks dictionary to show the grouped tracks by artist
    return artist_to_tracks


# Main logic to fetch tracks and create a new playlist
def main():
    global ACCESS_TOKEN
    ACCESS_TOKEN = retrieve_access_token()  # Get the access token

    # Fetch tracks from an existing playlist (replace with the actual playlist ID)
    existing_playlist_id = "4dp2jqNKNNv3kxj5hpTggL"  #"6VkQ8dJ08TCGOOCI8n4iN2"  # Replace with your playlist ID
    tracks = fetch_all_tracks(existing_playlist_id)
    print(f"Retrieved {len(tracks)} tracks from the existing playlist.")
    track_uris = [track['track']['name'] for track in tracks]  # Extract track URIs

    pprint(track_uris)

    with open('download_list', 'w') as file:
        for track in track_uris:
            file.write(track + '\n')  # Write each URI on a new line


    # x=group_tracks_by_artist(tracks)
    # pprint(x)
    # track_uris = [track['track']['uri'] for track in tracks]  # Extract track URIs
    # create_playlists(track_uris,500)

# Run the script
if __name__ == "__main__":
    main()