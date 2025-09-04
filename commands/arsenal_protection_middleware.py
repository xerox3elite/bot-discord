"""
🔥 Arsenal Command Protection & Registration Middleware
Système de protection qui vérifie l'enregistrement avant CHAQUE commande
Auteur: Arsenal Studio
"""

import discord
from discord.ext import commands
import aiosqlite
import functools
from typing import Dict, List, Optional, Callable
import logging

log = logging.getLogger(__name__)

class ArsenalProtectionMiddleware:
    """Middleware de protection des commandes Arsenal"""
    
    def __init__(self):
        self.db_path = "arsenal_users_central.db"
        self.protected_commands = set()
        self.role_permissions = {
            "membre": ["basic"],
            "beta": ["basic", "beta"],
            "premium": ["basic", "beta", "premium"],
            "dev": ["basic", "beta", "premium", "dev", "admin"],
            "creator": ["basic", "beta", "premium", "dev", "admin", "creator"]
        }
    
    async def is_user_registered(self, discord_id: int) -> bool:
        """Vérifier si l'utilisateur est enregistré"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT 1 FROM arsenal_users WHERE discord_id = ?", (discord_id,)
                )
                return await cursor.fetchone() is not None
        except Exception as e:
            log.error(f"Erreur vérification registration: {e}")
            return False
    
    async def get_user_arsenal_role(self, discord_id: int) -> Optional[str]:
        """Récupérer le rôle Arsenal de l'utilisateur"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT arsenal_role FROM arsenal_users WHERE discord_id = ?", (discord_id,)
                )
                result = await cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            log.error(f"Erreur récupération rôle: {e}")
            return None
    
    async def check_command_permission(self, discord_id: int, required_permission: str) -> bool:
        """Vérifier si l'utilisateur a la permission pour une commande"""
        user_role = await self.get_user_arsenal_role(discord_id)
        if not user_role:
            return False
        
        user_permissions = self.role_permissions.get(user_role, [])
        return required_permission in user_permissions
    
    async def update_command_usage(self, discord_id: int, command_name: str, guild_id: int = None):
        """Mettre à jour l'usage des commandes"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE arsenal_users 
                    SET total_commands_used = total_commands_used + 1,
                        last_activity = datetime('now') 
                    WHERE discord_id = ?
                """, (discord_id,))
                
                # Enregistrer l'historique
                cursor = await db.execute(
                    "SELECT arsenal_id FROM arsenal_users WHERE discord_id = ?", (discord_id,)
                )
                result = await cursor.fetchone()
                if result:
                    await db.execute("""
                        INSERT INTO user_activity 
                        (arsenal_id, discord_id, guild_id, activity_type, activity_data, timestamp)
                        VALUES (?, ?, ?, 'command_use', ?, datetime('now'))
                    """, (result[0], discord_id, guild_id, f'{{"command": "{command_name}"}}'))
                
                await db.commit()
        except Exception as e:
            log.error(f"Erreur mise à jour usage: {e}")

# Instance globale du middleware
protection_middleware = ArsenalProtectionMiddleware()

def require_registration(permission_level: str = "basic"):
    """Décorateur pour exiger l'enregistrement et vérifier les permissions"""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            # Vérifier l'enregistrement
            if not await protection_middleware.is_user_registered(interaction.user.id):
                embed = discord.Embed(
                    title="🚫 Accès Refusé",
                    description="**Vous devez d'abord vous enregistrer !**",
                    color=0xff0000
                )
                embed.add_field(
                    name="📝 Comment faire ?",
                    value="Utilisez `/rgst` pour vous enregistrer dans Arsenal",
                    inline=False
                )
                embed.add_field(
                    name="⚠️ Important",
                    value="L'enregistrement est **OBLIGATOIRE** pour toutes les commandes",
                    inline=False
                )
                embed.set_footer(text="Arsenal Studio • Système de protection")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Vérifier les permissions
            if not await protection_middleware.check_command_permission(interaction.user.id, permission_level):
                user_role = await protection_middleware.get_user_arsenal_role(interaction.user.id)
                
                embed = discord.Embed(
                    title="🔐 Permissions Insuffisantes",
                    description=f"Votre rôle `{user_role}` n'a pas accès à cette commande.",
                    color=0xffaa00
                )
                embed.add_field(
                    name="🎯 Requis",
                    value=f"Permission: `{permission_level}`",
                    inline=True
                )
                embed.add_field(
                    name="👤 Votre rôle",
                    value=f"`{user_role}`",
                    inline=True
                )
                embed.add_field(
                    name="📈 Comment améliorer ?",
                    value="Contactez un administrateur pour une promotion",
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Mettre à jour l'usage
            await protection_middleware.update_command_usage(
                interaction.user.id, 
                interaction.command.name if interaction.command else "unknown",
                interaction.guild.id if interaction.guild else None
            )
            
            # Exécuter la commande
            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator

def require_premium():
    """Décorateur pour les commandes premium"""
    return require_registration("premium")

def require_beta():
    """Décorateur pour les commandes beta"""
    return require_registration("beta")

def require_dev():
    """Décorateur pour les commandes dev"""
    return require_registration("dev")

def require_creator():
    """Décorateur pour les commandes créateur"""
    return require_registration("creator")

class ArsenalProtectionSystem(commands.Cog):
    """Système de protection des commandes"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.middleware = protection_middleware
    
    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: Exception):
        """Gérer les erreurs de commandes"""
        if "registration" in str(error).lower():
            embed = discord.Embed(
                title="⚠️ Erreur d'Accès",
                description="Problème d'enregistrement ou de permissions.",
                color=0xff0000
            )
            embed.add_field(
                name="🔧 Solution",
                value="Utilisez `/rgst` pour vous enregistrer",
                inline=False
            )
            
            try:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except:
                await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="check-registration", description="🔍 Vérifier votre statut d'enregistrement")
    async def check_registration(self, interaction: discord.Interaction):
        """Vérifier le statut d'enregistrement"""
        is_registered = await self.middleware.is_user_registered(interaction.user.id)
        
        if is_registered:
            user_role = await self.middleware.get_user_arsenal_role(interaction.user.id)
            user_permissions = self.middleware.role_permissions.get(user_role, [])
            
            embed = discord.Embed(
                title="✅ Statut: Enregistré",
                description="Vous êtes enregistré dans Arsenal !",
                color=0x00ff00
            )
            embed.add_field(
                name="🎯 Votre Rôle",
                value=f"`{user_role.upper()}`",
                inline=True
            )
            embed.add_field(
                name="🔐 Vos Permissions",
                value=f"`{', '.join(user_permissions)}`",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Statut: Non Enregistré",
                description="Vous n'êtes pas enregistré dans Arsenal.",
                color=0xff0000
            )
            embed.add_field(
                name="📝 Action Requise",
                value="Utilisez `/rgst` pour vous enregistrer",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    """Setup du système de protection"""
    await bot.add_cog(ArsenalProtectionSystem(bot))
