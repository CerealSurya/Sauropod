import random
import requests

def player(songList, ytToken, finished, shuffle=False):
    queue = songList
    print("\n\n")
    print(type(queue), queue)
    if type(queue) == str: #Getting it from url params
        queue = queue.split("c3R3@l")
        
        if finished:
            queue.pop(0)
            queue.pop(0)
        #print(queue)
    
    if len(queue) == 0:
        return "no songs left"
    elif shuffle:
        random.shuffle(queue)

    strungQueue = ""
    for i in range(len(queue)):
        strungQueue += "c3R3@l" + queue[i]

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "key": ytToken,
        "part": "snippet",
        "q": queue[0],
        "maxResults": 1,
        "type": ["Video"]
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        response = response.json()
        # with open("someth.json", "w") as f:
        #     f.write(json.dumps(response))
        vidId = response["items"][0]["id"]["videoId"]
        #return f"https://www.youtube.com/embed/{vidId}&autoplay=1"

        return {"id": vidId, "queue": strungQueue}
    else:
        print("Youtube API: ", response.status_code)
        return response.status_code
        