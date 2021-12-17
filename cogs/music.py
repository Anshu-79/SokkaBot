import asyncio
from config import config as cfg
from discord.ext import commands
import discord
from functions.music_functions.audio_configs import Video
import logging
import math
import youtube_dl

FFMPEG_BEFORE_OPTS = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'

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

class GuildState:
  #Helper class managing per-guild state.

  def __init__(self):
    self.volume = 0.05
    self.playlist = []
    self.skip_votes = set()
    self.now_playing = None

  def is_requester(self, user):
    return self.now_playing.requested_by == user


class MusicCog(commands.Cog):
  def __init__(self, bot, config):
    self.bot = bot
    self.config = config["music"]
    self.states = {}
    self.bot.add_listener(self.on_reaction_add, 'on_reaction_add')

  def get_state(self, guild):
    #Gets the state of guild & creates one if it doesn't exist
    if guild.id in self.states:
      return self.states[guild.id]
    else:
      self.states[guild.id] = GuildState()
      return self.states[guild.id]
  
  @commands.command(aliases=["leave"])
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def stop(self, ctx):
    #Music stops and bot leaves the voice channel.
    client = ctx.guild.voice_client
    state = self.get_state(ctx.guild)
    if client and client.channel:
      await client.disconnect()
      state.playlist = []
      state.now_playing = None
    else:
      await ctx.send("Not in a voice channel.")
    
  @commands.command(aliases=["resume"])
  @commands.guild_only()
  @commands.check(audio_playing)
  @commands.check(in_voice_channel)
  #@commands.check(is_audio_requester)
  async def pause(self, ctx):
    #Pauses or resumes any currently playing audio.
    client = ctx.guild.voice_client
    self._pause_audio(client)
    
  def _pause_audio(self, client):
    if client.is_paused():
      client.resume()
    else:
      client.pause()

  @commands.command(aliases=["vol"])
  @commands.guild_only()
  @commands.check(audio_playing)
  @commands.check(in_voice_channel)
  #@commands.check(is_audio_requester)
  async def volume(self, ctx, volume: int):
    #Changes the volume of currently playing audio (values 0-250).
    state = self.get_state(ctx.guild)

    if volume < 0:
      volume = 0
    
    max_vol = self.config['max_volume']
    if max_vol > -1:
      if volume > max_vol:
        volume = max_vol
    
    client = ctx.guild.voice_client

    state.volume = float(volume) / 100.0
    client.source.volume = state.volume


  @commands.command()
  @commands.guild_only()
  @commands.check(audio_playing)
  @commands.check(in_voice_channel)
  async def skip(self, ctx):
    #Votes for the currently playing song to be skipped.
    state = self.get_state(ctx.guild)
    client = ctx.guild.voice_client
    
    if ctx.channel.permissions_for(ctx.author).administrator or state.is_requester(ctx.author):
      client.stop()
      #skips if command sender is the requester or admin

    elif self.config['vote_skip']:
      #Checks if vote skipping is enabled & then executes _vote_skip()
      channel = client.channel
      self._vote_skip(channel, ctx.author)
      await ctx.send(
        f"{ctx.author.mention} skipped this song.")
      
      users_in_channel = len([
        member for member in channel.members if not member.bot
      ]) #counts users in channel & makes sure not to count bots
      
      #calculates number of votes required to skip
      required_votes = math.ceil(
        self.config['vote_skip_ratio'] * users_in_channel)
      
      await ctx.send(
        f"{ctx.author.mention} voted to skip. ({len(state.skip_votes)}/{required_votes} votes as of now).")
      
    else:
      await ctx.reply("Vote skipping is disabled.")

    def _vote_skip(self, channel, member):
      #Register a vote for 'member' to skip the song playing.
      logging.info(f"{member.name} votes to skip")
      state = self.get_state(channel.guild)
      state.skip_votes.add(member)
      
      users_in_channel = len([
        member for member in channel.members if not member.bot])
      
      if (float(len(state.skip_votes)) / users_in_channel) >= self.config['vote_skip_ratio']:
        logging.info(f"Enough votes, skipping...")
        channel.guild.voice_client.stop()
      
  def _play_song(self, client, state, song):
    state.now_playing = song
    state.skip_votes = set() #clears skip votes
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url, before_options=FFMPEG_BEFORE_OPTS), volume = state.volume) #gets the source of music

    def after_playing(err):
      #defines what to do after a song ends
      if len(state.playlist) > 0:
        next_song = state.playlist.pop(0)
        #removes the song that just played from the playlist
      
        self._play_song(client, state, next_song)
        #plays the next song if playlist isn't empty

      else:
        asyncio.run_coroutine_threadsafe(client.disconnect(), self.bot.loop) #disconnects if playlist is empty
    
    client.play(source, after=after_playing)
    #tells the bot to play song from the source

  async def _add_reaction_controls(self, message):
    #Adds a 'control-panel' of reactions to a message that can be used to control the bot.
    CONTROLS = ["\U000023ee","\U000023ef","\U000023ed"]
    for control in CONTROLS:
      await message.add_reaction(control)
  
  @commands.command(aliases=['np'])
  @commands.guild_only()
  @commands.check(audio_playing)
  async def nowplaying(self, ctx):
    #Displays information about the current song.
    state = self.get_state(ctx.guild)
    message = await ctx.send("", embed=state.now_playing.get_embed())
    #await message._add_reaction_controls(message)
    await self._add_reaction_controls(message)
    
  @commands.command(aliases=['q', 'playlist'])
  @commands.guild_only()
  @commands.check(audio_playing)
  async def queue(self, ctx):
    #Displays the current play queue.
    state = self.get_state(ctx.guild)
    await ctx.send(self._queue_text(state.playlist))

  def _queue_text(self, queue):
    #Returns a block of text describing a given song queue.
    if len(queue) > 0:
      message = [f"{len(queue)} songs in queue:"]
      message += [
        f"{index+1}. **{song.title}** (requested by **{song.requested_by.name}**)"
        for (index, song) in enumerate(queue)
      ] #add individual songs
      return "\n".join(message)
    else:
      return "The play queue is empty."

  @commands.command(aliases=['cq'])
  @commands.guild_only()
  @commands.check(audio_playing)
  @commands.has_permissions(administrator=True)
  async def clearqueue(self, ctx):
    #Clears the play queue without leaving the channel
    state = self.get_state(ctx.guild)
    state.playlist = []

  @commands.command(aliases=['jq'])
  @commands.guild_only()
  @commands.check(audio_playing)
  @commands.has_permissions(administrator=True)
  async def jumpqueue(self, ctx, old_index: int, new_index: int):
    #moves song at an index to 'new_index in queue'
    state = self.get_state(ctx.guild)
    
    if 1 <= old_index <= len(state.playlist) and 1 <= new_index:
      #checks if the song at old_index is at or between 2nd to last position & makes sure that we can't move the song to the currently playing position ie 0
      
      song = state.playlist.pop(old_index - 1) #take song at old_index...
      state.playlist.insert(new_index-1, song) #and inserts it at new_index

      await ctx.send(self._queue_text(state.playlist))
    else:
      await ctx.send("You must use a valid index.")

  @commands.command(brief="Plays audio from <url>.")
  @commands.guild_only()
  async def play(self, ctx, *, url):
    #Plays audio hosted at <url> (or performs a search for <url> and plays the first result).

    client = ctx.guild.voice_client
    state = self.get_state(ctx.guild)

    if client and client.channel:
      try:
        video = Video(url, ctx.author)
      except youtube_dl.DownloadError as e:
        logging.warn(f"Error downloading video: {e}")
        await ctx.send(
          "There was an error downloading your video, sorry.")
        return
      state.playlist.append(video)
      message = await ctx.send(
        "Added to queue.", embed=video.get_embed())
      await self._add_reaction_controls(message)
    else:
      if ctx.author.voice is not None and ctx.author.voice.channel is not None:
        channel = ctx.author.voice.channel
        try:
          video = Video(url, ctx.author)
        except youtube_dl.DownloadError as e:
          await ctx.send(
            "There was an error downloading your video, sorry.")
          return
        client = await channel.connect()
        self._play_song(client, state, video)
        message = await ctx.send("", embed=video.get_embed())
        await self._add_reaction_controls(message)
        logging.info(f"Now playing '{video.title}'")
      else:
        await ctx.send("You need to be in a voice channel to do that.")
        raise commands.CommandError(
          "You need to be in a voice channel to do that.")
        

  async def on_reaction_add(self, reaction, user):
    #Responds to reactions added to the bot's messages, allowing reactions to control playback.
    message = reaction.message
    if user != self.bot.user and message.author == self.bot.user:
      await message.remove_reaction(reaction, user)
      
      if message.guild and message.guild.voice_client:
        user_in_channel = user.voice and user.voice.channel and user.voice.channel == message.guild.voice_client.channel #determines if the user in that voice channel
        permissions = message.channel.permissions_for(user)
        guild = message.guild
        state = self.get_state(guild)
        
        if permissions.administrator or (user_in_channel and state.is_requester(user)):
          client = message.guild.voice_client
        
          if reaction.emoji == "\U000023ef":
            #pause audio
            self._pause_audio(client)
          
          elif reaction.emoji == "\U000023ed":
            #skip audio
            client.stop()
          
          elif reaction.emoji == "\U000023ee":
            state.playlist.insert(
              0, state.now_playing) #insert current song at beginning of playlist
            client.stop() #skip ahead
        
        elif reaction.emoji == "\U000023ed" and self.config["vote_skip"] and user_in_channel and message.guild.voice_client and message.guild.voice_client.channel:
          #ensure that skip was pressed, that vote skipping is enabled,
          #the user is in the channel, and that the bot is in a voice channel
          
          voice_channel = message.guild.voice_client.channel
          self._vote_skip(voice_channel, user)
          #announce vote
          channel = message.channel
          users_in_channel = len([
            member for member in voice_channel.members
            if not member.bot
          ]) #don't count bots
          required_votes = math.ceil(
            self.config["vote_skip_ratio"] * users_in_channel)
          await channel.send(
            f"{user.mention} voted to skip ({len(state.skip_votes)}/{required_votes} votes)")

  
def setup(bot):
  bot.add_cog(MusicCog(bot, cfg))
