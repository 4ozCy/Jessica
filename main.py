import discord
from discord.ext import commands, tasks
from fastapi import FastAPI
from uvicorn import Config, Server
import random
import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from datetime import datetime

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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=".cmds"))
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

bot.run(os.getenv('TOKEN'))
