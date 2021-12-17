import json
import requests

def joke_func():
  response = requests.get("https://v2.jokeapi.dev/joke/Miscellaneous,Dark,Pun,Spooky?blacklistFlags=nsfw,racist,sexist,explicit")
  json_data = json.loads(response.text)
  if 'joke' in json_data.keys():
    joke_string = json_data['joke']
    return joke_string
  if 'setup' and 'delivery' in json_data.keys():
    joke_setup = json_data['setup']
    joke_delivery = json_data['delivery']
    return [joke_setup, joke_delivery]
