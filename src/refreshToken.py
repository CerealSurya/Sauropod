import requests
import base64
import json
def getAccessToken(clientId, clientSecret, refresh_token):
    url = "https://accounts.spotify.com/api/token"
    message = f"{clientId}:{clientSecret}"
    message = message.encode('ascii')
    base64_bytes = base64.b64encode(message)
    base64_message = base64_bytes.decode('ascii')
    
    authorizationMessage = str("Basic " + base64_message)

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": authorizationMessage
    }
    params = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token 
    }
    response = requests.post(url, params=params, headers=headers)
    if response.status_code == 200:
        response = response.json()
        newJson = {}
        try:
            newJson = {
                "access_token": response["access_token"],
                "refresh_token": response["refresh_token"]
            }
        except:
            newJson = {
                "access_token": response["access_token"],
                "refresh_token": refresh_token
            }
        newJson = json.dumps(newJson)

        with open("info.json", "w") as f:
            f.write(newJson)
        return True
    else:
        print("howdy", response.status_code)
        #print(response.json())
        return False

    
