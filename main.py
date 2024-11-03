import discord
from discord.ext import commands
from discord.ui import Select, Button, View
import aiohttp
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
from datetime import datetime
import random
import requests 
import asyncio
afk_users = {}

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return "online"

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

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=".cmds"))
    print(f'We have logged in as {client.user}')

  
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
                embed.add_field(name="`avatar/av`", value="Display user avatar", inline=False)
                embed.add_field(name="`server_info/sf`", value="Get server information", inline=False)
                embed.add_field(name="`bot-info`", value="Get bot information", inline=False)

            elif self.values[0] == "Moderation":
                embed.add_field(name="`kick`", value="Kick a member", inline=False)
                embed.add_field(name="`ban`", value="Ban a member", inline=False)
                embed.add_field(name="`mute`", value="Mute a member", inline=False)
                embed.add_field(name="`unmute`", value="Unmute a member", inline=False)
                embed.add_field(name="`lock`", value="Lock a channel", inline=False)
                embed.add_field(name="`unlock`", value="Unlock a channel", inline=False)
                embed.add_field(name="`delete channel/dc`", value="Delete a specific channel", inline=False)
                embed.add_field(name="`give role/gr`", value="Give a role to someone", inline=False)
                embed.add_field(name="`add emoji/ad`", value="Add an emoji", inline=False)

            elif self.values[0] == "Fun":
                embed.add_field(name="`quote`", value="Send a random inspirational quote", inline=False)
                embed.add_field(name="`rizz`", value="Rizz You Up", inline=False)
                embed.add_field(name="`joke`", value="Tell a random joke", inline=False)
                embed.add_field(name="`anime quote/aq`", value="Send a random anime quote", inline=False)
                embed.add_field(name="`slap`", value="Slap someone", inline=False)
                embed.add_field(name="`Breakup/bp`", value="Break up with your love", inline=False)
                embed.add_field(name="`punch/p`", value="Punch someone", inline=False)
                embed.add_field(name="`dare/truth`", value="Play truth or dare", inline=False)
                embed.add_field(name="`coin flip`", value="Play coin flip", inline=False)
                embed.add_field(name="`8ball`", value="Magic 8-ball that gives a random response to yes/no questions", inline=False)
                embed.add_field(name="`dice`", value="Roll a dice", inline=False)

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
            
@client.command(name='slap')
async def slap(ctx, member: discord.Member):
    if member == ctx.author:
        await ctx.send(f"{ctx.author.mention} tries to slap themselves... but it doesn't work that way!")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get("https://purrbot.site/api/img/sfw/slap/gif") as response:
            if response.status == 200:
                data = await response.json()
                gif_url = data['link']
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

@client.command(name='say')
async def say(ctx, *, message: str):
    await ctx.message.delete()
    await ctx.send(message)

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

@client.command(name='afk')
async def afk(ctx, *, reason="No reason provided"):
    afk_users[ctx.author.id] = {'reason': reason, 'time': datetime.utcnow(), 'message_count': 0}

    embed = discord.Embed(
        title="AFK Status",
        description=f"{ctx.author.mention} is now AFK.",
        color=discord.Color.blurple()
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
            color=discord.Color.blurple()
        )
        embed.add_field(name="AFK Duration", value=f"{hours} hours, {minutes} minutes, and {seconds} seconds.", inline=False)

        await message.channel.send(embed=embed)
        afk_users.pop(message.author.id)

    else:
        mentions = [mention for mention in message.mentions if mention.id in afk_users]
        for mention in mentions:
            afk_data = afk_users[mention.id]
            afk_time = afk_data['time']
            duration = current_time - afk_time
            hours, remainder = divmod(int(duration.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)

            embed = discord.Embed(
                title="AFK Notification",
                description=f"{mention.mention} is currently AFK.",
                color=discord.Color.blurple()
            )
            embed.add_field(name="Reason", value=afk_data['reason'], inline=False)
            embed.add_field(name="AFK Duration", value=f"{hours} hours, {minutes} minutes, and {seconds} seconds.", inline=False)

            await message.channel.send(embed=embed)

            afk_data['message_count'] += 1
            afk_users[mention.id] = afk_data

    await client.process_commands(message)
        
@client.command(name='avatar', aliases=['av'])
async def avatar(ctx, *, member: discord.Member = None):
    if not member:
        member = ctx.author
    embed = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.blue())
    embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await ctx.send(embed=embed)

@client.command(name='server')
async def server(ctx, subcommand: str = None):
    if subcommand == 'info':
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
    else:
        embed = discord.Embed(description="Invalid command. Use ```.server info``` to get server information.", color=discord.Color.red())
        await ctx.send(embed=embed)
        
@client.command(name='binfo')
async def bot_info(ctx):
    embed = discord.Embed(title="Bot Information", color=discord.Color.blurple())
    embed.add_field(name="Bot Name", value=client.user.name, inline=True)
    embed.add_field(name="Bot ID", value=client.user.id, inline=True)
    embed.add_field(name="Server Count", value=len(client.guilds), inline=True)
    embed.add_field(name="User Count", value=len(set(client.get_all_members())), inline=True)
    embed.add_field(name="Ping", value=f"```{round(client.latency * 1000)}ms```", inline=True)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

@client.command(name='coin')
async def coin(ctx, *, subcommand=None):
    if subcommand == 'flip':
        result = random.choice(['Heads', 'Tails'])
        embed = discord.Embed(title="🪙 Coin Flip", description=f"The coin landed on **{result}**!", color=discord.Color.blurple())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)

@client.command(name='8ball')
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

@client.command(name='dice')
async def dice(ctx, rolls: int = 1):
    if rolls < 1 or rolls > 10:
        await ctx.send("Please choose a number of rolls between 1 and 10.")
        return

    roll_results = [random.randint(1, 6) for _ in range(rolls)]
    roll_sum = sum(roll_results)

    embed = discord.Embed(title="🎲 Dice Roll", color=discord.Color.blurple())
    embed.add_field(name="Roll Results:", value=", ".join(map(str, roll_results)), inline=False)
    embed.add_field(name="Total:", value=str(roll_sum), inline=False)

    if rolls == 1:
        embed.set_footer(text="Rolled 1 dice.")
    else:
        embed.set_footer(text=f"Rolled {rolls} dice.")

    await ctx.send(embed=embed)
    
client.run(os.getenv('TOKEN'))
