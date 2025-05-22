import discord
import os
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

client = discord.Client(intents=discord.Intents.all())

intents = discord.Intents.default()

client.run(token=token)