import requests

url = "http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"

response = requests.get(url)
data = response.json()

print("Games today:", len(data["events"]))

for game in data["events"]:
    print(game["name"])
