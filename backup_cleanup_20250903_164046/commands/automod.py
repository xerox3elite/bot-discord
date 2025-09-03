"""
🛡️ Arsenal Bot - Système d'Auto-Modération Avancé
Système intelligent de modération automatique avec IA et règles personnalisables
Développé par XeRoX - Arsenal Bot V4.5.0
"""
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import re
import json
import sqlite3
import datetime
from typing import Optional, List, Dict, Any
import difflib

class AutoModerationSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.automod_db = "automod_config.db"
        self.violations_db = "automod_violations.db"
        self.init_databases()
        self.load_default_filters()
        
        # Configuration par défaut
        self.default_config = {
            "spam_detection": True,
            "spam_threshold": 5,
            "spam_timeframe": 10,
            "link_filter": False,
            "caps_filter": True,
            "caps_threshold": 70,
            "profanity_filter": True,
            "mention_spam_limit": 5,
            "emoji_spam_limit": 10,
            "auto_timeout": True,
            "timeout_duration": 600,  # 10 minutes
            "delete_violations": True,
            "log_channel": None
        }

    def init_databases(self):
        """Initialise les bases de données d'automod"""
        # Configuration automod par serveur
        with sqlite3.connect(self.automod_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS automod_config (
                    guild_id INTEGER PRIMARY KEY,
                    config_json TEXT,
                    enabled BOOLEAN DEFAULT 1,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS filtered_words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    word TEXT,
                    severity INTEGER DEFAULT 1,
                    action TEXT DEFAULT 'delete'
                )
            """)
        
        # Violations et logs
        with sqlite3.connect(self.violations_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    channel_id INTEGER,
                    message_id INTEGER,
                    violation_type TEXT,
                    content TEXT,
                    action_taken TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def load_default_filters(self):
        """Charge les filtres par défaut"""
        self.profanity_words = [
            "merde", "putain", "connard", "salope", "fdp", "pd", "pute", 
            "bâtard", "enculé", "fuck", "shit", "bitch", "asshole"
        ]
        
        self.spam_patterns = [
            r"(.)\1{4,}",  # Répétition de caractères
            r"[A-Z]{10,}",  # Trop de majuscules
            r"[!@#$%^&*()]{5,}",  # Spam de caractères spéciaux
        ]

    @app_commands.command(name="automod", description="🛡️ Configuration du système d'auto-modération")
    @app_commands.describe(
        action="Action à effectuer",
        setting="Paramètre à modifier",
        value="Nouvelle valeur"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="📊 Status", value="status"),
        app_commands.Choice(name="⚙️ Configurer", value="config"),
        app_commands.Choice(name="🔧 Activer", value="enable"),
        app_commands.Choice(name="❌ Désactiver", value="disable"),
        app_commands.Choice(name="📜 Règles", value="rules"),
        app_commands.Choice(name="📈 Statistiques", value="stats")
    ])
    async def automod(
        self, 
        interaction: discord.Interaction,
        action: str,
        setting: Optional[str] = None,
        value: Optional[str] = None
    ):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ Vous devez avoir la permission de gérer le serveur!", 
                ephemeral=True
            )
            return

        if action == "status":
            await self.show_automod_status(interaction)
        elif action == "config":
            await self.configure_automod(interaction, setting, value)
        elif action == "enable":
            await self.toggle_automod(interaction, True)
        elif action == "disable":
            await self.toggle_automod(interaction, False)
        elif action == "rules":
            await self.show_rules(interaction)
        elif action == "stats":
            await self.show_stats(interaction)

    async def show_automod_status(self, interaction: discord.Interaction):
        """Affiche le statut de l'automod"""
        config = self.get_guild_config(interaction.guild.id)
        
        embed = discord.Embed(
            title="🛡️ Arsenal AutoMod - Status",
            color=discord.Color.green() if config.get("enabled", True) else discord.Color.red(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        
        status = "🟢 Activé" if config.get("enabled", True) else "🔴 Désactivé"
        embed.add_field(name="📊 Status", value=status, inline=True)
        
        # Fonctionnalités actives
        features = []
        if config.get("spam_detection", True):
            features.append("🚫 Anti-Spam")
        if config.get("link_filter", False):
            features.append("🔗 Filtrage Liens")
        if config.get("caps_filter", True):
            features.append("🔠 Anti-Majuscules")
        if config.get("profanity_filter", True):
            features.append("🤬 Anti-Insultes")
        
        embed.add_field(
            name="⚡ Fonctionnalités Actives",
            value="\n".join(features) if features else "Aucune",
            inline=False
        )
        
        # Statistiques rapides
        violations_count = self.get_violations_count(interaction.guild.id, days=7)
        embed.add_field(
            name="📈 Violations (7 jours)",
            value=f"{violations_count} détectées",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

    async def configure_automod(self, interaction: discord.Interaction, setting: Optional[str], value: Optional[str]):
        """Configuration interactive de l'automod"""
        if not setting:
            embed = discord.Embed(
                title="⚙️ Configuration AutoMod",
                description="Paramètres disponibles:",
                color=discord.Color.blue()
            )
            
            settings_info = [
                "`spam_detection` - Détection anti-spam (true/false)",
                "`spam_threshold` - Seuil messages spam (nombre)",
                "`link_filter` - Filtrage des liens (true/false)",
                "`caps_filter` - Anti-majuscules (true/false)",
                "`caps_threshold` - Seuil majuscules % (nombre)",
                "`profanity_filter` - Anti-insultes (true/false)",
                "`auto_timeout` - Timeout automatique (true/false)",
                "`timeout_duration` - Durée timeout secondes (nombre)"
            ]
            
            embed.add_field(
                name="📋 Paramètres",
                value="\n".join(settings_info),
                inline=False
            )
            
            embed.add_field(
                name="💡 Exemple",
                value="`/automod config spam_threshold 3`",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            return
        
        if not value:
            await interaction.response.send_message(
                "❌ Veuillez spécifier une valeur!", 
                ephemeral=True
            )
            return
        
        # Mise à jour de la configuration
        success = await self.update_guild_setting(interaction.guild.id, setting, value)
        
        if success:
            embed = discord.Embed(
                title="✅ Configuration Mise à Jour",
                description=f"**{setting}** → `{value}`",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Erreur Configuration",
                description="Paramètre ou valeur invalide",
                color=discord.Color.red()
            )
        
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listener principal pour la modération automatique"""
        # Ignore les bots et les MPs
        if message.author.bot or not message.guild:
            return
            
        # Ignore les modérateurs
        if message.author.guild_permissions.manage_messages:
            return
        
        config = self.get_guild_config(message.guild.id)
        if not config.get("enabled", True):
            return
        
        violations = []
        
        # Détection spam
        if config.get("spam_detection", True):
            if await self.detect_spam(message):
                violations.append("spam")
        
        # Filtrage profanité
        if config.get("profanity_filter", True):
            if self.detect_profanity(message.content):
                violations.append("profanity")
        
        # Détection majuscules
        if config.get("caps_filter", True):
            if self.detect_caps_spam(message.content, config.get("caps_threshold", 70)):
                violations.append("caps_spam")
        
        # Détection mention spam
        if len(message.mentions) > config.get("mention_spam_limit", 5):
            violations.append("mention_spam")
        
        # Actions selon violations
        if violations:
            await self.handle_violations(message, violations, config)

    async def detect_spam(self, message) -> bool:
        """Détecte le spam de messages"""
        # Vérification historique des messages récents
        async for msg in message.channel.history(limit=10, before=message):
            if msg.author == message.author:
                if msg.content == message.content:
                    return True  # Message identique récent
                    
                # Vérification timing (moins de 2 secondes)
                time_diff = (message.created_at - msg.created_at).total_seconds()
                if time_diff < 2:
                    return True
        
        return False

    def detect_profanity(self, content: str) -> bool:
        """Détecte les mots inappropriés"""
        content_lower = content.lower()
        for word in self.profanity_words:
            if word in content_lower:
                return True
        return False

    def detect_caps_spam(self, content: str, threshold: int) -> bool:
        """Détecte l'abus de majuscules"""
        if len(content) < 10:  # Messages courts ignorés
            return False
            
        caps_count = sum(1 for c in content if c.isupper())
        caps_percentage = (caps_count / len(content)) * 100
        
        return caps_percentage > threshold

    async def handle_violations(self, message, violations: List[str], config: Dict):
        """Gère les violations détectées"""
        # Suppression du message
        if config.get("delete_violations", True):
            try:
                await message.delete()
            except:
                pass
        
        # Timeout automatique
        if config.get("auto_timeout", True) and message.author.guild_permissions.timeout_members:
            try:
                timeout_duration = datetime.timedelta(seconds=config.get("timeout_duration", 600))
                await message.author.timeout(timeout_duration, reason=f"AutoMod: {', '.join(violations)}")
            except:
                pass
        
        # Log des violations
        await self.log_violation(message, violations)
        
        # Notification à l'utilisateur
        try:
            embed = discord.Embed(
                title="🛡️ Message Modéré - Arsenal AutoMod",
                description=f"Votre message a été supprimé pour: **{', '.join(violations)}**",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="📝 Message Original",
                value=f"```{message.content[:100]}{'...' if len(message.content) > 100 else ''}```",
                inline=False
            )
            embed.add_field(
                name="⚡ Action",
                value="Message supprimé" + (" + Timeout temporaire" if config.get("auto_timeout") else ""),
                inline=False
            )
            
            await message.author.send(embed=embed)
        except:
            pass  # L'utilisateur a peut-être désactivé les MPs

    async def log_violation(self, message, violations: List[str]):
        """Log une violation dans la base de données"""
        with sqlite3.connect(self.violations_db) as conn:
            conn.execute("""
                INSERT INTO violations 
                (guild_id, user_id, channel_id, message_id, violation_type, content, action_taken)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                message.guild.id,
                message.author.id,
                message.channel.id,
                message.id,
                ", ".join(violations),
                message.content,
                "delete" + ("_timeout" if self.get_guild_config(message.guild.id).get("auto_timeout") else "")
            ))

    def get_guild_config(self, guild_id: int) -> Dict:
        """Récupère la configuration d'un serveur"""
        with sqlite3.connect(self.automod_db) as conn:
            result = conn.execute(
                "SELECT config_json, enabled FROM automod_config WHERE guild_id = ?",
                (guild_id,)
            ).fetchone()
            
            if result:
                config = json.loads(result[0]) if result[0] else self.default_config.copy()
                config["enabled"] = bool(result[1])
                return config
            
            return self.default_config.copy()

    async def update_guild_setting(self, guild_id: int, setting: str, value: str) -> bool:
        """Met à jour un paramètre de configuration"""
        try:
            config = self.get_guild_config(guild_id)
            
            # Conversion de type selon le paramètre
            if setting in ["spam_threshold", "caps_threshold", "timeout_duration", "mention_spam_limit", "emoji_spam_limit"]:
                config[setting] = int(value)
            elif setting in ["spam_detection", "link_filter", "caps_filter", "profanity_filter", "auto_timeout", "delete_violations"]:
                config[setting] = value.lower() in ["true", "1", "yes", "on"]
            else:
                return False
            
            # Sauvegarde
            with sqlite3.connect(self.automod_db) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO automod_config (guild_id, config_json, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (guild_id, json.dumps(config)))
            
            return True
        except:
            return False

    def get_violations_count(self, guild_id: int, days: int = 7) -> int:
        """Compte les violations récentes"""
        with sqlite3.connect(self.violations_db) as conn:
            result = conn.execute("""
                SELECT COUNT(*) FROM violations 
                WHERE guild_id = ? AND timestamp > datetime('now', '-{} days')
            """.format(days), (guild_id,)).fetchone()
            
            return result[0] if result else 0

    async def toggle_automod(self, interaction: discord.Interaction, enabled: bool):
        """Active/désactive l'automod"""
        with sqlite3.connect(self.automod_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO automod_config (guild_id, enabled, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (interaction.guild.id, enabled))
        
        status = "activé" if enabled else "désactivé"
        emoji = "✅" if enabled else "❌"
        
        embed = discord.Embed(
            title=f"{emoji} AutoMod {status.title()}",
            description=f"Le système d'auto-modération a été **{status}** pour ce serveur.",
            color=discord.Color.green() if enabled else discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed)

    async def show_rules(self, interaction: discord.Interaction):
        """Affiche les règles d'automod actives"""
        embed = discord.Embed(
            title="📜 Règles d'Auto-Modération Arsenal",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        
        config = self.get_guild_config(interaction.guild.id)
        
        rules = []
        if config.get("spam_detection", True):
            rules.append(f"🚫 **Anti-Spam**: Max {config.get('spam_threshold', 5)} messages similaires")
        
        if config.get("caps_filter", True):
            rules.append(f"🔠 **Anti-Majuscules**: Max {config.get('caps_threshold', 70)}% de majuscules")
        
        if config.get("profanity_filter", True):
            rules.append("🤬 **Anti-Insultes**: Langage inapproprié interdit")
        
        if config.get("mention_spam_limit"):
            rules.append(f"📢 **Anti-Mention**: Max {config.get('mention_spam_limit', 5)} mentions par message")
        
        embed.add_field(
            name="⚖️ Règles Actives",
            value="\n".join(rules) if rules else "Aucune règle active",
            inline=False
        )
        
        if config.get("auto_timeout"):
            timeout_min = config.get("timeout_duration", 600) // 60
            embed.add_field(
                name="⏱️ Sanctions",
                value=f"Timeout automatique: {timeout_min} minutes",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

    async def show_stats(self, interaction: discord.Interaction):
        """Affiche les statistiques d'automod"""
        embed = discord.Embed(
            title="📈 Statistiques Auto-Modération",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        
        # Statistiques par période
        for days, period in [(1, "Aujourd'hui"), (7, "7 jours"), (30, "30 jours")]:
            count = self.get_violations_count(interaction.guild.id, days)
            embed.add_field(name=period, value=f"{count} violations", inline=True)
        
        # Types de violations les plus fréquents
        with sqlite3.connect(self.violations_db) as conn:
            results = conn.execute("""
                SELECT violation_type, COUNT(*) as count 
                FROM violations 
                WHERE guild_id = ? AND timestamp > datetime('now', '-30 days')
                GROUP BY violation_type 
                ORDER BY count DESC 
                LIMIT 5
            """, (interaction.guild.id,)).fetchall()
        
        if results:
            top_violations = "\n".join([f"• {vtype}: {count}" for vtype, count in results])
            embed.add_field(
                name="🏆 Top Violations (30j)",
                value=top_violations,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoModerationSystem(bot))

