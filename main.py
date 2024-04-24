import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()

client = commands.Bot(command_prefix='.', intents=discord.Intents.all())

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

async def fetch_joke():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"}) as response:
                data = await response.json()
                return data.get("joke")
    except Exception as e:
        print(f"An error occurred while fetching a joke: {e}")
        return None

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Jessica Rizz You Up"))
    print(f'We have logged in as {client.user}')
  
@client.command(name='quote')
async def send_quote(ctx):
    quote = await fetch_quote()
    if quote:
        embed = discord.Embed(description=quote, color=0x3498db)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Sorry, I couldn't fetch a quote at the moment.")

@client.command(name='rizz', aliases=['r'])
async def send_rizz(ctx):
    pickup_line = await fetch_pickup_line()
    if pickup_line:
        embed = discord.Embed(description=pickup_line, color=0x3498db)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Sorry, I couldn't fetch a pickup line at the moment.")

@client.command(name='joke')
async def send_joke(ctx):
    joke = await fetch_joke()
    if joke:
        embed = discord.Embed(title="Joke", description=joke, color=0x3498db)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Sorry, I couldn't fetch a joke at the moment.")

@client.command(name='cmd')
async def send_help(ctx):
    embed = discord.Embed(title="** Commands list **", color=0x3498db)
    embed.add_field(name="quote", value="send a random inspirational quote.", inline=False)
    embed.add_field(name="rizz", value="Rizz You Up", inline=False)
    embed.add_field(name="joke", value="Tells a random joke.", inline=False)
    embed.add_field(name="insult/in", value="send a random insult", inline=False)
    embed.add_field(name="animequote/aq", value="send a random anime quote.", inline=False)
    embed.add_field(name="slap", value="Slap you in the face", inline=False)
    embed.add_field(name="Breakup/bp", value="If you want to breakup with your love use this command.", inline=False)
    embed.add_field(name="autorole/ar", value="setup an auto-role here how to use this cmd (use .ar and mention role that you want to put to Autorole and mention channel for Autorole log)", inline=False)
    embed.add_field(name="punch/p", value="punch you in the f**king face", inline=False)
    embed.add_field(name="giverole/gr", value="give role to someone", inline=False)
    embed.add_field(name="auditlog/al", value="send an audit log to the specific channel", inline=False)
    await ctx.send(embed=embed)

@client.command(name='insult', aliases=['in'])
async def send_insult(ctx):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://insult.mattbas.org/api/insult") as response:
                insult = await response.text()
        embed = discord.Embed(description=insult, color=0x3498db)
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"An error occurred while fetching insult: {e}")
        await ctx.send("You're too weak to insult someone")
      
@client.command(name='animequote', aliases=['aq'])
async def send_anime_quote(ctx):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://animechan.xyz/api/random") as response:
                data = await response.json()
                quote = data['quote']
                character = data['character']
                anime = data['anime']
                embed = discord.Embed(description=f'"{quote}"\n-{character} ({anime})', color=0x3498db)
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
                embed = discord.Embed(title="slap you in the face because i wanted to.", description=f"{ctx.author.mention} slaps {member.mention}!!", color=0x3498db)
                embed.set_image(url=gif_url)  # Set the GIF URL as an image in the embed
                await ctx.send(embed=embed)
            else:
                await ctx.send("You're too weak to slap someone")

@client.command(name='breakup', aliases=['bp'])
async def send_breakup(ctx):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.jcwyt.com/breakup") as response:
                breakup_line = await response.text()
        embed = discord.Embed(title="Breakup Line", description=breakup_line, color=0xFF5733)
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
        
        embed = discord.Embed(title="Autorole Set", description=f"Autorole set to {role.mention} in {channel.mention}.", color=0x00ff00)
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
                embed = discord.Embed(description=f"{member.mention} has been assigned the autorole.", color=0x00ff00)
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
                embed = discord.Embed(title="punch you in the face because I'm bored.", description=f"{ctx.author.mention} punches {member.mention}!", color=0xFF5733)
                embed.set_image(url=gif_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send("You're to weak you can't punch someone")

@client.command(name='giverole', aliases=['gr'])
async def give_role(ctx, member: discord.Member, role: discord.Role):
    if ctx.author.guild_permissions.manage_roles:
        if role:
            if role in member.roles:
                embed = discord.Embed(description=f"{member.mention} already has the {role.mention} role.", color=discord.Color.orange())
            else:
                await member.add_roles(role)
                embed = discord.Embed(description=f"{member.mention} has been given the {role.mention} role.", color=discord.Color.green())
        else:
            embed = discord.Embed(description="Role not found.", color=discord.Color.red())
    else:
        embed = discord.Embed(description="You do not have permission to manage roles.", color=discord.Color.red())

    await ctx.send(embed=embed)

@client.command(name='auditlog', aliases=['al'])
async def audit_log(ctx, channel: discord.TextChannel):
    try:
        # Fetch the last 5 audit log entries
        audit_logs = [entry async for entry in ctx.guild.audit_logs(limit=5)]
        
        # Create an embed to display the audit logs
        embed = discord.Embed(title="Audit Log")
        for entry in audit_logs:
            embed.add_field(
                name=f"Action by {entry.user} (ID: {entry.user.id})",
                value=(f"Action: {entry.action}\n"
                       f"Target: {entry.target} (ID: {entry.target.id if entry.target else 'N/A'})\n"
                       f"Reason: {entry.reason or 'No reason provided.'}\n"
                       f"Time: {entry.created_at.strftime('%Y-%m-%d %H:%M:%S')}"),
                inline=False
            )
        
        # Send the embed to the specified channel
        await channel.send(embed=embed)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


client.run(os.getenv('TOKEN'))
