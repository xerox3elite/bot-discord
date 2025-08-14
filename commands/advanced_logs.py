"""
📝 Arsenal Bot - Système de Logs Avancé
Système de journalisation complet avec surveillance en temps réel
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

class AdvancedLoggingSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logs_db = "advanced_logs.db"
        self.init_databases()

    def init_databases(self):
        """Initialise les bases de données de logs"""
        with sqlite3.connect(self.logs_db) as conn:
            # Configuration des logs par serveur
            conn.execute("""
                CREATE TABLE IF NOT EXISTS log_config (
                    guild_id INTEGER PRIMARY KEY,
                    log_channel_id INTEGER,
                    enabled_events TEXT,
                    config_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Journal des événements
            conn.execute("""
                CREATE TABLE IF NOT EXISTS event_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    event_type TEXT,
                    user_id INTEGER,
                    target_id INTEGER,
                    channel_id INTEGER,
                    event_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Audit trail complet
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    action_type TEXT,
                    executor_id INTEGER,
                    target_type TEXT,
                    target_id INTEGER,
                    changes_json TEXT,
                    reason TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    @app_commands.command(name="logs", description="📝 Système de logs avancé")
    @app_commands.describe(
        action="Action à effectuer",
        type_log="Type de log à consulter",
        utilisateur="Utilisateur spécifique"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="📊 Voir logs", value="view"),
        app_commands.Choice(name="⚙️ Configurer", value="config"),
        app_commands.Choice(name="🔍 Rechercher", value="search"),
        app_commands.Choice(name="📈 Statistiques", value="stats"),
        app_commands.Choice(name="🗑️ Nettoyer", value="cleanup")
    ])
    async def logs(
        self, 
        interaction: discord.Interaction,
        action: str,
        type_log: Optional[str] = None,
        utilisateur: Optional[discord.Member] = None
    ):
        if not interaction.user.guild_permissions.view_audit_log:
            await interaction.response.send_message(
                "❌ Vous devez avoir la permission de voir les logs d'audit!", 
                ephemeral=True
            )
            return

        if action == "view":
            await self.view_logs(interaction, type_log, utilisateur)
        elif action == "config":
            await self.configure_logs(interaction)
        elif action == "search":
            await self.search_logs(interaction, type_log)
        elif action == "stats":
            await self.show_log_stats(interaction)
        elif action == "cleanup":
            await self.cleanup_logs(interaction)

    async def view_logs(self, interaction: discord.Interaction, type_log: Optional[str], user: Optional[discord.Member]):
        """Affiche les logs récents"""
        embed = discord.Embed(
            title="📝 Logs Arsenal - Vue d'ensemble",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        
        # Récupération des logs récents
        with sqlite3.connect(self.logs_db) as conn:
            if user:
                logs = conn.execute("""
                    SELECT event_type, event_data, timestamp 
                    FROM event_logs 
                    WHERE guild_id = ? AND user_id = ? 
                    ORDER BY timestamp DESC LIMIT 10
                """, (interaction.guild.id, user.id)).fetchall()
            else:
                logs = conn.execute("""
                    SELECT event_type, event_data, user_id, timestamp 
                    FROM event_logs 
                    WHERE guild_id = ? 
                    ORDER BY timestamp DESC LIMIT 15
                """, (interaction.guild.id,)).fetchall()
        
        if logs:
            logs_text = []
            for log in logs[:10]:  # Limit pour éviter l'overflow
                if user:
                    event_type, event_data, timestamp = log
                    timestamp_str = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime("%H:%M")
                    logs_text.append(f"`{timestamp_str}` **{event_type}** - {event_data[:50]}...")
                else:
                    event_type, event_data, user_id, timestamp = log
                    user_mention = f"<@{user_id}>" if user_id else "Système"
                    timestamp_str = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime("%H:%M")
                    logs_text.append(f"`{timestamp_str}` **{event_type}** {user_mention}")
            
            embed.add_field(
                name="📋 Événements Récents",
                value="\n".join(logs_text),
                inline=False
            )
        else:
            embed.add_field(
                name="📋 Aucun Log",
                value="Aucun événement récent trouvé",
                inline=False
            )
        
        # Statistiques rapides
        with sqlite3.connect(self.logs_db) as conn:
            today_count = conn.execute("""
                SELECT COUNT(*) FROM event_logs 
                WHERE guild_id = ? AND DATE(timestamp) = DATE('now')
            """, (interaction.guild.id,)).fetchone()[0]
            
            week_count = conn.execute("""
                SELECT COUNT(*) FROM event_logs 
                WHERE guild_id = ? AND timestamp > datetime('now', '-7 days')
            """, (interaction.guild.id,)).fetchone()[0]
        
        embed.add_field(
            name="📊 Activité",
            value=f"Aujourd'hui: {today_count}\nCette semaine: {week_count}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="audit", description="🔍 Audit détaillé du serveur")
    @app_commands.describe(
        periode="Période à analyser",
        type_audit="Type d'audit spécifique"
    )
    @app_commands.choices(periode=[
        app_commands.Choice(name="Aujourd'hui", value="today"),
        app_commands.Choice(name="Cette semaine", value="week"),
        app_commands.Choice(name="Ce mois", value="month")
    ])
    async def audit(self, interaction: discord.Interaction, periode: str = "today", type_audit: Optional[str] = None):
        """Audit détaillé des actions sur le serveur"""
        if not interaction.user.guild_permissions.view_audit_log:
            await interaction.response.send_message(
                "❌ Permissions insuffisantes pour l'audit!", 
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="🔍 Audit Arsenal - Rapport Détaillé",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        
        # Configuration période
        if periode == "today":
            date_filter = "DATE(timestamp) = DATE('now')"
            period_name = "Aujourd'hui"
        elif periode == "week":
            date_filter = "timestamp > datetime('now', '-7 days')"
            period_name = "Cette semaine"
        else:  # month
            date_filter = "timestamp > datetime('now', '-30 days')"
            period_name = "Ce mois"
        
        # Analyse des événements par type
        with sqlite3.connect(self.logs_db) as conn:
            event_stats = conn.execute(f"""
                SELECT event_type, COUNT(*) as count 
                FROM event_logs 
                WHERE guild_id = ? AND {date_filter}
                GROUP BY event_type 
                ORDER BY count DESC
            """, (interaction.guild.id,)).fetchall()
        
        if event_stats:
            stats_text = []
            for event_type, count in event_stats[:8]:  # Top 8
                stats_text.append(f"**{event_type}:** {count}")
            
            embed.add_field(
                name=f"📈 Événements - {period_name}",
                value="\n".join(stats_text),
                inline=False
            )
        
        # Utilisateurs les plus actifs
        with sqlite3.connect(self.logs_db) as conn:
            user_stats = conn.execute(f"""
                SELECT user_id, COUNT(*) as count 
                FROM event_logs 
                WHERE guild_id = ? AND {date_filter} AND user_id IS NOT NULL
                GROUP BY user_id 
                ORDER BY count DESC 
                LIMIT 5
            """, (interaction.guild.id,)).fetchall()
        
        if user_stats:
            users_text = []
            for user_id, count in user_stats:
                try:
                    user = await self.bot.fetch_user(user_id)
                    users_text.append(f"**{user.display_name}:** {count}")
                except:
                    users_text.append(f"**Utilisateur {user_id}:** {count}")
            
            embed.add_field(
                name="👥 Utilisateurs Actifs",
                value="\n".join(users_text),
                inline=True
            )
        
        # Actions de modération récentes
        mod_actions = ["ban", "kick", "timeout", "warn", "delete_message"]
        with sqlite3.connect(self.logs_db) as conn:
            mod_stats = conn.execute(f"""
                SELECT event_type, COUNT(*) as count 
                FROM event_logs 
                WHERE guild_id = ? AND {date_filter} 
                AND event_type IN ({','.join(['?' for _ in mod_actions])})
                GROUP BY event_type
            """, (interaction.guild.id, *mod_actions)).fetchall()
        
        if mod_stats:
            mod_text = []
            for action, count in mod_stats:
                mod_text.append(f"**{action}:** {count}")
            
            embed.add_field(
                name="⚖️ Actions Modération",
                value="\n".join(mod_text),
                inline=True
            )
        
        await interaction.followup.send(embed=embed)

    async def configure_logs(self, interaction: discord.Interaction):
        """Configuration du système de logs"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ Permissions insuffisantes!", ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="⚙️ Configuration Logs Arsenal",
            description="Système de logs avancé avec surveillance temps réel",
            color=discord.Color.blue()
        )
        
        # Configuration actuelle
        config = self.get_log_config(interaction.guild.id)
        
        status = "✅ Activé" if config.get("enabled") else "❌ Désactivé"
        log_channel = f"<#{config.get('log_channel_id')}>" if config.get('log_channel_id') else "Non configuré"
        
        embed.add_field(
            name="📊 Status Actuel",
            value=f"**Status:** {status}\n**Salon:** {log_channel}",
            inline=False
        )
        
        # Événements surveillés
        default_events = [
            "✅ Connexions/Déconnexions",
            "✅ Messages supprimés/modifiés", 
            "✅ Rôles ajoutés/supprimés",
            "✅ Sanctions (ban/kick/timeout)",
            "✅ Salons créés/supprimés",
            "✅ Invitations créées",
            "✅ Changements serveur"
        ]
        
        embed.add_field(
            name="📋 Événements Surveillés",
            value="\n".join(default_events),
            inline=False
        )
        
        embed.add_field(
            name="💡 Configuration",
            value="Utilisez `/logs config` avec un salon pour configurer les logs",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    def get_log_config(self, guild_id: int) -> Dict:
        """Récupère la configuration des logs"""
        with sqlite3.connect(self.logs_db) as conn:
            result = conn.execute(
                "SELECT config_json, log_channel_id FROM log_config WHERE guild_id = ?",
                (guild_id,)
            ).fetchone()
            
            if result:
                config = json.loads(result[0]) if result[0] else {}
                config["log_channel_id"] = result[1]
                config["enabled"] = bool(result[1])
                return config
            
            return {"enabled": False}

    async def log_event(self, guild_id: int, event_type: str, user_id: int = None, 
                       target_id: int = None, channel_id: int = None, event_data: str = ""):
        """Enregistre un événement dans les logs"""
        with sqlite3.connect(self.logs_db) as conn:
            conn.execute("""
                INSERT INTO event_logs (guild_id, event_type, user_id, target_id, channel_id, event_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (guild_id, event_type, user_id, target_id, channel_id, event_data))

    # Listeners pour capturer les événements
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Log des arrivées"""
        await self.log_event(
            member.guild.id, 
            "member_join", 
            member.id, 
            event_data=f"{member.display_name} a rejoint le serveur"
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log des départs"""
        await self.log_event(
            member.guild.id, 
            "member_leave", 
            member.id, 
            event_data=f"{member.display_name} a quitté le serveur"
        )

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Log des messages supprimés"""
        if message.author.bot:
            return
        
        await self.log_event(
            message.guild.id if message.guild else 0,
            "message_delete",
            message.author.id,
            channel_id=message.channel.id,
            event_data=f"Message supprimé dans #{message.channel.name}: {message.content[:100]}..."
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Log des messages modifiés"""
        if before.author.bot or before.content == after.content:
            return
        
        await self.log_event(
            before.guild.id if before.guild else 0,
            "message_edit",
            before.author.id,
            channel_id=before.channel.id,
            event_data=f"Message modifié dans #{before.channel.name}"
        )

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Log des changements de membre"""
        changes = []
        
        if before.nick != after.nick:
            changes.append(f"Pseudo: {before.nick} → {after.nick}")
        
        if before.roles != after.roles:
            added = set(after.roles) - set(before.roles)
            removed = set(before.roles) - set(after.roles)
            
            if added:
                changes.append(f"Rôles ajoutés: {', '.join([r.name for r in added])}")
            if removed:
                changes.append(f"Rôles supprimés: {', '.join([r.name for r in removed])}")
        
        if changes:
            await self.log_event(
                after.guild.id,
                "member_update",
                after.id,
                event_data="; ".join(changes)
            )

async def setup(bot):
    await bot.add_cog(AdvancedLoggingSystem(bot))
