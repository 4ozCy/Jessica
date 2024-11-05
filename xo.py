import discord
import random
from discord.ext import commands

def setup_xo(bot):

    @bot.command(name='xo')
    async def xo(ctx, opponent: discord.Member):
        if opponent == ctx.author:
            await ctx.send("You can't play against yourself!")
            return

        players = {ctx.author: "❌", opponent: "⭕"} if random.choice([True, False]) else {ctx.author: "⭕", opponent: "❌"}
        current_player = random.choice([ctx.author, opponent])

        class InvitationView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.value = None

            @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
            async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user != opponent:
                    await interaction.response.send_message("Only the invited player can accept!", ephemeral=True)
                    return
                self.value = True
                self.stop()

            @discord.ui.button(label="Decline", style=discord.ButtonStyle.secondary)
            async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user != opponent:
                    await interaction.response.send_message("Only the invited player can decline!", ephemeral=True)
                    return
                self.value = False
                self.stop()

        invitation_view = InvitationView()
        invitation_message = await ctx.send(
            f"{opponent.mention}, {ctx.author.mention} has challenged you to a game of Tic-Tac-Toe! Do you accept?", 
            view=invitation_view
        )
        await invitation_view.wait()
        await invitation_message.delete()

        if invitation_view.value is None:
            await ctx.send("Invitation timed out.")
            return
        elif not invitation_view.value:
            await ctx.send(f"{opponent.mention} declined the invitation.")
            return

        class TicTacToeButton(discord.ui.Button):
            def __init__(self, x, y):
                super().__init__(style=discord.ButtonStyle.secondary, label="➖", row=y)
                self.x = x
                self.y = y

            async def callback(self, interaction: discord.Interaction):
                nonlocal current_player
                if interaction.user != current_player:
                    await interaction.response.send_message("It's not your turn!", ephemeral=True)
                    return
                if self.label != "➖":
                    await interaction.response.send_message("This spot is already taken!", ephemeral=True)
                    return
                self.label = players[current_player]
                self.style = discord.ButtonStyle.primary
                self.disabled = True

                if check_winner():
                    for child in self.view.children:
                        child.disabled = True
                    await interaction.response.edit_message(content=f"{current_player.mention} wins!", view=self.view)
                    return
                elif all(button.disabled for button in self.view.children):
                    await interaction.response.edit_message(content="It's a tie!", view=self.view)
                    return

                current_player = opponent if current_player == ctx.author else ctx.author
                await interaction.response.edit_message(content=f"Game in progress! It's {current_player.mention}'s turn.", view=self.view)

        def check_winner():
            for row in board:
                if row[0].label == row[1].label == row[2].label != "➖":
                    return True
            for col in range(3):
                if board[0][col].label == board[1][col].label == board[2][col].label != "➖":
                    return True
            if board[0][0].label == board[1][1].label == board[2][2].label != "➖":
                return True
            if board[0][2].label == board[1][1].label == board[2][0].label != "➖":
                return True
            return False

        board = [[TicTacToeButton(x, y) for x in range(3)] for y in range(3)]
        view = discord.ui.View()
        for row in board:
            for button in row:
                view.add_item(button)

        await ctx.send(
            f"Game Start! {ctx.author.mention} is `{players[ctx.author]}`, {opponent.mention} is `{players[opponent]}`. {current_player.mention} goes first.", 
            view=view)
