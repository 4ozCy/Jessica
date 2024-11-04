# main.py

import discord
from discord.ext import commands, tasks
import asyncio
import aiohttp
import numpy as np
from fastapi import FastAPI
from uvicorn import Config, Server
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())
afk_users = {}
connect4_games = {}

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

class Connect4:
    def __init__(self):
        self.board = np.zeros((6, 7), int)
        self.current_player = 1

    def drop_piece(self, column):
        for row in range(5, -1, -1):
            if self.board[row][column] == 0:
                self.board[row][column] = self.current_player
                return row, column
        return None

    def is_winning_move(self, row, col):
        return (self.check_direction(row, col, 1, 0) or
                self.check_direction(row, col, 0, 1) or
                self.check_direction(row, col, 1, 1) or
                self.check_direction(row, col, 1, -1))

    def check_direction(self, row, col, delta_row, delta_col):
        count = 0
        for delta in range(-3, 4):
            r, c = row + delta * delta_row, col + delta * delta_col
            if 0 <= r < 6 and 0 <= c < 7 and self.board[r][c] == self.current_player:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
        return False

    def display_board(self):
        emoji_board = ''
        for row in self.board:
            emoji_board += ' '.join(['⚪' if cell == 0 else '🔴' if cell == 1 else '🟡' for cell in row]) + '\n'
        emoji_board += ' '.join([f'{i + 1}⃣' for i in range(7)])
        return emoji_board

@bot.command(name='cmds')
async def send_help(ctx):
    class HelpSelect(Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="General", description="General commands", emoji="🔧"),
                discord.SelectOption(label="Fun", description="Fun commands", emoji="🎉")
            ]
            super().__init__(placeholder='Choose a category...', min_values=1, max_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            embed = discord.Embed(title=f"{self.values[0]} Commands", color=discord.Color.blurple())
            embed.set_thumbnail(url=client.user.avatar.url)
            embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
            embed.timestamp = discord.utils.utcnow()

            if self.values[0] == "General":
                embed.add_field(name="av", value="Display user avatar", inline=False)
                embed.add_field(name="sf", value="Get server information", inline=False)
                embed.add_field(name="binfo", value="Get bot information", inline=False)

            elif self.values[0] == "Fun":
                embed.add_field(name="quote", value="Send a random inspirational quote", inline=False)
                embed.add_field(name="rizz", value="Rizz You Up", inline=False)
                embed.add_field(name="joke", value="Tell a random joke", inline=False)
                embed.add_field(name="slap", value="Slap someone", inline=False)
                embed.add_field(name="punch/p", value="Punch someone", inline=False)
                embed.add_field(name="coin flip", value="Play coin flip", inline=False)
                embed.add_field(name="8ball", value="Magic 8-ball that gives a random response to yes/no questions", inline=False)
                
            await interaction.response.edit_message(embed=embed, view=self.view)

    class HelpView(View):
        def __init__(self):
            super().__init__()
            self.add_item(HelpSelect())

    embed = discord.Embed(title="Commands List", description="Select a category to view commands.", color=discord.Color.blurple())
    embed.set_thumbnail(url=client.user.avatar.url)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
    embed.timestamp = discord.utils.utcnow()
    
    view = HelpView()
    await ctx.send(embed=embed, view=view)

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
    embed.add_field(name="Avatar URL", value=bot.user.avatar.url, inline=False)
    embed.add_field(name="Banner URL", value=bot.user.banner.url if bot.user.banner else "None", inline=False)
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
    embed = discord.Embed(title=f"{guild.name} Server Information", color=discord.Color.blue())
    embed.set_thumbnail(url=str(guild.icon.url))
    embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else 'N/A', inline=True)
    embed.add_field(name="Server ID", value=guild.id, inline=True)
    embed.add_field(name="Member Count", value=guild.member_count, inline=True)
    embed.add_field(name="Creation Date", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Role Count", value=len(guild.roles), inline=True)
    embed.add_field(name="Emoji Count", value=len(guild.emojis), inline=True)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
    embed.timestamp = discord.utils.utcnow()

    await ctx.send(embed=embed)

@bot.command(name='quote')
async def send_quote(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.quotable.io/random") as response:
            if response.status == 200:
                data = await response.json()
                quote = data.get("content", "Sorry for error:(")
                embed = discord.Embed(description=quote, color=discord.Color.blurple())
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
                gif_url = data['link']

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

@bot.command(name='c4')
async def connect4(ctx, opponent: discord.User):
    if ctx.channel.id in connect4_games:
        await ctx.send("A game is already in progress in this channel!")
        return

    if opponent == ctx.author:
        await ctx.send("You can't play against yourself!")
        return

    await ctx.send(f"{opponent.mention}, {ctx.author.mention} has challenged you to a game of Connect4! Type 'yes' to accept or 'no' to decline.")

    def check(message):
        return message.author == opponent and message.content.lower() in ["yes", "no"] and message.channel == ctx.channel

    try:
        response = await bot.wait_for("message", check=check, timeout=300.0)
        if response.content.lower() == "yes":
            connect4_games[ctx.channel.id] = Connect4()
            embed = discord.Embed(
                title=f"Connect 4: {ctx.author.mention} vs {opponent.mention}",
                description=connect4_games[ctx.channel.id].display_board()
            )
            await ctx.send(embed=embed)
            await ctx.send(f"{ctx.author.mention}, it's your turn! Type a column number (1-7) to drop your piece.")
        else:
            await ctx.send(f"{opponent.mention} declined the game.")
    except asyncio.TimeoutError:
        await ctx.send(f"{opponent.mention} did not respond in time. Game request canceled.")

@bot.listen('on_message')
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id in connect4_games:
        game = connect4_games[message.channel.id]
        if message.author.id == game.current_player:
            try:
                column = int(message.content) - 1
                if 0 <= column < 7:
                    position = game.drop_piece(column)
                    if position:
                        if game.is_winning_move(position[0], position[1]):
                            await message.channel.send(f"{message.author.mention} wins! 🎉")
                            del connect4_games[message.channel.id]
                        else:
                            game.current_player = 2 if game.current_player == 1 else 1
                            embed = discord.Embed(
                                title=f"Connect 4",
                                description=game.display_board()
                            )
                            await message.channel.send(embed=embed)
                            await message.channel.send(f"Your turn, <@{game.current_player}>! Type a column number (1-7).")
                    else:
                        await message.channel.send("Column is full! Choose another column.")
                else:
                    await message.channel.send("Please enter a valid column number (1-7).")
            except ValueError:
                await message.channel.send("Please enter a valid number.")

bot.run(os.getenv('TOKEN'))
