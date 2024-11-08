import discord
from discord.ext import commands
from discord import ButtonStyle, Interaction
from discord.ui import Button
import random

class RPSView(discord.ui.View):
    def __init__(self, ctx, opponent=None):
        super().__init__(timeout=70)
        self.ctx = ctx
        self.opponent = opponent
        self.user_choice = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.ctx.author or (self.opponent and interaction.user == self.opponent)

    async def play_rps(self, interaction: discord.Interaction, user_choice):
        self.user_choice = user_choice
        choices = ['rock', 'paper', 'scissors']
        opponent_choice = random.choice(choices)

        result = None
        if user_choice == opponent_choice:
            result = "It's a tie!"
        elif (user_choice == 'rock' and opponent_choice == 'scissors') or \
             (user_choice == 'scissors' and opponent_choice == 'paper') or \
             (user_choice == 'paper' and opponent_choice == 'rock'):
            result = f"{interaction.user.mention} wins!"
        else:
            result = f"{self.opponent.mention if self.opponent else 'Bot'} wins!"

        embed = discord.Embed(
            title="Rock-Paper-Scissors",
            description=f"**{interaction.user.mention}** chose {user_choice}.\n**{self.opponent.mention if self.opponent else 'Bot'}** chose {opponent_choice}.\n\n{result}",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(emoji="🪨", label="Rock", style=discord.ButtonStyle.primary)
    async def rock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play_rps(interaction, 'rock')

    @discord.ui.button(emoji="📄", label="Paper", style=discord.ButtonStyle.success)
    async def paper_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play_rps(interaction, 'paper')

    @discord.ui.button(emoji="✂️", label="Scissors", style=discord.ButtonStyle.danger)
    async def scissors_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play_rps(interaction, 'scissors')

def setup_rps(bot):
    @bot.command(name='pav')
    async def rps(ctx, member: discord.Member = None):
        if member:
            if member == ctx.author:
                await ctx.send("You can't invite yourself to play!")
                return

            embed = discord.Embed(
                title="Rock-Paper-Scissors Invitation",
                description=f"{member.mention}, {ctx.author.mention} has invited you to play Rock-Paper-Scissors! React below to accept.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed, view=RPSView(ctx, opponent=member))
        else:
            embed = discord.Embed(
                title="Rock-Paper-Scissors Game",
                description="Choose your move below!",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed, view=RPSView(ctx))
