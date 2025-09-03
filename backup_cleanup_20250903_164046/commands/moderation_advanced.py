# 🚀 Arsenal V4 - Système de Modération Intelligente
"""
Modération automatique avancée avec:
- Auto-modération multi-niveaux
- Détection de spam/flood
- Filtres de mots personnalisables
- Système d'escalade automatique
- Logs complets et dashboards
- Sanctions graduelles
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiosqlite
import json
import re
import asyncio
from datetime import datetime, timedelta
import os
from typing import Optional, Dict, List, Union
import time
from collections import defaultdict, deque

class ModerationAdvanced(commands.Cog):
    """Système de modération intelligente pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/moderation.db"
        self.config_path = "data/moderation_config.json"
        
        # Caches pour la performance
        self.user_warnings = defaultdict(int)
        self.user_messages = defaultdict(lambda: deque(maxlen=10))
        self.spam_tracking = defaultdict(lambda: deque(maxlen=5))
        self.automod_settings = {}
        
        # Patterns de détection
        self.spam_patterns = [
            r'(.)\1{4,}',  # Répétition de caractères
            r'[A-Z]{5,}',  # Caps excessifs
            r'(?:discord\.gg|dsc\.gg|invite)/\w+',  # Invitations Discord
            r'(?:https?://)?(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/\S*)?'  # URLs
        ]
        
        asyncio.create_task(self.setup_database())
        self.load_config()
        self.cleanup_expired_sanctions.start()

    async def setup_database(self):
        """Initialise la base de données de modération"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            # Table des sanctions
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sanctions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    sanction_type TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    duration INTEGER,
                    expires_at TIMESTAMP,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des avertissements
            await db.execute("""
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    auto_generated BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des actions auto-mod
            await db.execute("""
                CREATE TABLE IF NOT EXISTS automod_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    trigger_reason TEXT NOT NULL,
                    message_content TEXT,
                    channel_id INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Configuration par serveur
            await db.execute("""
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER PRIMARY KEY,
                    automod_enabled BOOLEAN DEFAULT TRUE,
                    spam_threshold INTEGER DEFAULT 5,
                    warning_threshold INTEGER DEFAULT 3,
                    banned_words TEXT DEFAULT '[]',
                    immune_roles TEXT DEFAULT '[]',
                    log_channel_id INTEGER,
                    escalation_enabled BOOLEAN DEFAULT TRUE,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.commit()

    def load_config(self):
        """Charge la configuration de modération"""
        if not os.path.exists(self.config_path):
            default_config = {
                "automod": {
                    "spam_limit": 5,
                    "spam_window": 10,
                    "caps_percentage": 70,
                    "max_mentions": 5,
                    "link_cooldown": 30
                },
                "escalation": {
                    "warn_threshold": 3,
                    "mute_threshold": 5,
                    "kick_threshold": 7,
                    "ban_threshold": 10
                },
                "durations": {
                    "mute": [300, 900, 3600, 86400],  # 5min, 15min, 1h, 24h
                    "timeout": [60, 300, 1800, 7200]   # 1min, 5min, 30min, 2h
                }
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
        
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {"automod": {"spam_limit": 5}}

    @commands.Cog.listener()
    async def on_message(self, message):
        """Analyseur de messages pour l'auto-modération"""
        
        if not message.guild or message.author.bot:
            return
        
        # Vérifier si l'auto-mod est activé pour ce serveur
        settings = await self.get_guild_settings(message.guild.id)
        if not settings.get('automod_enabled', True):
            return
        
        # Vérifier les rôles immunisés
        immune_roles = settings.get('immune_roles', [])
        if any(role.id in immune_roles for role in message.author.roles):
            return
        
        # Vérifications de modération
        violations = []
        
        # 1. Détection de spam
        if await self.check_spam(message):
            violations.append("spam")
        
        # 2. Mots interdits
        if await self.check_banned_words(message, settings.get('banned_words', [])):
            violations.append("banned_word")
        
        # 3. Caps excessifs
        if self.check_caps(message.content):
            violations.append("caps")
        
        # 4. Mentions excessives
        if self.check_mentions(message):
            violations.append("mentions")
        
        # 5. Liens suspects
        if await self.check_suspicious_links(message):
            violations.append("suspicious_link")
        
        # Appliquer les sanctions si violations détectées
        if violations:
            await self.handle_violations(message, violations)

    async def check_spam(self, message) -> bool:
        """Détecte le spam/flood"""
        user_id = message.author.id
        now = time.time()
        
        # Ajouter le message au tracking
        self.spam_tracking[user_id].append(now)
        
        # Vérifier le nombre de messages dans la fenêtre de temps
        spam_window = self.config['automod'].get('spam_window', 10)
        recent_messages = [t for t in self.spam_tracking[user_id] if now - t < spam_window]
        
        spam_limit = self.config['automod'].get('spam_limit', 5)
        return len(recent_messages) >= spam_limit

    async def check_banned_words(self, message, banned_words) -> bool:
        """Vérifie les mots interdits"""
        if not banned_words:
            return False
        
        content = message.content.lower()
        for word in banned_words:
            if re.search(rf'\b{re.escape(word.lower())}\b', content):
                return True
        return False

    def check_caps(self, content: str) -> bool:
        """Vérifie les majuscules excessives"""
        if len(content) < 10:
            return False
        
        caps_count = sum(1 for c in content if c.isupper())
        caps_percentage = (caps_count / len(content)) * 100
        
        threshold = self.config['automod'].get('caps_percentage', 70)
        return caps_percentage > threshold

    def check_mentions(self, message) -> bool:
        """Vérifie les mentions excessives"""
        max_mentions = self.config['automod'].get('max_mentions', 5)
        total_mentions = len(message.mentions) + len(message.role_mentions)
        return total_mentions > max_mentions

    async def check_suspicious_links(self, message) -> bool:
        """Détecte les liens suspects"""
        for pattern in self.spam_patterns[2:]:  # URLs et invitations
            if re.search(pattern, message.content, re.IGNORECASE):
                return True
        return False

    async def handle_violations(self, message, violations):
        """Gère les violations détectées"""
        user_id = message.author.id
        guild_id = message.guild.id
        
        try:
            # Supprimer le message
            await message.delete()
            
            # Compter les violations récentes
            violation_count = await self.get_recent_violations(user_id, guild_id)
            
            # Enregistrer l'action auto-mod
            await self.log_automod_action(
                guild_id, user_id, "message_deleted", 
                f"Violations: {', '.join(violations)}", 
                message.content, message.channel.id
            )
            
            # Appliquer l'escalade
            await self.apply_escalation(message, violation_count, violations)
            
        except discord.NotFound:
            pass  # Message déjà supprimé
        except discord.Forbidden:
            pass  # Pas les permissions

    async def apply_escalation(self, message, violation_count, violations):
        """Applique l'escalade automatique"""
        
        escalation_config = self.config.get('escalation', {})
        member = message.author
        
        # Déterminer l'action selon le nombre de violations
        if violation_count >= escalation_config.get('ban_threshold', 10):
            action = "ban"
            reason = f"Auto-ban après {violation_count} violations"
        elif violation_count >= escalation_config.get('kick_threshold', 7):
            action = "kick" 
            reason = f"Auto-kick après {violation_count} violations"
        elif violation_count >= escalation_config.get('mute_threshold', 5):
            action = "timeout"
            duration = min(violation_count * 300, 86400)  # Max 24h
            reason = f"Auto-timeout {duration}s après {violation_count} violations"
        elif violation_count >= escalation_config.get('warn_threshold', 3):
            action = "warn"
            reason = f"Auto-avertissement après {violation_count} violations"
        else:
            return  # Pas d'action
        
        try:
            if action == "ban":
                await member.ban(reason=reason, delete_message_days=1)
            elif action == "kick":
                await member.kick(reason=reason)
            elif action == "timeout":
                await member.timeout(timedelta(seconds=duration), reason=reason)
            elif action == "warn":
                await self.add_warning(member, message.guild, self.bot.user, reason, auto=True)
            
            # Log dans le channel de modération
            await self.send_mod_log(message.guild, action, member, reason, violations)
            
        except discord.Forbidden:
            pass  # Permissions insuffisantes

    @app_commands.command(name="automod", description="🛡️ Configuration de l'auto-modération")
    @app_commands.describe(
        enabled="Activer/désactiver l'auto-mod",
        spam_threshold="Nombre de messages pour déclencher anti-spam",
        log_channel="Channel pour les logs de modération"
    )
    @app_commands.default_permissions(manage_guild=True)
    async def automod_config(self, interaction: discord.Interaction, 
                           enabled: Optional[bool] = None,
                           spam_threshold: Optional[int] = None,
                           log_channel: Optional[discord.TextChannel] = None):
        """Configuration de l'auto-modération"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Permission refusée !", ephemeral=True)
            return
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Récupérer les paramètres actuels
                cursor = await db.execute("""
                    SELECT * FROM guild_settings WHERE guild_id = ?
                """, (interaction.guild.id,))
                
                current = await cursor.fetchone()
                
                # Créer ou mettre à jour
                if not current:
                    await db.execute("""
                        INSERT INTO guild_settings (guild_id, automod_enabled, spam_threshold, log_channel_id)
                        VALUES (?, ?, ?, ?)
                    """, (
                        interaction.guild.id,
                        enabled if enabled is not None else True,
                        spam_threshold or 5,
                        log_channel.id if log_channel else None
                    ))
                else:
                    updates = []
                    params = []
                    
                    if enabled is not None:
                        updates.append("automod_enabled = ?")
                        params.append(enabled)
                    
                    if spam_threshold is not None:
                        updates.append("spam_threshold = ?")
                        params.append(spam_threshold)
                    
                    if log_channel is not None:
                        updates.append("log_channel_id = ?")
                        params.append(log_channel.id)
                    
                    if updates:
                        updates.append("updated_at = CURRENT_TIMESTAMP")
                        params.append(interaction.guild.id)
                        
                        await db.execute(f"""
                            UPDATE guild_settings 
                            SET {', '.join(updates)}
                            WHERE guild_id = ?
                        """, params)
                
                await db.commit()
                
                # Récupérer les nouveaux paramètres
                cursor = await db.execute("""
                    SELECT automod_enabled, spam_threshold, log_channel_id
                    FROM guild_settings WHERE guild_id = ?
                """, (interaction.guild.id,))
                
                settings = await cursor.fetchone()
                
                embed = discord.Embed(
                    title="🛡️ Configuration Auto-Modération",
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                
                embed.add_field(
                    name="⚡ Statut",
                    value="✅ Activé" if settings[0] else "❌ Désactivé",
                    inline=True
                )
                
                embed.add_field(
                    name="📊 Seuil Spam",
                    value=f"{settings[1]} messages/10s",
                    inline=True
                )
                
                log_ch = self.bot.get_channel(settings[2]) if settings[2] else None
                embed.add_field(
                    name="📝 Channel Logs",
                    value=log_ch.mention if log_ch else "Non configuré",
                    inline=True
                )
                
                embed.add_field(
                    name="🔧 Fonctionnalités",
                    value=(
                        "• Anti-spam/flood\n"
                        "• Filtrage mots interdits\n"
                        "• Détection caps excessifs\n"
                        "• Limitation mentions\n"
                        "• Blocage liens suspects\n"
                        "• Escalade automatique"
                    ),
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed)
                
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {str(e)}", ephemeral=True)

    @app_commands.command(name="warn", description="⚠️ Avertir un utilisateur")
    @app_commands.describe(user="Utilisateur à avertir", reason="Raison de l'avertissement")
    @app_commands.default_permissions(moderate_members=True)
    async def warn_user(self, interaction: discord.Interaction, 
                       user: discord.Member, reason: str):
        """Avertir un utilisateur"""
        
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ Permission refusée !", ephemeral=True)
            return
        
        if user.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            await interaction.response.send_message("❌ Vous ne pouvez pas avertir cet utilisateur !", ephemeral=True)
            return
        
        await self.add_warning(user, interaction.guild, interaction.user, reason)
        
        # Compter les avertissements
        warning_count = await self.get_user_warnings(user.id, interaction.guild.id)
        
        embed = discord.Embed(
            title="⚠️ Avertissement Émis",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="👤 Utilisateur",
            value=f"{user.mention} ({user.display_name})",
            inline=True
        )
        
        embed.add_field(
            name="👮 Modérateur",
            value=interaction.user.mention,
            inline=True
        )
        
        embed.add_field(
            name="📊 Total",
            value=f"{warning_count} avertissement(s)",
            inline=True
        )
        
        embed.add_field(
            name="📝 Raison",
            value=reason,
            inline=False
        )
        
        if warning_count >= 3:
            embed.add_field(
                name="⚠️ Attention",
                value=f"Cet utilisateur a {warning_count} avertissements !",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
        
        # Notifier l'utilisateur en DM
        try:
            dm_embed = discord.Embed(
                title="⚠️ Avertissement Reçu",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            
            dm_embed.add_field(
                name="🏰 Serveur",
                value=interaction.guild.name,
                inline=True
            )
            
            dm_embed.add_field(
                name="📝 Raison",
                value=reason,
                inline=False
            )
            
            dm_embed.add_field(
                name="📊 Vos Avertissements",
                value=f"{warning_count}/10",
                inline=True
            )
            
            await user.send(embed=dm_embed)
        except:
            pass  # L'utilisateur a désactivé les DMs

    @app_commands.command(name="warnings", description="📊 Voir les avertissements d'un utilisateur")
    @app_commands.describe(user="Utilisateur à vérifier")
    async def check_warnings(self, interaction: discord.Interaction, 
                           user: Optional[discord.Member] = None):
        """Affiche les avertissements d'un utilisateur"""
        
        target = user or interaction.user
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT reason, moderator_id, auto_generated, created_at
                    FROM warnings 
                    WHERE user_id = ? AND guild_id = ?
                    ORDER BY created_at DESC
                    LIMIT 10
                """, (target.id, interaction.guild.id))
                
                warnings = await cursor.fetchall()
        
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📊 Avertissements - {target.display_name}",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        if not warnings:
            embed.description = "✅ Aucun avertissement"
        else:
            embed.description = f"**{len(warnings)} avertissement(s)**"
            
            warnings_text = ""
            for i, (reason, mod_id, auto, created_at) in enumerate(warnings[:5], 1):
                moderator = self.bot.get_user(mod_id)
                mod_name = moderator.display_name if moderator else "Inconnu"
                auto_text = " (Auto)" if auto else ""
                
                date = datetime.fromisoformat(created_at).strftime("%d/%m %H:%M")
                warnings_text += f"**{i}.** {reason}\n*Par: {mod_name}{auto_text} - {date}*\n\n"
            
            embed.add_field(
                name="📝 Historique",
                value=warnings_text[:1024] or "Aucun détail",
                inline=False
            )
            
            if len(warnings) > 5:
                embed.set_footer(text=f"... et {len(warnings)-5} autres avertissements")
        
        await interaction.response.send_message(embed=embed)

    async def add_warning(self, user: discord.Member, guild: discord.Guild, 
                         moderator: discord.User, reason: str, auto: bool = False):
        """Ajoute un avertissement à un utilisateur"""
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO warnings (guild_id, user_id, moderator_id, reason, auto_generated)
                VALUES (?, ?, ?, ?, ?)
            """, (guild.id, user.id, moderator.id, reason, auto))
            await db.commit()

    async def get_user_warnings(self, user_id: int, guild_id: int) -> int:
        """Récupère le nombre d'avertissements d'un utilisateur"""
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT COUNT(*) FROM warnings 
                WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id))
            
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def get_recent_violations(self, user_id: int, guild_id: int) -> int:
        """Compte les violations récentes (dernière heure)"""
        
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT COUNT(*) FROM automod_actions 
                WHERE user_id = ? AND guild_id = ? AND timestamp > ?
            """, (user_id, guild_id, one_hour_ago.isoformat()))
            
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def log_automod_action(self, guild_id: int, user_id: int, action_type: str,
                               trigger_reason: str, message_content: str, channel_id: int):
        """Enregistre une action d'auto-modération"""
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO automod_actions 
                (guild_id, user_id, action_type, trigger_reason, message_content, channel_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (guild_id, user_id, action_type, trigger_reason, message_content, channel_id))
            await db.commit()

    async def get_guild_settings(self, guild_id: int) -> Dict:
        """Récupère les paramètres d'un serveur"""
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT automod_enabled, spam_threshold, banned_words, immune_roles, log_channel_id
                FROM guild_settings WHERE guild_id = ?
            """, (guild_id,))
            
            result = await cursor.fetchone()
            
            if result:
                return {
                    'automod_enabled': bool(result[0]),
                    'spam_threshold': result[1],
                    'banned_words': json.loads(result[2] or '[]'),
                    'immune_roles': json.loads(result[3] or '[]'),
                    'log_channel_id': result[4]
                }
            else:
                return {'automod_enabled': True, 'spam_threshold': 5}

    async def send_mod_log(self, guild, action, member, reason, violations):
        """Envoie un log de modération"""
        
        settings = await self.get_guild_settings(guild.id)
        log_channel_id = settings.get('log_channel_id')
        
        if not log_channel_id:
            return
        
        log_channel = self.bot.get_channel(log_channel_id)
        if not log_channel:
            return
        
        action_colors = {
            'warn': discord.Color.orange(),
            'timeout': discord.Color.red(),
            'kick': discord.Color.dark_red(),
            'ban': discord.Color.dark_red()
        }
        
        embed = discord.Embed(
            title=f"🤖 Auto-Modération: {action.upper()}",
            color=action_colors.get(action, discord.Color.blue()),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="👤 Utilisateur",
            value=f"{member.mention} ({member.display_name})",
            inline=True
        )
        
        embed.add_field(
            name="⚖️ Action",
            value=action.capitalize(),
            inline=True
        )
        
        embed.add_field(
            name="🚨 Violations",
            value=", ".join(violations),
            inline=True
        )
        
        embed.add_field(
            name="📝 Raison",
            value=reason,
            inline=False
        )
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass

    @tasks.loop(minutes=5)
    async def cleanup_expired_sanctions(self):
        """Nettoie les sanctions expirées"""
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Marquer les sanctions expirées comme inactives
                await db.execute("""
                    UPDATE sanctions 
                    SET active = FALSE 
                    WHERE active = TRUE AND expires_at < ?
                """, (datetime.now().isoformat(),))
                
                await db.commit()
        except Exception as e:
            print(f"Erreur nettoyage sanctions: {e}")

    @cleanup_expired_sanctions.before_loop
    async def before_cleanup(self):
        """Attend que le bot soit prêt"""
        await self.bot.wait_until_ready()

async def setup(bot):
    """Charge le module ModerationAdvanced"""
    await bot.add_cog(ModerationAdvanced(bot))
    print("🛡️ [Moderation Advanced] Module chargé avec succès!")

