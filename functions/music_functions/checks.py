
async def audio_playing(ctx):
  #Checks if audio is playing currently before continuing.
  client = ctx.guild.voice_client
  if client and client.channel and client.source:
    return True
  else:
    # print("Not playing any audio currently.")
    return False

async def in_voice_channel(ctx):
  #Checks if the command sender is in the same voice channel as the bot.
  voice = ctx.author.voice
  bot_voice = ctx.guild.voice_client
  if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
    return True
  else:
    print("Command sender is not in the same voice channel as the bot.")
    return False


async def is_audio_requester(ctx):
  #Checks if the command sender is also the song requester.
  music = ctx.bot.get_cog("Music")
  state = music.get_state(ctx.guild)
  permissions = ctx.channel.permissions_for(ctx.author)
  if permissions.administrator or state.is_requester(ctx.author):
    return True
  else:
    print("Command sender is not song requester.")
    return False

