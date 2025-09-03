"""
Système de sanctions Arsenal V4.5.2
Module principal pour la gestion des sanctions
"""

import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class SanctionDatabase:
    """Gestionnaire de base de données pour les sanctions"""
    
    def __init__(self, db_path: str = "arsenal_sanctions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sanctions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    active INTEGER DEFAULT 1,
                    data TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sanction_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sanction_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reason TEXT,
                    FOREIGN KEY (sanction_id) REFERENCES sanctions (id)
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
    
    def add_sanction(self, guild_id: int, user_id: int, moderator_id: int, 
                    sanction_type: str, reason: str = None, expires_at: datetime = None,
                    data: Dict[str, Any] = None) -> int:
        """Ajoute une nouvelle sanction"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO sanctions (guild_id, user_id, moderator_id, type, reason, expires_at, data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (guild_id, user_id, moderator_id, sanction_type, reason, expires_at, 
                 json.dumps(data) if data else None))
            
            sanction_id = cursor.lastrowid
            
            # Ajouter à l'historique
            cursor.execute("""
                INSERT INTO sanction_history (sanction_id, action, moderator_id, reason)
                VALUES (?, ?, ?, ?)
            """, (sanction_id, f"Sanction créée: {sanction_type}", moderator_id, reason))
            
            conn.commit()
            conn.close()
            
            return sanction_id
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de la sanction: {e}")
            return -1
    
    def get_user_sanctions(self, guild_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Récupère les sanctions d'un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM sanctions 
                WHERE guild_id = ? AND user_id = ? 
                ORDER BY created_at DESC
            """, (guild_id, user_id))
            
            sanctions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return sanctions
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des sanctions: {e}")
            return []

class SanctionManager:
    """Gestionnaire principal des sanctions"""
    
    def __init__(self, bot: commands.Bot = None):
        self.bot = bot
        self.db = SanctionDatabase()
    
    async def warn_user(self, guild: discord.Guild, user: discord.Member, 
                       moderator: discord.Member, reason: str = None) -> int:
        """Avertir un utilisateur"""
        try:
            sanction_id = self.db.add_sanction(
                guild_id=guild.id,
                user_id=user.id,
                moderator_id=moderator.id,
                sanction_type="warn",
                reason=reason or "Aucune raison spécifiée"
            )
            
            # Envoyer un message privé à l'utilisateur
            try:
                embed = discord.Embed(
                    title="⚠️ Avertissement reçu",
                    description=f"Vous avez reçu un avertissement sur **{guild.name}**",
                    color=0xFF9900
                )
                embed.add_field(name="Raison", value=reason or "Aucune raison spécifiée", inline=False)
                embed.add_field(name="Modérateur", value=moderator.display_name, inline=True)
                
                await user.send(embed=embed)
            except:
                pass  # Si on ne peut pas envoyer de MP
            
            return sanction_id
            
        except Exception as e:
            logger.error(f"Erreur lors de l'avertissement: {e}")
            raise
    
    async def timeout_user(self, guild: discord.Guild, user: discord.Member,
                          moderator: discord.Member, duration_seconds: int,
                          reason: str = None) -> int:
        """Mettre un utilisateur en timeout"""
        try:
            expires_at = datetime.now() + timedelta(seconds=duration_seconds)
            
            # Appliquer le timeout
            await user.timeout(timedelta(seconds=duration_seconds), reason=reason)
            
            sanction_id = self.db.add_sanction(
                guild_id=guild.id,
                user_id=user.id,
                moderator_id=moderator.id,
                sanction_type="timeout",
                reason=reason or "Aucune raison spécifiée",
                expires_at=expires_at,
                data={"duration": duration_seconds}
            )
            
            # Envoyer un message privé à l'utilisateur
            try:
                embed = discord.Embed(
                    title="⏰ Timeout appliqué",
                    description=f"Vous avez été mis en timeout sur **{guild.name}**",
                    color=0xFF0000
                )
                embed.add_field(name="Durée", value=f"{duration_seconds // 60} minutes", inline=True)
                embed.add_field(name="Raison", value=reason or "Aucune raison spécifiée", inline=False)
                embed.add_field(name="Modérateur", value=moderator.display_name, inline=True)
                
                await user.send(embed=embed)
            except:
                pass  # Si on ne peut pas envoyer de MP
            
            return sanction_id
            
        except Exception as e:
            logger.error(f"Erreur lors du timeout: {e}")
            raise

# Instance globale du gestionnaire
_sanction_manager = None

def get_sanctions_manager() -> Optional[SanctionManager]:
    """Récupère l'instance globale du gestionnaire de sanctions"""
    return _sanction_manager

def set_sanctions_manager(manager: SanctionManager):
    """Définit l'instance globale du gestionnaire de sanctions"""
    global _sanction_manager
    _sanction_manager = manager

class SanctionCog(commands.Cog):
    """Cog principal pour les sanctions"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = SanctionManager(bot)
        set_sanctions_manager(self.manager)
    
    @commands.hybrid_command(name="warn")
    @commands.has_permissions(moderate_members=True)
    async def warn_command(self, ctx: commands.Context, user: discord.Member, *, reason: str = None):
        """Avertir un utilisateur"""
        try:
            sanction_id = await self.manager.warn_user(ctx.guild, user, ctx.author, reason)
            
            embed = discord.Embed(
                title="⚠️ Avertissement donné",
                description=f"{user.mention} a reçu un avertissement.",
                color=0xFF9900
            )
            embed.add_field(name="Raison", value=reason or "Aucune raison spécifiée", inline=False)
            embed.add_field(name="ID Sanction", value=f"`{sanction_id}`", inline=True)
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de l'avertissement: {e}")
    
    @commands.hybrid_command(name="timeout")
    @commands.has_permissions(moderate_members=True)
    async def timeout_command(self, ctx: commands.Context, user: discord.Member, 
                             duration: int, *, reason: str = None):
        """Mettre un utilisateur en timeout (durée en minutes)"""
        try:
            duration_seconds = duration * 60
            sanction_id = await self.manager.timeout_user(ctx.guild, user, ctx.author, duration_seconds, reason)
            
            embed = discord.Embed(
                title="⏰ Timeout appliqué",
                description=f"{user.mention} a été mis en timeout.",
                color=0xFF0000
            )
            embed.add_field(name="Durée", value=f"{duration} minutes", inline=True)
            embed.add_field(name="Raison", value=reason or "Aucune raison spécifiée", inline=False)
            embed.add_field(name="ID Sanction", value=f"`{sanction_id}`", inline=True)
            embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du timeout: {e}")
    
    @commands.hybrid_command(name="casier", aliases=["sanctions"])
    @commands.has_permissions(moderate_members=True)
    async def casier_command(self, ctx: commands.Context, user: discord.Member):
        """Afficher le casier judiciaire d'un utilisateur"""
        try:
            db = SanctionDatabase()
            sanctions = db.get_user_sanctions(ctx.guild.id, user.id)
            
            embed = discord.Embed(
                title=f"📋 Casier de {user.display_name}",
                color=0x3498DB
            )
            
            if not sanctions:
                embed.description = "Aucune sanction trouvée pour cet utilisateur."
            else:
                embed.description = f"**{len(sanctions)} sanctions trouvées**"
                
                for i, sanction in enumerate(sanctions[:5]):  # Limiter à 5 dernières
                    sanction_type = sanction['type'].upper()
                    created_at = sanction['created_at']
                    reason = sanction['reason'] or "Aucune raison"
                    
                    embed.add_field(
                        name=f"{i+1}. {sanction_type} - ID #{sanction['id']}",
                        value=f"**Date:** {created_at}\n**Raison:** {reason}",
                        inline=False
                    )
                
                if len(sanctions) > 5:
                    embed.add_field(
                        name="📋 Total",
                        value=f"... et {len(sanctions) - 5} autres sanctions",
                        inline=False
                    )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la récupération du casier: {e}")

# Groupe de commandes slash pour compatibilité
class SanctionSlashGroup(app_commands.Group):
    """Groupe de commandes slash pour les sanctions"""
    
    def __init__(self):
        super().__init__(name="sanction", description="⚖️ Système de sanctions Arsenal")
    
    @app_commands.command(name="warn", description="⚠️ Avertir un utilisateur")
    @app_commands.describe(
        user="Utilisateur à avertir",
        reason="Raison de l'avertissement"
    )
    async def warn_slash(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Aucune raison spécifiée"):
        """Avertir un utilisateur via slash command"""
        if not interaction.user.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Vous n'avez pas les permissions nécessaires.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            manager = get_sanctions_manager()
            if not manager:
                manager = SanctionManager()
            
            sanction_id = await manager.warn_user(interaction.guild, user, interaction.user, reason)
            
            embed = discord.Embed(
                title="⚠️ Avertissement donné",
                description=f"{user.mention} a reçu un avertissement.",
                color=0xFF9900
            )
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.add_field(name="ID Sanction", value=f"`{sanction_id}`", inline=True)
            embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur slash warn: {e}")
            await interaction.response.send_message("❌ Erreur lors de l'avertissement.", ephemeral=True)
    
    @app_commands.command(name="timeout", description="⏰ Mettre un utilisateur en timeout")
    @app_commands.describe(
        user="Utilisateur à timeout",
        duration="Durée en minutes",
        reason="Raison du timeout"
    )
    async def timeout_slash(self, interaction: discord.Interaction, user: discord.Member, duration: int, reason: str = "Aucune raison spécifiée"):
        """Timeout un utilisateur via slash command"""
        if not interaction.user.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Vous n'avez pas les permissions nécessaires.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            manager = get_sanctions_manager()
            if not manager:
                manager = SanctionManager()
            
            duration_seconds = duration * 60
            sanction_id = await manager.timeout_user(interaction.guild, user, interaction.user, duration_seconds, reason)
            
            embed = discord.Embed(
                title="⏰ Timeout appliqué",
                description=f"{user.mention} a été mis en timeout.",
                color=0xFF0000
            )
            embed.add_field(name="Durée", value=f"{duration} minutes", inline=True)
            embed.add_field(name="Raison", value=reason, inline=False)
            embed.add_field(name="ID Sanction", value=f"`{sanction_id}`", inline=True)
            embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur slash timeout: {e}")
            await interaction.response.send_message("❌ Erreur lors du timeout.", ephemeral=True)
    
    @app_commands.command(name="casier", description="📋 Voir le casier judiciaire d'un utilisateur")
    @app_commands.describe(user="Utilisateur dont voir le casier")
    async def casier_slash(self, interaction: discord.Interaction, user: discord.Member):
        """Afficher le casier via slash command"""
        if not interaction.user.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Vous n'avez pas les permissions nécessaires.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            db = SanctionDatabase()
            sanctions = db.get_user_sanctions(interaction.guild.id, user.id)
            
            embed = discord.Embed(
                title=f"📋 Casier de {user.display_name}",
                color=0x3498DB
            )
            
            if not sanctions:
                embed.description = "Aucune sanction trouvée."
            else:
                embed.description = f"**{len(sanctions)} sanctions trouvées**"
                
                for i, sanction in enumerate(sanctions[:5]):
                    sanction_type = sanction['type'].upper()
                    created_at = sanction['created_at']
                    reason = sanction['reason'] or "Aucune raison"
                    
                    embed.add_field(
                        name=f"{i+1}. {sanction_type} - ID #{sanction['id']}",
                        value=f"**Date:** {created_at}\n**Raison:** {reason}",
                        inline=False
                    )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur slash casier: {e}")
            await interaction.response.send_message("❌ Erreur lors de la récupération du casier.", ephemeral=True)

# Instance du groupe slash
sanction_group = SanctionSlashGroup()

async def setup(bot: commands.Bot):
    """Fonction de setup pour le module"""
    await bot.add_cog(SanctionCog(bot))
    bot.tree.add_command(sanction_group)
    logger.info("✅ Module sanctions chargé avec succès")

async def teardown(bot: commands.Bot):
    """Fonction de nettoyage"""
    bot.tree.remove_command(sanction_group.name)
    logger.info("🔄 Module sanctions déchargé")
