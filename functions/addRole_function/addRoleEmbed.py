import disnake
from functions.addRole_function.addRoleEmbedURL import url as url


def addRoleEmbed_func(author):
    addRoleEmbed = disnake.Embed(title="Choose Your Bending!", colour=author.color)
    addRoleEmbed.set_image(url=url)
    # fire = Button(style=ButtonStyle.red, label="Fire-bender")

    return addRoleEmbed
