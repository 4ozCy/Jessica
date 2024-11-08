import discord
from discord.ext import commands
import aiohttp
import random

def setup_trivia(bot):
    @bot.command(name="trivia", aliases=['tr'])
    async def trivia(ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://opentdb.com/api.php?amount=1") as response:
                data = await response.json()

        question_data = data["results"][0]
        question = question_data["question"]
        correct_answer = question_data["correct_answer"]
        incorrect_answers = question_data["incorrect_answers"]
        all_answers = incorrect_answers + [correct_answer]
        random.shuffle(all_answers)

        embed = discord.Embed(title="Trivia Time!", description=question, color=discord.Color.blurple())
        view = discord.ui.View()
        for answer in all_answers:
            button = discord.ui.Button(label=answer, style=discord.ButtonStyle.secondary)
            async def button_callback(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("This isn't your game!", ephemeral=True)
                if button.label == correct_answer:
                    embed.description = f"✅ Correct! The answer is {correct_answer}."
                else:
                    embed.description = f"❌ Wrong! The correct answer was {correct_answer}."
                await interaction.response.edit_message(embed=embed, view=None)
            button.callback = button_callback
            view.add_item(button)
        await ctx.send(embed=embed, view=view)
