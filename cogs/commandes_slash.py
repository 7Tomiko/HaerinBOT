import discord
from discord import app_commands
from discord.ext import commands
import random

class SlashCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def lol(self, interaction: discord.Interaction, qui: str, role: str):
        qui = qui.lower()
        role = role.lower()
        if qui == "apy" and role == "mid":
            champs = ["Zoe", "Ahri", "Shyvana", "Neeko", "Viktor"]
            champ = random.choice(champs)
            await interaction.response.send_message(f"Le champion aléatoire de {qui} en {role} est : {champ}")
        elif qui == "tomiko" and role == "jungle":
            champs = ["Sejuani", "Viegz", "Shyvana", "Kindred", "Lilia"]
            champ = random.choice(champs)
            await interaction.response.send_message(f"Le champion aléatoire de {qui} en {role} est : {champ}")
        else:
            await interaction.response.send_message("Aucune combinaison correspondante trouvée.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SlashCog(bot))