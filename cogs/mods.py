from datetime import datetime
import disnake
from disnake.ext import commands, tasks
from disnake.utils import get
import uuid

import globals
from mod_functions.data_check import data_check
from mod_functions.text_to_timestamp import t2t
from mod_functions.sch_database_functions import insert, reader, remover
from mod_functions.generate_ticket import newTicket


class ScheduleView(disnake.ui.View):
    def __init__(self, timeLoop):
        super().__init__()
        self.subcommand = None
        self.timeLoop = timeLoop

    # A form that's displayed when the user selects 'New' in ScheduleView
    class NewMsgForm(disnake.ui.Modal):
        def __init__(self, timeLoop):
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

        # Executed when the user submits the form
        async def callback(self, inter):
            embed = disnake.Embed(title="The below data was saved.")

            keys = [pair[0] for pair in inter.text_values.items()]
            vals = [pair[1] for pair in inter.text_values.items()]

            # A dictionary with the data collected from the form
            data = dict(zip(keys, vals))

            guild = disnake.utils.get(inter.client.guilds, id=inter.guild_id)
            data["guild_name"] = guild.name

            data["author"] = inter.author.name + "#" + inter.author.discriminator

            text_channel_list = [
                channel.name
                for channel in guild.channels
                if str(channel.type) == "text"
            ]
            print(text_channel_list)

            if data_check(data, text_channel_list):

                for key, value in inter.text_values.items():
                    embed.add_field(name=key.capitalize(), value=value, inline=False)
                # A ticket ID is only generated when data_check returns True
                # Repeatedly generating ticket_ids using the while loop
                # if there's a duplicate present in the database
                ticket_id = await newTicket()
                while ticket_id == False:
                    ticket_id = await newTicket()

                data["ticket_id"] = ticket_id

                embed.add_field(name="Ticket ID", value=data["ticket_id"], inline=False)
                embed.set_footer(text="--Remember your Ticket ID--")
                await insert(data)

                print(
                    f"\nAn announcement was scheduled for {data['date']} {data['time']} in {data['channel name']} ({data['guild_name']}) by {inter.author}"
                )
                # A temporary embed is sent to the user
                # displaying inputted data & ticket ID
                await inter.response.send_message(embed=embed, ephemeral=True)

                # Starts the loop if announcements was empty before
                # and loop wasn't running
                if not self.checkTime.is_running():
                    self.checkTime.start()

            else:
                await inter.response.send_message(
                    "Unexpected input. Please try again.", ephemeral=True
                )

    @disnake.ui.button(label="New", style=disnake.ButtonStyle.green)
    async def new(self, button, inter):
        self.subcommand = "New"
        await inter.response.send_modal(self.NewMsgForm(self.timeLoop))

    @disnake.ui.button(label="Edit", style=disnake.ButtonStyle.blurple)
    async def edit(self, button, interaction):
        pass

    @disnake.ui.button(label="Delete", style=disnake.ButtonStyle.red)
    async def delete(self, button, interaction):
        pass


class ModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__doc__ = "Module with commands for mods"

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
        print("\nThe checkTime loop has started.")

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

            # We're passing the checkTime loop to the View because
            # NewMsgForm needs to manage it too
            await ctx.send(
                "Make the choice Neo.",
                view=ScheduleView(self.checkTime),
            )

    @disnake.ext.tasks.loop(seconds=1)
    async def checkTime(self):
        data = await reader()

        # Only continuing the loop if there are some announcements in the DB
        if len(data) != 0:
            msgData = data.pop(0)

            # currentTimestamp is converted to int since we don't deal in ms
            currentTimestamp = int(datetime.now(globals.general["tz"]).timestamp())

            # Sends the message if its send time was in the past or present
            # Sending the messages from past too because they may not have been sent due to some outage
            if t2t(msgData[1]) <= currentTimestamp:

                guild = disnake.utils.get(self.bot.guilds, name=msgData[3])
                channel = disnake.utils.get(guild.text_channels, name=msgData[0])
                author_name = msgData[5].split("#")[0]
                author = disnake.utils.get(guild.members, name=author_name)

                # Getting rid of the extra \ which prevents
                # us from treating \'n' as an escape character
                msg = msgData[2].replace("\\n", "\n")

                msg = (
                    msg
                    + f"\n\nThis message was scheduled by {author.mention} ({msgData[5]})"
                )

                await channel.send(msg)
                await author.send(f"Your message with Ticket ID {msgData[4]} was sent.")
                print(
                    f"\nAn announcement was made in {channel.name} ({msgData[3]}) at {msgData[1]} by {msgData[5]}"
                )

                # Deletes the row of the announcement that was just made
                await remover(msgData[4])

                # Stops the loop if there are no more elements in data
                # after popping out the first element
                if len(data) == 0:
                    self.checkTime.stop()
                    print("\nThe checkTime loop has exited.")

        # Stops the loop if there's no message scheduled
        elif len(data) == 0:
            self.checkTime.stop()
            print("\nThe checkTime loop has exited.")


def setup(bot):
    bot.add_cog(ModCog(bot))
