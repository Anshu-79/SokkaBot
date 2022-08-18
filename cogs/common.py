import aiohttp
import asyncio
import disnake
from disnake.ext import commands

from common_functions.gif_function import get_gif
from loggers import cmdLogger as infoLogger


class CommonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__doc__ = "Module with common commands for everyone's use"
        self.joke_api_request = "https://v2.jokeapi.dev/joke/Miscellaneous,Dark,Pun,Spooky?blacklistFlags=nsfw,racist,sexist,explicit"

    @commands.command(name="ping", help="Pings you back along with latency")
    async def ping(self, ctx):
        await ctx.send(
            f"Pong! I'm alive.\nLatency = {round(self.bot.latency * 1000, 3)} ms"
        )
        infoLogger.info(f"Told {ctx.author} that I'm alive.")

    @commands.command(name="hello", help="Says hello")
    @commands.guild_only()
    async def say_hello(self, ctx):
        await ctx.reply(f"Hello, {ctx.author.name}! Sokka, the boomerang guy here.")
        infoLogger.info(f"Said hello to {ctx.author}.")

    @commands.command(name="joke", help="Tells you a joke")
    async def tell_joke(self, ctx):
        async with aiohttp.ClientSession() as session:
            request = await session.get(self.joke_api_request)
            json_data = await request.json()

            if json_data['type'] == 'single':
                await ctx.reply(json_data["joke"])
                infoLogger.info(f"Told a one-part joke to {ctx.author}.")

            if json_data['type'] == 'twopart':
                await ctx.reply(json_data["setup"])
                await asyncio.sleep(1)
                await ctx.reply(json_data["delivery"])
                infoLogger.info(f"Told a two-part joke to {ctx.author}.")

    @commands.Cog.listener("on_message")
    async def send_gif(self, ctx):
        if ctx.author != self.bot.user and len(ctx.embeds) == 0:
            message = ctx.content

            if (gif_data := await get_gif(message)) != None:
                gif_file = gif_data[2]
                gif_phrase = gif_data[1]
                gif_title = gif_data[0]

                if gif_phrase:
                    embed = disnake.Embed(title=gif_phrase, color=ctx.author.color)
                    embed.set_image(file=gif_file)
                    await ctx.reply(embed=embed)
                else:
                    await ctx.reply(file=gif_file)
                infoLogger.info(
                    f"Reacted with the {gif_title} GIF to {ctx.author}'s message."
                )


def setup(bot):
    bot.add_cog(CommonCog(bot))
