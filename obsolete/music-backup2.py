import asyncio
import discord
from discord.ext import commands
from discord.utils import get
#from functions.music_functions.audio_extract import get_audio
from functions.music_functions.music_embed import make_embed
from functions.music_functions.video_getter import get_video as get_video_url
from functions.music_functions.audio_extract import get_audio

music_channel_id = 879026668331761675 #This is the Music! channel_id
songs = asyncio.Queue()
play_next_song = asyncio.Event()
queue = []


class VoiceState:
  def __init__(self, bot):
    self.current = None
    self.voice = None
    self.bot = bot
    self.play_next_song = asyncio.Event()
    self.songs = asyncio.Queue()
    self.audio_player = self.bot.loop.create_task(self.audio_player_task())

  def toggle_next(self):
    self.bot.loop.call_soon_threadsafe(self.play_next_song.set)
  
  async def audio_player_task(self):
    while True:
      self.play_next_song.clear()
      self.current = await self.songs.get()
      await self.bot.send_message(self.current.channel, 'Now playing ' + str(self.current))
      self.current.player.start()
      await self.play_next_song.wait()


class MusicCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.voice_states = {}

  @commands.command(pass_context=True, no_pm=True)
  async def summon(self, ctx):
    user_voice = ctx.message.author.voice
    if user_voice is None:
      await ctx.send('You are not in a voice channel.')
      return False
    else:
      user_voice_channel = user_voice.channel
      await user_voice_channel.connect()

  def get_voice_state(self, server):
    state = self.voice_states.get(server.id)
    if state is None:
      state = VoiceState(self.bot)
      self.voice_states[server.id] = state

    return state

  @commands.command(name='play')
  async def play(self, ctx, *, song : str):
    vid_url = get_video_url(ctx)
    state = self.get_voice_state(ctx.message.guild)
    opts = {
      'default_search': 'auto',
      'quiet': True,
    }

    if state.voice is None:
      success = await ctx.invoke(self.summon)
      if not success:
        return

    #player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
    player = await get_audio(self.bot, ctx, vid_url)
    player.volume = 0.6

    
  @commands.command(name="pause")
  async def pause(self, ctx):
    voice = get(self.bot.voice_clients, guild=ctx.guild)
  
    if voice.is_playing():
      voice.pause()
      await ctx.send("Music paused")
  
  @commands.command(name="resume")
  async def resume(self, ctx):
    voice = get(self.bot.voice_clients, guild=ctx.guild)
    
    if voice.is_connected():
      if not voice.is_playing():
        voice.resume()
        await ctx.send("Music resumed")
  
  @commands.command(name="stop")
  async def stop(self, ctx):
    voice = get(self.bot.voice_clients, guild=ctx.guild)

    if voice.is_connected():
        await voice.disconnect()
        await ctx.send('Music stopped')


def setup(bot):
  bot.add_cog(MusicCog(bot))
