import discord
from discord.ext import commands
from discord import app_commands
import shutil

class Systeme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stockage", description="Affiche l'état du stockage AWS")
    async def stockage(self, interaction: discord.Interaction):
        total, used, free = shutil.disk_usage("/")
        
        total_gb = total // (2**30)
        used_gb = used // (2**30)
        free_gb = free // (2**30)
        percent = (used / total) * 100

        embed = discord.Embed(title="💾 État du stockage AWS", color=discord.Color.blue())
        embed.add_field(name="Total", value=f"{total_gb} Go", inline=True)
        embed.add_field(name="Utilisé", value=f"{used_gb} Go ({percent:.1f}%)", inline=True)
        embed.add_field(name="Libre", value=f"{free_gb} Go", inline=True)
        
        if percent > 90:
            embed.description = "⚠️ **Attention : Stockage presque plein !**"
            embed.color = discord.Color.red()

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Systeme(bot))