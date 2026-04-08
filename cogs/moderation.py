import discord
from discord.ext import commands
from discord import app_commands


class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, *, reason: str = None):
        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(f"{member.name} a été expulsé du serveur pour : {reason}")
        except Exception as e:
            await interaction.response.send_message(f"Erreur lors de l'expulsion : {e}", ephemeral=True)

    @app_commands.command()
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Choisis un nombre entre 1 et 100.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"✅ {len(deleted)} message(s) supprimé(s).", ephemeral=True)

    @app_commands.command()
    async def say(self, interaction: discord.Interaction, *, message: str):
        await interaction.response.send_message(message)

    @app_commands.command(name="nettoyer_mp", description="[ADMIN] Fait supprimer au bot ses derniers MP")
    async def nettoyer_mp(self, interaction: discord.Interaction, nombre: int = 10):
        """Demande au bot d'effacer ses propres messages dans tes MP"""
        await interaction.response.defer(ephemeral=True)

        try:
            mp_channel = await interaction.user.create_dm()
            
            messages_supprimes = 0
            async for message in mp_channel.history(limit=nombre * 2): 
                if message.author == self.bot.user:
                    await message.delete()
                    messages_supprimes += 1
                    
                if messages_supprimes >= nombre:
                    break
                    
            await interaction.followup.send(f"🧹 Le bot a supprimé ses {messages_supprimes} derniers messages dans tes MP !", ephemeral=True)
            
        except discord.Forbidden:
            await interaction.followup.send("❌ Je n'ai pas la permission de gérer tes MP. Vérifie tes paramètres de confidentialité.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Une erreur est survenue : {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))