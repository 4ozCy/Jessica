import discord
from discord.ext import commands
from discord.ui import Button, View
import httpx
import random

user_streaks = {}
highest_streak = {"user_id": None, "streak": 0}

async def setup_trivia(bot):
    @bot.command(name="trivia", aliases=['tr'])
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
            button = Button(label=answer, style=discord.ButtonStyle.primary)
            buttons.append(button)

        class TriviaView(View):
            def __init__(self, correct_answer):
                super().__init__()
                self.correct_answer = correct_answer

            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                return interaction.user == ctx.author

            @discord.ui.button(label="Answer", style=discord.ButtonStyle.primary)
            async def answer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                global highest_streak

                if button.label == self.correct_answer:
                    await interaction.response.send_message("Correct! 🎉")

                    if interaction.user.id not in user_streaks:
                        user_streaks[interaction.user.id] = 1
                    else:
                        user_streaks[interaction.user.id] += 1

                    streak = user_streaks[interaction.user.id]

                    if streak > highest_streak["streak"]:
                        if highest_streak["user_id"] and highest_streak["user_id"] != interaction.user.id:
                            user_streaks[highest_streak["user_id"]] = 0

                        highest_streak["user_id"] = interaction.user.id
                        highest_streak["streak"] = streak

                        await ctx.send(f"Congratulations {interaction.user.mention}! You have the highest streak of {streak} and are now titled as **The Smartest**!")
                    else:
                        await ctx.send(f"{interaction.user.mention}, you now have a {streak}-win streak!")

                else:
                    await interaction.response.send_message(f"Wrong! The correct answer was: {self.correct_answer}.")
                    user_streaks[interaction.user.id] = 0

        trivia_view = TriviaView(correct_answer)

        for button in buttons:
            trivia_view.add_item(button)

        await ctx.send(embed=embed, view=trivia_view)
