import json
from mod_functions.text_to_timestamp import text_2_timestamp

def minTimeDict():
  
  file = open('announcements.json', 'r')
  file_data = json.load(file)
  
  if len(file_data) != 0:
    for d in file_data:
      if file_data.index(d) == 0:
        min_dt = text_2_timestamp(d['datetime'])
        ticket = d['ticket_id']
      else:
        if text_2_timestamp(d['datetime']) < min_dt:
          min_dt = d['datetime'].timestamp()
          ticket = d['ticket_id']
          

    for i in file_data:
      if i['ticket_id'] == ticket:
        return i
    
  else:
    return None
