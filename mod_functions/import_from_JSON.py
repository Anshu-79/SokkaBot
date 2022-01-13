import json

def get_data():
  file = open('announcements.json', 'r')
  file_data = json.load(file)
  if len(file_data) != 0:
    return file_data[0]
  else:
    return None
