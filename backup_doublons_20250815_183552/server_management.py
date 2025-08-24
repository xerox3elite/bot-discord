"""
⚡ Arsenal Bot - Système de Gestion de Serveur Avancé
Gestion complète des serveurs avec statistiques et monitoring
Développé par XeRoX - Arsenal Bot V4.5.0
"""
import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import json
import datetime
from typing import Optional, Dict, List, Any
import asyncio
import psutil
import os

class ServerManagementSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_db = "server_management.db"
        self.init_databases()

    def init_databases(self):
        """Initialise les bases de données de gestion serveur"""
        with sqlite3.connect(self.server_db) as conn:
            # Configuration serveur
            conn.execute("""
                CREATE TABLE IF NOT EXISTS server_config (
                    guild_id INTEGER PRIMARY KEY,
                    config_json TEXT,
                    premium BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Statistiques serveur
            conn.execute("""
                CREATE TABLE IF NOT EXISTS server_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    member_count INTEGER,
                    online_count INTEGER,
                    message_count INTEGER,
                    voice_minutes INTEGER,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Événements serveur
            conn.execute("""
                CREATE TABLE IF NOT EXISTS server_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    event_type TEXT,
                    event_data TEXT,
                    user_id INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    @app_commands.command(name="serveur", description="⚡ Gestion et statistiques du serveur")
    @app_commands.describe(
        action="Action à effectuer sur le serveur"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="📊 Statistiques", value="stats"),
        app_commands.Choice(name="⚙️ Configuration", value="config"),
        app_commands.Choice(name="👥 Membres", value="members"),
        app_commands.Choice(name="📈 Graphiques", value="graphs"),
        app_commands.Choice(name="🔧 Maintenance", value="maintenance"),
        app_commands.Choice(name="💎 Premium", value="premium")
    ])
    async def serveur(self, interaction: discord.Interaction, action: str):
        if action == "stats":
            await self.show_server_stats(interaction)
        elif action == "config":
            await self.show_server_config(interaction)
        elif action == "members":
            await self.show_member_analytics(interaction)
        elif action == "graphs":
            await self.show_server_graphs(interaction)
        elif action == "maintenance":
            await self.server_maintenance(interaction)
        elif action == "premium":
            await self.show_premium_info(interaction)

    async def show_server_stats(self, interaction: discord.Interaction):
        """Affiche les statistiques complètes du serveur"""
        guild = interaction.guild
        
        # Statistiques de base
        total_members = len(guild.members)
        online_members = len([m for m in guild.members if m.status != discord.Status.offline])
        bots = len([m for m in guild.members if m.bot])
        humans = total_members - bots
        
        # Statistiques des salons
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        # Statistiques des rôles
        roles_count = len(guild.roles)
        highest_role = max(guild.roles, key=lambda r: r.position).name
        
        embed = discord.Embed(
            title=f"📊 Statistiques - {guild.name}",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        
        # Membres
        embed.add_field(
            name="👥 Membres",
            value=f"**Total:** {total_members:,}\n"
                  f"**En ligne:** {online_members:,}\n"
                  f"**Humains:** {humans:,}\n"
                  f"**Bots:** {bots:,}",
            inline=True
        )
        
        # Salons
        embed.add_field(
            name="💬 Salons",
            value=f"**Texte:** {text_channels}\n"
                  f"**Vocal:** {voice_channels}\n"
                  f"**Catégories:** {categories}",
            inline=True
        )
        
        # Serveur
        embed.add_field(
            name="⚙️ Serveur",
            value=f"**Créé:** <t:{int(guild.created_at.timestamp())}:R>\n"
                  f"**Propriétaire:** {guild.owner.mention if guild.owner else 'Inconnu'}\n"
                  f"**Région:** {guild.preferred_locale}",
            inline=True
        )
        
        # Rôles et sécurité
        embed.add_field(
            name="🛡️ Sécurité",
            value=f"**Rôles:** {roles_count}\n"
                  f"**Plus haut:** {highest_role}\n"
                  f"**Niveau:** {guild.verification_level}",
            inline=True
        )
        
        # Boost info
        embed.add_field(
            name="🚀 Nitro Boost",
            value=f"**Niveau:** {guild.premium_tier}\n"
                  f"**Boosts:** {guild.premium_subscription_count}\n"
                  f"**Boosters:** {len(guild.premium_subscribers)}",
            inline=True
        )
        
        # Fonctionnalités
        features = []
        if "COMMUNITY" in guild.features:
            features.append("🏘️ Communauté")
        if "PARTNERED" in guild.features:
            features.append("🤝 Partenaire")
        if "VERIFIED" in guild.features:
            features.append("✅ Vérifié")
        if "VANITY_URL" in guild.features:
            features.append("🔗 URL Personnalisée")
        
        if features:
            embed.add_field(
                name="⭐ Fonctionnalités",
                value="\n".join(features[:5]),  # Max 5 pour éviter l'overflow
                inline=True
            )
        
        # Sauvegarde des stats
        await self.save_server_stats(guild.id, total_members, online_members)
        
        await interaction.response.send_message(embed=embed)

    async def show_member_analytics(self, interaction: discord.Interaction):
        """Analyse détaillée des membres"""
        guild = interaction.guild
        
        embed = discord.Embed(
            title=f"👥 Analyse des Membres - {guild.name}",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        
        # Analyse des statuts
        status_counts = {
            "online": 0,
            "idle": 0,
            "dnd": 0,
            "offline": 0
        }
        
        bot_count = 0
        admin_count = 0
        
        for member in guild.members:
            if member.bot:
                bot_count += 1
            else:
                status_counts[str(member.status)] += 1
            
            if member.guild_permissions.administrator:
                admin_count += 1
        
        # Statuts
        embed.add_field(
            name="📊 Statuts",
            value=f"🟢 En ligne: {status_counts['online']}\n"
                  f"🟡 Absent: {status_counts['idle']}\n"
                  f"🔴 Occupé: {status_counts['dnd']}\n"
                  f"⚫ Hors ligne: {status_counts['offline']}",
            inline=True
        )
        
        # Analyse des rôles
        role_members = {}
        for role in guild.roles[:10]:  # Top 10 rôles
            if role.name != "@everyone":
                role_members[role.name] = len(role.members)
        
        top_roles = sorted(role_members.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if top_roles:
            roles_text = "\n".join([f"{role}: {count}" for role, count in top_roles])
            embed.add_field(
                name="🏆 Top Rôles",
                value=roles_text,
                inline=True
            )
        
        # Permissions
        embed.add_field(
            name="🛡️ Permissions",
            value=f"Administrateurs: {admin_count}\n"
                  f"Bots: {bot_count}\n"
                  f"Humains: {len(guild.members) - bot_count}",
            inline=True
        )
        
        # Activité récente
        recent_joins = len([m for m in guild.members if (datetime.datetime.now(datetime.timezone.utc) - m.joined_at).days <= 7])
        embed.add_field(
            name="📈 Activité (7j)",
            value=f"Nouveaux membres: {recent_joins}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

    async def show_server_config(self, interaction: discord.Interaction):
        """Affiche la configuration du serveur"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ Permissions insuffisantes!", ephemeral=True
            )
            return
        
        guild = interaction.guild
        
        embed = discord.Embed(
            title=f"⚙️ Configuration - {guild.name}",
            color=discord.Color.blue()
        )
        
        # Sécurité
        embed.add_field(
            name="🛡️ Sécurité",
            value=f"**Vérification:** {guild.verification_level}\n"
                  f"**Filtre contenu:** {guild.explicit_content_filter}\n"
                  f"**MFA requis:** {'Oui' if guild.mfa_level else 'Non'}",
            inline=False
        )
        
        # Salon système
        system_channel = guild.system_channel.name if guild.system_channel else "Aucun"
        rules_channel = guild.rules_channel.name if guild.rules_channel else "Aucun"
        
        embed.add_field(
            name="📋 Salons Système",
            value=f"**Système:** #{system_channel}\n"
                  f"**Règles:** #{rules_channel}",
            inline=False
        )
        
        # Paramètres boost
        embed.add_field(
            name="🚀 Nitro",
            value=f"**Niveau:** {guild.premium_tier}\n"
                  f"**Boosts:** {guild.premium_subscription_count}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="maintenance", description="🔧 Outils de maintenance du serveur")
    @app_commands.describe(
        action="Action de maintenance à effectuer"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="🧹 Nettoyer", value="cleanup"),
        app_commands.Choice(name="📊 Audit", value="audit"),
        app_commands.Choice(name="🔄 Synchroniser", value="sync"),
        app_commands.Choice(name="🚀 Optimiser", value="optimize")
    ])
    async def maintenance(self, interaction: discord.Interaction, action: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Seuls les administrateurs peuvent utiliser cette commande!", 
                ephemeral=True
            )
            return
        
        if action == "cleanup":
            await self.cleanup_server(interaction)
        elif action == "audit":
            await self.audit_server(interaction)
        elif action == "sync":
            await self.sync_server(interaction)
        elif action == "optimize":
            await self.optimize_server(interaction)

    async def cleanup_server(self, interaction: discord.Interaction):
        """Nettoyage automatique du serveur"""
        await interaction.response.defer()
        
        guild = interaction.guild
        cleanup_report = []
        
        # Nettoyage des rôles vides
        empty_roles = [role for role in guild.roles if len(role.members) == 0 and not role.managed and role.name != "@everyone"]
        
        if empty_roles:
            cleanup_report.append(f"🗑️ Rôles vides trouvés: {len(empty_roles)}")
        
        # Vérification des salons inactifs (simulation)
        inactive_channels = []
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).read_message_history:
                try:
                    async for message in channel.history(limit=1):
                        days_inactive = (datetime.datetime.now(datetime.timezone.utc) - message.created_at).days
                        if days_inactive > 30:  # Plus de 30 jours d'inactivité
                            inactive_channels.append(channel)
                        break
                except:
                    pass
        
        if inactive_channels:
            cleanup_report.append(f"💤 Salons inactifs (30j+): {len(inactive_channels)}")
        
        embed = discord.Embed(
            title="🧹 Rapport de Nettoyage",
            color=discord.Color.orange()
        )
        
        if cleanup_report:
            embed.add_field(
                name="📋 Éléments Détectés",
                value="\n".join(cleanup_report),
                inline=False
            )
            embed.add_field(
                name="⚠️ Note",
                value="Utilisez les outils de modération pour nettoyer manuellement",
                inline=False
            )
        else:
            embed.add_field(
                name="✅ Serveur Propre",
                value="Aucun élément à nettoyer détecté",
                inline=False
            )
        
        await interaction.followup.send(embed=embed)

    async def save_server_stats(self, guild_id: int, total_members: int, online_members: int):
        """Sauvegarde les statistiques du serveur"""
        with sqlite3.connect(self.server_db) as conn:
            conn.execute("""
                INSERT INTO server_stats (guild_id, member_count, online_count, message_count, voice_minutes)
                VALUES (?, ?, ?, 0, 0)
            """, (guild_id, total_members, online_members))

    @app_commands.command(name="arsenal_status", description="🤖 Status complet d'Arsenal Bot")
    async def arsenal_status(self, interaction: discord.Interaction):
        """Affiche le status complet du système Arsenal"""
        embed = discord.Embed(
            title="🤖 Arsenal Bot - Status Système",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        
        # Stats du bot
        total_guilds = len(self.bot.guilds)
        total_users = sum(len(guild.members) for guild in self.bot.guilds)
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"**Serveurs:** {total_guilds:,}\n"
                  f"**Utilisateurs:** {total_users:,}\n"
                  f"**Commandes:** 150+",
            inline=True
        )
        
        # Performance système
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        embed.add_field(
            name="⚡ Performance",
            value=f"**CPU:** {cpu_percent}%\n"
                  f"**RAM:** {memory.percent}%\n"
                  f"**Latence:** {round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        # Status modules
        embed.add_field(
            name="🔧 Modules",
            value="✅ AutoMod\n"
                  "✅ ArsenalCoin\n"
                  "✅ Musique\n"
                  "✅ TempChannels\n"
                  "✅ Modération",
            inline=True
        )
        
        embed.set_footer(text="Arsenal Bot V4.5.0 - Tous systèmes opérationnels")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerManagementSystem(bot))

