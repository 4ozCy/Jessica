import discord
from discord.ext import commands, tasks
from fastapi import FastAPI
from uvicorn import Config, Server
import random
import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())
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
    bot.start_time = discord.utils.utcnow()
    print(f'Bot connected as {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Valentine - laufey"))
    start_fastapi.start()

@bot.command(name='cmds')
async def commands_list(ctx):
    command_names = [command.name for command in bot.commands]
    embed = discord.Embed(
        title="Available Commands", 
        description="\n".join(command_names), 
        color=discord.Color.blurple()
    )
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    embed = discord.Embed(
        title="Kick", 
        description=f"{member.mention} has been kicked. Reason: {reason or 'No reason provided'}", 
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    embed = discord.Embed(
        title="Ban", 
        description=f"{member.mention} has been banned. Reason: {reason or 'No reason provided'}", 
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.command(name='purge')
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    embed = discord.Embed(
        title="Purge", 
        description=f"Purged {amount} messages.", 
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed, delete_after=5)

@bot.command(name='bring')
@commands.has_permissions(move_members=True)
async def bring(ctx, member: discord.Member):
    embed = discord.Embed(color=discord.Color.blue())
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        await member.move_to(channel)
        embed.title = "Bring"
        embed.description = f"Moved {member.mention} to {channel.mention}."
    else:
        embed.title = "Error"
        embed.description = "You must be in a voice channel to use this command."
    await ctx.send(embed=embed)

@bot.command(name='cf')
async def coin(ctx):
    result = random.choice(['Heads', 'Tails'])
    embed = discord.Embed(
        title="Coin Flip", 
        description=f"The coin landed on {result}!", 
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

@bot.command(name='8ball')
async def eight_ball(ctx, *, question: str):
    responses = [
        "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes – definitely.",
        "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.",
        "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
        "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.",
        "My sources say no.", "Outlook not so good.", "Very doubtful."
    ]
    response = random.choice(responses)
    embed = discord.Embed(
        title="8Ball", 
        description=f"🎱 {response}", 
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

@bot.command(name='roll')
async def roll_dice(ctx, sides: int = 6):
    result = random.randint(1, sides)
    embed = discord.Embed(
        title="Dice Roll",
        description=f"You rolled a {result}!",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='random')
async def random_number(ctx, min_num: int, max_num: int):
    if min_num >= max_num:
        embed = discord.Embed(
            title="Error",
            description="Minimum number must be less than maximum number.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    result = random.randint(min_num, max_num)
    embed = discord.Embed(
        title="Random Number",
        description=f"Your random number is {result}!",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command(name='quote')
async def random_quote(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.quotable.io/random') as response:
            if response.status == 200:
                data = await response.json()
                quote = data['content']
                author = data['author']
                embed = discord.Embed(
                    title="Random Quote",
                    description=f"\"{quote}\" - {author}",
                    color=discord.Color.teal()
                )
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Error",
                    description="Failed to fetch a quote.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)

@bot.command(name='choose')
async def choose_option(ctx, *, options: str):
    choices = options.split()
    if len(choices) < 2:
        embed = discord.Embed(
            title="Error",
            description="Please provide at least two options.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    choice = random.choice(choices)
    embed = discord.Embed(
        title="Choose",
        description=f"I choose {choice}!",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    latency = bot.latency * 1000
    embed = discord.Embed(
        title="Ping",
        description=f"Pong! Latency is {latency:.2f}ms.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='uptime')
async def uptime(ctx):
    now = discord.utils.utcnow()
    delta = now - bot.start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    embed = discord.Embed(
        title="Uptime",
        description=f"{days}d {hours}h {minutes}m {seconds}s",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command(name='animal')
async def random_animal(ctx, animal: str):
    animal = animal.lower()
    if animal == 'cat':
        url = 'https://api.thecatapi.com/v1/images/search'
    elif animal == 'dog':
        url = 'https://dog.ceo/api/breeds/image/random'
    else:
        embed = discord.Embed(
            title="Error",
            description="Invalid animal. Please choose 'cat' or 'dog'.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if animal == 'cat':
                    image_url = data[0]['url']
                elif animal == 'dog':
                    image_url = data['message']
                embed = discord.Embed(
                    title=f"Random {animal.capitalize()}",
                    color=discord.Color.orange()
                )
                embed.set_image(url=image_url)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Error",
                    description=f"Failed to fetch a {animal} image.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)

@bot.command(name='timeout', aliases=['to'])
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, duration: str, member: discord.Member, *, reason: str = None):
    duration = duration.lower()
    if not duration or not duration[0].isdigit():
        embed = discord.Embed(
            title="Error",
            description="Please provide a valid duration (e.g., 5m, 2h, 1d).",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    num = ""
    unit = ""
    for char in duration:
        if char.isdigit():
            num += char
        else:
            unit += char
    try:
        num = int(num)
        if num <= 0:
            raise ValueError
    except ValueError:
        embed = discord.Embed(
            title="Error",
            description="Duration must be a positive number.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    units = {
        's': ('seconds', num),
        'sec': ('seconds', num),
        'm': ('minutes', num),
        'min': ('minutes', num),
        'h': ('hours', num),
        'hr': ('hours', num),
        'd': ('days', num),
        'day': ('days', num),
        'w': ('weeks', num),
        'wk': ('weeks', num),
        'y': ('years', num * 365),
        'yr': ('days', num * 365)
    }
    if unit not in units:
        embed = discord.Embed(
            title="Error",
            description="Invalid unit. Use s, m, h, d, w, or y.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    unit_name, value = units[unit]
    time_delta = timedelta(**{unit_name: value})
    if time_delta > timedelta(days=10000):
        embed = discord.Embed(
            title="Error",
            description="Timeout cannot exceed 10000 days.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    await member.timeout(time_delta, reason=reason)
    embed = discord.Embed(
        title="Timeout",
        description=f"{member.mention} has been timed out for {num}{unit}. Reason: {reason or 'No reason provided'}",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)

@bot.command(name="mute")
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: str, *, reason=None):
    guild = ctx.guild
    muted_role = discord.utils.get(guild.roles, name="Muted")

    if not muted_role:
        muted_role = await guild.create_role(name="Muted")
        for channel in guild.text_channels:
            await channel.set_permissions(muted_role, send_messages=False)
        for channel in guild.voice_channels:
            await channel.set_permissions(muted_role, speak=False)

    await member.add_roles(muted_role, reason=reason)

    duration_seconds = convert_duration(duration)
    if not duration_seconds:
        await ctx.send("Invalid duration format. Use `m` for minutes, `h` for hours, or `d` for days (e.g., 10m, 2h, 1d).")
        return

    embed = discord.Embed(
        title="Member Muted",
        description=f"{member.mention} has been muted.",
        color=discord.Color.red()
    )
    embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=False)
    embed.add_field(name="Duration", value=duration, inline=False)
    embed.set_footer(text=f"Muted by {ctx.author}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

    await asyncio.sleep(duration_seconds)
    await member.remove_roles(muted_role, reason="Mute duration expired.")

    unmute_embed = discord.Embed(
        title="Mute Ended",
        description=f"{member.mention} has been unmuted.",
        color=discord.Color.green()
    )
    unmute_embed.set_footer(text=f"Unmuted by {bot.user}", icon_url=bot.user.avatar.url)
    await ctx.send(embed=unmute_embed)

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error", 
            description="You do not have permission to kick members.", 
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error", 
            description="You do not have permission to ban members.", 
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error", 
            description="You do not have permission to delete messages.", 
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bring.error
async def bring_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error", 
            description="You do not have permission to move members.", 
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@timeout.error
async def timeout_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error",
            description="You do not have permission to use this command.",
            color=discord.Color.red()
        )
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="Error",
            description="Invalid member specified.",
            color=discord.Color.red()
        )
    else:
        embed = discord.Embed(
            title="Error",
            description="An error occurred while trying to timeout the member.",
            color=discord.Color.red()
        )
    await ctx.send(embed=embed)

def convert_duration(duration):
    regex = re.match(r'(\d+)([mhd])', duration)
    if regex:
        value = int(regex.group(1))
        unit = regex.group(2)
        if unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
        elif unit == 'd':
            return value * 86400
    return None

bot.run(os.getenv('TOKEN'))
