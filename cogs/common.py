import aiohttp
import disnake
from disnake.ext import commands
import time

#from functions.gif_functions.gif_function import gif_func
from common_functions.gif_function import get_gif

class CommonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__doc__ = "Module with common commands for everyone's use"
  
    
    @commands.command(name='ping', help="Pings you back along with latency")
    async def ping(self, ctx):
        await ctx.send(f"Pong! I'm alive.\nLatency = {round(self.bot.latency * 1000, 3)} ms")
        print(f"Told {ctx.author.name} that I'm alive.")
  
    
    @commands.command(name="hello", help="Says hello")
    @commands.guild_only()
    async def say_hello(self, ctx):
        await ctx.reply(f"Hello, {ctx.author.name}! Sokka, the boomerang guy here.")
        print(f"\nSaid hello to {ctx.author.name}.")

    
    @commands.command(name="joke", help='Tells you a joke')
    async def tell_joke(self, ctx):
        async with aiohttp.ClientSession() as session:
            request = await session.get("https://v2.jokeapi.dev/joke/Miscellaneous,Dark,Pun,Spooky?blacklistFlags=nsfw,racist,sexist,explicit")
            json_data = await request.json()
            if 'joke' in json_data.keys():
                await ctx.reply(json_data['joke'])
                print(f"\nTold a one-part joke to {ctx.author.name}.")
        
            if 'setup' and 'delivery' in json_data.keys():
                await ctx.reply(json_data['setup'])
                time.sleep(1)
                await ctx.reply(json_data['delivery'])
                print(f"\nTold a two-part joke to {ctx.author.name}.")

    
    @commands.Cog.listener("on_message")
    async def send_gif(self, ctx):
        if ctx.author != self.bot.user and len(ctx.embeds) == 0:
            message = ctx.content
    
            if (gif_data := await get_gif(message)) != None:
                gif_file = gif_data[2]
                gif_phrase = gif_data[1]
                gif_title = gif_data[0]
        
                if gif_phrase:
                    embed = disnake.Embed(
                      title = gif_phrase,
                      #description = "",
                      color = ctx.author.color)
                    embed.set_image(file=gif_file)
                    await ctx.reply(embed=embed)
                else:
                    await ctx.reply(file=gif_file)
                print(f"\nReacted with the {gif_title} GIF to {ctx.author.name}'s message.")

def setup(bot):
  bot.add_cog(CommonCog(bot))
