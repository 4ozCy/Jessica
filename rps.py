import discord
from discord.ext import commands
from discord import ButtonStyle, Interaction
import random

class RPSView(discord.ui.View):
    def __init__(self, opponent=None):
        super().__init__(timeout=60)
        self.opponent = opponent
        self.result = None

    @discord.ui.button(emoji="<:Rock:1304345338630504489>", style=ButtonStyle.secondary, custom_id="rock")
    async def rock_button(self, interaction: Interaction, button: discord.ui.Button):
        await self.handle_interaction(interaction, "rock")

    @discord.ui.button(emoji="<:Paper:1304345295672442891>", style=ButtonStyle.secondary, custom_id="paper")
    async def paper_button(self, interaction: Interaction, button: discord.ui.Button):
        await self.handle_interaction(interaction, "paper")

    @discord.ui.button(emoji="<:Scissor:1304346304243306596>", style=ButtonStyle.secondary, custom_id="scissors")
    async def scissors_button(self, interaction: Interaction, button: discord.ui.Button):
        await self.handle_interaction(interaction, "scissors")

    async def handle_interaction(self, interaction: Interaction, choice: str):
        if self.opponent and interaction.user != self.opponent:
            await interaction.response.send_message("This game isn't for you!", ephemeral=True)
            return
        self.result = choice
        self.stop()
        await interaction.response.defer()

async def play_rps(ctx, opponent=None):
    choices = ["rock", "paper", "scissors"]
    if opponent:
        embed = discord.Embed(title=f"{ctx.author.display_name} has invited {opponent.display_name} to a Rock Paper Scissors game!", color=discord.Color.blurple())
    else:
        embed = discord.Embed(title="Rock Paper Scissors - Challenge the bot!", color=discord.Color.blurple())
    view = RPSView(opponent=opponent)
    message = await ctx.send(embed=embed, view=view)
    await view.wait()

    if not view.result:
        embed.description = "The game timed out!"
        await message.edit(embed=embed, view=None)
        return

    player_choice = view.result
    bot_choice = random.choice(choices)

    if opponent:
        embed.description = f"{ctx.author.display_name} chose {player_choice}\n{opponent.display_name} chose {bot_choice}"
    else:
        embed.description = f"You chose {player_choice}\nBot chose {bot_choice}"

    winner_thumbnail = None
    if player_choice == bot_choice:
        embed.add_field(name="Outcome", value="It's a tie!")
        winner_thumbnail = None
    elif (player_choice == "rock" and bot_choice == "scissors") or (player_choice == "scissors" and bot_choice == "paper") or (player_choice == "paper" and bot_choice == "rock"):
        embed.add_field(name="Outcome", value="You win!")
        winner_thumbnail = ctx.author.avatar.url  # Player's avatar as winner thumbnail
    else:
        embed.add_field(name="Outcome", value="You lose!")
        winner_thumbnail = "https://cdn.discordapp.com/icons/1020864330173129728/a_44123ecf57b0348f76f5ab22cd5b95a5.gif"  # Bot thumbnail

    if winner_thumbnail:
        embed.set_thumbnail(url=winner_thumbnail)

    await message.edit(embed=embed, view=None)

def setup_rps(bot):
    @bot.command(name="rps")
    async def rps_command(ctx, member: discord.Member = None):
        if member:
            await play_rps(ctx, opponent=member)
        else:
            await play_rps(ctx)
