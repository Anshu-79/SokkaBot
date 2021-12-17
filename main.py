import discord
from discord.ext import commands

import globals
from keep_alive import keep_alive

import os

botToken = os.environ['botToken']

def get_prefix(bot, message):
    # Notice how you can use spaces in prefixes. Try to keep them simple though.
    prefixes = ['$']

    if not message.guild:
        return '$'

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)

cogs = ['cogs.owner','cogs.common', 'cogs.members', 'cogs.music']

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=get_prefix, intents=intents)

# bot.remove_command("help")

@bot.event
async def on_ready():
  print(f'\nLogged in as: {bot.user.name} - {bot.user.id}\n')
  print("Loading cogs...\n")
  for cog in cogs:
    bot.load_extension(cog)
    print(cog+" was loaded.")
  
  print("\nI'm ready to chat!")

@bot.command()
async def ping(ctx):
  await ctx.send("Ping! I'm alive.")
  print(f"Told {ctx.message.author} that I'm alive.")

keep_alive()

bot.run(botToken, bot=True, reconnect=True)
