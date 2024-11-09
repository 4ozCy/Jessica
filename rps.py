import discord
from discord.ext import commands
from discord.ui import View
from discord import ButtonStyle, Interaction
import random

class RPSView(discord.ui.View):
    def __init__(self, player1, player2):
        super().__init__(timeout=120)
        self.player1 = player1
        self.player2 = player2
        self.player1_choice = None
        self.player2_choice = None
        self.result_ready = False

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
        if interaction.user == self.player1:
            if self.player1_choice:
                await interaction.response.send_message("You have already chosen!", ephemeral=True)
                return
            self.player1_choice = choice
            await interaction.response.send_message("You chose your move! Waiting for your opponent...", ephemeral=True)

        elif interaction.user == self.player2:
            if self.player2_choice:
                await interaction.response.send_message("You have already chosen!", ephemeral=True)
                return
            self.player2_choice = choice
            await interaction.response.send_message("You chose your move! Waiting for results...", ephemeral=True)

        else:
            await interaction.response.send_message("This game isn't for you!", ephemeral=True)
            return

        if self.player1_choice and self.player2_choice:
            self.result_ready = True
            self.stop()

async def play_rps(ctx, opponent):
    embed = discord.Embed(
        title=f"{ctx.author.display_name} has invited {opponent.display_name} to a Rock Paper Scissors game!",
        color=discord.Color.blurple()
    )
    view = RPSView(player1=ctx.author, player2=opponent)
    message = await ctx.send(embed=embed, view=view)
    await view.wait()

    if not view.result_ready:
        embed.description = "The game timed out due to inactivity!"
        await message.edit(embed=embed, view=None)
        return

    player1_choice = view.player1_choice
    player2_choice = view.player2_choice

    embed.description = (
        f"{ctx.author.display_name} chose {player1_choice}\n"
        f"{opponent.display_name} chose {player2_choice}\n"
    )

    if player1_choice == player2_choice:
        embed.add_field(name="Outcome", value="It's a tie!")
    elif (player1_choice == "rock" and player2_choice == "scissors") or \
         (player1_choice == "scissors" and player2_choice == "paper") or \
         (player1_choice == "paper" and player2_choice == "rock"):
        embed.add_field(name="Outcome", value=f"{ctx.author.display_name} wins!")
    else:
        embed.add_field(name="Outcome", value=f"{opponent.display_name} wins!")

    await message.edit(embed=embed, view=None)

def setup_rps(bot):
    @bot.command(name="rps")
    async def rps_command(ctx, member: discord.Member):
        if member:
            await play_rps(ctx, opponent=member)
        else:
            await ctx.send("You need to mention an opponent to play!")
