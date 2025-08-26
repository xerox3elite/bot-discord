import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
from datetime import datetime, timezone
from typing import Optional

class CasierSystem(commands.Cog):
    """Système de casier judiciaire global pour Arsenal"""

    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/global_sanctions.db"
        self.bot.loop.create_task(self.init_database())

    async def init_database(self):
        """Initialise la base de données pour le casier global."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS global_sanctions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    sanction_type TEXT NOT NULL,
                    reason TEXT,
                    timestamp TEXT NOT NULL,
                    duration_seconds INTEGER,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            await db.commit()
            print("✅ Base de données du casier judiciaire global initialisée.")

    @app_commands.command(name="casier", description="Consulte le casier judiciaire global d'un utilisateur.")
    @app_commands.describe(utilisateur="L'utilisateur dont vous voulez voir le casier.")
    async def casier(self, interaction: discord.Interaction, utilisateur: discord.Member):
        """Affiche le casier judiciaire d'un utilisateur sur tous les serveurs du bot."""
        await interaction.response.defer(ephemeral=True)

        user_id_to_check = utilisateur.id

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT guild_id, moderator_id, sanction_type, reason, timestamp FROM global_sanctions WHERE user_id = ? ORDER BY timestamp DESC",
                (user_id_to_check,)
            )
            sanctions = await cursor.fetchall()

        embed = discord.Embed(
            title=f"⚖️ Casier Judiciaire Global de {utilisateur.display_name}",
            color=discord.Color.orange()
        )

        if not sanctions:
            embed.description = "Cet utilisateur a un casier vierge sur l'ensemble des serveurs."
            await interaction.followup.send(embed=embed)
            return

        embed.description = f"Total de **{len(sanctions)}** sanction(s) enregistrée(s)."

        for sanction in sanctions[:10]:  # Limite à 10 pour la lisibilité
            guild_id, moderator_id, sanc_type, reason, timestamp_str = sanction

            guild = self.bot.get_guild(guild_id)
            guild_name = guild.name if guild else f"Serveur Inconnu (ID: {guild_id})"

            moderator = self.bot.get_user(moderator_id)
            moderator_name = moderator.name if moderator else f"Modérateur Inconnu (ID: {moderator_id})"

            timestamp = datetime.fromisoformat(timestamp_str)

            embed.add_field(
                name=f"**{sanc_type.upper()}** - <t:{int(timestamp.timestamp())}:R>",
                value=f"**Serveur :** {guild_name}\n"
                      f"**Raison :** {reason or 'Non spécifiée'}\n"
                      f"**Par :** {moderator_name}",
                inline=False
            )

        if len(sanctions) > 10:
            embed.set_footer(text=f"Affiche les 10 sanctions les plus récentes sur {len(sanctions)}.")

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CasierSystem(bot))
