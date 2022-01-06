import disnake
from disnake.ext import commands


class HelpCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Command(aliases=['h'])
  async def help(self, ctx):
    return

def setup(bot):
  bot.add_cog(HelpCog(bot))
