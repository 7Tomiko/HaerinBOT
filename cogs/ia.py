import discord
from discord import app_commands, Interaction
from discord.ext import commands
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    print("⚠️ ATTENTION : La clé GEMINI_API_KEY est introuvable dans le fichier .env !")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

class IACog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ask", description="Pose une question à l'intelligence artificielle Gemini")
    @app_commands.describe(question="Ta question pour l'IA")
    async def ask(self, interaction: Interaction, question: str):
        await interaction.response.defer()

        try:
            response = await interaction.client.loop.run_in_executor(
                None, 
                lambda: model.generate_content(question)
            )
            
            reponse_texte = response.text
            if len(reponse_texte) > 1950:
                reponse_texte = reponse_texte[:1950] + "\n\n*(Réponse tronquée car trop longue pour Discord)*"
            
            msg = f"**❓ Question :** {question}\n\n**🤖 Réponse :**\n{reponse_texte}"
            await interaction.followup.send(msg)

        except Exception as e:
            await interaction.followup.send(f"❌ Oups, j'ai eu un bug de cerveau : {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(IACog(bot))