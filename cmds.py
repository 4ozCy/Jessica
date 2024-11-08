import discord
from discord.ext import commands
from discord.ui import Select, View

def setup_cmds(bot):

    @bot.command(name='cmds')
    async def send_help(ctx):
        class HelpSelect(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="General", description="General commands", emoji="🌐"),
                    discord.SelectOption(label="Fun", description="Fun commands", emoji="🎉")
                ]
                super().__init__(placeholder='Choose a category...', min_values=1, max_values=1, options=options)

            async def callback(self, interaction: discord.Interaction):
                embed = discord.Embed(title=f"{self.values[0]} Commands", color=discord.Color.blurple())
                embed.set_thumbnail(url=bot.user.avatar.url)
                embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
                embed.timestamp = discord.utils.utcnow()

                if self.values[0] == "General":
                    embed.add_field(name="av", value="Display user avatar", inline=True)
                    embed.add_field(name="sf", value="Get server information", inline=True)
                    embed.add_field(name="binfo", value="Get bot information", inline=True)
                    embed.add_field(name="uf", value="Get user information", inline=True)

                elif self.values[0] == "Fun":
                    embed.add_field(name="xo", value="Play XO with someone", inline=True)
                    embed.add_field(name="rizz", value="Rizz You Up", inline=True)
                    embed.add_field(name="slap", value="Slap someone", inline=True)
                    embed.add_field(name="coin flip", value="Play coin flip", inline=True)
                    embed.add_field(name="8ball", value="Magic 8-ball response", inline=True)
                    embed.add_field(name="rps", value="Play Rock Paper Scissor", inline=True)

                await interaction.response.edit_message(embed=embed, view=self.view)

        class HelpView(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.add_item(HelpSelect())

        embed = discord.Embed(title="Commands List", description="Select a category to view commands.", color=discord.Color.blurple())
        embed.set_thumbnail(url=bot.user.avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.timestamp = discord.utils.utcnow()

        view = HelpView()
        await ctx.send(embed=embed, view=view)
