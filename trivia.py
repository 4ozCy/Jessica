import discord
from discord.ext import commands
from discord.ui import Button, View
import httpx
import random

async def setup_trivia(bot):
    @bot.command(name="trivia")
    async def trivia(ctx):
        url = "https://opentdb.com/api.php?amount=1&type=multiple"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()

        question_data = data['results'][0]
        question = question_data['question']
        correct_answer = question_data['correct_answer']
        incorrect_answers = question_data['incorrect_answers']
        all_answers = incorrect_answers + [correct_answer]
        random.shuffle(all_answers)

        embed = discord.Embed(title="Trivia Game", description=question, color=discord.Color.blurple())
        buttons = []

        for answer in all_answers:
            button = Button(label=answer, style=discord.ButtonStyle.secondary)
            buttons.append(button)

        class TriviaView(View):
            def __init__(self, correct_answer):
                super().__init__()
                self.correct_answer = correct_answer

            @discord.ui.button(label="Answer", style=discord.ButtonStyle.secondary)
            async def answer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                if button.label == self.correct_answer:
                    await interaction.response.send_message("Correct!")
                else:
                    await interaction.response.send_message(f"Wrong! The correct answer was: {self.correct_answer}")

        trivia_view = TriviaView(correct_answer)

        await ctx.send(embed=embed, view=trivia_view)
