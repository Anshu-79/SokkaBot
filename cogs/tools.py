import aiohttp
import disnake
from disnake.ext import commands
import json

from loggers import cmdLogger as infoLogger

class ToolsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__doc__ = "Module with commands for general-purpose tools"
        self.ddg_url = "https://cdn.icon-icons.com/icons2/2699/PNG/512/duckduckgo_logo_icon_170206.png"


    @commands.command(name='duckduckgo', help='Does a simple DuckDuckGo search', aliases=['ddg'])
    async def ddg(self, ctx, *, query):
        request = f"https://api.duckduckgo.com/?q={query}&format=json"
        async with aiohttp.ClientSession() as session:
            async with session.get(request) as response:
                
                html = await response.text()
                data = json.loads(html)

        queryEmbed = disnake.Embed(
            title = data['Heading'],
            color = ctx.author.color)

        if data['RelatedTopics']:
            other_results = ''
            for result in data["RelatedTopics"][:5]:
                if 'Text' in result.keys() and 'FirstURL' in result.keys():
                    name=result['Text'][:50]
                    value=result['FirstURL']
                    other_results += f"[{name}...]({value})\n"
            queryEmbed.add_field(
                name="Related Results",
                value=other_results,
                inline=False
            )
    
            if data['Abstract']:
                queryEmbed.add_field(
                    name="Answer",
                    value=data['Abstract'], inline=False
                )
    
            if data['Image']:
                queryEmbed.set_image(
                    url=f'https://duckduckgo.com{data["Image"]}')
    
            if data['Infobox']:
                for section in data['Infobox']['content'][:-1]:
                    queryEmbed.add_field(
                        name=section['label'].title(),
                        value=section['value'],
                        inline=False
                    )
            
            if data['AbstractSource']:
                queryEmbed.add_field(
                    name=data['AbstractSource'],
                    value=f"[{data['Heading']}]({data['AbstractURL']})",
                    inline=True)
    
    
            
        elif not data['RelatedTopics']:
            queryEmbed.set_image(url="https://c.tenor.com/KOZLvzU0o4kAAAAC/no-results.gif")
        
        queryEmbed.set_footer(
            text="Results from DuckDuckGo",
            icon_url = self.ddg_url)

        await ctx.reply(embed=queryEmbed)
        infoLogger.info(f"{ctx.author} queried DDG for {query}")
        

def setup(bot):
    bot.add_cog(ToolsCog(bot))
    