import discord
from discord.ext import commands
from discord.ui import Button, View
import requests
import random

def setup_trivia(bot):
    @bot.command(name="trivia", aliases=['tr'])
    async def trivia(ctx):
        url = "https://opentdb.com/api.php?amount=1&type=multiple"
        response = requests.get(url)
        data = response.json()

        question_data = data['results'][0]
        question = question_data['question']
        correct_answer = question_data['correct_answer']
        incorrect_answers = question_data['incorrect_answers']
        all_answers = incorrect_answers + [correct_answer]
        random.shuffle(all_answers)

        embed = discord.Embed(title="Trivia Game", description=question, color=discord.Color.blurple())

        class TriviaView(View):
            def __init__(self, correct_answer):
                super().__init__()
                self.correct_answer = correct_answer

            async def button_callback(self, interaction: discord.Interaction, button: Button):
                if button.label == self.correct_answer:
                    await interaction.response.send_message("Correct!", ephemeral=True)
                else:
                    await interaction.response.send_message(f"Wrong! The correct answer was: {self.correct_answer}", ephemeral=True)

        trivia_view = TriviaView(correct_answer)

        for answer in all_answers:
            button = Button(label=answer, style=discord.ButtonStyle.secondary)
            button.callback = lambda interaction, answer=answer: trivia_view.button_callback(interaction, button)
            trivia_view.add_item(button)

        await ctx.send(embed=embed, view=trivia_view)
