import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from keep_alive import keep_alive
import shutil

if os.path.exists("./temp"):
    shutil.rmtree("./temp")
os.makedirs("./temp")

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

class MonBot(commands.Bot):
    async def setup_hook(self):
        for extension in ['commandes', 'commandes_slash', 'moderation', 'musique']:
            await self.load_extension(f'cogs.{extension}')
        await self.tree.sync()

intents = discord.Intents.all()
bot = MonBot(command_prefix='*', intents=intents)

keep_alive()
bot.run(token=token)