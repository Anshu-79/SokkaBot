import json

def delete(data):
  file = open('announcements.json', 'r')
  f = json.load(file)
  file.seek(0)
  for i in range(len(f)):
    if f[i] == data:
      f.pop(i)
      break

  open("announcements.json", "w").write(json.dumps(f, sort_keys=True, indent=2))
  