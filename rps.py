import discord
from discord.ext import commands
import random

class RPSView(discord.ui.View):
    def __init__(self, ctx, opponent=None):
        super().__init__(timeout=70)
        self.ctx = ctx
        self.opponent = opponent
        self.user_choice = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.ctx.author or interaction.user == self.opponent

    async def play_rps(self, interaction: discord.Interaction, user_choice):
        self.user_choice = user_choice
        choices = ['rock', 'paper', 'scissors']
        opponent_choice = random.choice(choices) if not self.opponent else random.choice(choices)

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

    @discord.ui.button(emoji="🪨", custom_id="rock")
    async def rock_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.play_rps(interaction, 'rock')

    @discord.ui.button(emoji="📄", custom_id="paper")
    async def paper_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.play_rps(interaction, 'paper')

    @discord.ui.button(emoji="✂️", custom_id="scissors")
    async def scissors_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.play_rps(interaction, 'scissors')

def setup_rps(bot):
    @bot.command(name='rps')
    async def rps(ctx, member: discord.Member = None):
        if member:
            if member == ctx.author:
                await ctx.send("You can't invite yourself to play!")
                return

            embed = discord.Embed(
                title="Rock-Paper-Scissors Invitation",
                description=f"{member.mention}, {ctx.author.mention} has invited you to play Rock-Paper-Scissors! React with ✅ to accept or ❌ to decline.",
                color=discord.Color.orange()
            )

            confirm_msg = await ctx.send(embed=embed)
          
            await confirm_msg.add_reaction("✅")
            await confirm_msg.add_reaction("❌")

            def check(reaction, user):
                return user == member and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == confirm_msg.id

            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
                if str(reaction.emoji) == "✅":
                    await ctx.send(f"{member.mention} accepted the invitation! Let's play!")
                    view = RPSView(ctx, opponent=member)
                    game_embed = discord.Embed(
                        title="Rock-Paper-Scissors",
                        description=f"{member.mention} vs {ctx.author.mention}\nChoose your move by clicking a button below!",
                        color=discord.Color.green()
                    )
                    await ctx.send(embed=game_embed, view=view)
                else:
                    await ctx.send(f"{member.mention} declined the invitation.")
            except discord.TimeoutError:
                await ctx.send(f"{member.mention} did not respond in time. Invitation cancelled.")
        else:
            view = RPSView(ctx)
            embed = discord.Embed(
                title="Rock-Paper-Scissors",
                description="Choose your move by clicking a button below!",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed, view=view)
