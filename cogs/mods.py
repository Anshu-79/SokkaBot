from datetime import datetime
import disnake
from disnake.ext import commands, tasks
from disnake.utils import get
import pytz
import uuid

import globals
from mod_functions.data_check import data_check
from mod_functions.text_to_timestamp import t2t
from mod_functions.sch_database_functions import insert, reader, remover


class ScheduleView(disnake.ui.View):
    def __init__(self, timeLoop, channel_list):
        super().__init__()
        self.subcommand = None
        self.timeLoop = timeLoop
        self.channel_list = channel_list

    class NewMsgForm(disnake.ui.Modal):
        def __init__(self, timeLoop, channel_list):
            self.channel_list = channel_list
            self.checkTime = timeLoop
            components = [
                disnake.ui.TextInput(
                    label="Channel Name",
                    custom_id="channel name",
                    placeholder="Scheduled message's destination channel",
                    style=disnake.TextInputStyle.short,
                    max_length=100,
                    required=True,
                ),
                disnake.ui.TextInput(
                    label="Date",
                    custom_id="date",
                    placeholder="DD-MM-YYYY",
                    style=disnake.TextInputStyle.short,
                    min_length=10,
                    max_length=10,
                    required=True,
                ),
                disnake.ui.TextInput(
                    label="Time",
                    custom_id="time",
                    placeholder="HH:MM:SS",
                    style=disnake.TextInputStyle.short,
                    min_length=8,
                    max_length=8,
                    required=True,
                ),
                disnake.ui.TextInput(
                    label="Your Message",
                    custom_id="message",
                    placeholder="Type your message here",
                    style=disnake.TextInputStyle.long,
                    min_length=1,
                    max_length=2000,
                    required=True,
                ),
            ]
            super().__init__(
                title="Schedule New Message",
                custom_id="schNewMsg",
                components=components,
            )

        async def callback(self, inter):
            embed = disnake.Embed(title="The below data was saved.")
            keys = [pair[0] for pair in inter.text_values.items()]
            vals = [pair[1] for pair in inter.text_values.items()]
            data = dict(zip(keys, vals))

            data["guild_name"] = disnake.utils.get(
                inter.client.guilds, id=inter.guild_id
            ).name
            data["author"] = inter.author.name + "#" + inter.author.discriminator

            if data_check(data, self.channel_list):
                for key, value in inter.text_values.items():
                    embed.add_field(name=key.capitalize(), value=value, inline=False)

                ticket_id = uuid.uuid4().fields[1]
                data["ticket_id"] = ticket_id
                embed.add_field(name="Ticket ID", value=ticket_id, inline=False)
                embed.set_footer(text="--Remember your Ticket ID--")
                await insert(data)

                print(
                    f"An announcement was scheduled for {data['date']} {data['time']} in {data['channel name']} by {inter.author}"
                )
                await inter.response.send_message(embed=embed, ephemeral=True)

                if self.checkTime.is_running():
                    self.checkTime.restart()

                if not self.checkTime.is_running():
                    self.checkTime.start()

            else:
                await inter.response.send_message(
                    "Unexpected input. Please try again.", ephemeral=True
                )

    @disnake.ui.button(label="New", style=disnake.ButtonStyle.green)
    async def new(self, button, inter):
        self.subcommand = "New"
        await inter.response.send_modal(
            self.NewMsgForm(self.timeLoop, self.channel_list)
        )

    @disnake.ui.button(label="Edit", style=disnake.ButtonStyle.blurple)
    async def edit(self, button, interaction):
        pass

    @disnake.ui.button(label="Delete", style=disnake.ButtonStyle.red)
    async def delete(self, button, interaction):
        pass


class ModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tz = pytz.timezone("Asia/Kolkata")
        self.time_format = "%d-%m-%Y %H:%M:%S"
        self.__doc__ = "Module with commands for mods"

    def get_channel_list(self):
        text_channel_list = []
        for server in self.bot.guilds:
            for channel in server.channels:
                if str(channel.type) == "text":
                    text_channel_list.append(channel)

    def is_admin(self, ctx):
        permissions = ctx.channel.permissions_for(ctx.author)
        mods = [
            i["mods"] for i in globals.server_dict if i["id"] == ctx.message.guild.id
        ]
        if permissions.administrator or ctx.author in mods:
            return True
        else:
            return False

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        self.checkTime.start()

    @commands.has_permissions(administrator=True)
    @commands.command(name="purge", help="Deletes a specific number of messages")
    async def purge(self, ctx, number: int):
        await ctx.channel.purge(limit=number)
        print(f"Purged {number} messages in {ctx.channel.name}")

    @commands.group(
        name="sch", aliases=["schedule"], help="Message scheduling related commands"
    )
    @commands.guild_only()
    async def sch(self, ctx):
        if ctx.invoked_subcommand is None:
            text_channel_list = [
                channel.name
                for channel in ctx.guild.channels
                if str(channel.type) == "text"
            ]

            await ctx.send(
                "Make the choice, Neo.",
                view=ScheduleView(self.checkTime, text_channel_list),
            )

    @disnake.ext.tasks.loop(seconds=1)
    async def checkTime(self):
        data = await reader()

        if len(data) != 0:
            msgData = data.pop(0)

            # currentTimestamp is converted to int since we don't deal in ms
            currentTimestamp = int(datetime.now(globals.general["tz"]).timestamp())

            if t2t(msgData[1]) <= currentTimestamp:
                guild = disnake.utils.get(self.bot.guilds, name=msgData[3])
                channel = disnake.utils.get(guild.text_channels, name=msgData[0])
                author_name = msgData[5].split("#")[0]
                author = disnake.utils.get(guild.members, name=author_name)
                msg = (
                    msgData[2]
                    + f"\n\nThis message was scheduled by {author.mention} ({msgData[5]})"
                )

                await channel.send(msg)

                print(
                    f"An announcement was made in {channel.name} at {msgData[1]} by {msgData[5]}"
                )
                await remover(msgData[4])

                if len(data) == 0:
                    self.checkTime.stop()

        elif len(data) == 0:
            self.checkTime.stop()


def setup(bot):
    bot.add_cog(ModCog(bot))
