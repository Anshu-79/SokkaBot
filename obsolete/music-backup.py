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

class MusicCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command(name='play')
  async def play(self, ctx, *, song : str):
    vid_url = get_video_url(ctx)

    if vid_url != None:
      music_channel = self.bot.get_channel(music_channel_id)
      voice = get(self.bot.voice_clients, guild=ctx.guild)
      queue.append(vid_url)
      
      if voice is None:
        voice = await music_channel.connect()
        #print(voice)
        await ctx.send("Connected to music voice channel...")

      elif voice.channel and voice.channel.id != music_channel.id:
        await voice.disconnect(force=True)
        await music_channel.connect()
        await ctx.send("Connected to music voice channel...")
      
      #elif voice.channel and voice.channel.id == music_channel.id:
       # pass

      if not voice.is_playing():
        if len(queue) >= 1:
            vid_info = get_audio(self.bot, ctx, queue[0])
            music_embed = make_embed(vid_info)
            await ctx.send(embed=music_embed)
            print(queue)
            del queue[0]
            
      elif voice.is_playing():
        await ctx.send("Added to queue...")

      elif vid_url == None:
        await ctx.reply("No such videos found :(")

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
