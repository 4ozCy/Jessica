import discord
from discord.ext import commands, tasks
from discord import ButtonStyle, Interaction
from discord.ui import Select, View
import asyncio
import aiohttp
import random
from fastapi import FastAPI
from uvicorn import Config, Server
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())
afk_users = {}

app = FastAPI()

@app.get("/")
async def read_root():
    return {"status": "online"}

@tasks.loop(count=1)
async def start_fastapi():
    config = Config(app=app, host="0.0.0.0", port=8080, log_level="info")
    server = Server(config)
    await server.serve()

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=".cmds"))
    bot.start_time = discord.utils.utcnow()
    print(f'Bot connected as {bot.user}')
    start_fastapi.start()

@bot.command(name='cmds')
async def send_help(ctx):
    class HelpSelect(Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="General", description="General commands", emoji="<a:general:1303003546387480606>"),
                discord.SelectOption(label="Fun", description="Fun commands", emoji="<a:confetti:1303003580122529852>")
            ]
            super().__init__(placeholder=' Choose a category...', min_values=1, max_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            embed = discord.Embed(title=f"{self.values[0]} Commands", color=discord.Color.blurple())
            embed.set_thumbnail(url=bot.user.avatar.url)
            embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
            embed.timestamp = discord.utils.utcnow()

            if self.values[0] == "General":
                
                embed.add_field(name="av", value="Display user avatar", inline=True)
                embed.add_field(name="sf", value="Get server information", inline=True)
                embed.add_field(name="binfo", value="Get bot information", inline=True)

            elif self.values[0] == "Fun":

                embed.add_field(name="xo", value="play xo with someone", inline=True)
                embed.add_field(name="rizz", value="Rizz You Up", inline=True)
                embed.add_field(name="slap", value="Slap someone", inline=True)
                embed.add_field(name="coin flip", value="Play coin flip", inline=True)
                embed.add_field(name="8ball", value="Magic 8-ball that response to yes/no questions", inline=True)
                
            await interaction.response.edit_message(embed=embed, view=self.view)

    class HelpView(View):
        def __init__(self):
            super().__init__()
            self.add_item(HelpSelect())

    embed = discord.Embed(title="Commands List", description="Select a category to view commands.", color=discord.Color.blurple())
    embed.set_thumbnail(url=bot.user.avatar.url)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
    embed.timestamp = discord.utils.utcnow()
    
    view = HelpView()
    await ctx.send(embed=embed, view=view)

@bot.command(name='xo')
async def xo(ctx, opponent: discord.Member):
    if opponent == ctx.author:
        await ctx.send("You can't play against yourself!")
        return

    players = {ctx.author: "❌", opponent: "⭕"} if random.choice([True, False]) else {ctx.author: "O", opponent: "X"}
    current_player = random.choice([ctx.author, opponent])

    turn_message = await ctx.send(f"Game Start! {ctx.author.mention} is `{players[ctx.author]}`, {opponent.mention} is `{players[opponent]}`. {current_player.mention}'s turn.")

    class TicTacToeButton(discord.ui.Button):
        def __init__(self, x, y):
            super().__init__(label="‎‎  - ‎ ", style=discord.ButtonStyle.secondary, row=x)
            self.x = x
            self.y = y

        async def callback(self, interaction: discord.Interaction):
            nonlocal current_player

            if interaction.user != current_player:
                await interaction.response.send_message("It's not your turn!", ephemeral=True)
                return

            self.label = players[current_player]
            self.style = discord.ButtonStyle.success if players[current_player] == "X" else discord.ButtonStyle.danger
            self.disabled = True
            await interaction.response.edit_message(view=view)

            if check_winner():
                await turn_message.edit(content=f"{current_player.mention} wins!")
                view.disable_all_items()
                await interaction.message.edit(view=view)
                return

            if all(button.disabled for button in view.children):
                await turn_message.edit(content="It's a draw!")
                return

            current_player = opponent if current_player == ctx.author else ctx.author
            await turn_message.edit(content=f"{current_player.mention}'s turn.")

    def check_winner():
        for i in range(3):
            if view.board[i][0].label == view.board[i][1].label == view.board[i][2].label != "·":
                return True
            if view.board[0][i].label == view.board[1][i].label == view.board[2][i].label != "·":
                return True
        if view.board[0][0].label == view.board[1][1].label == view.board[2][2].label != "·":
            return True
        if view.board[0][2].label == view.board[1][1].label == view.board[2][0].label != "·":
            return True
        return False

    class TicTacToeView(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.board = [[TicTacToeButton(x, y) for y in range(3)] for x in range(3)]
            for row in self.board:
                for button in row:
                    self.add_item(button)

    view = TicTacToeView()
    await ctx.send("Tic Tac Toe:", view=view)
            
@bot.command(name='rizz', aliases=['r'])
async def send_rizz(ctx, member: discord.Member = None):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.jcwyt.com/pickup") as response:
                data = await response.text()

        lines = data.split("{answer}")
        pickup_line = "\n".join(lines).strip()

        if member:
            response_message = f"Hey {member.mention},\n{pickup_line}"
        else:
            response_message = pickup_line

        embed = discord.Embed(description=response_message, color=discord.Color.blurple())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"An error occurred while fetching pickup line: {e}")
        await ctx.send("Sorry for error:(")

@bot.command(name='binfo')
async def bot_info(ctx):
    embed = discord.Embed(title="Bot Information", color=discord.Color.blurple())
    
    embed.add_field(name="Bot Name", value=bot.user.name, inline=True)
    embed.add_field(name="Bot ID", value=bot.user.id, inline=True)
    
    owner = await bot.fetch_user(bot.application.owner.id)
    embed.add_field(name="Bot Owner", value="@n.int", inline=True)
    embed.add_field(name="Owner ID", value=owner.id, inline=True)

    embed.add_field(name="Server Count", value=len(bot.guilds), inline=True)
    embed.add_field(name="User Count", value=len(set(bot.get_all_members())), inline=True)
    embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    
    embed.add_field(name="Creation Date", value=bot.user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Language", value="Python", inline=True)
    embed.add_field(name="Library", value="discord.py", inline=True)
    embed.add_field(name="Version", value="2.0.0", inline=True)
    embed.add_field(name="Total Commands", value=len(bot.commands), inline=True)
    
    uptime = discord.utils.utcnow() - bot.start_time
    embed.add_field(name="Uptime", value=str(uptime).split(".")[0], inline=True)
    
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
    embed.timestamp = discord.utils.utcnow()
    
    await ctx.send(embed=embed)
    
@bot.command(name='cf')
async def coin(ctx):
    result = random.choice(['Heads', 'Tails'])
    embed = discord.Embed(title="🪙 Coin Flip", description=f"The coin landed on **{result}**!", color=discord.Color.blurple())
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

@bot.command(name='8ball')
async def eight_ball(ctx, *, question: str):
    responses = [
        "It is certain.", "It is decidedly so.", "Without a doubt.",
        "Yes – definitely.", "You may rely on it.", "As I see it, yes.",
        "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
        "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.",
        "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."
    ]
    response = random.choice(responses)
    
    embed = discord.Embed(title="🎱 8Ball", color=discord.Color.blurple())
    embed.add_field(name="Question:", value=question, inline=False)
    embed.add_field(name="Answer:", value=response, inline=False)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

@bot.command(name='sf')
async def server(ctx):
    guild = ctx.guild

    if guild is None:
        await ctx.send("This command can only be used in a server.")
        return

    embed = discord.Embed(title=f"{guild.name} Server Information", color=discord.Color.blue())
    
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else 'N/A', inline=True)
    embed.add_field(name="Server ID", value=guild.id, inline=True)
    embed.add_field(name="Member Count", value=guild.member_count, inline=True)
    embed.add_field(name="Creation Date", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Role Count", value=len(guild.roles), inline=True)
    embed.add_field(name="Emoji Count", value=len(guild.emojis), inline=True)
    embed.add_field(name="Verification Level", value=guild.verification_level, inline=True)
    embed.add_field(name="Boost Count", value=guild.premium_subscription_count, inline=True)

    top_roles = ', '.join([role.name for role in guild.roles if role.name != "@everyone"][:5]) or 'None'
    embed.add_field(name="Top Roles", value=top_roles, inline=False)

    if ctx.author.avatar:
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
    else:
        embed.set_footer(text=f"Requested by {ctx.author}")

    embed.timestamp = discord.utils.utcnow()

    await ctx.send(embed=embed)
    
@bot.command(name='slap')
async def slap(ctx, member: discord.Member):
    if member == ctx.author:
        await ctx.send(f"{ctx.author.mention} tries to slap themselves... but it doesn't work that way!")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.otakugifs.xyz/gif?reaction=slap&format=gif") as response:
            if response.status == 200:
                data = await response.json()
                gif_url = data['url']

                embed = discord.Embed(
                    title="Slap!",
                    description=f"{ctx.author.mention} slaps {member.mention} in the face!",
                    color=discord.Color.blurple()
                )
                embed.set_image(url=gif_url)
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
                embed.timestamp = discord.utils.utcnow()
                await ctx.send(embed=embed)
            else:
                await ctx.send("Sorry for error:(")

@bot.command(name='av')
async def avatar(ctx, *, member: discord.Member = None):
    if not member:
        member = ctx.author

    embed = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.blue())
    embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)

    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
    embed.timestamp = discord.utils.utcnow()
    
    await ctx.send(embed=embed)

bot.run(os.getenv('TOKEN'))
