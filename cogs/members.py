import disnake
from disnake.ext import commands
import os

# from functions.get_mod_func import get_mods

addRoleEmbedURL = os.environ["addRoleURL"]


class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__doc__ = "Module with members-related commands"
        self.reactions = {
            "Fire-Bender": "🔥",
            "Water-Bender": "🌊",
            "Earth-Bender": "⛰️",
            "Air-Bender": "🌪️",
        }

    def new_member_message(member_name):
        new_member_greeting = f"What's up, {member_name}? I'm Sokka Bot from the Southern Water Tribe.\n\nI can do a bunch of totally weird random stuff.\nTo know more about that, type '$help'.\nAnd if there's something that I can't do, well, blame @Anshu79 for that."
        return new_member_greeting

    def get_roles(self, ctx):
        ourRoles = set(self.reactions.keys())
        userRoles = []
        for role in ctx.author.roles:
            userRoles.append(role.name)
        userRoles = set(userRoles)
        commonRoles = ourRoles.intersection(userRoles)
        return list(commonRoles)

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: disnake.Member):
        guild = member.guild
        sys_msg_channel = guild.system_channel
        await sys_msg_channel.send(self.new_member_message(member.display_name))

    @commands.group(name="role", help="Role related functions")
    async def role(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                """
$role show = Shows your current Bending element
$role add = Choose your Bending element
$role remove = Remove your current element"""
            )

    @role.command()
    async def show(self, ctx):

        commonRoles = self.get_roles(ctx)
        if len(commonRoles) == 1:
            await ctx.reply(f"You are a {str(commonRoles[0])}.")
            print(f"\nTold {ctx.author.name} their bending type.")

        elif len(commonRoles) == 0:
            await ctx.reply("You're not a Bender currently.")

        elif len(commonRoles) > 1:
            await ctx.reply(
                f"Error code: <Not Yet Decided>. Please report this to the admin."
            )

    @role.command()
    async def remove(self, ctx):
        role_list = ctx.author.roles
        for role in role_list:
            if role.name in self.reactions.keys():
                await ctx.author.remove_roles(role)
                print(f"\n{ctx.author.name} is not a {role.name} anymore.")

    @role.command()
    async def add(self, ctx):
        member_roles = []
        for x in ctx.author.roles:
            member_roles.append(x.name)

        if len(self.get_roles(ctx)) == 0:

            addRoleEmbed = disnake.Embed(
                title="Choose Your Bending!", colour=ctx.author.color
            )
            addRoleEmbed.set_image(url=addRoleEmbedURL)

            add_role_message = await ctx.send(embed=addRoleEmbed)

            for reaction in self.reactions:
                await add_role_message.add_reaction(self.reactions[reaction])
        else:
            await ctx.send(
                "You're already a Bender.\nOnly the Avatar can master all 4 elements."
            )

    @commands.Cog.listener("on_raw_reaction_add")
    async def add_role(self, payload):
        user_id = payload.user_id
        bot_id = self.bot.user.id
        payload_emoji = payload.emoji.name
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        msg_link = message.jump_url
        if message.embeds:
            if message.embeds[0].image.url == addRoleEmbedURL:

                def get_commons(member):
                    memberRoles = []
                    for role in member.roles:
                        memberRoles.append(role.name)
                    ourRoles = set(self.reactions.keys())
                    commonRoles = list(set(memberRoles).intersection(ourRoles))
                    return commonRoles

                if user_id != bot_id:
                    guild_id = payload.guild_id
                    guild = self.bot.get_guild(guild_id)
                    member = guild.get_member(user_id)

                    if len(get_commons(member)) == 0:
                        for our_emoji in self.reactions:
                            if payload_emoji == self.reactions[our_emoji]:
                                role = disnake.utils.get(guild.roles, name=our_emoji)
                                if role is not None:
                                    if member is not None:
                                        print(f"\n{member.name} is now a {role.name}")
                                        await member.add_roles(role)
                    else:
                        await member.send(
                            f"Hi! About your reaction to ||<{msg_link}>||\nYou're already a Bender.\nOnly the Avatar can master all 4 elements."
                        )


def setup(bot):
    bot.add_cog(MembersCog(bot))
