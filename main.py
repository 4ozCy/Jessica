import discord
from discord.ext import commands
from discord.ui import Select, View
import aiohttp
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
from datetime import datetime
import random
import requests
import openai
afk_users = {}

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return "made by: @nozcy."

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()

client = commands.Bot(command_prefix='.', intents=discord.Intents.all())

roasts = [
    "Don't let the door hit you on the way out!",
    "Well, that escalated quickly...",
    "Maybe you'll find better luck elsewhere.",
    "It's not me, it's you.",
    "why did you broke the rules",
    "lollll ez",
    "noob"
]

async def fetch_pickup_line():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.jcwyt.com/pickup") as response:
                data = await response.text()
        lines = data.split("{answer}")
        pickup_line = "\n".join(lines)
        return pickup_line
    except Exception as e:
        print(f"An error occurred while fetching pickup line: {e}")
        return None

async def fetch_quote():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://zenquotes.io/api/random") as response:
                data = await response.json()
                if data and len(data) > 0:
                    quote_text = data[0]['q']
                    quote_author = data[0]['a']
                    return f"{quote_text} - {quote_author}"
                else:
                    return None
    except Exception as e:
        print(f"An error occurred while fetching quote: {e}")
        return None

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Made by: @nozcy. | .cmds"))
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('.'):
        await client.process_commands(message)
        return

    try:
        response = openai.Completion.create(
            engine="gpt-4",
            prompt=f"You are a helpful assistant. {message.content}",
            max_tokens=150
        )
        reply = response.choices[0].text.strip()
        await message.channel.send(reply)
    except Exception as e:
        await message.channel.send(f"An error occurred: {e}")
  
@client.command(name='quote')
async def send_quote(ctx):
    quote = await fetch_quote()
    if quote:
        embed = discord.Embed(description=quote, color=discord.Color.blurple())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
    else:
        await ctx.send("Sorry, I couldn't fetch a quote at the moment.")

@client.command(name='rizz', aliases=['r'])
async def send_rizz(ctx):
    pickup_line = await fetch_pickup_line()
    if pickup_line:
        embed = discord.Embed(description=pickup_line, color=discord.Color.blurple())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
    else:
        await ctx.send("Sorry, I couldn't fetch a pickup line at the moment.")

@client.command(name='joke')
async def joke(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://v2.jokeapi.dev/joke/Any') as response:
            if response.status:
                data = await response.json()
                if data['type'] == 'single':
                    joke = data['joke']
                else:
                    joke = f"{data['setup']} - {data['delivery']}"

                embed = discord.Embed(description=joke, color=discord.Color.blurple())
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
                embed.timestamp = discord.utils.utcnow()
                await ctx.send(embed=embed)

@client.command(name='cmds')
async def send_help(ctx):
    class HelpSelect(Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="General", description="General commands", emoji="🔧"),
                discord.SelectOption(label="Moderation", description="Moderation commands", emoji="🛡️"),
                discord.SelectOption(label="Fun", description="Fun commands", emoji="🎉")
            ]
            super().__init__(placeholder='Choose a category...', min_values=1, max_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            embed = discord.Embed(title=f"{self.values[0]} Commands", color=discord.Color.blurple())
            embed.set_thumbnail(url=client.user.avatar.url)
            embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
            embed.timestamp = discord.utils.utcnow()

            if self.values[0] == "General":
                embed.add_field(name="ping", value="Show bot ping", inline=False)
                embed.add_field(name="avatar/av", value="Display user avatar", inline=False)
                embed.add_field(name="server_info/sf", value="Get server information", inline=False)
                embed.add_field(name="bot-info", value="Get bot information", inline=False)

            elif self.values[0] == "Moderation":
                embed.add_field(name="kick", value="Kick a member", inline=False)
                embed.add_field(name="ban", value="Ban a member", inline=False)
                embed.add_field(name="mute", value="Mute a member", inline=False)
                embed.add_field(name="unmute", value="Unmute a member", inline=False)
                embed.add_field(name="lock", value="Lock a channel", inline=False)
                embed.add_field(name="unlock", value="Unlock a channel", inline=False)
                embed.add_field(name="delete_channel/dc", value="Delete a specific channel", inline=False)

            elif self.values[0] == "Fun":
                embed.add_field(name="quote", value="Send a random inspirational quote", inline=False)
                embed.add_field(name="rizz", value="Rizz You Up", inline=False)
                embed.add_field(name="joke", value="Tell a random joke", inline=False)
                embed.add_field(name="animequote/aq", value="Send a random anime quote", inline=False)
                embed.add_field(name="slap", value="Slap someone", inline=False)
                embed.add_field(name="Breakup/bp", value="Break up with your love", inline=False)
                embed.add_field(name="punch/p", value="Punch someone", inline=False)
                embed.add_field(name="giverole/gr", value="Give a role to someone", inline=False)
                embed.add_field(name="dare/truth", value="Play truth or dare", inline=False)
                embed.add_field(name="add-emoji", value="Add an emoji", inline=False)

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
      
@client.command(name='animequote', aliases=['aq'])
async def send_anime_quote(ctx):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nozcy-api.onrender.com/anime/quote") as response:
                data = await response.json()
                quote = data['quote']
                character = data['character']
                anime = data['anime']
                embed = discord.Embed(description=f'"{quote}"\n-{character} ({anime})', color=discord.Color.blurple())
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
                embed.timestamp = discord.utils.utcnow()
                await ctx.send(embed=embed)
    except Exception as e:
        print(f"An error occurred while fetching anime quote: {e}")
        await ctx.send("Sorry, I couldn't send an anime quote at the moment.")

@client.command(name='slap')
async def slap(ctx, member: discord.Member):
    if member == ctx.author:
        await ctx.send(f"{ctx.author.mention} tries to slap themselves... but it doesn't work that way!")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.otakugifs.xyz/gif?reaction=slap&format=gif") as response:
            if response.status == 200:
                data = await response.json()
                gif_url = data['url']
                embed = discord.Embed(title="slap you in the face because i wanted to.", description=f"{ctx.author.mention} slaps {member.mention}!!", color=discord.Color.blurple())
                embed.set_image(url=gif_url)
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
                embed.timestamp = discord.utils.utcnow()
                await ctx.send(embed=embed)
            else:
                await ctx.send("You're too weak to slap someone")

@client.command(name='breakup', aliases=['bp'])
async def send_breakup(ctx):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.jcwyt.com/breakup") as response:
                breakup_line = await response.text()
        embed = discord.Embed(title="Breakup Line", description=breakup_line, color=discord.Color.blurple())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"An error occurred while fetching breakup line: {e}")
        await ctx.send("You're Not Ready to breakup yet.")
        
@client.command(name='autorole', aliases=['ar'])
async def set_autorole(ctx, role: discord.Role, channel: discord.TextChannel):
    if ctx.author.guild_permissions.manage_roles:
        global autorole_role_id, autorole_channel_id
        autorole_role_id = role.id
        autorole_channel_id = channel.id
        
        embed = discord.Embed(title="Autorole Set", description=f"Autorole set to {role.mention} in {channel.mention}.", color=discord.Color.blurple())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
    else:
        await ctx.send("You don't have permission to use this command.")

@client.event
async def on_member_join(member):
    global autorole_role_id, autorole_channel_id
    if autorole_role_id:
        autorole_role = member.guild.get_role(autorole_role_id)
        if autorole_role:
            await member.add_roles(autorole_role)
            
            channel = member.guild.get_channel(autorole_channel_id)
            if channel:
                embed = discord.Embed(description=f"{member.mention} has been assigned the autorole.", color=discord.Color.blurple())
                await channel.send(embed=embed)
            else:
                print("Channel not found.")
            
            print(f"{member.name} has been given rolw.")
        else:
            print("Autorole role not found.")
    else:
        print("Autorole not set.")

@client.command(name='punch', aliases=['p'])
async def punch_member(ctx, member: discord.Member):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.otakugifs.xyz/gif?reaction=punch&format=gif") as response:
            if response.status == 200:
                data = await response.json()
                gif_url = data['url']
                embed = discord.Embed(title="punch you in the face because I'm bored.", description=f"{ctx.author.mention} punches {member.mention}!", color=discord.Color.blurple())
                embed.set_image(url=gif_url)
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
                embed.timestamp = discord.utils.utcnow()
                await ctx.send(embed=embed)
            else:
                await ctx.send("You're to weak you can't punch someone")

@client.command(name='giverole', aliases=['gr'])
async def give_role(ctx, member: discord.Member, role: discord.Role):
    if ctx.author.guild_permissions.manage_roles:
        if role:
            if role in member.roles:
                embed = discord.Embed(description=f"{member.mention} already has the {role.mention} role.", color=discord.Color.blurple())
            else:
                await member.add_roles(role)
                embed = discord.Embed(description=f"{member.mention} has been given the {role.mention} role.", color=discord.Color.blurple())
        else:
            embed = discord.Embed(description="Role not found.", color=discord.Color.red())
    else:
        embed = discord.Embed(description="You do not have permission to manage roles.", color=discord.Color.red())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

@client.command(name='purge')
async def purge(ctx, amount: int):
    if ctx.author.guild_permissions.manage_messages:
        await ctx.message.delete()

        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)
    else:
        await ctx.send("You do not have permission to manage messages.")

@client.command(name='afk')
async def afk(ctx, *, reason="No reason provided"):
    afk_users[ctx.author.id] = {'reason': reason, 'time': datetime.utcnow(), 'message_count': 0}

    embed = discord.Embed(
        title="AFK Status",
        description=f"{ctx.author.mention} is now AFK.",
        color=discord.Color.blue())
    )
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="AFK Since", value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'), inline=False)
    embed.set_footer(text="You will be removed from AFK status when you send a message.")

    await ctx.send(embed=embed)

@client.event
async def on_message(message):
    if message.author.bot:
        return

    current_time = datetime.utcnow()

    if message.author.id in afk_users:
        afk_time = afk_users[message.author.id]['time']
        duration = current_time - afk_time
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        embed = discord.Embed(
            title="Welcome Back!",
            description=f"{message.author.mention}, you are no longer AFK.",
            color=discord.Color.blue())
        )
        embed.add_field(name="AFK Duration", value=f"{hours} hours, {minutes} minutes, and {seconds} seconds.", inline=False)

        await message.channel.send(embed=embed)
        afk_users.pop(message.author.id)

    mentions = [mention for mention in message.mentions if mention.id in afk_users]
    for mention in mentions:
        afk_data = afk_users[mention.id]
        afk_time = afk_data['time']
        duration = current_time - afk_time
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        embed = discord.Embed(
            title="AFK Notification",
            description=f"{mention.mention} is currently AFK.", color=discord.Color.blue())
        embed.add_field(name="Reason", value=afk_data['reason'], inline=False)
        embed.add_field(name="AFK Duration", value=f"{hours} hours, {minutes} minutes, and {seconds} seconds.", inline=False)

        await message.channel.send(embed=embed)

        afk_data['message_count'] += 1
        afk_users[mention.id] = afk_data

    await client.process_commands(message)
    
@client.command(name='spam')
async def spam(ctx, message: str, member: discord.Member, count: int):
    allowed_user_id = '1107744228773220473'
    if str(ctx.author.id) != allowed_user_id:
        await ctx.send("You are not authorized to use this command. (bot owner only)")
        return
    await ctx.message.delete()
    if count > 50:
        await ctx.send("Error: Too many messages to spam.")
        return
    for _ in range(count):
        await ctx.send(f"{message} {member.mention}")
        
@client.command(name='avatar', aliases=['av'])
async def avatar(ctx, *, member: discord.Member = None):
    if not member:
        member = ctx.author
    embed = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.blue())
    embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await ctx.send(embed=embed)

@client.command(name='server_info', aliases=['sf'])
async def serverinfo(ctx):
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

@client.command(name='dare')
async def dare(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.truthordarebot.xyz/v1/dare') as response:
            if response.status == 200:
                data = await response.json()
                dare_question = data['question']
                embed = discord.Embed(title="Dare", description=dare_question, color=discord.Color.blurple())
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
                embed.timestamp = discord.utils.utcnow()
                await ctx.send(embed=embed)
            else:
                await ctx.send("I couldn't dare you at the moment, please try again later.")

@client.command(name='truth')
async def truth(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.truthordarebot.xyz/v1/truth') as response:
            if response.status == 200:
                data = await response.json()
                truth_question = data['question']
                embed = discord.Embed(title="Truth", description=truth_question, color=discord.Color.blurple())
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
                embed.timestamp = discord.utils.utcnow()
                await ctx.send(embed=embed)
            else:
                await ctx.send("I couldn't send a question at the moment, please try again later.")

@client.command(name='delete_channel', aliases=['dc'])
async def delete_channel(ctx, channel: discord.TextChannel):
    if ctx.author.guild_permissions.manage_channels:
        try:
            await channel.delete()
            await ctx.send(f"Channel {channel.name} has been deleted.")
        except discord.Forbidden:
            await ctx.send(f"Failed to delete channel {channel.name} due to insufficient permissions.")
        except Exception as e:
            await ctx.send(f"An error occurred while deleting channel {channel.name}: {e}")
    else:
        await ctx.send("You don't have permission to use this command.")

@client.command(name='add-emoji', aliases=['ad'])
async def add_emoji(ctx, name: str, emoji_url: str):
    if ctx.author.guild_permissions.manage_emojis:
        async with ctx.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(emoji_url) as response:
                        image_data = await response.read()
                emoji = await ctx.guild.create_custom_emoji(name=name, image=image_data)
                await ctx.send(f"Emoji {emoji.name} has been added.")
            except discord.Forbidden:
                await ctx.send("Failed to add emoji due to insufficient permissions.")
            except discord.HTTPException as e:
                await ctx.send(f"Failed to add emoji: {e}")
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")
    else:
        await ctx.send("You don't have permission to use this command.")

@client.command(name='lock')
async def channel_lock(ctx, channel: discord.TextChannel):
    if ctx.author.guild_permissions.manage_channels:
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            await ctx.send(f"Channel {channel.name} is now locked.")
        except discord.Forbidden:
            await ctx.send("Failed to lock channel due to insufficient permissions.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
    else:
        await ctx.send("You don't have permission to use this command.")

@client.command(name='unlock')
async def unlock_channel(ctx, channel: discord.TextChannel):
    if ctx.author.guild_permissions.manage_channels:
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
            await ctx.send(f"Channel {channel.name} is now unlocked.")
        except discord.Forbidden:
            await ctx.send("Failed to unlock channel due to insufficient permissions.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
    else:
        await ctx.send("You don't have permission to use this command.")

@client.command(name='server-lock', aliases=['sl'])
async def lockdown(ctx):
    if ctx.author.guild_permissions.manage_channels:
        try:
            for channel in ctx.guild.channels:
                if isinstance(channel, discord.TextChannel):
                    await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            await ctx.send("Server is now locked.")
        except discord.Forbidden:
            await ctx.send("Failed to lock down server due to insufficient permissions.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
    else:
        await ctx.send("You don't have permission to use this command.")

@client.command(name='server-unlock', aliases=['sun'])
async def unlock_server(ctx):
    if ctx.author.guild_permissions.manage_channels:
        try:
            for channel in ctx.guild.channels:
                if isinstance(channel, discord.TextChannel):
                    await channel.set_permissions(ctx.guild.default_role, send_messages=True)
            await ctx.send("Server is now unlocked.")
        except discord.Forbidden:
            await ctx.send("Failed to unlock server due to insufficient permissions.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
    else:
        await ctx.send("You don't have permission to use this command.")

@client.command(name='bring', aliases=['br'])
async def bring(ctx, member: discord.Member):
    if not ctx.author.voice:
        await ctx.send("You are not connected to a voice channel.")
        return

    author_vc = ctx.author.voice.channel
    member_vc = member.voice.channel

    if not member_vc:
        await ctx.send(f"{member.display_name} is not connected to a voice channel.")
        return

    try:
        await member.move_to(author_vc)
        await ctx.send(f"{member.display_name} has been moved to {author_vc.name}.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to move members.")

@client.command(name='goto', aliases=['to'])
async def teleport(ctx, member: discord.Member):
    if not member.voice:
        await ctx.send(f"{member.display_name} is not connected to a voice channel.")
        return

    try:
        await ctx.author.move_to(member.voice.channel)
        await ctx.send(f"You have been teleported to {member.display_name}'s voice channel.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to move you to another voice channel.")

@client.command(name='teleport', aliases=['tp'])
async def tp(ctx, member: discord.Member, channel: discord.VoiceChannel):
    try:
        await member.move_to(channel)
        await ctx.send(f"{member.display_name} has been teleported to {channel.name}.")
    except discord.Forbidden:
        await ctx.send(f"I don't have permission to move {member.display_name}.")

@client.command(name='ping')
async def ping(ctx):
    embed = discord.Embed(description=f'Bot Ping: {round(client.latency * 1000)}ms', color=discord.Color.blurple())
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

@client.command(name='mute', help='Mutes someone from chatting')
async def mute(ctx, target: discord.Member = None):
    if not target:
        target = ctx.author
        
    if ctx.author.guild_permissions.manage_channels:
        await ctx.channel.set_permissions(target, send_messages=False)
        embed = discord.Embed(title="User Muted", description=f"{target.display_name} has been muted in this channel.", color=discord.Color.blurple())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
    else:
        await ctx.send("You don't have permission to mute members.")

@client.command(name='unmute', help='Unmutes someone from chatting')
async def unmute(ctx, target: discord.Member = None):
    if not target:
        target = ctx.author
        
    if ctx.author.guild_permissions.manage_channels:
        await ctx.channel.set_permissions(target, send_messages=True)
        embed = discord.Embed(title="User Unmuted", description=f"{target.display_name} has been unmuted in this channel.", color=discord.Color.blurple())
        await ctx.send(embed=embed)
    else:
        await ctx.send("You don't have permission to unmute members.")

@client.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if reason is None:
        reason = "No reason provided"

    await member.kick(reason=reason)
    gif = random.choice(kick_gifs)
    roast = random.choice(roasts)
    embed = discord.Embed(title=f'{member} has been kicked!', description=f'Reason: {reason}\n{roast}', color=discord.Color.blurple())
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)
    
    log_channel = discord.utils.get(ctx.guild.text_channels, name='log-channel')
    if log_channel:
        await log_channel.send(f'{member} was kicked by {ctx.author} for: {reason}')

@client.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if reason is None:
        reason = "No reason provided"

    await member.ban(reason=reason)
    gif = random.choice(ban_gifs)
    roast = random.choice(roasts)
    embed = discord.Embed(title=f'{member} has been banned!', description=f'Reason: {reason}\n{roast}', color=discord.Color.blurple())
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)
    
    log_channel = discord.utils.get(ctx.guild.text_channels, name='log-channel')
    if log_channel:
        await log_channel.send(f'{member} was banned by {ctx.author} for: {reason}')

@kick.error
@ban.error
async def kick_ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to do that!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention a member and provide a reason.")
    else:
        await ctx.send("An error occurred.")

@client.command(name='bot-info')
async def bot_info(ctx):
    embed = discord.Embed(title="Bot Information", color=discord.Color.blurple())
    embed.add_field(name="Bot Name", value=client.user.name, inline=True)
    embed.add_field(name="Bot ID", value=client.user.id, inline=True)
    embed.add_field(name="Server Count", value=len(client.guilds), inline=True)
    embed.add_field(name="User Count", value=len(set(client.get_all_members())), inline=True)
    embed.add_field(name="Ping", value=f"{round(client.latency * 1000)}ms", inline=True)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

client.run(os.getenv('TOKEN'))
