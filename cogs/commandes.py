import discord
import random
from discord.ext import commands

class CommandesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def img(self, context):
        nb = random.randint(1, 3)
        chemin = f"img/{nb}.jpg"
        fichier = discord.File(chemin, filename=f"image{nb}.jpg")
        await context.send(file=fichier)

async def setup(bot):
    await bot.add_cog(CommandesCog(bot))