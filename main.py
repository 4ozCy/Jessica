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
        embed = discord.Embed(title="Quote", description=quote, color=0x3498db)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Sorry, I couldn't fetch a quote at the moment.")

@client.command(name='rizz', aliases=['r'])
async def send_rizz(ctx):
    pickup_line = await fetch_pickup_line()
    if pickup_line:
        embed = discord.Embed(title="Rizz You Up", description=pickup_line, color=0x3498db)
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
    embed = discord.Embed(title=" ``` Commands list", color=0x3498db)
    embed.add_field(name="quote", value="send a random inspirational quote.", inline=False)
    embed.add_field(name="rizz", value="Rizz You Up", inline=False)
    embed.add_field(name="joke", value="Tells a random joke.", inline=False)
    embed.add_field(name="insult/in", value="send a random insult", inline=False)
    embed.add_field(name="animequote/aq", value="send a random anime quote.", inline=False)
    embed.add_field(name="slap", value="Slap you in the face", inline=False)
    embed.add_field(name="Breakup/bp", value="If you want to breakup with your love use this command. ``` ", inline=False)
    await ctx.send(embed=embed)

@client.command(name='insult', aliases=['in'])
async def send_insult(ctx):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://insult.mattbas.org/api/insult") as response:
                insult = await response.text()
        embed = discord.Embed(title="Insulting You because why not", description=insult, color=0x3498db)
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
                embed = discord.Embed(title="Anime Quote", description=f'" ``` {quote}"\n- {character} ({anime}) ``` ', color=0x3498db)
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
                embed = discord.Embed(title="Slap You in the face because I'm bored", description=f"{ctx.author.mention} slaps {member.mention}!!", color=0x3498db)
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

client.run(os.getenv('TOKEN'))
