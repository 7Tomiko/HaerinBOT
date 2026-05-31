import discord
from discord.ext import commands
from discord import app_commands
import shutil
import asyncio  # Ajouté pour exécuter des commandes système sans bloquer le bot

class Systeme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stockage", description="Affiche l'état du stockage AWS en Mo")
    async def stockage(self, interaction: discord.Interaction):
        total, used, free = shutil.disk_usage("/")
        
        total_mb = total / (1024**2)
        used_mb = used / (1024**2)
        free_mb = free / (1024**2)
        percent = (used / total) * 100

        embed = discord.Embed(title="💾 État du stockage AWS", color=discord.Color.blue())
        
        embed.add_field(name="Total", value=f"{total_mb:.2f} Mo", inline=True)
        embed.add_field(name="Utilisé", value=f"{used_mb:.2f} Mo ({percent:.1f}%)", inline=True)
        embed.add_field(name="Libre", value=f"{free_mb:.2f} Mo", inline=True)
        
        if percent > 90:
            embed.description = "⚠️ **Attention : Stockage presque plein !**"
            embed.color = discord.Color.red()

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="logs", description="Affiche les derniers logs du serveur AWS (Linux)")
    async def logs(self, interaction: discord.Interaction):
        if interaction.user.id != 364103319184211969:
            return await interaction.response.send_message("⛔ Accès refusé.", ephemeral=True)

        await interaction.response.defer(thinking=True)

        try:
            process = await asyncio.create_subprocess_exec(
                'sudo', 'journalctl', '-n', '15', '--no-pager',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logs_text = stdout.decode('utf-8')
                
                if len(logs_text) > 1900:
                    logs_text = "...\n" + logs_text[-1850:]
                
                await interaction.followup.send(f"📜 **Logs récents (Ubuntu) :**\n```text\n{logs_text}\n```")
            else:
                error_text = stderr.decode('utf-8')
                await interaction.followup.send(f"❌ **Erreur Linux :**\n```text\n{error_text}\n```")

        except Exception as e:
            await interaction.followup.send(f"❌ **Erreur inattendue :** {e}")


async def setup(bot):
    await bot.add_cog(Systeme(bot))