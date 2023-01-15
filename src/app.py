from flask import Flask, request, redirect, render_template, make_response
from dotenv import load_dotenv
import os
import requests
import base64
import traceback
import json
load_dotenv()

from getPlaylistItems import getPlaylistItems
from player import player
from refreshToken import getAccessToken

clientId = os.environ.get("client_id")
callbackUrl = os.environ.get("redirect_uri")
clientSecret = os.environ.get("client_secret") 
ytToken = os.environ.get("youtube_token") 

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"]) #main/login page
def main():
    info = {}
    with open("info.json", "r") as f:
        info = json.load(f)
    try:
        if info["refresh_token"] == None or info["refresh_token"] == "": 
            print("no Refresh")
            params = f"response_type=code&client_id={clientId}&redirect_uri={callbackUrl}"
            return redirect(f"https://accounts.spotify.com/authorize?{params}")

        else: #this is where the mainfile and the magic happens
            playlistId = request.cookies.get("playlistId")
            if "submit_playlist" in request.form:
                playlistId = request.form["playlisturl"]
                playlistId = playlistId[34:len(playlistId)]

            if playlistId == "" or playlistId == None:
                print("running")
                return render_template("index.html", videoId = "", songList = "", fullLink="")

            finished = request.args.get("finished")
            playListItems = ""
            playlistName = ""
            playlistUrl = ""
            if finished == None:
                playlist = getPlaylistItems(playlistId, info["access_token"])
                if playlist != "badAccessToken":
                    playListItems = playlist["queue"]
                    playlistName = playlist["details"]["name"]
                    playlistUrl = playlist["details"]["img"]
                else:
                    playListItems = "badAccessToken"

            if playListItems == "badAccessToken":
                print(finished)
                if getAccessToken(clientId, clientSecret, info["refresh_token"]):
                    if finished == "True":
                        return redirect("http://localhost:6969/?finished=True")

                    respo = make_response(redirect("http://localhost:6969"))
                    respo.set_cookie("queue", "")
                    respo.set_cookie("playlistId", "")
                    return respo
                else:
                    return ""

            else: #Acess token is good, do the things we want wit the playlist
                queue = playListItems
                if finished == "True":
                    finished = True
                    queue = request.cookies.get("queue")
                    playlistName = request.cookies.get("playlistName")
                    playlistUrl = request.cookies.get("playlistUrl")
                    print("Howdy", playlistName)
                else:
                    finished = False
                link = player(queue, ytToken, finished, shuffle=True) #Figure the shuffle out
                if type(link) == int:
                    return ""
                if type(link) == str:
                    if link == "no songs left":
                        respo = make_response(redirect("http://localhost:6969"))
                        respo.set_cookie("queue", "")
                        respo.set_cookie("playlistId", "")
                        return respo
                daQueue = link["queue"]
                resp = make_response(render_template("index.html", videoId = link["id"], playlistName = playlistName, playlistUrl = playlistUrl, songList = daQueue, fullLink="https://www.youtube.com/embed/" + link["id"]))
                resp.set_cookie("queue", daQueue)
                resp.set_cookie("playlistId", playlistId)
                resp.set_cookie("playlistName", playlistName)
                resp.set_cookie("playlistUrl", playlistUrl)
                return resp
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        return ""
        # params = f"response_type=code&client_id={clientId}&redirect_uri={callbackUrl}&scope=playlist-read-private"
        # return redirect(f"https://accounts.spotify.com/authorize?{params}")

@app.route("/callback", methods=["GET", "POST"]) #callback page
def callback():
    code = request.args.get("code")
    errorCode = request.args.get("error")
    
    if errorCode == None: #no error
        #make request for auth token and refresh
        message = f"{clientId}:{clientSecret}"
        message = message.encode('ascii')
        base64_bytes = base64.b64encode(message)
        base64_message = base64_bytes.decode('ascii')
        
        authorizationMessage = str("Basic " + base64_message)
        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": authorizationMessage
        }
        params = {
            "code": code,
            "redirect_uri": callbackUrl,
            "grant_type": "authorization_code" 
        }
        response = requests.post(url, params=params, headers=headers)
        if response.status_code == 200:
            response = response.json()
            newJson = {
                "access_token": response["access_token"],
                "refresh_token": response["refresh_token"]
            }
            newJson = json.dumps(newJson)
            print(response["access_token"])
            print(response["refresh_token"])

            with open("info.json", "w") as f:
                f.write(newJson)
            return redirect("http://localhost:6969")
        else:
            print(response.status_code)
            #print(response)
            return ""

if __name__ == "__main__":
    app.run(host = "localhost", port=6969, debug=True)
