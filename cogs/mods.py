from datetime import datetime
from disnake.ext import commands, tasks
from disnake.utils import get
import pytz
import uuid


from functions.get_mod_func import get_mods
from mod_functions.export_to_JSON import save_data
from mod_functions.import_from_JSON import get_data
from mod_functions import remove_announcement
from mod_functions.min_time_dict import minTimeDict
from mod_functions.ticket_id_functions import getDictByTicketID
from mod_functions.ticket_id_functions import updateDictByTicketID
from mod_functions.text_to_timestamp import text_2_timestamp

class ModCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.tz = pytz.timezone('Asia/Kolkata')
    self.time_format = "%d-%m-%Y %H:%M:%S"
    self.__doc__ = 'Module with commands for mods'

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

  
  @commands.has_permissions(administrator=True)
  @commands.command(name='purge', help='Deletes a specific number of messages')
  async def purge(self, ctx, number: int):
    await ctx.channel.purge(limit=number)
    print(f'Purged {number} messages in {ctx.channel.name}')

  
  @commands.Cog.listener('on_ready')
  async def on_ready(self):
    if minTimeDict() != None:
      self.checkTime.start(minTimeDict())

  
  @commands.group(name='sch', aliases=['schedule'], help="Message scheduling related commands")
  @commands.guild_only()
  async def sch(self, ctx):
    if ctx.invoked_subcommand is None:
      await ctx.send("""
$sch msg = To enter the date, time, place & text of announcement
      Syntax: $sch msg <name of channel> DD-MM-YYYY HH:MM:SS <your text of announcement>\nPS: Use 24-hr format\n\n
$sch edit = To edit a pre-scheduled message
      Syntax: $sch edit <ticket ID>
      {<Whichever entry you want to edit>}
      For eg: {"text": "<New text>",
              "channel": "<New channel>"} \nPS: The curly braces and quotes are important
  """)
  
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
          ticket_id = uuid.uuid4().fields[1]
          
          save_data(ctx, channel_name, dt, text, self.tz, self.time_format, ticket_id)
          await ctx.reply(f"Message scheduled. Your ticket id is {ticket_id}")
          print(f"An announcement was scheduled for {dt} in {channel_name} by {ctx.author.name}")
          try:
            self.checkTime.start('anything go here rn')
          except RuntimeError:
            print('\nAnother message was scheduled earlier than the current one...\n')
        else:
          await ctx.send("Please ensure that you're entering correct datetime.")
      else:
        await ctx.send("Invalid input")

  @sch.command()
  async def edit(self, ctx, t_id, *, data):
    print(getDictByTicketID(int(t_id)))
    if getDictByTicketID(int(t_id)) != None:
      #try:
      updateDictByTicketID(int(t_id), eval(data))
      #except NameError:
       # await ctx.send('You forgot the quotes, mate. Try again.')
      #except SyntaxError:
       # await ctx.send('You forgot the curly braces. Try again.')

  
  @tasks.loop(seconds=1)
  async def checkTime(self, data):
    
    current_time = datetime.now(self.tz)
    final_timestamp = text_2_timestamp(minTimeDict()['datetime'])
    
    if final_timestamp != int(current_time.timestamp()):
      final_timestamp = text_2_timestamp(minTimeDict()['datetime'])
    
    elif final_timestamp == int(current_time.timestamp()):
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
  bot.add_cog(ModCog(bot))
