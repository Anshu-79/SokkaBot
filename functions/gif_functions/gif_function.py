
from functions.gif_functions.gif_database import gif_data_list

def gif_func(input_msg):
  input_msg = input_msg.lower()
  for gif_data in gif_data_list:
    for gif_tag in gif_data["tags"]:
      if gif_tag in input_msg:
        return gif_data
