import discord
from discord import app_commands, FFmpegPCMAudio, Interaction
from discord.ext import commands
from yt_dlp import YoutubeDL
import asyncio
from collections import defaultdict



class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = defaultdict(asyncio.Queue)
        self.currently_playing = {}

    def extract_stream_url(self, url):
        ydl_opts = {
            'format': 'bestaudio',
            'quiet': True,
            'no_warnings': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info['url'], info.get("title", "Inconnu")

    async def play_next(self, interaction: Interaction, voice_client):
        guild_id = interaction.guild.id
        if self.queues[guild_id].empty():
            self.currently_playing.pop(guild_id, None)
            return

        stream_url, title = await self.queues[guild_id].get()
        self.currently_playing[guild_id] = title

        def after_playing(error):
            if error:
                print(f"Erreur audio : {error}")
            asyncio.run_coroutine_threadsafe(
                self.play_next(interaction, voice_client),
                self.bot.loop
            )

        voice_client.play(FFmpegPCMAudio(stream_url), after=after_playing)
        await interaction.followup.send(f"▶️ Lecture : **{title}**")

    @app_commands.command()
    async def play(self, interaction: Interaction, url: str):
        await interaction.response.defer()

        if interaction.user.voice is None:
            await interaction.followup.send("❌ Tu dois être dans un salon vocal.", ephemeral=True)
            return

        voice_client = interaction.guild.voice_client
        if voice_client is None:
            voice_client = await interaction.user.voice.channel.connect()

        try:
            stream_url, title = await asyncio.to_thread(self.extract_stream_url, url)
            await self.queues[interaction.guild.id].put((stream_url, title))

            if not voice_client.is_playing() and interaction.guild.id not in self.currently_playing:
                await self.play_next(interaction, voice_client)
            else:
                await interaction.followup.send(f"⏳ Ajouté à la file d’attente : **{title}**")
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors de l'extraction : {e}", ephemeral=True)

    @app_commands.command()
    async def queue(self, interaction: Interaction):
        guild_id = interaction.guild.id
        queue = list(self.queues[guild_id]._queue)

        if not queue:
            await interaction.response.send_message("📭 La file d'attente est vide.", ephemeral=True)
            return

        msg = "\n".join([f"{idx+1}. {title}" for idx, (_, title) in enumerate(queue)])
        await interaction.response.send_message(f"📃 File d’attente :\n{msg}")

    @app_commands.command()
    async def skip(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭️ Musique suivante...")
        else:
            await interaction.response.send_message("❌ Rien n’est en cours de lecture.", ephemeral=True)

    @app_commands.command()
    async def pause(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Musique mise en pause.")
        else:
            await interaction.response.send_message("❌ Aucune musique à mettre en pause.", ephemeral=True)

    @app_commands.command()
    async def resume(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Reprise de la musique.")
        else:
            await interaction.response.send_message("❌ Aucune musique en pause.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
