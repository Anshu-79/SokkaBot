import asyncio
from datetime import datetime
import disnake
from disnake.ext import commands, tasks
from disnake.utils import get
import logging

import globals
from logger import logger
import dbm_functions as dbm
from loggers import infoLogger
from mod_functions.data_check import data_check
from mod_functions.form_components import formComponents
from mod_functions.sch_database_functions import insert, reader, remover
from mod_functions.text_to_timestamp import t2t
from mod_functions.tickets import newTicket, ticketExists


# The form to be displayed when the user clicks on the New button
class NewMsgForm(disnake.ui.Modal):
    def __init__(self, timeLoop):
        self.checkTime = timeLoop
        # Using a pre-defined list of TextInputs to prevent writing duplicate code
        self.components = formComponents.copy()

        # Making necessary changes
        for comp in self.components:
            comp.required = True
            if comp.placeholder.endswith(" Leave blank if no changes required."):
                comp.placeholder = comp.placeholder[: len(comp.placeholder) - 36]

        super().__init__(
            title="Schedule New Message",
            custom_id="newMsgForm",
            components=self.components,
        )

    # Executed when the user submits the form
    async def callback(self, inter):
        embed = disnake.Embed(
            title="The below data was saved.", color=inter.author.color
        )

        keys = [pair[0] for pair in inter.text_values.items()]
        vals = [pair[1] for pair in inter.text_values.items()]

        # A dictionary with the data collected from the form
        data = dict(zip(keys, vals))

        guild = disnake.utils.get(inter.client.guilds, id=inter.guild_id)
        data["guild"] = guild.name

        data["author"] = inter.author.name + "#" + inter.author.discriminator

        textChannelList = [
            channel.name for channel in guild.channels if str(channel.type) == "text"
        ]

        if await data_check(data, textChannelList):

            for key, value in inter.text_values.items():
                embed.add_field(name=key.capitalize(), value=value, inline=False)
            # A ticket ID is only generated when data_check returns True
            # Repeatedly generating ticket_ids using the while loop
            # if there's a duplicate present in the database
            ticket_id = await newTicket()
            while ticket_id == False:
                ticket_id = await newTicket()

            data["ticket"] = ticket_id

            embed.add_field(name="Ticket ID", value=data["ticket"], inline=False)
            embed.set_footer(text="--Remember your Ticket ID--")
            await insert(data)

            infoLogger.info(
                f"\nAn announcement was scheduled for {data['date']} {data['time']} in {data['channel']} ({data['guild']}) by {inter.author}"
            )
            # A temporary embed is sent to the user
            # displaying inputted data & ticket ID
            await inter.response.send_message(embed=embed, ephemeral=True)
            del self.components

            # Starts the loop if announcements was empty before
            # and loop wasn't running
            if not self.checkTime.is_running():
                self.checkTime.start()
                infoLogger.info("\nThe checkTime loop has started.")

        else:
            await inter.response.send_message(
                "Invalid input. Please try again.", ephemeral=True
            )


# The form to be displayed when the user clicks on Edit
class EditMsgForm(disnake.ui.Modal):
    def __init__(self):

        self.components = formComponents.copy()

        for comp in self.components:
            comp.required = False
            comp.placeholder += " Leave blank if no changes required."

        self.components.insert(
            0,
            disnake.ui.TextInput(
                label="Ticket ID",
                custom_id="ticket_id",
                placeholder="Your message's ticket ID",
                style=disnake.TextInputStyle.short,
                max_length=6,
                required=True,
            ),
        )
        super().__init__(
            title="Edit Message",
            custom_id="editMsgForm",
            components=self.components,
        )

    async def callback(self, inter):

        keys = [pair[0] for pair in inter.text_values.items()]
        vals = [pair[1] for pair in inter.text_values.items()]
        newData = dict(zip(keys, vals))

        if oldData := await ticketExists(newData["ticket_id"]):

            guild = disnake.utils.get(inter.bot.guilds, id=inter.guild_id)
            textChannelList = [
                channel.name
                for channel in guild.channels
                if str(channel.type) == "text"
            ]

            # Replaching items that weren't edited with older data taken from DB
            for key in oldData:
                if key in newData.keys() and newData[key] == "":
                    newData[key] = oldData[key]

            if await data_check(newData, textChannelList):
                embed = disnake.Embed(
                    title="The new data is as follows.", color=inter.author.color
                )

                # Creating a new file new_vals to give it to the DB updater
                # We're doing so because newData needs to have separate date, time
                # columns but updater() only accepts values that are in the table itself
                new_vals = newData.copy()
                new_vals["datetime"] = new_vals["date"] + new_vals["time"]
                del new_vals["date"], new_vals["time"]

                await dbm.updater(
                    table="announcements",
                    new_vals=new_vals,
                    conditions=f"ticket_id = {int(new_vals['ticket_id'])}",
                )

                for key in newData:
                    embed.add_field(
                        name=key.capitalize().replace("_", " "),
                        value=newData[key],
                        inline=False,
                    )

                embed.set_footer(text="--Remember your Ticket ID--")
                await inter.response.send_message(embed=embed, ephemeral=True)
                del self.components

            else:
                await inter.response.send_message(
                    "Invalid input. Please try again.", ephemeral=True
                )

        else:
            await inter.response.send_message("Invalid ticket ID", ephemeral=True)


class DeleteMsgForm(disnake.ui.Modal):
    def __init__(self, delay):
        self.delay = delay

        self.components = [
            disnake.ui.TextInput(
                label="Ticket ID",
                placeholder="Enter your Ticket ID",
                custom_id="ticket_id",
                style=disnake.TextInputStyle.short,
                max_length=6,
                required=True,
            ),
        ]

        super().__init__(
            title="Delete Scheduled Message",
            components=self.components,
            custom_id="deleteMsgForm",
        )

    async def callback(self, inter):
        # Getting the value of the first item in
        ticket_id = [item[1] for item in inter.text_values.items()][0]

        if await ticketExists(ticket_id):

            data = [i for i in await reader() if i[4] == int(ticket_id)][0]

            if data[5] == str(inter.author):

                await inter.response.send_message(
                    f"The message will be deleted after {self.delay} seconds.\nSend a 'Q' to cancel the operation.",
                    ephemeral=True,
                )

                def check(m):
                    return (
                        m.content.upper() == "Q"
                        and m.channel.id == inter.channel_id
                        and m.author == inter.author
                    )

                # Waits for some time before deletion
                try:
                    quitMessage = await inter.client.wait_for(
                        "message", check=check, timeout=self.delay
                    )
                    await inter.send(content="Deletion cancelled", ephemeral=True)
                    await quitMessage.delete(delay=self.delay)

                except asyncio.exceptions.TimeoutError:
                    await remover(ticket_id)
                    await inter.send(
                        content=f"Deleted message with Ticket ID = {ticket_id}",
                        ephemeral=True,
                    )
                    infoLogger.info(f"\nDeleted message with Ticket ID = {ticket_id}")
            else:
                await inter.response.send_message(
                    f"You are not the maker of the announcement with Ticket ID = {ticket_id}"
                )
        else:
            await inter.response.send_message("Invalid Ticket ID", ephemeral=True)


class ScheduleView(disnake.ui.View):
    def __init__(self, timeLoop):
        super().__init__()
        self.subcommand = None
        self.timeLoop = timeLoop

    @disnake.ui.button(label="New", style=disnake.ButtonStyle.green)
    async def new(self, button, inter):
        await inter.response.send_modal(NewMsgForm(self.timeLoop))

    @disnake.ui.button(label="Edit", style=disnake.ButtonStyle.blurple)
    async def edit(self, button, inter):
        await inter.response.send_modal(EditMsgForm())

    @disnake.ui.button(label="Delete", style=disnake.ButtonStyle.red)
    async def delete(self, button, inter):
        await inter.response.send_modal(DeleteMsgForm(5))


class ModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__doc__ = "Module with commands for mods"

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        self.checkTime.start()
        infoLogger.info("\nThe checkTime loop has started.")

    @commands.has_permissions(administrator=True)
    @commands.command(name="purge", help="Deletes a specific number of messages")
    async def purge(self, ctx, number: int):
        await ctx.channel.purge(limit=number)
        infoLogger.info(f"Purged {number} messages in {ctx.channel.name}")

    @commands.has_permissions(administrator=True)
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
                infoLogger.info(
                    f"\nAn announcement was made in {channel.name} ({msgData[3]}) at {msgData[1]} by {msgData[5]}"
                )

                # Deletes the row of the announcement that was just made
                await remover(msgData[4])

                # Stops the loop if there are no more elements in data
                # after popping out the first element
                if len(data) == 0:
                    self.checkTime.stop()
                    infoLogger.info("\nThe checkTime loop has exited.")

        # Stops the loop if there's no message scheduled
        elif len(data) == 0:
            self.checkTime.stop()
            infoLogger.info("\nThe checkTime loop has exited.")


def setup(bot):
    bot.add_cog(ModCog(bot))
