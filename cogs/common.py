import discord
from discord.ext import commands
import time

from functions.joke_function import joke_func
from functions.gif_functions.gif_function import gif_func

class CommonCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command(name="hello", brief="Says hello")
  @commands.guild_only()
  async def say_hello(self, ctx):
    await ctx.reply(f"Hello, {ctx.author.name}! Sokka, the boomerang guy here.")
    print(f"\nSaid hello to {ctx.author.name}.")
  
  @commands.command(name="joke")
  async def tell_joke(self, ctx):
    joke = joke_func()
    if isinstance(joke, str):
      await ctx.reply(joke)
      print(f"\nTold a one-part joke to {ctx.author.name}.")
    if isinstance(joke, list):
      await ctx.reply(joke[0])
      time.sleep(1)
      await ctx.reply(joke[1])
      print(f"\nTold a two-part joke to {ctx.author.name}.")

    
  @commands.Cog.listener("on_message")
  async def send_gif(self, ctx):
    if ctx.author != self.bot.user:
      message = ctx.content
      if gif_func(message) != None:
        gif_data = gif_func(message)
        gif_url = gif_data["url"]
        gif_phrase = gif_data["phrase"]
        gif_title = gif_data["name"]
      
        embed = discord.Embed(
          title = gif_phrase,
          #description = "",
          color = ctx.author.color)
        embed.set_image(url=gif_url)
        await ctx.reply(embed=embed)
        print(f"\nReacted with the {gif_title} GIF to {ctx.author.name}'s message.")

def setup(bot):
  bot.add_cog(CommonCog(bot))
