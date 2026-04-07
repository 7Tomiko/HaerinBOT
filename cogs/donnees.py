import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import datetime
from zoneinfo import ZoneInfo

class Donnees(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "haerin_database.db"

    async def cog_load(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titre TEXT,
                    date_evenement TIMESTAMP,
                    createur TEXT
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS music_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titre TEXT,
                    artiste TEXT,
                    user_name TEXT,
                    date_ecoute TIMESTAMP
                )
            ''')
            await db.commit()


    @app_commands.command(name="event_ajouter", description="Ajouter un évènement au calendrier")
    async def event_ajouter(self, interaction: discord.Interaction, titre: str, date: str):
        """Date au format JJ/MM/AAAA"""
        try:
            date_obj = datetime.datetime.strptime(date, "%d/%m/%Y")
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO events (titre, date_evenement, createur) VALUES (?, ?, ?)",
                    (titre, date_obj, interaction.user.display_name)
                )
                await db.commit()
            
            await interaction.response.send_message(f"✅ Évènement **{titre}** ajouté pour le {date} !")
        except ValueError:
            await interaction.response.send_message("❌ Format de date invalide. Utilise JJ/MM/AAAA")

    @app_commands.command(name="event_liste", description="Voir les prochains évènements")
    async def event_liste(self, interaction: discord.Interaction):
        fuseau_paris = ZoneInfo("Europe/Paris")
        maintenant = datetime.datetime.now(fuseau_paris)

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT titre, date_evenement, createur FROM events WHERE date_evenement >= ? ORDER BY date_evenement ASC",
                (maintenant.date(),)
            ) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            return await interaction.response.send_message("📅 Aucun évènement à venir.")

        embed = discord.Embed(title="🗓️ Agenda du Serveur", color=discord.Color.gold())
        for row in rows:
            date_f = datetime.datetime.fromisoformat(row[1]).strftime("%d/%m/%Y")
            embed.add_field(name=f"{date_f} - {row[0]}", value=f"Organisé par : {row[2]}", inline=False)
        
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="music_log", description="Enregistrer une pépite musicale")
    async def music_log(self, interaction: discord.Interaction, titre: str, artiste: str):
        """Permet aux membres de partager ce qu'ils écoutent et crée un classement"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO music_history (titre, artiste, user_name, date_ecoute) VALUES (?, ?, ?, ?)",
                (titre, artiste, interaction.user.display_name, datetime.datetime.now())
            )
            await db.commit()
        
        await interaction.response.send_message(f"🎶 **{titre}** ({artiste}) a été ajouté aux morceaux préférés du serveur !")

    @app_commands.command(name="music_top", description="Le top des musiques partagées sur le serveur")
    async def music_top(self, interaction: discord.Interaction):
        query = """
            SELECT titre, artiste, COUNT(*) as nb 
            FROM music_history 
            GROUP BY titre, artiste 
            ORDER BY nb DESC 
            LIMIT 5
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            return await interaction.response.send_message("📉 Pas encore de stats musicales.")

        embed = discord.Embed(title="🏆 Top 5 du serveur", color=discord.Color.purple())
        for i, row in enumerate(rows, 1):
            embed.add_field(name=f"{i}. {row[0]}", value=f"de **{row[1]}** (partagé {row[2]} fois)", inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Donnees(bot))