from datetime import datetime
import disnake
from disnake.ext import commands, tasks
from disnake.utils import get
import pytz
import uuid

import globals
from mod_functions.data_check import data_check
from mod_functions.export_to_JSON import save_data
from mod_functions.import_from_JSON import get_data
from mod_functions import remove_announcement
from mod_functions.min_time_dict import minTimeDict
from mod_functions.ticket_id_functions import getDictByTicketID
from mod_functions.ticket_id_functions import updateDictByTicketID
from mod_functions.text_to_timestamp import text_2_timestamp
from mod_functions.sch_database_functions import insert


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

    class ScheduleView(disnake.ui.View):
        def __init__(self, ctx, channel_list):
            super().__init__()
            self.subcommand = None
            self.ctx = ctx
            self.channel_list = channel_list

        class NewMsgForm(disnake.ui.Modal):
            def __init__(self, channel_list):
                self.channel_list = channel_list
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

                
                data['guild_name'] = disnake.utils.get(inter.client.guilds, id=inter.guild_id).name

                if data_check(data, self.channel_list):
                    for key, value in inter.text_values.items():
                        embed.add_field(
                            name=key.capitalize(), value=value, inline=False
                        )
                    
                    ticket_id = uuid.uuid4().fields[1]
                    data['ticket_id'] = ticket_id
                    embed.add_field(
                        name='Ticket ID', value=ticket_id, inline=False
                    )
                    embed.set_footer(text='--Remember your Ticket ID--')
                    await insert(data)

                    await inter.response.send_message(embed=embed, ephemeral=True)
                    
                else:
                    await inter.response.send_message(
                        "Unexpected input. Please try again.", ephemeral=True
                    )

        @disnake.ui.button(label="New", style=disnake.ButtonStyle.green)
        async def new(self, button, inter):
            self.subcommand = "New"
            await inter.response.send_modal(self.NewMsgForm(self.channel_list))

        @disnake.ui.button(label="Edit", style=disnake.ButtonStyle.blurple)
        async def edit(self, button, interaction):
            pass

        @disnake.ui.button(label="Delete", style=disnake.ButtonStyle.red)
        async def delete(self, button, interaction):
            pass

    @commands.has_permissions(administrator=True)
    @commands.command(name="purge", help="Deletes a specific number of messages")
    async def purge(self, ctx, number: int):
        await ctx.channel.purge(limit=number)
        print(f"Purged {number} messages in {ctx.channel.name}")

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        if minTimeDict() != None:
            self.checkTime.start(minTimeDict())

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
                "Make the choice, Neo.", view=self.ScheduleView(ctx, text_channel_list)
            )

    @sch.command()
    async def msg(self, ctx, *, inp):
        if self.is_admin(ctx):
            if inp != "":
                inp_list = inp.split()
                channel_name = inp_list.pop(0)

                # as date and time are separated, we are joining them...
                dt = inp_list.pop(0) + " " + inp_list.pop(0)

                text = "".join(i + " " for i in inp_list).rstrip()

                # dtObj will be an aware datetime obj after localization
                dtObj = self.tz.localize(datetime.strptime(dt, self.time_format))

                if dtObj.timestamp() > datetime.now(self.tz).timestamp():
                    # saves the data to a JSON file
                    ticket_id = uuid.uuid4().fields[1]

                    save_data(
                        ctx,
                        channel_name,
                        dt,
                        text,
                        self.tz,
                        self.time_format,
                        ticket_id,
                    )
                    await ctx.reply(f"Message scheduled. Your ticket id is {ticket_id}")
                    print(
                        f"An announcement was scheduled for {dt} in {channel_name} by {ctx.author}"
                    )
                    try:
                        self.checkTime.start("anything go here rn")
                    except RuntimeError:
                        print(
                            "\nAnother message was scheduled earlier than the current one...\n"
                        )
                else:
                    await ctx.send(
                        "Please ensure that you're entering correct datetime."
                    )
            else:
                await ctx.send("Invalid input")

    @sch.command()
    async def edit(self, ctx, t_id, *, data):
        print(getDictByTicketID(int(t_id)))
        if getDictByTicketID(int(t_id)) != None:
            # try:
            updateDictByTicketID(int(t_id), eval(data))
            # except NameError:
            # await ctx.send('You forgot the quotes, mate. Try again.')
            # except SyntaxError:
            # await ctx.send('You forgot the curly braces. Try again.')

    @tasks.loop(seconds=1)
    async def checkTime(self, data):

        current_time = datetime.now(self.tz)
        final_timestamp = text_2_timestamp(minTimeDict()["datetime"])

        if final_timestamp != int(current_time.timestamp()):
            final_timestamp = text_2_timestamp(minTimeDict()["datetime"])

        elif final_timestamp == int(current_time.timestamp()):
            data = get_data()
            guild = get(self.bot.guilds, name=data["guild"])
            channel = get(guild.text_channels, name=data["channel"])

            print(
                f"An announcement was made in {channel.name} at {data['datetime']} by {data['author']}"
            )
            await channel.send(data["text"])
            remove_announcement.delete(data)

            if get_data() != None:
                self.checkTime(get_data())
            elif get_data() == None:
                self.checkTime.stop()


def setup(bot):
    bot.add_cog(ModCog(bot))
