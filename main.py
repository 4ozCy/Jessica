import discord
from discord.ext import commands, tasks
from fastapi import FastAPI
from uvicorn import Config, Server
import os
from dotenv import load_dotenv
from datetime import datetime
import requests
import cmds
import xo

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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=".cmds"))
    bot.start_time = discord.utils.utcnow()
    print(f'Bot connected as {bot.user}')
    start_fastapi.start()

cmds.setup_cmds(bot)
xo.setup_xo(bot)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "host file" in message.content.lower():
        await message.channel.send("Processing your request...")

        file_url = None

        if message.attachments:
            file_url = message.attachments[0].url
            filename = message.attachments[0].filename

        if not file_url:
            words = message.content.split()
            for word in words:
                if word.startswith("http://") or word.startswith("https://"):
                    file_url = word
                    filename = file_url.split("/")[-1]
                    break

        if not file_url:
            await message.channel.send("Please attach a file or provide a URL.")
            return

        try:
            response = requests.get(file_url)
            with open(filename, "wb") as file:
                file.write(response.content)

            filebox_response = requests.post(
                "https://filebox.lol/api/file",
                files={"file": open(filename, "rb")}
            )

            filebox_data = filebox_response.json()

            if filebox_response.status_code == 200 and "url" in filebox_data:
                await message.channel.send(f"File hosted successfully! Here's your link: {filebox_data['url']}")
            else:
                await message.channel.send("Error: Could not upload to Filebox.")

            os.remove(filename)

        except Exception as e:
            await message.channel.send(f"An error occurred: {e}")
            
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
