import json
import requests

def joke_func(msg):
  response = requests.get("https://v2.jokeapi.dev/joke/Miscellaneous,Dark,Pun,Spooky?blacklistFlags=nsfw,racist,sexist,explicit&type=single")
  json_data = json.loads(response.text)
  joke_string = json_data['joke']
  joke = msg.channel.send(joke_string)
  return joke
