import discord
import random
from discord.ext import commands
from yt_dlp import YoutubeDL


def get_champions_list():
        url = "https://ddragon.leagueoflegends.com/cdn/13.24.1/data/fr_FR/champion.json"
        response = requests.get(url)
        data = response.json()
        champions = list(data['data'].keys())
        return champions


class CommandesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def img(self, context):
        nb = random.randint(1, 3)
        chemin = f"img/{nb}.jpg"
        fichier = discord.File(chemin, filename=f"image{nb}.jpg")
        await context.send(file=fichier)

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

    @commands.command()
    async def reseaux(self, context):
        insta = discord.utils.get(self.bot.emojis, name='logoInsta')
        twit = discord.utils.get(self.bot.emojis, name='logoX')
        yt = discord.utils.get(self.bot.emojis, name='logoYT')
        tiktok = discord.utils.get(self.bot.emojis, name='logoTikTok')
        await context.send(f"Voici les réseaux sociaux de NJZ :\n"
                           f"{insta} : <https://www.instagram.com/njz.officials/>\n"
                           f"{twit} : <https://x.com/NJZ_official>\n"
                           f"{yt} : <https://www.youtube.com/@njz_official>\n"
                           f"{tiktok} : <https://www.tiktok.com/@njz_official>")
    
    @commands.command()
    async def join(self, context):
        if context.author.voice:
            channel = context.author.voice.channel
            await channel.connect()
            await context.send(f"J'ai rejoint le salon vocal : {channel.name}")
        else:
            await context.send("Tu dois être dans un salon vocal pour que je puisse te rejoindre.")

    @commands.command()
    async def leave(self, context):
        if context.voice_client:
            await context.voice_client.disconnect()
            await context.send("J'ai quitté le salon vocal.")
        else:
            await context.send("Je ne suis connecté à aucun salon vocal.")

async def setup(bot):

    await bot.add_cog(CommandesCog(bot))

