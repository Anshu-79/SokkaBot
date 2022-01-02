from datetime import datetime
import json
  
def save_data(ctx, channel, dt, text, tz, tf):
  file = open('announcements.json', 'r+')
  file_data = json.load(file)
  #going back to the beginning after reading the whole file...
  file.seek(0)
  exportList = [
    {"channel": channel,
     "guild": ctx.guild.name,
    "datetime": dt,
    "text": text + f"\nThis was an announcement by {ctx.author.name}",
    "author": ctx.author.name}]
  
  file_data.extend(exportList)
  sorted_data = sorted(file_data, key=lambda x : tz.localize(datetime.strptime(x['datetime'], tf)).timestamp())

  json.dump(sorted_data, file, indent=2)
