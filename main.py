import disnake
from disnake.ext import commands
import os

from keep_alive import keep_alive

import traceback

hal_url = os.environ["halURL"]

botToken = os.environ["botToken"]


def get_prefix(bot, message):

    prefixes = ["$"]

    if not message.guild:
        return "$"

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


def fancy_traceback(exc: Exception) -> str:
    # if the text may not fit the message content limit
    text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    return f"```py\n{text[-512:]}\n```"


cogs = [
    "cogs.mods",
    "cogs.common",
    "cogs.members",
    "cogs.music",
    "cogs.help",
    "cogs.test",
]

intents = disnake.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=get_prefix, intents=intents)


class SokkaBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            intents=intents,
            help_command=None,
        )

    def load_all_extensions(self, cogs_list):
        print("Loading cogs...\n")
        for cog in cogs_list:
            self.load_extension(cog)
            print(f"{cog} was loaded.")

    async def on_ready(self):
        print(f"\nLogged in as: {bot.user.name} - {bot.user.id}")

        # loop = asyncio.get_event_loop()
        # await loop.run_until_complete(reader)

        print("\nI'm ready to chat!")

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
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
