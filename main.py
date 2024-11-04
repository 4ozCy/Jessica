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

    class InvitationView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            self.value = None

        @discord.ui.button(label="Accept", style=ButtonStyle.success)
        async def accept(self, interaction: Interaction, button: discord.ui.Button):
            if interaction.user != opponent:
                await interaction.response.send_message("Only the invited player can accept!", ephemeral=True)
                return
            self.value = True
            self.stop()

        @discord.ui.button(label="Decline", style=ButtonStyle.danger)
        async def decline(self, interaction: Interaction, button: discord.ui.Button):
            if interaction.user != opponent:
                await interaction.response.send_message("Only the invited player can decline!", ephemeral=True)
                return
            self.value = False
            self.stop()

    invitation_view = InvitationView()
    invitation_message = await ctx.send(
        f"Hey {opponent.mention}, {ctx.author.mention} has challenge you to play XO", 
        view=invitation_view
    )
    await invitation_view.wait()
    await invitation_message.delete()

    if invitation_view.value is None:
        await ctx.send("Invitation timed out.")
        return
    elif not invitation_view.value:
        await ctx.send(f"{opponent.mention} declined the invitation.")
        return

    symbols = ["X", "O"]
    random.shuffle(symbols)
    players = {ctx.author: symbols[0], opponent: symbols[1]}
    current_player = random.choice([ctx.author, opponent])

    board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]

    def check_winner():
        for row in board:
            if row[0] == row[1] == row[2] != " ":
                return True
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] != " ":
                return True
        if board[0][0] == board[1][1] == board[2][2] != " ":
            return True
        if board[0][2] == board[1][1] == board[2][0] != " ":
            return True
        return False

    def board_to_string():
        return "\n".join(" | ".join(row) for row in board)

    class TicTacToeView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)

        async def interaction_check(self, interaction: Interaction) -> bool:
            if interaction.user != current_player:
                await interaction.response.send_message("It's not your turn!", ephemeral=True)
                return False
            return True

        @discord.ui.button(label=" ", row=0, style=ButtonStyle.secondary)
        async def button_0(self, interaction: Interaction, button: discord.ui.Button):
            await self.handle_move(interaction, 0, 0, button)

        @discord.ui.button(label=" ", row=0, style=ButtonStyle.secondary)
        async def button_1(self, interaction: Interaction, button: discord.ui.Button):
            await self.handle_move(interaction, 0, 1, button)

        @discord.ui.button(label=" ", row=0, style=ButtonStyle.secondary)
        async def button_2(self, interaction: Interaction, button: discord.ui.Button):
            await self.handle_move(interaction, 0, 2, button)

        @discord.ui.button(label=" ", row=1, style=ButtonStyle.secondary)
        async def button_3(self, interaction: Interaction, button: discord.ui.Button):
            await self.handle_move(interaction, 1, 0, button)

        @discord.ui.button(label=" ", row=1, style=ButtonStyle.secondary)
        async def button_4(self, interaction: Interaction, button: discord.ui.Button):
            await self.handle_move(interaction, 1, 1, button)

        @discord.ui.button(label=" ", row=1, style=ButtonStyle.secondary)
        async def button_5(self, interaction: Interaction, button: discord.ui.Button):
            await self.handle_move(interaction, 1, 2, button)

        @discord.ui.button(label=" ", row=2, style=ButtonStyle.secondary)
        async def button_6(self, interaction: Interaction, button: discord.ui.Button):
            await self.handle_move(interaction, 2, 0, button)

        @discord.ui.button(label=" ", row=2, style=ButtonStyle.secondary)
        async def button_7(self, interaction: Interaction, button: discord.ui.Button):
            await self.handle_move(interaction, 2, 1, button)

        @discord.ui.button(label=" ", row=2, style=ButtonStyle.secondary)
        async def button_8(self, interaction: Interaction, button: discord.ui.Button):
            await self.handle_move(interaction, 2, 2, button)

        async def handle_move(self, interaction: Interaction, row: int, col: int, button: discord.ui.Button):
            nonlocal current_player
            symbol = players[current_player]
            board[row][col] = symbol
            button.label = f" {symbol} "
            button.style = ButtonStyle.success if symbol == "X" else ButtonStyle.danger
            button.disabled = True
            await interaction.response.edit_message(view=self)

            if check_winner():
                await ctx.send(f"{current_player.mention} wins!\n\n{board_to_string()}")
                self.stop()
                return
            elif all(cell != " " for row in board for cell in row):
                await ctx.send(f"It's a tie!\n\n{board_to_string()}")
                self.stop()
                return
            current_player = opponent if current_player == ctx.author else ctx.author
            await ctx.send(f"It's {current_player.mention}'s turn.")

    await ctx.send(f"Game Start! {ctx.author.mention} is `{players[ctx.author]}`, {opponent.mention} is `{players[opponent]}`. {current_player.mention} goes first.", view=TicTacToeView())
    
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
