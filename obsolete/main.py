import discord
from discord.ext import commands
from gif_function import gif_func
from greeting_function import say_hello
from joke_function import joke_func
from keep_alive import keep_alive
import os

botToken = os.environ['botToken']
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="$")
bot.remove_command("help")

@bot.event
async def on_ready():
  print("\nI'm ready & logged in as {0.user}!".format(bot))

@bot.event
async def on_member_join(member):
  channel = bot.get_channel(843500905123020802)
  await channel.send("""What's up, {0.name}? I'm Sokka Bot from the Southern Water Tribe.\nI can do a bunch of totally random weird stuff. To know more about that type "$help".\nAnd if there's something that I can't do, well, blame @Anshu79 for that.""".format(member))

@bot.event
async def on_message(message):
  await bot.process_commands(message)

  me = message.guild.get_member(843749034544070666)
  
  if message.author == bot:
    return
  #print(client.users)
  else:
    if gif_func(message):
      await gif_func(message)
  
    if message.content.startswith('$hello'):
      await say_hello(message)
    
    if message.content.startswith('$joke'):
      await joke_func(message)

    if me in message.mentions:
      if "fuck" in message.content.lower():
        gif_url = gif_func(message.content)
        embed = discord.Embed(
          title = '',
          description = "",
          color = message.author.color)
        embed.set_image(url=gif_url)
        await message.channel.send(embed=embed)

@bot.group(invoke_without_command=True)
async def help(ctx):
  em = discord.Embed(title = "Help", description = "Use $help <command> for extended information.", color=ctx.author.color)
  em.add_field(name = "Regular", value="hello")
  em.add_field(name = "Fun", value="joke")
  await ctx.send(embed = em)

@help.command()
async def hello(ctx):
  em = discord.Embed(title = "Say Hello", description="Says Hello to the user.", color=ctx.author.color)
  em.add_field(name="-Syntax-", value="$hello")
  await ctx.send(embed=em)

@help.command()
async def joke(ctx):
  em = discord.Embed(title = "Joke", description="Tells a joke.", color=ctx.author.color)
  em.add_field(name="-Syntax-", value="$joke")
  await ctx.send(embed=em)


keep_alive()
bot.run(botToken)

