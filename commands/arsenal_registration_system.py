"""
🔥 Arsenal Registration System V2.0 ULTIMATE
Système d'enregistrement central obligatoire pour utiliser le bot
Auteur: Arsenal Studio
"""

import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import asyncio
from datetime import datetime
import uuid
import json
from typing import Optional, Dict, List
import logging

log = logging.getLogger(__name__)

class ArsenalUserDatabase:
    """Base de données centrale des utilisateurs Arsenal"""
    
    def __init__(self):
        self.db_path = "arsenal_users_central.db"
    
    async def init_database(self):
        """Initialiser la base de données centrale"""
        async with aiosqlite.connect(self.db_path) as db:
            # Table principale des utilisateurs
            await db.execute("""
                CREATE TABLE IF NOT EXISTS arsenal_users (
                    arsenal_id TEXT PRIMARY KEY,
                    discord_id INTEGER UNIQUE NOT NULL,
                    discord_username TEXT NOT NULL,
                    discord_display_name TEXT,
                    arsenal_role TEXT DEFAULT 'membre',
                    registration_date TEXT NOT NULL,
                    last_activity TEXT,
                    global_level INTEGER DEFAULT 1,
                    global_coins INTEGER DEFAULT 100,
                    premium_status INTEGER DEFAULT 0,
                    beta_access INTEGER DEFAULT 0,
                    total_commands_used INTEGER DEFAULT 0,
                    profile_data TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des rôles par serveur
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_server_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    arsenal_id TEXT NOT NULL,
                    discord_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    server_level INTEGER DEFAULT 1,
                    server_coins INTEGER DEFAULT 50,
                    server_roles TEXT DEFAULT '[]',
                    highest_role TEXT DEFAULT 'membre',
                    join_date TEXT,
                    last_seen TEXT,
                    server_permissions TEXT DEFAULT '{}',
                    FOREIGN KEY (arsenal_id) REFERENCES arsenal_users (arsenal_id),
                    UNIQUE(discord_id, guild_id)
                )
            """)
            
            # Table des permissions et restrictions
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    arsenal_id TEXT NOT NULL,
                    permission_type TEXT NOT NULL,
                    permission_value TEXT NOT NULL,
                    granted_by TEXT,
                    granted_date TEXT,
                    expires_at TEXT,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (arsenal_id) REFERENCES arsenal_users (arsenal_id)
                )
            """)
            
            # Table de l'historique d'activité
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    arsenal_id TEXT NOT NULL,
                    discord_id INTEGER NOT NULL,
                    guild_id INTEGER,
                    activity_type TEXT NOT NULL,
                    activity_data TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (arsenal_id) REFERENCES arsenal_users (arsenal_id)
                )
            """)
            
            await db.commit()
            log.info("🔥 Base de données Arsenal Users initialisée")
    
    def generate_arsenal_id(self) -> str:
        """Générer un ID Arsenal unique"""
        return f"ARS-{uuid.uuid4().hex[:12].upper()}"
    
    async def register_user(self, user: discord.Member, guild: discord.Guild) -> Dict:
        """Enregistrer un nouvel utilisateur"""
        arsenal_id = self.generate_arsenal_id()
        now = datetime.now().isoformat()
        
        # Déterminer le rôle Arsenal basé sur les permissions Discord
        arsenal_role = await self._determine_arsenal_role(user)
        
        async with aiosqlite.connect(self.db_path) as db:
            try:
                # Insérer l'utilisateur principal
                await db.execute("""
                    INSERT INTO arsenal_users 
                    (arsenal_id, discord_id, discord_username, discord_display_name, 
                     arsenal_role, registration_date, last_activity, profile_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    arsenal_id, user.id, str(user), user.display_name,
                    arsenal_role, now, now, "{}"
                ))
                
                # Ajouter les données du serveur
                server_roles = [role.name for role in user.roles if role.name != "@everyone"]
                highest_role = await self._get_highest_role(user)
                
                await db.execute("""
                    INSERT INTO user_server_data 
                    (arsenal_id, discord_id, guild_id, server_roles, highest_role, join_date, last_seen)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    arsenal_id, user.id, guild.id, json.dumps(server_roles),
                    highest_role, now, now
                ))
                
                # Enregistrer l'activité
                await db.execute("""
                    INSERT INTO user_activity 
                    (arsenal_id, discord_id, guild_id, activity_type, activity_data, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    arsenal_id, user.id, guild.id, "registration", 
                    json.dumps({"guild_name": guild.name}), now
                ))
                
                await db.commit()
                
                return {
                    "success": True,
                    "arsenal_id": arsenal_id,
                    "arsenal_role": arsenal_role,
                    "message": f"✅ Enregistrement réussi ! ID Arsenal: `{arsenal_id}`"
                }
                
            except aiosqlite.IntegrityError:
                return {
                    "success": False,
                    "message": "❌ Vous êtes déjà enregistré dans Arsenal !"
                }
    
    async def get_user_profile(self, discord_id: int) -> Optional[Dict]:
        """Récupérer le profil complet d'un utilisateur"""
        async with aiosqlite.connect(self.db_path) as db:
            # Données principales
            cursor = await db.execute("""
                SELECT arsenal_id, discord_username, discord_display_name, 
                       arsenal_role, registration_date, global_level, global_coins,
                       premium_status, beta_access, total_commands_used
                FROM arsenal_users WHERE discord_id = ?
            """, (discord_id,))
            user_data = await cursor.fetchone()
            
            if not user_data:
                return None
            
            # Données des serveurs
            cursor = await db.execute("""
                SELECT guild_id, server_level, server_coins, highest_role, server_roles
                FROM user_server_data WHERE discord_id = ?
            """, (discord_id,))
            servers_data = await cursor.fetchall()
            
            return {
                "arsenal_id": user_data[0],
                "discord_username": user_data[1],
                "display_name": user_data[2],
                "arsenal_role": user_data[3],
                "registration_date": user_data[4],
                "global_level": user_data[5],
                "global_coins": user_data[6],
                "premium_status": bool(user_data[7]),
                "beta_access": bool(user_data[8]),
                "total_commands": user_data[9],
                "servers": [
                    {
                        "guild_id": server[0],
                        "level": server[1],
                        "coins": server[2],
                        "highest_role": server[3],
                        "roles": json.loads(server[4] or "[]")
                    } for server in servers_data
                ]
            }
    
    async def is_user_registered(self, discord_id: int) -> bool:
        """Vérifier si l'utilisateur est enregistré"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT 1 FROM arsenal_users WHERE discord_id = ?", (discord_id,)
            )
            return await cursor.fetchone() is not None
    
    async def update_user_activity(self, discord_id: int, guild_id: int, activity_type: str, data: Dict = None):
        """Mettre à jour l'activité utilisateur"""
        async with aiosqlite.connect(self.db_path) as db:
            now = datetime.now().isoformat()
            
            # Mettre à jour last_activity
            await db.execute("""
                UPDATE arsenal_users SET last_activity = ?, total_commands_used = total_commands_used + 1
                WHERE discord_id = ?
            """, (now, discord_id))
            
            # Ajouter à l'historique
            cursor = await db.execute(
                "SELECT arsenal_id FROM arsenal_users WHERE discord_id = ?", (discord_id,)
            )
            result = await cursor.fetchone()
            if result:
                await db.execute("""
                    INSERT INTO user_activity 
                    (arsenal_id, discord_id, guild_id, activity_type, activity_data, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    result[0], discord_id, guild_id, activity_type,
                    json.dumps(data or {}), now
                ))
            
            await db.commit()
    
    async def _determine_arsenal_role(self, user: discord.Member) -> str:
        """Déterminer le rôle Arsenal basé sur les permissions Discord"""
        
        # Vérifier les rôles Discord spécifiques d'abord
        user_roles = [role.name.lower() for role in user.roles]
        
        # Rôles spéciaux
        if any(role in user_roles for role in ["owner", "fondateur", "founder", "créateur"]):
            return "fondateur"
        
        if any(role in user_roles for role in ["developer", "dev", "développeur"]):
            return "dev"
            
        if any(role in user_roles for role in ["admin", "administrator", "administrateur"]):
            return "admin"
            
        if any(role in user_roles for role in ["mod", "moderator", "modérateur", "staff"]):
            return "moderator"
            
        if any(role in user_roles for role in ["premium", "vip", "donateur", "supporter"]):
            return "premium"
            
        if any(role in user_roles for role in ["beta", "tester", "testeur"]):
            return "beta"
        
        # Basé sur les permissions Discord si pas de rôle spécifique
        if user.guild_permissions.administrator:
            return "admin"
        elif user.guild_permissions.manage_guild or user.guild_permissions.manage_channels:
            return "moderator"
        elif user.guild_permissions.manage_messages:
            return "beta"
        else:
            return "membre"
    
    async def _get_highest_role(self, user: discord.Member) -> str:
        """Obtenir le rôle le plus élevé"""
        if not user.roles:
            return "membre"
        return user.top_role.name if user.top_role.name != "@everyone" else "membre"

class RegistrationModal(discord.ui.Modal, title="🔥 Enregistrement Arsenal"):
    """Modal pour l'enregistrement utilisateur"""
    
    def __init__(self, db: ArsenalUserDatabase):
        super().__init__()
        self.db = db
    
    confirmation = discord.ui.TextInput(
        label="Confirmation d'enregistrement",
        placeholder="Tapez 'CONFIRMER' pour valider votre enregistrement...",
        required=True,
        max_length=20
    )
    
    accept_terms = discord.ui.TextInput(
        label="Acceptation des conditions",
        placeholder="Tapez 'J'ACCEPTE' pour accepter les conditions d'utilisation...",
        required=True,
        max_length=20
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.confirmation.value.upper() != "CONFIRMER":
            await interaction.response.send_message(
                "❌ Vous devez taper 'CONFIRMER' exactement !", ephemeral=True
            )
            return
        
        if self.accept_terms.value.upper() != "J'ACCEPTE":
            await interaction.response.send_message(
                "❌ Vous devez accepter les conditions en tapant 'J'ACCEPTE' !", ephemeral=True
            )
            return
        
        # Procéder à l'enregistrement
        result = await self.db.register_user(interaction.user, interaction.guild)
        
        if result["success"]:
            embed = discord.Embed(
                title="🔥 Enregistrement Arsenal Réussi !",
                description=result["message"],
                color=0x00ff00
            )
            embed.add_field(
                name="🎯 Votre Rôle Arsenal",
                value=f"`{result['arsenal_role'].upper()}`",
                inline=True
            )
            embed.add_field(
                name="🏆 Statut",
                value="✅ Activé",
                inline=True
            )
            embed.add_field(
                name="💡 Information",
                value="Vous pouvez maintenant utiliser toutes les commandes Arsenal !",
                inline=False
            )
            embed.set_footer(text="Arsenal Studio • Système d'enregistrement V2.0")
            
        else:
            embed = discord.Embed(
                title="❌ Erreur d'enregistrement",
                description=result["message"],
                color=0xff0000
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class RegistrationView(discord.ui.View):
    """Interface d'enregistrement avec boutons"""
    
    def __init__(self, db: ArsenalUserDatabase):
        super().__init__(timeout=300)
        self.db = db
    
    @discord.ui.button(
        label="📝 S'enregistrer",
        style=discord.ButtonStyle.green,
        emoji="🔥"
    )
    async def register_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Vérifier si déjà enregistré
        if await self.db.is_user_registered(interaction.user.id):
            await interaction.response.send_message(
                "✅ Vous êtes déjà enregistré dans Arsenal !", ephemeral=True
            )
            return
        
        # Ouvrir le modal d'enregistrement
        modal = RegistrationModal(self.db)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(
        label="📊 Mon Profil",
        style=discord.ButtonStyle.blue,
        emoji="👤"
    )
    async def profile_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        profile = await self.db.get_user_profile(interaction.user.id)
        
        if not profile:
            await interaction.response.send_message(
                "❌ Vous devez d'abord vous enregistrer avec `/rgst` !", ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="👤 Votre Profil Arsenal",
            color=0x7289da
        )
        embed.add_field(
            name="🆔 ID Arsenal",
            value=f"`{profile['arsenal_id']}`",
            inline=False
        )
        embed.add_field(
            name="🎯 Rôle Arsenal",
            value=f"`{profile['arsenal_role'].upper()}`",
            inline=True
        )
        embed.add_field(
            name="🏆 Niveau Global",
            value=f"`{profile['global_level']}`",
            inline=True
        )
        embed.add_field(
            name="💰 Coins Globaux",
            value=f"`{profile['global_coins']}`",
            inline=True
        )
        embed.add_field(
            name="📈 Commandes Utilisées",
            value=f"`{profile['total_commands']}`",
            inline=True
        )
        embed.add_field(
            name="⭐ Statut Premium",
            value="✅ Activé" if profile['premium_status'] else "❌ Désactivé",
            inline=True
        )
        embed.add_field(
            name="🧪 Accès Beta",
            value="✅ Activé" if profile['beta_access'] else "❌ Désactivé",
            inline=True
        )
        
        # Informations des serveurs
        if profile['servers']:
            server_info = []
            total_server_level = sum(s['level'] for s in profile['servers'])
            total_server_coins = sum(s['coins'] for s in profile['servers'])
            
            for server in profile['servers'][:3]:  # Limiter à 3 serveurs
                server_info.append(
                    f"🏰 **Serveur {server['guild_id']}**\n"
                    f"├ Niveau: `{server['level']}`\n"
                    f"├ Coins: `{server['coins']}`\n"
                    f"└ Rôle: `{server['highest_role']}`"
                )
            
            embed.add_field(
                name="🏰 Serveurs",
                value="\n\n".join(server_info),
                inline=False
            )
            embed.add_field(
                name="📊 Totaux Serveurs",
                value=f"Niveau: `{total_server_level}` • Coins: `{total_server_coins}`",
                inline=False
            )
        
        embed.set_footer(text=f"Enregistré le: {profile['registration_date'][:10]}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ArsenalRegistrationSystem(commands.Cog):
    """Système d'enregistrement central Arsenal"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = ArsenalUserDatabase()
        bot.loop.create_task(self.init_system())
    
    async def init_system(self):
        """Initialiser le système"""
        await self.db.init_database()
        log.info("🔥 Arsenal Registration System initialisé")
    
    async def check_registration(self, interaction: discord.Interaction) -> bool:
        """Vérifier si l'utilisateur est enregistré (middleware)"""
        if not await self.db.is_user_registered(interaction.user.id):
            embed = discord.Embed(
                title="⚠️ Enregistrement Requis",
                description="Vous devez d'abord vous enregistrer pour utiliser cette commande !",
                color=0xffaa00
            )
            embed.add_field(
                name="📝 Comment s'enregistrer ?",
                value="Utilisez la commande `/rgst` pour vous enregistrer",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        
        # Mettre à jour l'activité
        await self.db.update_user_activity(
            interaction.user.id, 
            interaction.guild.id if interaction.guild else 0,
            "command_use",
            {"command": interaction.command.name if interaction.command else "unknown"}
        )
        return True
    
    @app_commands.command(name="rgst", description="🔥 S'enregistrer dans Arsenal (OBLIGATOIRE)")
    async def register_command(self, interaction: discord.Interaction):
        """Commande d'enregistrement principale"""
        
        # Vérifier si déjà enregistré
        if await self.db.is_user_registered(interaction.user.id):
            profile = await self.db.get_user_profile(interaction.user.id)
            embed = discord.Embed(
                title="✅ Déjà Enregistré !",
                description=f"Vous êtes déjà enregistré dans Arsenal !",
                color=0x00ff00
            )
            embed.add_field(
                name="🆔 Votre ID Arsenal",
                value=f"`{profile['arsenal_id']}`",
                inline=False
            )
            embed.add_field(
                name="🎯 Votre Rôle",
                value=f"`{profile['arsenal_role'].upper()}`",
                inline=True
            )
            embed.add_field(
                name="🏆 Niveau Global",
                value=f"`{profile['global_level']}`",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Interface d'enregistrement
        embed = discord.Embed(
            title="🔥 Enregistrement Arsenal",
            description="**Bienvenue dans Arsenal Studio !**\n\n"
                       "L'enregistrement est **OBLIGATOIRE** pour utiliser le bot.\n"
                       "Voici ce que vous obtiendrez :",
            color=0x7289da
        )
        embed.add_field(
            name="🆔 ID Arsenal Unique",
            value="Un identifiant personnel pour le bot",
            inline=False
        )
        embed.add_field(
            name="🎯 Système de Rôles",
            value="• **Membre**: Accès standard\n"
                  "• **Beta**: Accès aux fonctionnalités beta\n"
                  "• **Premium**: Fonctionnalités avancées\n"
                  "• **Dev**: Accès développeur",
            inline=False
        )
        embed.add_field(
            name="📊 Système Multi-Serveurs",
            value="• Niveau global + niveau par serveur\n"
                  "• Coins globaux + coins par serveur\n"
                  "• Synchronisation automatique",
            inline=False
        )
        embed.add_field(
            name="⚠️ Important",
            value="**Sans enregistrement, aucune commande ne fonctionnera !**",
            inline=False
        )
        
        embed.set_footer(text="Arsenal Studio • Cliquez sur 'S'enregistrer' pour commencer")
        
        view = RegistrationView(self.db)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="profile-arsenal", description="👤 Voir votre profil Arsenal complet")
    async def profile_command(self, interaction: discord.Interaction):
        """Commande pour voir son profil Arsenal"""
        
        if not await self.check_registration(interaction):
            return
        
        profile = await self.db.get_user_profile(interaction.user.id)
        
        embed = discord.Embed(
            title="👤 Profil Arsenal Complet",
            color=0x7289da
        )
        embed.set_author(
            name=f"{profile['display_name'] or profile['discord_username']}",
            icon_url=interaction.user.display_avatar.url
        )
        
        # Informations principales
        embed.add_field(
            name="🆔 Identifiants",
            value=f"**Arsenal ID:** `{profile['arsenal_id']}`\n"
                  f"**Discord:** `{profile['discord_username']}`",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Statuts",
            value=f"**Rôle Arsenal:** `{profile['arsenal_role'].upper()}`\n"
                  f"**Premium:** {'✅ Oui' if profile['premium_status'] else '❌ Non'}\n"
                  f"**Beta:** {'✅ Oui' if profile['beta_access'] else '❌ Non'}",
            inline=True
        )
        
        embed.add_field(
            name="📊 Statistiques Globales",
            value=f"**Niveau:** `{profile['global_level']}`\n"
                  f"**Coins:** `{profile['global_coins']}`\n"
                  f"**Commandes:** `{profile['total_commands']}`",
            inline=True
        )
        
        # Statistiques des serveurs
        if profile['servers']:
            total_level = sum(s['level'] for s in profile['servers'])
            total_coins = sum(s['coins'] for s in profile['servers'])
            
            embed.add_field(
                name="🏰 Multi-Serveurs",
                value=f"**Serveurs actifs:** `{len(profile['servers'])}`\n"
                      f"**Niveau total:** `{total_level}`\n"
                      f"**Coins totaux:** `{total_coins}`",
                inline=True
            )
        
        embed.set_footer(
            text=f"Membre Arsenal depuis le {profile['registration_date'][:10]} • Arsenal Studio"
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    """Setup du cog"""
    await bot.add_cog(ArsenalRegistrationSystem(bot))
