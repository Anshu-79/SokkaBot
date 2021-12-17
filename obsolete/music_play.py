if video != "" and is_url(video) == False:
      vid_url = search(video)
      print(vid_url)
    elif video != "" and is_url(video):
      vid_url = video
      print(vid_url)
    else:
      ctx.send("No such videos found :(")
    
    music_channel = self.bot.get_channel(music_channel_id)
    await music_channel.connect()

    voice = get(self.bot.voice_clients, guild=ctx.guild)

    if voice is None:
      voice = await music_channel.connect()

    elif voice.channel and voice.channel.id != music_channel.id:
      await voice.disconnect(force=True)
      await music_channel.connect()      

    elif voice.channel and voice.channel.id == music_channel.id:  
      get_audio(self.bot, ctx, vid_url)
      await ctx.send('Now playing...')