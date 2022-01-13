
import disnake
from disnake.ext import commands

import globals
from keep_alive import keep_alive

import os
import traceback

hal_url = "https://res.cloudinary.com/teepublic/image/private/s--UA3EJ8el--/t_Preview/b_rgb:191919,c_limit,f_jpg,h_630,q_90,w_630/v1489665271/production/designs/1328689_1.jpg"

botToken = os.environ['botToken']

def get_prefix(bot, message):
    
    prefixes = ['$']

    if not message.guild:
        return '$'

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


def fancy_traceback(exc: Exception) -> str:
  """May not fit the message content limit"""
  text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
  return f"```py\n{text[-512:]}\n```"


cogs = ['cogs.mods','cogs.common', 'cogs.members', 'cogs.music', 'cogs.help']

intents = disnake.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=get_prefix, intents=intents)


class SokkaBot(commands.Bot):
  def __init__(self):
    super().__init__(
      command_prefix = get_prefix,
      intents = intents,
      help_command = None,
    )

  def load_all_extensions(self, cogs_list):
    print('Loading cogs...\n')
    for cog in cogs_list:
      self.load_extension(cog)
      print(f"{cog} was loaded.")

  async def on_ready(self):
    print(f'\nLogged in as: {bot.user.name} - {bot.user.id}\n')
    
    print("I'm ready to chat!\n")


  async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
    embed = disnake.Embed(
        title="I'm sorry, Dave. I'm afraid I can't do that.",
        description=f"Command `{ctx.command}` failed due to `{error}`\n{fancy_traceback(error)}",
        color=disnake.Color.red(),
    )
    embed.set_thumbnail(url=hal_url)
    await ctx.send(embed=embed)

  

bot = SokkaBot()
bot.remove_command("help")
bot.load_all_extensions(cogs)

print(f"disnake: {disnake.__version__}\n")

keep_alive()

bot.run(botToken)
