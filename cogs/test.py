import disnake
from disnake.ext import commands


class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.__doc__ == "Commands that are currently under development"

    class MyView(disnake.ui.View):
        def __init__(self):
            super().__init__()

        class MyModal(disnake.ui.Modal):
            def __init__(self):
                components = [
                    disnake.ui.TextInput(
                        label="Text",
                        placeholder="The name of the tag",
                        custom_id="name",
                        style=disnake.TextInputStyle.short,
                        max_length=50,
                    )
                ]
                super().__init__(title="stuff", custom_id="tags", components=components)

            async def callback(self, inter: disnake.ModalInteraction) -> None:
                embed = disnake.Embed(title="Tag Creation")
                for key, value in inter.text_values.items():
                    embed.add_field(name=key.capitalize(), value=value, inline=False)
                await inter.response.send_message(embed=embed)

        @disnake.ui.button(label="Do", style=disnake.ButtonStyle.success)
        async def btn(self, button, interaction):
            form = self.MyModal()
            await interaction.response.send_modal(form)

    @commands.command(name="t")
    async def test(self, ctx):
        view = self.MyView()
        await ctx.send("text", view=view)


def setup(bot):
    bot.add_cog(TestCog(bot))
