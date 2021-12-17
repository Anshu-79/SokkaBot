import discord

def get_key(input_dict, val):
    for key, value in input_dict.items():
        if val == value:
            return key

def word_finder(input_str):
  input_str = input_str.content.lower()
  keyword_dict = {
      "Water Tribe": ["water tribe"],
      "Head Bump": ["dumb", "stupid", "bad move"],
      "Mushroom Cloud": ["worship", "explosion"],
      "What": ["angry", "shocked", "wtf", "what?!", "fuck you sokka", "fuck sokka"],
      "Clap": ["bravo", "good one", "well played"],
      "Awesome": ["cool", "awesome", "dope", "amazing"],
      "Wait": ["wait what", "wait a minute", "ghost", "creepy"],
      "Stuck": ["stuck", "coming", "wait"],
      "Facepalm": ["disappointed", "idiot"],
      "Cactus Juice": ["water", "hungry", "food", "thirsty"],
      "Bored": ["bore", "boring", "not interesting"],
      "I don't Care": ["idc", "don't care"],
      "Sherlock Holmes": ["mystery", "sherlock", "philosopher", "detective"],
      "Fighting": ["fight"],
      "Sad": ["sad", "depressing"],
      "Conversation Muted": ["annfiejfnafneionfefdfew"],
      "Choking": ["choke", "vomit"],
      "Good Bot": ["good bot", "funny bot"],
      "Fuck Sokka": ["fuck sokka", "sokka bad", "fuck this bot"]
      
  }
  
  for x in keyword_dict:
      for tag in keyword_dict[x]:
          if tag in input_str:
              answer = get_key(keyword_dict, keyword_dict[x])
              #print(answer)
              return answer


def link_finder(input_msg):
  gif_name = word_finder(input_msg)
  gif_dict = {
      "Water Tribe": "https://media3.giphy.com/media/J5deqXb35R6hDQHJJV/giphy.gif",
      "Head Bump": "https://media.giphy.com/media/YtJWtIdkHzV7i/giphy.gif",
      "Mushroom Cloud": "https://media.giphy.com/media/M7E5AkSXD7z4A/giphy.gif",
      "What": "https://media.giphy.com/media/npcUEgHlNLIzu/giphy.gif",
      "Clap": "https://media.giphy.com/media/rC9e6sdnlqGqI/giphy.gif",
      "Awesome": "https://media.giphy.com/media/HGlX8heqhaBNe/giphy.gif",
      "Wait": "https://media.tenor.com/images/9b95c17560e464a6697dce5f211d357b/tenor.gif",
      "Stuck": "https://media.giphy.com/media/QYwMxfDpoH3VBfPEET/giphy.gif",
      "Facepalm": "https://media1.tenor.com/images/d6e40167e5e5cd3f9a0206b7517cd009/tenor.gif",
      "Cactus Juice": "https://media.tenor.com/images/188b8cfa29705db16431fb455109a2bb/tenor.gif",
      "Bored": "https://media.tenor.com/images/7032c52e5cc4d0a3151d579041043d22/tenor.gif",
      "I don't Care": "https://media.tenor.com/images/312a718422f5d88137b18b7075c39b3a/tenor.gif",
      "Sherlock Holmes": "https://media.tenor.com/images/905a02ca1a190353f6d44140b7241a5b/tenor.gif",
      "Fighting": "https://media.tenor.com/images/beb0861608a2c7a66049a3105f23e4d4/tenor.gif",
      "Sad": "https://media.tenor.com/images/b07cbd0bbf280c310bfd6d0620e064e4/tenor.gif",
      "Conversation Muted": "https://media.tenor.com/images/372090c212759f51fa3c506b5a331854/tenor.gif",
      "Choking": "https://media.tenor.com/images/ca25e9e616203a6c1714c2ead1b52c04/tenor.gif",
      "Good Bot": "https://media.tenor.com/images/292cbfc74d2c92c8ddd92ade458e765d/tenor.gif",
      "Fuck Sokka": "https://media.tenor.com/images/fd027f49ab7250268ae36c7c31a2280a/tenor.gif"

  }
  for x in gif_dict:
      if x == gif_name:
          url = gif_dict[x]
          #print(url)
          return url

def gif_func(msg):
  gif_url = link_finder(msg)
  if gif_url != None:
    embed = discord.Embed(
      title = '',
      description = "",
      color = msg.author.color)
    embed.set_image(url=gif_url)
    answer = msg.channel.send(embed=embed)
    return answer
