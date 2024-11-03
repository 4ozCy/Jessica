import discord
from discord.ext import commands
from discord.ui import Select, View
import aiohttp
from flask import Flask
from threading import Thread
import os
from datetime import datetime
import numpy as np
from dotenv import load_dotenv

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

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())

class Connect4:
    def __init__(self):
        self.board = np.zeros((6, 7), int)
        self.current_player = 1

    def drop_piece(self, column):
        for row in range(5, -1, -1):
            if self.board[row][column] == 0:
                self.board[row][column] = self.current_player
                return row, column
        return None

    def is_winning_move(self, row, col):
        return (self.check_direction(row, col, 1, 0) or
                self.check_direction(row, col, 0, 1) or
                self.check_direction(row, col, 1, 1) or
                self.check_direction(row, col, 1, -1))

    def check_direction(self, row, col, delta_row, delta_col):
        count = 0
        for delta in range(-3, 4):
            r = row + delta * delta_row
            c = col + delta * delta_col
            if 0 <= r < 6 and 0 <= c < 7 and self.board[r][c] == self.current_player:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
        return False

    def display_board(self):
        emoji_board = ''
        for row in self.board:
            emoji_board += ' '.join(['⚪' if cell == 0 else '🔴' if cell == 1 else '🟡' for cell in row]) + '\n'
        emoji_board += ' '.join([f'{i + 1}⃣' for i in range(7)])  # Column numbers
        return emoji_board

connect4_games = {}

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=".cmds"))
    print(f'We have logged in as {bot.user}')

@bot.command(name='quote')
async def send_quote(ctx):
    quote = await fetch_quote()
    if quote:
        embed = discord.Embed(description=quote, color=discord.Color.blurple())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
    else:
        await ctx.send("Sorry, I couldn't fetch a quote at the moment.")

@bot.command(name='rizz', aliases=['r'])
async def send_rizz(ctx):
    pickup_line = await fetch_pickup_line()
    if pickup_line:
        embed = discord.Embed(description=pickup_line, color=discord.Color.blurple())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
    else:
        await ctx.send("Sorry, I couldn't fetch a pickup line at the moment.")

@bot.command(name='c4')
async def connect4(ctx, opponent: discord.User):
    if ctx.channel.id in connect4_games:
        await ctx.send("A game is already in progress in this channel!")
        return

    connect4_games[ctx.channel.id] = Connect4()
    embed = discord.Embed(title=f"Connect 4: {ctx.author.mention} vs {opponent.mention}", description=connect4_games[ctx.channel.id].display_board())
    await ctx.send(embed=embed)
    await ctx.send("It's your turn! Type a column number (1-7) to drop your piece.")

@bot.listen('on_message')
async def on_message(message):
    if message.channel.id in connect4_games:
        game = connect4_games[message.channel.id]
        if message.author.id == game.current_player:
            try:
                column = int(message.content) - 1
                if 0 <= column < 7:
                    position = game.drop_piece(column)
                    if position:
                        if game.is_winning_move(position[0], position[1]):
                            await message.channel.send(f"{message.author.mention} wins! 🎉")
                            del connect4_games[message.channel.id]
                        else:
                            game.current_player = 2 if game.current_player == 1 else 1
                            embed = discord.Embed(title=f"Connect 4: {message.author.mention} vs {message.mentions[0].mention}", description=game.display_board())
                            await message.channel.send(embed=embed)
                            await message.channel.send(f"It's your turn, <@{game.current_player}>! Type a column number (1-7).")
                    else:
                        await message.channel.send("Column is full! Choose another column.")
                else:
                    await message.channel.send("Please enter a valid column number (1-7).")
            except ValueError:
                await message.channel.send("Please enter a valid number.")

@bot.command(name='say')
async def say(ctx, *, message: str):
    await ctx.message.delete()
    await ctx.send(message)

bot.run(os.getenv('TOKEN'))
