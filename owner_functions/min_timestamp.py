from datetime import datetime
import json
import pytz

def min_timestamp():
  tz = pytz.timezone('Asia/Kolkata')
  tf = "%d-%m-%Y %H:%M:%S" 
  
  
  file = open('announcements.json', 'r')
  file_data = json.load(file)
  if len(file_data) != 0:
    for d in file_data:
      if file_data.index(d) == 0:
        min_dt = tz.localize(datetime.strptime(d['datetime'], tf)).timestamp()
      else:
        if tz.localize(datetime.strptime(d['datetime'], tf)).timestamp() < min_dt:
          min_dt = d['datetime'].timestamp()
    
    return min_dt
  
  else:
    return None
