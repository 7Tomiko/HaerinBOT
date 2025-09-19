from discord import app_commands, FFmpegPCMAudio
from discord.ext import commands
from yt_dlp import YoutubeDL
import discord
import random
import os
import requests

#Commande LoL
def get_champions_list():
        url = "https://ddragon.leagueoflegends.com/cdn/13.24.1/data/fr_FR/champion.json"
        response = requests.get(url)
        data = response.json()
        champions = list(data['data'].keys())
        return champions
#Fin commande LoL

class SlashCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def champions(self, ctx):
        champions = get_champions_list()
        champion_list = ", ".join(champions)
        # Pour éviter d'envoyer trop de texte, on coupe si nécessaire
        chunks = [champion_list[i:i+1900] for i in range(0, len(champion_list), 1900)]
        for chunk in chunks:
            await ctx.send(chunk)
        z = random.choice(champions)
        await ctx.send(f"Champion aléatoire à ban est : {z}")

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