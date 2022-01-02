from datetime import datetime
from discord.ext import commands, tasks
from discord.utils import get
import pytz

from functions.get_mod_func import get_mods
from owner_functions.export_to_JSON import save_data
from owner_functions.import_from_JSON import get_data
from owner_functions import remove_announcement
from owner_functions.min_timestamp import min_timestamp

class OwnerCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.tz = pytz.timezone('Asia/Kolkata')
    self.time_format = "%d-%m-%Y %H:%M:%S"

  def joiner(self, l):
    s = ''
    for i in l:
      s += i + ' '
    return s
  
  def is_admin(self, ctx):
    permissions = ctx.channel.permissions_for(ctx.author)
    mods = get_mods(self.bot, ctx)
    if permissions.administrator or ctx.author in mods:
      return True
    else:
      return False

  
  @commands.group(name='sch', aliases=['schedule'])
  @commands.guild_only()
  async def sch(self, ctx):
    if ctx.invoked_subcommand is None:
      await ctx.send("""
$sch msg = To enter the date, time, place & text of announcement
  Syntax: $sch msg <name of channel> DD-MM-YYYY HH:MM:SS\n<your text of announcement>\nPS: Use 24-hr format""")
  
  @sch.command()
  async def msg(self, ctx, *, inp):
    if self.is_admin(ctx):
      if inp != '':
        inp_list = inp.split()
        channel_name = inp_list.pop(0)

        #as date and time are separated, we are joining them...
        dt = inp_list.pop(0) + ' ' + inp_list.pop(0)

        #using joiner as "".join(inp_list) will just join all words without spaces
        text = self.joiner(inp_list)
        
        #dtObj will be an aware datetime obj after localization
        dtObj = self.tz.localize(datetime.strptime(dt, self.time_format))
        
        if dtObj.timestamp() > datetime.now(self.tz).timestamp():
          #saves the data to a JSON file
          save_data(ctx, channel_name, dt, text, self.tz, self.time_format)
          print(f"An announcement was scheduled for {dt} in {channel_name} by {ctx.author.name}")
          self.checkTime.start('anything go here rn')
        else:
          await ctx.send("Please ensure that you're entering correct datetime.")
      else:
        await ctx.send("Invalid input")
  
  @tasks.loop(seconds=1)
  async def checkTime(self, data):
  
    current_time = datetime.now(self.tz)
    final_timestamp = min_timestamp()
    
    if final_timestamp == int(current_time.timestamp()):
      data = get_data()
      guild = get(self.bot.guilds, name=data['guild'])
      channel = get(guild.text_channels, name=data['channel'])

      print(f"An announcement was made in {channel.name} at {data['datetime']} by {data['author']}")
      await channel.send(data['text'])
      remove_announcement.delete(data)
      
      if get_data() != None:
        self.checkTime(get_data())
      elif get_data() == None:
        self.checkTime.stop()
      
def setup(bot):
  bot.add_cog(OwnerCog(bot))
