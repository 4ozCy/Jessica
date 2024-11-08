import discord
from discord.ui import Button, View
import aiohttp
import random

async def fetch_tr():
    url = "https://opentdb.com/api.php?amount=1&type=multiple"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            if data["response_code"] == 0:
                question_data = data["results"][0]
                question = question_data["question"]
                correct_answer = question_data["correct_answer"]
                incorrect_answers = question_data["incorrect_answers"]
                all_answers = incorrect_answers + [correct_answer]
                random.shuffle(all_answers)
                return question, correct_answer, all_answers
            else:
                return None, None, None

class AnswerButton(Button):
    def __init__(self, label, is_correct, *args, **kwargs):
        super().__init__(label=label, *args, **kwargs)
        self.is_correct = is_correct

    async def callback(self, interaction: discord.Interaction):
        if self.is_correct:
            await interaction.response.send_message("Correct!", ephemeral=True)
        else:
            await interaction.response.send_message("Incorrect!", ephemeral=True)

def setup_tr(bot):
    @bot.command(name="tr")
    async def tr(ctx):
        question, correct_answer, all_answers = await fetch_trivia()
        if not question:
            await ctx.send("Failed to retrieve a trivia question. Please try again.")
            return

        buttons = [AnswerButton(label=answer, is_correct=(answer == correct_answer)) for answer in all_answers]
        view = View(timeout=60)
        for button in buttons:
            view.add_item(button)

        embed = discord.Embed(title="Trivia Time!", description=question, color=discord.Color.blurple())
        await ctx.send(embed=embed, view=view)
