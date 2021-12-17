import os

import globals

def get_mod(bot, ctx):
  for guild in bot.guilds:
    if guild.id == globals.server_dict["The White Lotus"]:
      mod_id = int(os.environ["anshu79_id"])
      mod = ctx.guild.get_member(mod_id)
      #mod = bot.get_user(mod_id)
      return mod
