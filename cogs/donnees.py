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
            await db.execute("PRAGMA foreign_keys = ON;")
            
            await db.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
                discord_id VARCHAR(50) PRIMARY KEY,
                pseudo VARCHAR(100),
                score_activite INT DEFAULT 0
            )''')

            await db.execute('''CREATE TABLE IF NOT EXISTS musiques (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titre VARCHAR(150),
                artiste VARCHAR(150),
                genre VARCHAR(50) DEFAULT 'Inconnu'
            )''')

            await db.execute('''CREATE TABLE IF NOT EXISTS evenements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titre VARCHAR(200),
                date_event DATETIME,
                organisateur_id VARCHAR(50),
                FOREIGN KEY(organisateur_id) REFERENCES utilisateurs(discord_id) ON DELETE CASCADE
            )''')

            await db.execute('''CREATE TABLE IF NOT EXISTS participations (
                event_id INTEGER,
                utilisateur_id VARCHAR(50),
                PRIMARY KEY (event_id, utilisateur_id),
                FOREIGN KEY(event_id) REFERENCES evenements(id) ON DELETE CASCADE,
                FOREIGN KEY(utilisateur_id) REFERENCES utilisateurs(discord_id) ON DELETE CASCADE
            )''')

            await db.execute('''CREATE TABLE IF NOT EXISTS historique_ecoutes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id VARCHAR(50),
                musique_id INTEGER,
                date_ecoute DATETIME,
                FOREIGN KEY(user_id) REFERENCES utilisateurs(discord_id) ON DELETE CASCADE,
                FOREIGN KEY(musique_id) REFERENCES musiques(id) ON DELETE CASCADE
            )''')
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
            await interaction.response.send_message("❌ Format de date invalide. Utilise JJ/MM/AAAA (ex: 25/12/2026)")

    @app_commands.command(name="event_liste", description="Voir les prochains évènements")
    async def event_liste(self, interaction: discord.Interaction):
        fuseau_paris = ZoneInfo("Europe/Paris")
        maintenant = datetime.datetime.now(fuseau_paris)

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, titre, date_evenement, createur FROM events WHERE date_evenement >= ? ORDER BY date_evenement ASC",
                (maintenant.date(),)
            ) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            return await interaction.response.send_message("📅 Aucun évènement à venir.")

        embed = discord.Embed(title="🗓️ Agenda du Serveur", color=discord.Color.gold())
        for row in rows:
            date_f = datetime.datetime.fromisoformat(row[2]).strftime("%d/%m/%Y")
            embed.add_field(name=f"[{row[0]}] {date_f} - {row[1]}", value=f"Organisé par : {row[3]}", inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="event_supprimer", description="Supprimer un évènement via son ID")
    async def event_supprimer(self, interaction: discord.Interaction, id_event: int):
        """Supprime une ligne de la base de données de manière propre via la clé primaire"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM events WHERE id = ?", (id_event,))
            await db.commit()
            
            if cursor.rowcount > 0:
                await interaction.response.send_message(f"🗑️ L'évènement numéro **{id_event}** a été supprimé.")
            else:
                await interaction.response.send_message(f"❌ Impossible de trouver un évènement avec l'ID {id_event}.")


    @app_commands.command(name="music_log", description="Enregistrer une pépite musicale")
    async def music_log(self, interaction: discord.Interaction, titre: str, artiste: str):
        """Permet aux membres de partager ce qu'ils écoutent pour créer un classement"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO music_history (titre, artiste, user_name, date_ecoute) VALUES (?, ?, ?, ?)",
                (titre, artiste, interaction.user.display_name, datetime.datetime.now())
            )
            await db.commit()
        
        await interaction.response.send_message(f"🎶 **{titre}** ({artiste}) a été ajouté aux favoris du serveur !")

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
            return await interaction.response.send_message("📉 Pas encore de stats musicales. Utilisez /music_log pour commencer !")

        embed = discord.Embed(title="🏆 Top 5 des pépites du serveur", color=discord.Color.purple())
        for i, row in enumerate(rows, 1):
            embed.add_field(name=f"{i}. {row[0]}", value=f"de **{row[1]}** (partagé {row[2]} fois)", inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="export_sql", description="[ADMIN] Télécharger le Dump SQL")
    async def export_sql(self, interaction: discord.Interaction):
        try:
            fichier = discord.File("sauvegarde_bts.sql")
            await interaction.response.send_message("📂 Voici le code SQL pour le prof :", file=fichier, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur, problème du coté serveur : {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Donnees(bot))