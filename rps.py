import discord
from discord.ext import commands
from discord.ui import Button, View
from discord import ButtonStyle, Interaction
import random

class RPSView(discord.ui.View):
    def __init__(self, player1, player2):
        super().__init__(timeout=120)
        self.player1 = player1
        self.player2 = player2
        self.player1_choice = None
        self.player2_choice = None
        self.invitation_accepted = False

    @discord.ui.button(label="Accept", style=ButtonStyle.success, custom_id="accept")
    async def accept_button(self, interaction: Interaction, button: discord.ui.Button):
        if interaction.user != self.player2:
            await interaction.response.send_message("Only the invited opponent can accept the game!", ephemeral=True)
            return

        self.invitation_accepted = True
        await interaction.response.send_message("Invitation accepted! You can now make your move.", ephemeral=True)
        for child in self.children:
            if child.custom_id in ["accept", "decline"]:
                child.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Decline", style=ButtonStyle.danger, custom_id="decline")
    async def decline_button(self, interaction: Interaction, button: discord.ui.Button):
        if interaction.user != self.player2:
            await interaction.response.send_message("Only the invited opponent can decline the game!", ephemeral=True)
            return

        await interaction.response.send_message("Invitation declined!", ephemeral=True)
        await interaction.message.edit(content="The game invitation was declined.", view=None)
        self.stop()

    @discord.ui.button(emoji="<:Rock:1304345338630504489>", style=ButtonStyle.secondary, custom_id="rock", disabled=True)
    async def rock_button(self, interaction: Interaction, button: discord.ui.Button):
        await self.handle_interaction(interaction, "rock")

    @discord.ui.button(emoji="<:Paper:1304345295672442891>", style=ButtonStyle.secondary, custom_id="paper", disabled=True)
    async def paper_button(self, interaction: Interaction, button: discord.ui.Button):
        await self.handle_interaction(interaction, "paper")

    @discord.ui.button(emoji="<:Scissor:1304346304243306596>", style=ButtonStyle.secondary, custom_id="scissors", disabled=True)
    async def scissors_button(self, interaction: Interaction, button: discord.ui.Button):
        await self.handle_interaction(interaction, "scissors")

    async def handle_interaction(self, interaction: Interaction, choice: str):
        if not self.invitation_accepted:
            await interaction.response.send_message("The game hasn't been accepted yet!", ephemeral=True)
            return

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

        # Check if both players have made their choices
        if self.player1_choice and self.player2_choice:
            self.stop()

async def play_rps(ctx, opponent):
    embed = discord.Embed(
        title=f"{ctx.author.display_name} has invited {opponent.display_name} to a Rock Paper Scissors game!",
        description="Waiting for the opponent to accept the invitation...",
        color=discord.Color.blurple()
    )
    view = RPSView(player1=ctx.author, player2=opponent)
    message = await ctx.send(embed=embed, view=view)
    await view.wait()

    if not view.invitation_accepted:
        embed.description = "The invitation was not accepted in time or was declined."
        await message.edit(embed=embed, view=None)
        return

    if not (view.player1_choice and view.player2_choice):
        embed.description = "The game timed out due to inactivity!"
        await message.edit(embed=embed, view=None)
        return

    # Determine and display the results
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
