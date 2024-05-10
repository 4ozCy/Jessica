import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
from datetime import datetime
import random
afk_users = {}

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

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())

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

@bot.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Made by: @nozcy. | .cmd"))
    print(f'We have logged in as {client.user}')
  
@bot.command(name='quote')
async def send_quote(ctx):
    quote = await fetch_quote()
    if quote:
        embed = discord.Embed(description=quote, color=0x3498db)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Sorry, I couldn't fetch a quote at the moment.")

@bot.command(name='rizz', aliases=['r'])
async def send_rizz(ctx):
    pickup_line = await fetch_pickup_line()
    if pickup_line:
        embed = discord.Embed(description=pickup_line, color=0x3498db)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Sorry, I couldn't fetch a pickup line at the moment.")

@bot.command(name='joke')
async def joke(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://v2.jokeapi.dev/joke/Any') as response:
            if response.status:
                data = await response.json()
                if data['type'] == 'single':
                    joke = data['joke']
                else:  # For a two-part joke
                    joke = f"{data['setup']} - {data['delivery']}"

                # Create an embed instance with the joke
                embed = discord.Embed(description=joke, color=0x00ff00)

                await ctx.send(embed=embed)


@bot.command(name='cmd')
async def send_help(ctx):
    embed = discord.Embed(title="Commands list", color=0x3498db)
    embed.add_field(name="quote", value="send a random inspirational quote.", inline=False)
    embed.add_field(name="rizz", value="Rizz You Up", inline=False)
    embed.add_field(name="joke", value="Tells a random joke.", inline=False)
    embed.add_field(name="insult/in", value="send a random insult", inline=False)
    embed.add_field(name="animequote/aq", value="send a random anime quote.", inline=False)
    embed.add_field(name="slap", value="Slap you in the face", inline=False)
    embed.add_field(name="Breakup/bp", value="If you want to breakup with your love use this command.", inline=False)
    embed.add_field(name="autorole/ar", value="setup an auto-role here how to use this cmd (use .ar and mention role that you want to put to Autorole and mention channel for Autorole log)", inline=False)
    embed.add_field(name="punch/p", value="punch you in the face", inline=False)
    embed.add_field(name="giverole/gr", value="give role to someone", inline=False)
    embed.add_field(name="Purge", value="delete massage in specific channel", inline=False)
    embed.add_field(name="afk", value="away from keyboard", inline=False)
    embed.add_field(name="meme", value="send an random meme", inline=False)
    embed.add_field(name="avatar/av", value="you already know what this is", inline=False)
    embed.add_field(name="server_info/sf", value="get server information", inline=False)
    embed.add_field(name="dare/truth", value="play truth or dare", inline=False)
    embed.add_field(name="delete_channel/dc", value="delete specific channel", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='insult', aliases=['in'])
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
      
@bot.command(name='animequote', aliases=['aq'])
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
                embed = discord.Embed(title="slap you in the face because i wanted to.", description=f"{ctx.author.mention} slaps {member.mention}!!", color=0x3498db)
                embed.set_image(url=gif_url)  # Set the GIF URL as an image in the embed
                await ctx.send(embed=embed)
            else:
                await ctx.send("You're too weak to slap someone")

@bot.command(name='breakup', aliases=['bp'])
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
        

@bot.command(name='autorole', aliases=['ar'])
async def set_autorole(ctx, role: discord.Role, channel: discord.TextChannel):
    if ctx.author.guild_permissions.manage_roles:
        global autorole_role_id, autorole_channel_id
        autorole_role_id = role.id
        autorole_channel_id = channel.id
        
        embed = discord.Embed(title="Autorole Set", description=f"Autorole set to {role.mention} in {channel.mention}.", color=0x00ff00)
        await ctx.send(embed=embed)
    else:
        await ctx.send("You don't have permission to use this command.")

@bot.event
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

@bot.command(name='punch', aliases=['p'])
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

@bot.command(name='giverole', aliases=['gr'])
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

@bot.command(name='purge')
async def purge(ctx, amount: int):
    if ctx.author.guild_permissions.manage_messages:
        await ctx.message.delete()  # Delete the command message

        # Fetch and delete messages
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)
    else:
        await ctx.send("You do not have permission to manage messages.")

@bot.command(name='afk')
async def afk(ctx, *, reason="No reason provided"):
    global afk_users
    afk_users[ctx.author.id] = {'reason': reason, 'time': datetime.utcnow()}
    await ctx.send(f"{ctx.author.mention} is now AFK Reason: `{reason}`")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    current_time = datetime.utcnow()
    if message.author.id in afk_users:
        afk_time = afk_users[message.author.id]['time']
        duration = current_time - afk_time
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        await message.channel.send(f"Welcome back {message.author.mention}, you were AFK for {hours} hours, {minutes} minutes.")
        afk_users.pop(message.author.id)

    mentions = [mention for mention in message.mentions if mention.id in afk_users]
    for mention in mentions:
        afk_time = afk_users[mention.id]['time']
        duration = current_time - afk_time
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        await message.channel.send(f"{mention.display_name} is AFK: {afk_users[mention.id]['reason']} - AFK for {hours} hours, {minutes} minutes.")
        
@bot.command(name='spam')
async def spam(ctx, message: str, member: discord.Member, count: int):
    if count > 30:  # Limit the count to prevent abuse
        await ctx.send("Error: Too many messages to spam.")
        return

    for _ in range(count):
        await ctx.send(f"{message} {member.mention}")

@bot.command(name='meme')
async def meme(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.imgflip.com/get_memes') as response:
            meme_data = await response.json()
            memes = meme_data['data']['memes']
            meme = random.choice(memes)
            embed = discord.Embed(title=meme['name'])
            embed.set_image(url=meme['url'])
            await ctx.send(embed=embed)

@bot.command(name='avatar', aliases=['av'])
async def avatar(ctx, *, member: discord.Member = None):
    if not member:
        member = ctx.author
    embed = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.blue())
    embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name='server_info', aliases=['sf'])
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
    await ctx.send(embed=embed)

@bot.command(name='dare')
async def dare(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.truthordarebot.xyz/v1/dare') as response:
            if response.status == 200:
                data = await response.json()
                dare_question = data['question']
                embed = discord.Embed(title="Dare", description=dare_question, color=discord.Color.red())
                await ctx.send(embed=embed)
            else:
                await ctx.send("I couldn't dare you at the moment, please try again later.")

@bot.command(name='truth')
async def truth(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.truthordarebot.xyz/v1/truth') as response:
            if response.status == 200:
                data = await response.json()
                truth_question = data['question']
                embed = discord.Embed(title="Truth", description=truth_question, color=discord.Color.blue())
                await ctx.send(embed=embed)
            else:
                await ctx.send("I couldn't send a question at the moment, please try again later.")
                
@bot.command(name='kick_all', aliases=['kl'])
async def kick_all(ctx):
    if ctx.author.guild_permissions.kick_members:
        new_server_link = "https://discord.gg/zEWHxD6eCY"
        for member in ctx.guild.members:
            try:
                if member != ctx.guild.owner and not member.guild_permissions.administrator:
                    await member.kick(reason="Server security issue")
                    print(f"Kicked {member} from the server.")
            except discord.Forbidden:
                print(f"Failed to kick {member} due to insufficient permissions.")
            except Exception as e:
                print(f"An error occurred while kicking {member}: {e}")
        await ctx.send("All non-administrator members (except the server owner) have been kicked from the server. Join the new server using this link: " + new_server_link)
    else:
        await ctx.send("You don't have permission to use this command.")

@bot.command(name='delete_all_channel', aliases=['dac'])
async def delete_all_channels(ctx):
    if ctx.author.guild_permissions.manage_channels:
        for channel in ctx.guild.channels:
            try:
                await channel.delete()
                print(f"Deleted channel {channel.name}")
            except discord.Forbidden:
                print(f"Failed to delete channel {channel.name} due to insufficient permissions.")
            except Exception as e:
                print(f"An error occurred while deleting channel {channel.name}: {e}")
        await ctx.send("All channels have been deleted from the server.")
    else:
        await ctx.send("You don't have permission to use this command.")

@bot.command(name='delete_channel', aliases=['dc'])
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

@bot.command(name='add_emoji', aliases=['ad'])
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

await bot.process_commands(message)

bot.run(os.getenv('TOKEN'))
