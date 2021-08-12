from os import name
import os
import spotipy
import spotipy.util as util
import time
from json.decoder import JSONDecodeError
from secondary import playlists
from secrets import secrets

notes_path = "C:\Riot Games\League of Legends\MyNotes.txt"

def authenticate():
    try:
        token = util.prompt_for_user_token(
            username=secrets['username'],
            scope='user-read-private user-read-playback-state user-modify-playback-state user-read-recently-played',
            client_id=secrets['client_id'],
            client_secret=secrets['client_secret'],
            redirect_uri='https://www.google.com/'
        )
    except (AttributeError, JSONDecodeError):
        os.remove(f".cache-{secrets['username']}")
        token = util.prompt_for_user_token(
            username=secrets['username'],
            scope='user-read-private user-read-playback-state user-modify-playback-state user-read-recently-played',
            client_id=secrets['client_id'],
            client_secret=secrets['client_secret'],
            redirect_uri='https://www.google.com/'
        )
    return token

def follow(thefile):
    thefile.seek(0,2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def play(song_name, spotify_object, deviceID):
    try:
        result = spotify_object.search(q=song_name, type='track', limit=1)['tracks']['items'][0]['uri']
        spotify_object.add_to_queue(result, deviceID)
        spotify_object.next_track(deviceID)
    except KeyError:
        pass

def playlist(playlist_name, spotify_object, deviceID):
    try:
        playlist_name = playlists[playlist_name]
        for track in spotify_object.playlist_items(playlist_name)['items']:
            spotify_object.add_to_queue(track['track']['uri'], deviceID)
    except KeyError:
        pass

commands_to_functions = {"/play" : play, '/playlist' : playlist}


if __name__ == "__main__":
    spotify_object = spotipy.Spotify(auth=authenticate())
    devices = spotify_object.devices()
    deviceID = devices['devices'][0]['id']
    logfile = open(notes_path,"r")
    loglines = follow(logfile)
    for line in loglines:
        command = line.split()
        if not command:
            continue
        if command[0] in commands_to_functions:
            commands_to_functions[command[0]](' '.join(command[1:]), spotify_object, deviceID)