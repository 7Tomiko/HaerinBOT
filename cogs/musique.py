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

    def extract_stream_url(self, query):
        ydl_opts = {
            'format': 'bestaudio/best',
            'default_search': 'scsearch',
            'quiet': True,
            'no_warnings': True,
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                return info['url'], info.get("title", "Inconnu")
        except Exception as e:
            raise e

    async def play_next(self, interaction: Interaction, voice_client):
        guild_id = interaction.guild.id
        if self.queues[guild_id].empty():
            self.currently_playing.pop(guild_id, None)
            return

        stream_url, title = await self.queues[guild_id].get()
        self.currently_playing[guild_id] = title

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -b:a 128k'
        }

        def after_playing(error):
            asyncio.run_coroutine_threadsafe(
                self.play_next(interaction, voice_client),
                self.bot.loop
            )

        voice_client.play(FFmpegPCMAudio(stream_url, **ffmpeg_options), after=after_playing)
        
        try:
            await interaction.followup.send(f"▶️ Lecture : **{title}**")
        except:
            pass

    @app_commands.command(name="play", description="Joue une musique")
    async def play(self, interaction: Interaction, query: str):
        await interaction.response.defer()

        if interaction.user.voice is None:
            await interaction.followup.send("❌ Tu dois être dans un salon vocal.", ephemeral=True)
            return

        voice_client = interaction.guild.voice_client
        if voice_client is None:
            voice_client = await interaction.user.voice.channel.connect()

        try:
            stream_url, title = await asyncio.to_thread(self.extract_stream_url, query)
            await self.queues[interaction.guild.id].put((stream_url, title))

            if not voice_client.is_playing() and interaction.guild.id not in self.currently_playing:
                await self.play_next(interaction, voice_client)
            else:
                await interaction.followup.send(f"⏳ Ajouté à la file d'attente : **{title}**")
        except Exception:
            await interaction.followup.send("❌ Erreur lors du chargement de la musique.", ephemeral=True)

    @app_commands.command(name="queue", description="Affiche la file d'attente")
    async def queue(self, interaction: Interaction):
        guild_id = interaction.guild.id
        queue = list(self.queues[guild_id]._queue)

        if not queue:
            await interaction.response.send_message("📭 La file d'attente est vide.", ephemeral=True)
            return

        msg = "📃 **File d'attente :**\n"
        msg += "\n".join([f"{idx+1}. {title}" for idx, (_, title) in enumerate(queue)])
        
        if guild_id in self.currently_playing:
            msg = f"▶️ **En cours :** {self.currently_playing[guild_id]}\n\n" + msg
        
        await interaction.response.send_message(msg)

    @app_commands.command(name="skip", description="Passe à la musique suivante")
    async def skip(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭️ Musique suivante...")
        else:
            await interaction.response.send_message("❌ Rien n'est en cours de lecture.", ephemeral=True)

    @app_commands.command(name="pause", description="Met la musique en pause")
    async def pause(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Musique mise en pause.")
        else:
            await interaction.response.send_message("❌ Aucune musique à mettre en pause.", ephemeral=True)

    @app_commands.command(name="resume", description="Reprend la musique")
    async def resume(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Reprise de la musique.")
        else:
            await interaction.response.send_message("❌ Aucune musique en pause.", ephemeral=True)

    @app_commands.command(name="stop", description="Arrête la musique et vide la file")
    async def stop(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if vc:
            guild_id = interaction.guild.id
            while not self.queues[guild_id].empty():
                try:
                    self.queues[guild_id].get_nowait()
                except:
                    break
            self.currently_playing.pop(guild_id, None)
            vc.stop()
            await vc.disconnect()
            await interaction.response.send_message("⏹️ Musique arrêtée et déconnecté.")
        else:
            await interaction.response.send_message("❌ Je ne suis pas dans un canal vocal.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MusicCog(bot))