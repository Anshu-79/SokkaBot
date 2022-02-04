import disnake
from disnake.ext import commands
import os

# from functions.get_mod_func import get_mods

addRoleEmbedURL = os.environ["addRoleURL"]

reactions = {
    "Fire-Bender": "🔥",
    "Water-Bender": "🌊",
    "Earth-Bender": "⛰️",
    "Air-Bender": "🌪️",
}


class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__doc__ = "Module with members-related commands"

    class Role(disnake.ui.View):
        def __init__(self, ctx):
            super().__init__()
            self.chosen_func = None
            self.ctx = ctx

        def get_roles(self, ctx):
            ourRoles = set(reactions.keys())
            userRoles = set([role.name for role in ctx.author.roles])
            commonRoles = ourRoles.intersection(userRoles)
            return list(commonRoles)

        async def show_func(self, ctx):
            commonRoles = self.get_roles(ctx)
            if len(commonRoles) == 1:
                print(f"\nTold {ctx.author.name} their bending type.")
                return f"You are a {commonRoles[0]}."

            elif len(commonRoles) == 0:
                return "You're not a Bender currently."

            elif len(commonRoles) > 1:
                return (
                    "Wait... How can you bend 2 elements?! Please contact Anshu79#2928."
                )

        async def remove_func(self, ctx):
            for role in ctx.author.roles:
                if role.name in reactions.keys():
                    await ctx.author.remove_roles(role)
                    print(f"\n{ctx.author.name} is not a {role.name} anymore.")
                    return f"You're not a {role.name} anymore."
            else:
                return "You already aren't a bender."

        async def add_func(self, ctx):
            if len(self.get_roles(ctx)) == 0:

                addRoleEmbed = disnake.Embed(
                    title="Choose Your Bending!", colour=ctx.author.color
                )
                addRoleEmbed.set_image(url=addRoleEmbedURL)

                add_role_message = await ctx.send(embed=addRoleEmbed)

                for reaction in reactions:
                    await add_role_message.add_reaction(reactions[reaction])

                return "Add a reaction to the above message :arrow_up:"

            else:
                return "You're already a Bender.\nOnly the Avatar can master all 4 elements."

        @disnake.ui.button(label="Show Role", style=disnake.ButtonStyle.blurple)
        async def show(
            self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
        ):
            self.chosen_func = "show"
            role = await self.show_func(self.ctx)
            await interaction.response.send_message(role, ephemeral=True)

        @disnake.ui.button(label="Add Role", style=disnake.ButtonStyle.green)
        async def add(self, button, interaction):
            self.chosen_func = "add"
            add_return = await self.add_func(self.ctx)

            await interaction.response.send_message(add_return, ephemeral=True)

        @disnake.ui.button(label="Remove Role", style=disnake.ButtonStyle.red)
        async def remove(self, button, interaction):
            self.chosen_func = "remove"
            removal_msg = await self.remove_func(self.ctx)
            await interaction.response.send_message(removal_msg, ephemeral=True)

    def get_commons(self, member):
        memberRoles = [role.name for role in member.roles]
        ourRoles = set(reactions.keys())
        commonRoles = list(set(memberRoles).intersection(ourRoles))
        return commonRoles

    def new_member_message(member_name):
        new_member_greeting = f"What's up, {member_name}? I'm Sokka Bot from the Southern Water Tribe.\n\nI can do a bunch of totally weird random stuff.\nTo know more about that, type '$help'.\nAnd if there's something that I can't do, well, blame Anshu79#2928 for that."
        return new_member_greeting

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: disnake.Member):
        guild = member.guild
        sys_msg_channel = guild.system_channel
        await sys_msg_channel.send(self.new_member_message(member.display_name))

    @commands.group(name="role", help="Role related functions")
    async def role(self, ctx):
        if ctx.invoked_subcommand is None:
            view = self.Role(ctx)
            await ctx.send("Zhu-Li, do the thing!", view=view)
            await view.wait()

            if view.chosen_func == None:
                print("Role Buttons timed out...")
                await ctx.message.delete()

    # this waits for a reaction to be added to our addRoleEmbed
    @commands.Cog.listener("on_raw_reaction_add")
    async def add_role(self, payload):

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        msg_link = message.jump_url
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        if message.embeds and message.embeds[0].image.url == addRoleEmbedURL:

            if payload.user_id != self.bot.user.id:

                if len(self.get_commons(member)) == 0:
                    for our_emoji in reactions:
                        if payload.emoji.name == reactions[our_emoji]:
                            role = disnake.utils.get(guild.roles, name=our_emoji)
                            if role is not None:
                                if member is not None:
                                    await member.add_roles(role)
                                    print(f"\n{member.name} is now a {role.name}")
                                    await message.delete()
                else:
                    await member.send(
                        f"Hi! About your reaction to ||<{msg_link}>||\nYou're already a Bender.\nOnly the Avatar can master all 4 elements."
                    )


def setup(bot):
    bot.add_cog(MembersCog(bot))
