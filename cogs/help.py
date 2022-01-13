import disnake
from disnake.ext import commands
from disnake.errors import Forbidden
import os

async def send_embed(ctx, embed):
  try:
    await ctx.send(embed=embed)
    
  except Forbidden:
    try:
      await ctx.send("Hey, seems like I can't send embeds. Please check my permissions.")
    except Forbidden:
      #personally DMs the author if bot can't send messages in given channel
      await ctx.author.send(
        f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
        f"Could you inform the server mods about this issue?", embed=embed)

class HelpCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.owner_id = os.environ['anshu79_id']
    self.prefix = '$'
    self.__doc__ = "Help module"
    
  @commands.command()
  async def help(self, ctx, *input):
    #if no module is specified, all of them are sent
    if not input:
      try:
        owner = ctx.guild.get_member(self.owner_id).mention
      except AttributeError as e:
        owner = self.bot.get_user(self.owner_id)
        
      #defining an embed
      emb = disnake.Embed(
        title='Commands and modules',
        color=ctx.author.color,
        description=f'Use `{self.prefix}help <module>` to learn more about that module')

      cogs_desc = ''
      for cog in self.bot.cogs:
        cogs_desc += f"`{cog.replace('Cog','')}` {self.bot.cogs[cog].__doc__}\n"

      emb.add_field(name='Modules', value=cogs_desc, inline=False)

      #iterating through uncategorized commands
      commands_desc = ""
      for command in self.bot.walk_commands():
        if not command.cog_name and not command.hidden:
          commands_desc += f"{command.name} - {command.help}\n"
          
      if commands_desc:
        emb.add_field(name='Not belonging to a module', value=commands_desc, inline=False)
        
      emb.add_field(name="About", value=f"This bot is developed & maintained by Anshu79#2928 \nPlease DM me to submit ideas & bugs")
        
      emb.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

    elif len(input) == 1:
      
      for cog in self.bot.cogs:
        if cog.replace('Cog', '').lower() == input[0].lower():
          emb = disnake.Embed(title=f"{cog.replace('Cog', '')} - Commands",
                             description=self.bot.cogs[cog].__doc__,
                             color = ctx.author.color)

          for command in self.bot.get_cog(cog).get_commands():
            if not command.hidden:
              emb.add_field(name=f"\n`{self.prefix}{command.name}`",
                           value=command.help, inline=False)
          break

      #this is the else statement for the for loop 
      else:
        emb = disnake.Embed(title="No such command found",
                     description="You sure you didn't eat some expired Smile Dip?",
                           color=ctx.author.color)

    elif len(input) > 1:
      emb = disnake.Embed(title="That's a lot of modules.",
                         description="Please request one module at a time. I'm not the Avatar or something.",
                         color=ctx.author.color)
    else:
      emb = disnake.Embed(title="Wait... What?",
                         description=f"If everything went right, you shouldn't be here. Please report this to {owner} right away.\nThank you!",
                         color=ctx.author.color)

    await send_embed(ctx, emb)
    
        
def setup(bot):
  bot.add_cog(HelpCog(bot))
