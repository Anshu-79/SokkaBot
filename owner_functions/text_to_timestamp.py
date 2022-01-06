from datetime import datetime
import pytz


def text_2_timestamp(text):
  tz = pytz.timezone('Asia/Kolkata')
  tf = "%d-%m-%Y %H:%M:%S" 
  
  return tz.localize(datetime.strptime(text, tf)).timestamp()