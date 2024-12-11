import discord
from discord.ext import commands, tasks
from discord.ui import Button
from discord import ButtonStyle, Interaction
from fastapi import FastAPI
from uvicorn import Config, Server
import random
import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from datetime import datetime
import requests
import cmds
import xo
import sqlite3

load_dotenv()

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())

app = FastAPI()

@app.get("/")
async def read_root():
    return {"status": "online"}

conn = sqlite3.connect("invites.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS invite_tracker (
    inviter_id TEXT,
    invites INTEGER DEFAULT 0
)
""")
conn.commit()

invites_cache = {}

LOG_CHANNEL_ID = 1310098528210653256

@tasks.loop(count=1)
async def start_fastapi():
    config = Config(app=app, host="0.0.0.0", port=8080, log_level="info")
    server = Server(config)
    await server.serve()
    
@bot.event
async def on_ready():
    bot.start_time = discord.utils.utcnow()
    print(f'Bot connected as {bot.user}')
    discord.Activity(type=discord.ActivityType.playing, name=".cmds")
    for guild in bot.guilds:
        try:
            invites_cache[guild.id] = await guild.invites()
        except Exception as e:
            print(f"Failed to fetch invites for {guild.name}: {e}")
    start_fastapi.start()

@bot.event
async def on_member_join(member):
    guild = member.guild
    cached_invites = invites_cache.get(guild.id, [])
    new_invites = await guild.invites()
    invites_cache[guild.id] = new_invites

    used_invite = None
    for invite in new_invites:
        for cached_invite in cached_invites:
            if invite.code == cached_invite.code and invite.uses > cached_invite.uses:
                used_invite = invite
                break

    if used_invite:
        inviter = used_invite.inviter
        cursor.execute("SELECT invites FROM invite_tracker WHERE inviter_id = ?", (str(inviter.id),))
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE invite_tracker SET invites = invites + 1 WHERE inviter_id = ?", (str(inviter.id),))
        else:
            cursor.execute("INSERT INTO invite_tracker (inviter_id, invites) VALUES (?, ?)", (str(inviter.id), 1))
        conn.commit()

        total_invites = row[0] + 1 if row else 1

        embed = discord.Embed(
            title="New Member Joined",
            timestamp=member.joined_at
        )
        embed.add_field(name="Member", value=f"{member} ({member.id})", inline=True)
        embed.add_field(name="Inviter", value=f"{inviter} ({inviter.id})", inline=True)
        embed.add_field(name="Invite Code", value=used_invite.code, inline=True)
        embed.add_field(name="Total Invites by Inviter", value=str(total_invites), inline=True)
        embed.set_footer(text="Powered by: @n.int | Invite Tracker")

        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(embed=embed)
    
@bot.command(name="uf")
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [role.mention for role in member.roles[1:]]
    created_at = member.created_at.strftime("%Y-%m-%d %H:%M:%S")
    joined_at = member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "N/A"
    status = str(member.status).title()
    activity = member.activity.name if member.activity else "None"
    permissions = [perm[0].replace('_', ' ').title() for perm in member.guild_permissions if perm[1]]
    highest_role = member.top_role.mention

    embed = discord.Embed(title=f"User Information - {member}", color=member.color)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="Discriminator", value=member.discriminator, inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Created On", value=created_at, inline=True)
    embed.add_field(name="Joined On", value=joined_at, inline=True)
    embed.add_field(name="Status", value=status, inline=True)
    embed.add_field(name="Activity", value=activity, inline=True)
    embed.add_field(name="Roles", value=", ".join(roles) if roles else "No roles", inline=False)
    embed.add_field(name="Permissions", value=", ".join(permissions) if permissions else "No special permissions", inline=False)
    embed.add_field(name="Highest Role", value=highest_role, inline=True)
    embed.add_field(name="Boosting Server", value="Yes" if member.premium_since else "No", inline=True)
    embed.add_field(name="Bot", value="Yes" if member.bot else "No", inline=True)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)
            
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
