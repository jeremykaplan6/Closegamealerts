print("SCRIPT STARTING")

import requests

print("REQUESTS IMPORTED")

APP_TOKEN = "abc"
USER_KEY = "def"

print("BEFORE REQUEST")

response = requests.post("https://api.pushover.net/1/messages.json")

print("AFTER REQUEST")


import requests

USER_KEY = "udhkmqdag5zjgm2r9k2ay3x51zf8r1"
APP_TOKEN = "a7w3uqzjsyp5iuw3hmjdpvh4gb8iu4"

response = requests.post(
    "https://api.pushover.net/1/messages.json",
    data={
        "token": APP_TOKEN,
        "user": USER_KEY,
        "message": "🔥 Test Alert from AI Gym",
        "title": "Close Game Detector"
    },
)

print(response.status_code)
print(response.text)
