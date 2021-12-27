import discord
from discord.utils import get
import globals

# This isn't updated with the current globals configs
def get_mods(bot, ctx):
  mods = []
  input_guild = ctx.message.guild
  for guild in bot.guilds:
    if guild == input_guild:
      for mod_name in globals.server_dict[input_guild.name]['mods']:
        mods.append(discord.utils.get(bot.users, name=mod_name))
  
  return mods