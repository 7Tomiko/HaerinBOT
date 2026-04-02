import discord
from discord.ext import commands
from discord import app_commands
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class IA(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

    @app_commands.command(name="ask", description="Pose une question à Haerin (Version 2026)")
    async def ask(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer()

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash', 
                contents=question
            )
            
            answer = response.text
            
            if len(answer) > 2000:
                await interaction.followup.send(answer[:1990] + "...")
            else:
                await interaction.followup.send(answer)

        except Exception as e:
            print(f"Erreur IA GenAI: {e}")
            await interaction.followup.send(f"❌ Oups, mon nouveau cerveau a un souci : {e}")

async def setup(bot):
    await bot.add_cog(IA(bot))