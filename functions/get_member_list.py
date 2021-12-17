
def get_member_list(bot):
  members = []
  for guild in bot.guilds:
    for member in guild.members:
      members.append(member)
  return members