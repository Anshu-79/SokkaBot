import disnake
from disnake.ext import commands
import logging
import os
from sty import fg
import traceback

from keep_alive import keep_alive
from loggers import initLogger
from loggers import errorLogger
initLogger.setLevel(logging.INFO)

hal_url = os.environ["halURL"]

botToken = os.environ["botToken"]


def get_prefix(bot, message):

    prefixes = ["$"]

    if not message.guild:
        return "$"

    # Allow user to mention bot using above prefixes if in a guild 
    return commands.when_mentioned_or(*prefixes)(bot, message)


def fancy_traceback(exc: Exception) -> str:
    # if the text may not fit the message content limit
    text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    errorLogger.warning(f"Exception occured\n{text}")
    return f"```py\n{text[-512:]}\n```"


cogs = os.listdir("cogs")
cogs = ["cogs." + file.split(".")[0] for file in cogs if file.endswith(".py")]

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
        initLogger.info("Loading cogs...\n")
        for cog in cogs_list:
            self.load_extension(cog)
            initLogger.info(f"{cog} was loaded.")

    async def on_ready(self):
        initLogger.info(f"\nLogged in as: {bot.user.name} - {bot.user.id}")

        # loop = asyncio.get_event_loop()
        # await loop.run_until_complete(reader)

        initLogger.info("\nI'm ready to chat!")

    async def on_command_error(self, ctx, error):
        embed = disnake.Embed(
            title=f"I'm sorry, {ctx.author.name}. I'm afraid I can't do that.",
            description=f"Command `{ctx.command}` failed due to `{error}`\n{fancy_traceback(error)}",
            color=disnake.Color.red(),
        )
        embed.set_thumbnail(url=hal_url)
        await ctx.send(embed=embed)

bot = SokkaBot()
bot.remove_command("help")
bot.load_all_extensions(cogs)

initLogger.info(f"disnake: {disnake.__version__}\n")

keep_alive()

bot.run(botToken)
