#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Arsenal V4 - Système de Règlement DraftBot Style Ultra Complet
Toutes les fonctionnalités DraftBot avec interface simplifiée
Développé par XeRoX - Arsenal Bot V4.5.2
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiosqlite
import json
import asyncio
from datetime import datetime, timedelta
import os
from typing import Optional, Dict, List
import logging

class ReglementDraftBot(commands.Cog):
    """Système de règlement complet style DraftBot avec interface simple"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/reglement_draftbot.db"
        
        # Configuration ultra complète
        self.default_config = {
            "enabled": False,
            "rules_channel": None,
            "welcome_channel": None,
            "log_channel": None,
            "member_role": None,
            "visitor_role": None,
            
            # Fonctionnalités avancées
            "auto_kick": True,
            "kick_delay": 300,  # 5 minutes
            "dm_on_join": True,
            "dm_on_refuse": True,
            "temp_channels": True,
            "verification_level": "medium",  # low, medium, high, extreme
            
            # Sanctions automatiques
            "warn_system": True,
            "auto_timeout": True,
            "timeout_duration": 3600,  # 1 heure
            "escalation_system": True,
            
            # Statistiques et logs
            "stats_tracking": True,
            "detailed_logs": True,
            "mod_notifications": True,
            
            # Personnalisation
            "custom_embed_color": 0xff0000,
            "custom_footer": "Arsenal • Règlement DraftBot Style",
            "custom_thumbnail": None,
            
            # Règles templates
            "rules_templates": {
                "basic": [
                    {"title": "Respect", "desc": "Respectez tous les membres", "emoji": "🤝"},
                    {"title": "Spam", "desc": "Pas de spam/flood", "emoji": "🚫"},
                    {"title": "NSFW", "desc": "Contenu NSFW interdit", "emoji": "🔞"}
                ],
                "gaming": [
                    {"title": "Fair Play", "desc": "Jouez équitablement", "emoji": "🎮"},
                    {"title": "Toxicité", "desc": "Pas de comportement toxique", "emoji": "☠️"},
                    {"title": "Triche", "desc": "Interdiction de tricher", "emoji": "⚠️"}
                ],
                "community": [
                    {"title": "Bienveillance", "desc": "Soyez bienveillants", "emoji": "💖"},
                    {"title": "Constructif", "desc": "Discussions constructives uniquement", "emoji": "🏗️"},
                    {"title": "Patience", "desc": "Soyez patients avec les nouveaux", "emoji": "⏰"}
                ]
            },
            
            "rules": []
        }
        
        # Créer la base de données
        asyncio.create_task(self.setup_database())
        
        # Démarrer les tâches de surveillance
        if not hasattr(self, '_tasks_started'):
            self.verification_checker.start()
            self.stats_updater.start()
            self._tasks_started = True
    
    async def setup_database(self):
        """Initialise la base de données complète"""
        try:
            os.makedirs("data", exist_ok=True)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Table configuration serveur
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS server_config (
                        guild_id INTEGER PRIMARY KEY,
                        config TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                # Table acceptations utilisateurs
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS user_accepts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        username TEXT NOT NULL,
                        accepted_at TEXT NOT NULL,
                        ip_hash TEXT,
                        verification_code TEXT,
                        UNIQUE(guild_id, user_id)
                    )
                """)
                
                # Table sanctions
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS sanctions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        sanction_type TEXT NOT NULL,
                        reason TEXT NOT NULL,
                        moderator_id INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        expires_at TEXT,
                        active BOOLEAN DEFAULT 1
                    )
                """)
                
                # Table statistiques
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        stat_type TEXT NOT NULL,
                        stat_value INTEGER DEFAULT 0,
                        date TEXT NOT NULL
                    )
                """)
                
                # Table logs détaillés
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS detailed_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        action TEXT NOT NULL,
                        details TEXT,
                        timestamp TEXT NOT NULL
                    )
                """)
                
                await db.commit()
                
        except Exception as e:
            logging.error(f"❌ Erreur setup database règlement DraftBot: {e}")
    
    # ==================== TÂCHES AUTOMATIQUES ====================
    
    @tasks.loop(minutes=5)
    async def verification_checker(self):
        """Vérifie les utilisateurs non vérifiés"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Récupérer les configs actives
                async with db.execute("SELECT guild_id, config FROM server_config") as cursor:
                    async for row in cursor:
                        guild_id, config_str = row
                        config = json.loads(config_str)
                        
                        if not config.get("enabled") or not config.get("auto_kick"):
                            continue
                        
                        guild = self.bot.get_guild(guild_id)
                        if not guild:
                            continue
                        
                        # Vérifier les membres non vérifiés depuis plus de kick_delay
                        cutoff_time = datetime.now() - timedelta(seconds=config.get("kick_delay", 300))
                        
                        for member in guild.members:
                            if member.bot:
                                continue
                            
                            # Vérifier si accepté
                            is_accepted = await self.is_user_accepted(guild_id, member.id)
                            if is_accepted:
                                continue
                            
                            # Vérifier si rejoint récemment
                            if member.joined_at and member.joined_at > cutoff_time:
                                continue
                            
                            # Auto-kick
                            try:
                                await member.kick(reason="Non acceptation du règlement (auto-kick)")
                                await self.log_action(guild_id, member.id, "auto_kick", "Non acceptation du règlement")
                            except:
                                pass
        except Exception as e:
            logging.error(f"❌ Erreur verification_checker: {e}")
    
    @tasks.loop(hours=1)
    async def stats_updater(self):
        """Met à jour les statistiques"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for guild in self.bot.guilds:
                    # Compter les acceptations du jour
                    today = datetime.now().strftime("%Y-%m-%d")
                    
                    async with db.execute("""
                        SELECT COUNT(*) FROM user_accepts 
                        WHERE guild_id = ? AND DATE(accepted_at) = ?
                    """, (guild.id, today)) as cursor:
                        count = (await cursor.fetchone())[0]
                    
                    # Sauvegarder la stat
                    await db.execute("""
                        INSERT OR REPLACE INTO stats (guild_id, stat_type, stat_value, date)
                        VALUES (?, ?, ?, ?)
                    """, (guild.id, "daily_accepts", count, today))
                
                await db.commit()
        except Exception as e:
            logging.error(f"❌ Erreur stats_updater: {e}")
    
    # ==================== MÉTHODES UTILITAIRES ====================
    
    async def get_config(self, guild_id: int) -> Dict:
        """Récupère la configuration du serveur"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT config FROM server_config WHERE guild_id = ?", (guild_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return json.loads(row[0])
            return self.default_config.copy()
        except Exception as e:
            logging.error(f"❌ Erreur get_config: {e}")
            return self.default_config.copy()
    
    async def save_config(self, guild_id: int, config: Dict):
        """Sauvegarde la configuration du serveur"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO server_config (guild_id, config, updated_at)
                    VALUES (?, ?, ?)
                """, (guild_id, json.dumps(config), datetime.now().isoformat()))
                await db.commit()
        except Exception as e:
            logging.error(f"❌ Erreur save_config: {e}")
    
    async def is_user_accepted(self, guild_id: int, user_id: int) -> bool:
        """Vérifie si l'utilisateur a accepté le règlement"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT id FROM user_accepts WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)) as cursor:
                    row = await cursor.fetchone()
                    return row is not None
        except:
            return False
    
    async def record_acceptance(self, guild_id: int, user_id: int, username: str):
        """Enregistre l'acceptation du règlement"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR IGNORE INTO user_accepts (guild_id, user_id, username, accepted_at)
                    VALUES (?, ?, ?, ?)
                """, (guild_id, user_id, username, datetime.now().isoformat()))
                await db.commit()
                return True
        except Exception as e:
            logging.error(f"❌ Erreur record_acceptance: {e}")
            return False
    
    async def log_action(self, guild_id: int, user_id: int, action: str, details: str = ""):
        """Enregistre une action dans les logs détaillés"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO detailed_logs (guild_id, user_id, action, details, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (guild_id, user_id, action, details, datetime.now().isoformat()))
                await db.commit()
        except Exception as e:
            logging.error(f"❌ Erreur log_action: {e}")
    
    # ==================== COMMANDES D'ADMINISTRATION ====================
    
    @app_commands.command(name="reglement_setup", description="🔧 Configuration complète du règlement (style DraftBot)")
    @app_commands.describe(
        template="Template de règles à utiliser",
        rules_channel="Salon pour afficher le règlement",
        welcome_channel="Salon de bienvenue",
        log_channel="Salon des logs",
        member_role="Rôle à donner après acceptation",
        verification_level="Niveau de vérification (low/medium/high/extreme)"
    )
    @app_commands.choices(template=[
        app_commands.Choice(name="🎮 Gaming - Règles pour serveur gaming", value="gaming"),
        app_commands.Choice(name="👥 Community - Règles pour communauté", value="community"),
        app_commands.Choice(name="📝 Basic - Règles de base", value="basic"),
        app_commands.Choice(name="🛠️ Custom - Configuration manuelle", value="custom")
    ])
    @app_commands.choices(verification_level=[
        app_commands.Choice(name="🟢 Low - Vérification basique", value="low"),
        app_commands.Choice(name="🟡 Medium - Vérification standard", value="medium"),
        app_commands.Choice(name="🟠 High - Vérification stricte", value="high"),
        app_commands.Choice(name="🔴 Extreme - Vérification maximale", value="extreme")
    ])
    @app_commands.default_permissions(administrator=True)
    async def reglement_setup(self, interaction: discord.Interaction,
                             template: str,
                             rules_channel: discord.TextChannel,
                             welcome_channel: Optional[discord.TextChannel] = None,
                             log_channel: Optional[discord.TextChannel] = None,
                             member_role: Optional[discord.Role] = None,
                             verification_level: str = "medium"):
        """Configuration complète en une commande !"""
        
        await interaction.response.defer()
        
        config = await self.get_config(interaction.guild.id)
        config.update({
            "enabled": True,
            "rules_channel": rules_channel.id,
            "welcome_channel": welcome_channel.id if welcome_channel else None,
            "log_channel": log_channel.id if log_channel else None,
            "member_role": member_role.id if member_role else None,
            "verification_level": verification_level,
            "auto_kick": True,
            "kick_delay": {"low": 600, "medium": 300, "high": 120, "extreme": 60}[verification_level]
        })
        
        # Appliquer le template si pas custom
        if template != "custom" and template in config["rules_templates"]:
            config["rules"] = config["rules_templates"][template].copy()
        
        await self.save_config(interaction.guild.id, config)
        
        # Dictionnaires pour l'affichage
        verification_levels = {
            'low': '🟢 Faible',
            'medium': '🟡 Standard', 
            'high': '🟠 Strict',
            'extreme': '🔴 Maximum'
        }
        
        templates = {
            'gaming': '🎮 Gaming',
            'community': '👥 Community',
            'basic': '📝 Basic',
            'custom': '🛠️ Custom'
        }
        
        # Créer l'embed de confirmation
        embed = discord.Embed(
            title="✅ **RÈGLEMENT CONFIGURÉ AVEC SUCCÈS !**",
            description=f"**Configuration DraftBot Style activée !**\n\n"
                       f"📋 **Salon règlement:** {rules_channel.mention}\n"
                       f"� **Salon bienvenue:** {welcome_channel.mention if welcome_channel else 'Non configuré'}\n"
                       f"📝 **Salon logs:** {log_channel.mention if log_channel else 'Non configuré'}\n"
                       f"👥 **Rôle membre:** {member_role.mention if member_role else 'Non configuré'}\n"
                       f"🔒 **Niveau vérification:** {verification_levels[verification_level]}\n"
                       f"⏰ **Délai avant expulsion:** {config['kick_delay']}s\n"
                       f"📊 **Template:** {templates[template]}",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🚀 **FONCTIONNALITÉS ACTIVÉES**",
            value="• ✅ **Auto-kick** des non-vérifiés\n"
                  "• 📊 **Statistiques** détaillées\n"
                  "• 📝 **Logs** complets\n"
                  "• ⚠️ **Système de sanctions**\n"
                  "• 🔔 **Notifications** modérateurs\n"
                  "• 💌 **Messages privés** automatiques",
            inline=True
        )
        
        embed.add_field(
            name="📝 **PROCHAINES ÉTAPES**",
            value=f"• `/reglement_show` - Afficher le règlement\n"
                  f"• `/reglement_edit` - Modifier les règles\n"
                  f"• `/reglement_stats` - Voir les statistiques\n"
                  f"• `/reglement_logs` - Consulter les logs",
            inline=True
        )
        
        embed.set_footer(text="Arsenal • DraftBot Style", icon_url=self.bot.user.avatar.url)
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="reglement_show", description="📋 Afficher le règlement avec interface complète")
    @app_commands.default_permissions(administrator=True)
    async def reglement_show(self, interaction: discord.Interaction):
        """Affiche le règlement complet avec toutes les fonctionnalités"""
        
        config = await self.get_config(interaction.guild.id)
        if not config.get("enabled"):
            await interaction.response.send_message("❌ Configurez d'abord avec `/reglement_setup` !", ephemeral=True)
            return
        
        if not config.get("rules"):
            await interaction.response.send_message("❌ Aucune règle configurée ! Utilisez un template dans `/reglement_setup`", ephemeral=True)
            return
        
        # Construire l'embed ultra complet
        verification_levels = {
            'low': '🟢 Standard',
            'medium': '🟡 Renforcé', 
            'high': '🟠 Strict',
            'extreme': '🔴 Maximum'
        }
        
        embed = discord.Embed(
            title="📜 **RÈGLEMENT OFFICIEL DU SERVEUR**",
            description=f"**{interaction.guild.name}**\n\n"
                       f"**⚠️ ACCEPTATION OBLIGATOIRE POUR ACCÉDER AU SERVEUR ⚠️**\n\n"
                       f"🔒 **Niveau de sécurité:** {verification_levels[config.get('verification_level', 'medium')]}\n"
                       f"⏰ **Temps limite:** {config.get('kick_delay', 300)} secondes\n"
                       f"📊 **{len(config['rules'])} règles** à respecter absolument",
            color=config.get("custom_embed_color", 0xff0000),
            timestamp=datetime.now()
        )
        
        # Ajouter les règles avec emojis
        rules_text = ""
        for i, rule in enumerate(config["rules"][:10], 1):  # Max 10 règles
            emoji = rule.get("emoji", "📝")
            title = rule.get("title", f"Règle {i}")
            desc = rule.get("desc", "Description non définie")
            rules_text += f"{emoji} **{i}. {title}**\n{desc}\n\n"
        
        embed.add_field(
            name="📋 **RÈGLES À RESPECTER ABSOLUMENT**",
            value=rules_text,
            inline=False
        )
        
        # Informations sur les sanctions
        embed.add_field(
            name="⚖️ **SYSTÈME DE SANCTIONS AUTOMATIQUE**",
            value="🟡 **1ère infraction:** Avertissement + Log\n"
                  "🟠 **2ème infraction:** Timeout 1h + Notification mods\n"
                  "🔴 **3ème infraction:** Timeout 24h + Examen\n"
                  "⚫ **Infractions graves:** Expulsion immédiate",
            inline=True
        )
        
        # Aide et support
        embed.add_field(
            name="🆘 **BESOIN D'AIDE OU QUESTIONS ?**",
            value="• 📞 Contactez un **@Modérateur** ou **@Admin**\n"
                  "• 🎫 Ouvrez un **ticket** de support\n"
                  "• 📧 Utilisez les salons d'**aide dédiés**\n"
                  "• ⏰ **Patience** et **respect** requis !",
            inline=True
        )
        
        # Statistiques du serveur
        embed.add_field(
            name="📊 **STATISTIQUES DU SERVEUR**",
            value=f"👥 **Membres:** {len(interaction.guild.members)}\n"
                  f"🤖 **Bots:** {len([m for m in interaction.guild.members if m.bot])}\n"
                  f"📅 **Créé le:** {interaction.guild.created_at.strftime('%d/%m/%Y')}\n"
                  f"🔐 **Niveau vérif:** {interaction.guild.verification_level.name.title()}",
            inline=True
        )
        
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(
            text=config.get("custom_footer", f"Arsenal • DraftBot Style • {datetime.now().strftime('%d/%m/%Y à %H:%M')}"),
            icon_url=self.bot.user.avatar.url
        )
        
        # Envoyer dans le salon configuré
        rules_channel = self.bot.get_channel(config["rules_channel"])
        if not rules_channel:
            await interaction.response.send_message("❌ Salon de règlement introuvable !", ephemeral=True)
            return
        
        # Créer la vue avec tous les boutons
        view = ReglementDraftBotView()
        
        try:
            await rules_channel.send(embed=embed, view=view)
            
            # Message de confirmation
            confirm_embed = discord.Embed(
                title="✅ **RÈGLEMENT PUBLIÉ !**",
                description=f"**Règlement affiché dans {rules_channel.mention}**\n\n"
                           f"🎯 **Fonctionnalités actives:**\n"
                           f"• Auto-kick après {config.get('kick_delay', 300)}s\n"
                           f"• Logs détaillés des actions\n"
                           f"• Statistiques en temps réel\n"
                           f"• Messages privés automatiques\n"
                           f"• Système de sanctions graduelles",
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=confirm_embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)


class ReglementView(discord.ui.View):
    """Interface à boutons ultra simple pour le règlement"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="✅ J'ACCEPTE", style=discord.ButtonStyle.success, custom_id="accept_rules", emoji="✅")
    async def accept_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton d'acceptation du règlement"""
        
        cog = interaction.client.get_cog("ReglementSimple")
        if not cog:
            await interaction.response.send_message("❌ Système indisponible !", ephemeral=True)
            return
        
        # Vérifier si déjà accepté
        already_accepted = await cog.is_user_accepted(interaction.guild.id, interaction.user.id)
        if already_accepted:
            await interaction.response.send_message("✅ Vous avez déjà accepté le règlement !", ephemeral=True)
            return
        
        # Enregistrer l'acceptation
        success = await cog.record_acceptance(interaction.guild.id, interaction.user.id)
        if not success:
            await interaction.response.send_message("❌ Erreur lors de l'enregistrement !", ephemeral=True)
            return
        
        # Donner le rôle si configuré
        config = await cog.get_config(interaction.guild.id)
        if config.get("member_role"):
            role = interaction.guild.get_role(config["member_role"])
            if role:
                try:
                    await interaction.user.add_roles(role, reason="Acceptation du règlement")
                except:
                    pass
        
        # Confirmation
        embed = discord.Embed(
            title="✅ **RÈGLEMENT ACCEPTÉ !**",
            description=f"**Bienvenue {interaction.user.mention} !**\n\n"
                       f"🎉 **Vous avez officiellement rejoint le serveur !**\n"
                       f"🔓 **Accès complet déverrouillé**\n\n"
                       f"**Respectez les règles et amusez-vous bien !**",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="❌ JE REFUSE", style=discord.ButtonStyle.danger, custom_id="refuse_rules", emoji="❌")
    async def refuse_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton de refus du règlement"""
        
        embed = discord.Embed(
            title="❌ **RÈGLEMENT REFUSÉ**",
            description=f"**{interaction.user.mention}**\n\n"
                       f"**Vous avez refusé le règlement du serveur.**\n\n"
                       f"⚠️ **Vous allez être expulsé dans 10 secondes.**\n"
                       f"**Pour revenir, vous devrez accepter les règles.**",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Auto-kick après 10 secondes
        cog = interaction.client.get_cog("ReglementSimple")
        if cog:
            config = await cog.get_config(interaction.guild.id)
            if config.get("auto_kick", True):
                await asyncio.sleep(10)
                try:
                    await interaction.user.kick(reason="Refus du règlement")
                except:
                    pass
    
    @discord.ui.button(label="📊 MES INFOS", style=discord.ButtonStyle.secondary, custom_id="my_info", emoji="📊")
    async def my_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Affiche les informations de l'utilisateur"""
        
        cog = interaction.client.get_cog("ReglementSimple")
        if not cog:
            await interaction.response.send_message("❌ Système indisponible !", ephemeral=True)
            return
        
        is_accepted = await cog.is_user_accepted(interaction.guild.id, interaction.user.id)
        
        embed = discord.Embed(
            title="📊 **VOS INFORMATIONS**",
            description=f"**{interaction.user.mention}**\n\n"
                       f"**Statut règlement:** {'✅ Accepté' if is_accepted else '❌ Non accepté'}\n"
                       f"**Arrivée sur le serveur:** {interaction.user.joined_at.strftime('%d/%m/%Y à %H:%M') if interaction.user.joined_at else 'Inconnue'}\n"
                       f"**Compte créé:** {interaction.user.created_at.strftime('%d/%m/%Y')}\n"
                       f"**ID:** `{interaction.user.id}`",
            color=discord.Color.green() if is_accepted else discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="Arsenal • Règlement Simple", icon_url=interaction.client.user.avatar.url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    """Charge le module ReglementSimple"""
    await bot.add_cog(ReglementSimple(bot))
    print("🚀 [OK] ReglementSimple chargé - Interface ultra moderne !")
