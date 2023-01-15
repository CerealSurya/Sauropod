import requests

def getPlaylistItems(playlistId, OAuth):
    url = f"https://api.spotify.com/v1/playlists/{playlistId}"
    header={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OAuth}"
    }
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        response = response.json()
        tracks = response["tracks"]
        tracks = tracks["items"] #list of dicts
        songList = []
        for i in range(len(tracks)):# Caps out at 100
            singleTrack = tracks[i]
            name = singleTrack["track"]["name"]
            artist = singleTrack["track"]["artists"][0]["name"]
            songList.append(f"{name} by {artist}")
        playlistDetails = {
            "name": response["name"],
            "img": response["images"][0]["url"]
        }
        return {"queue": songList, "details": playlistDetails}
    else:
        print("Spotify playlist", response.status_code)
        if response.status_code == 401:
            return "badAccessToken"
