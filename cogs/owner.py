from datetime import datetime, timedelta
from discord.ext import commands
from discord.utils import get
import pytz
import time
import threading

from functions.get_mod_func import get_mods
from announcement_storage import declare_list

global Queue
#a Queue class to be able to return a value from a thread
class Queue(object):
  def __init__(self):
    self.item = []

  def __repr__(self):
    return f"{self.item}"

  def __str__(self):
    return f"{self.item}"
  
  def enque(self, add):
    self.item.insert(0, add)
    return True

  def size(self):
    return len(self.item)

  def deque(self):
    if self.size() == 0:
      return None
    else:
      return self.item.pop()
  
  def isempty(self):
    if self.size() == 0:
      return True
    else: 
      return False


class OwnerCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.timezone = pytz.timezone('Asia/Kolkata')
    self.time_format = "%d-%m-%Y %H:%M:%S"
    self.queue = Queue()

  def is_admin(self, ctx):
    permissions = ctx.channel.permissions_for(ctx.author)
    mods = get_mods(self.bot, ctx)
    if permissions.administrator or ctx.author in mods:
      return True
    else:
      return False

  def checkTime(self, sendTimeObj, out_queue):
    current_time = datetime.now(self.timezone)
    
    while current_time.timestamp() <= sendTimeObj.timestamp():
      time.sleep(1)
      current_time = datetime.now(self.timezone)
      print(int(current_time.timestamp()), int(sendTimeObj.timestamp()))
    
      if int(current_time.timestamp()) == int(sendTimeObj.timestamp()):
        self.queue.enque(True)

  
  @commands.group(name='sch', aliases=['schedule'])
  @commands.guild_only()
  async def sch(self, ctx):
    if ctx.invoked_subcommand is None:
      await ctx.send("""
$sch msg = To enter the date, time, place & text of announcement
  Syntax: $sch msg <name of channel> DD-MM-YYYY HH:MM:SS\n<your text of announcement>\nPS: Use 24-hr format""")

  @sch.command()
  async def msg(self, ctx, channel_name, d, t, text):
    if self.is_admin(ctx):
      if text != '':
        #dt & dtObj will be in IST
        dt = d + ' ' + t
        dtObj = self.timezone.localize(datetime.strptime(dt, self.time_format))
        print('step1')
        #print(dtObj.timestamp(), datetime.now(self.timezone).timestamp())
        if dtObj.timestamp() > datetime.now(self.timezone).timestamp():
          
          declare_list.append({'channel': channel_name})
          declare_list[-1]['text'] = f"{text}\n\nThis was an announcement made by {ctx.author}."
          declare_list[-1]['datetime'] = dtObj
          print('step2')
        t1 = threading.Thread(target=self.checkTime, args=(dtObj, self.queue))
        t1.start()

        while True:
          flag = self.queue.isempty()
          if flag:
            break
          else:
            print(self.queue.deque())
            break
          
      else:
        await ctx.send("Please ensure that you're entering correct datetime.")
     
def setup(bot):
  bot.add_cog(OwnerCog(bot))
