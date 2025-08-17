#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
� Arsenal V4 - Système de Règlement Intelligent Complet
Toutes les fonctionnalités avancées avec interface ultra-simple
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

class ReglementSystem(commands.Cog):
    """Système de règlement complet style DraftBot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/reglement_draftbot.db"
        
        # Configuration ultra-complète
        self.default_config = {
            "enabled": False,
            "rules_channel": None,
            "log_channel": None,
            "member_role": None,
            "auto_kick": True,
            "kick_delay": 300,
            "verification_level": "medium",
            "rules": [],
            "templates": {
                "gaming": [
                    {"title": "🎮 Respect Gaming", "desc": "Pas de toxicité en jeu", "emoji": "🎮"},
                    {"title": "🚫 Anti-Cheat", "desc": "Interdiction de tricher", "emoji": "🚫"},
                    {"title": "🤝 Fair Play", "desc": "Jouez équitablement", "emoji": "🤝"}
                ],
                "community": [
                    {"title": "💖 Bienveillance", "desc": "Soyez bienveillants", "emoji": "💖"},
                    {"title": "🗣️ Discussion", "desc": "Discussions constructives", "emoji": "🗣️"},
                    {"title": "🆘 Entraide", "desc": "Aidez les nouveaux", "emoji": "🆘"}
                ],
                "basic": [
                    {"title": "🤝 Respect", "desc": "Respectez tout le monde", "emoji": "🤝"},
                    {"title": "🚫 Pas de spam", "desc": "Évitez le spam", "emoji": "🚫"},
                    {"title": "🔞 Contenu", "desc": "Pas de contenu NSFW", "emoji": "🔞"}
                ]
            }
        }
        
        # La base de données sera initialisée dans cog_load()
        self._tasks_started = False

    async def cog_load(self):
        """Initialisation async du cog"""
        await self.setup_database()
        
        # Démarrer les tâches
        if not self._tasks_started:
            self.auto_kick_checker.start()
            self._tasks_started = True
    
    async def setup_database(self):
        """Base de données complète"""
        try:
            os.makedirs("data", exist_ok=True)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Configuration serveur
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS server_config (
                        guild_id INTEGER PRIMARY KEY,
                        config TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                # Acceptations utilisateurs
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS user_accepts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        username TEXT NOT NULL,
                        accepted_at TEXT NOT NULL,
                        UNIQUE(guild_id, user_id)
                    )
                """)
                
                # Logs d'actions
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS action_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        action TEXT NOT NULL,
                        details TEXT,
                        timestamp TEXT NOT NULL
                    )
                """)
                
                # Statistiques
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS stats (
                        guild_id INTEGER PRIMARY KEY,
                        total_accepts INTEGER DEFAULT 0,
                        total_refuses INTEGER DEFAULT 0,
                        total_kicks INTEGER DEFAULT 0,
                        last_updated TEXT NOT NULL
                    )
                """)
                
                await db.commit()
                
        except Exception as e:
            logging.error(f"Erreur setup database: {e}")
    
    @tasks.loop(minutes=1)
    async def auto_kick_checker(self):
        """Vérification auto-kick toutes les minutes"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT guild_id, config FROM server_config") as cursor:
                    async for row in cursor:
                        guild_id, config_str = row
                        config = json.loads(config_str)
                        
                        if not config.get("enabled") or not config.get("auto_kick"):
                            continue
                        
                        guild = self.bot.get_guild(guild_id)
                        if not guild:
                            continue
                        
                        cutoff_time = datetime.now() - timedelta(seconds=config.get("kick_delay", 300))
                        
                        for member in guild.members:
                            if member.bot or await self.is_user_accepted(guild_id, member.id):
                                continue
                            
                            if member.joined_at and member.joined_at < cutoff_time:
                                try:
                                    await member.kick(reason="Non acceptation du règlement")
                                    await self.log_action(guild_id, member.id, "auto_kick", "Délai dépassé")
                                except:
                                    pass
                                    
        except Exception as e:
            logging.error(f"Erreur auto_kick_checker: {e}")
    
    # Méthodes utilitaires
    async def get_config(self, guild_id: int) -> Dict:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT config FROM server_config WHERE guild_id = ?", (guild_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return json.loads(row[0])
            return self.default_config.copy()
        except:
            return self.default_config.copy()
    
    async def save_config(self, guild_id: int, config: Dict):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO server_config (guild_id, config, updated_at)
                    VALUES (?, ?, ?)
                """, (guild_id, json.dumps(config), datetime.now().isoformat()))
                await db.commit()
        except Exception as e:
            logging.error(f"Erreur save_config: {e}")
    
    async def is_user_accepted(self, guild_id: int, user_id: int) -> bool:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT id FROM user_accepts WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)) as cursor:
                    return (await cursor.fetchone()) is not None
        except:
            return False
    
    async def record_acceptance(self, guild_id: int, user_id: int, username: str):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR IGNORE INTO user_accepts (guild_id, user_id, username, accepted_at)
                    VALUES (?, ?, ?, ?)
                """, (guild_id, user_id, username, datetime.now().isoformat()))
                await db.commit()
                return True
        except:
            return False
    
    async def log_action(self, guild_id: int, user_id: int, action: str, details: str = ""):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO action_logs (guild_id, user_id, action, details, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (guild_id, user_id, action, details, datetime.now().isoformat()))
                await db.commit()
        except Exception as e:
            logging.error(f"Erreur log_action: {e}")
    
    # ==================== COMMANDES ====================
    
    @app_commands.command(name="reglement_setup", description="🔧 Setup complet du règlement (style DraftBot)")
    @app_commands.describe(
        template="Template de règles",
        rules_channel="Salon du règlement",
        member_role="Rôle membre existant (optionnel)",
        create_role="Créer automatiquement un rôle membre (si pas de rôle existant)",
        role_name="Nom du rôle à créer (par défaut: Membre)",
        log_channel="Salon logs (optionnel)",
        verification_level="Niveau de vérification"
    )
    @app_commands.choices(template=[
        app_commands.Choice(name="🎮 Gaming", value="gaming"),
        app_commands.Choice(name="👥 Community", value="community"),
        app_commands.Choice(name="📝 Basic", value="basic"),
        app_commands.Choice(name="🛠️ Custom", value="custom")
    ])
    @app_commands.choices(verification_level=[
        app_commands.Choice(name="🟢 Low (10 min)", value="low"),
        app_commands.Choice(name="🟡 Medium (5 min)", value="medium"),
        app_commands.Choice(name="🟠 High (2 min)", value="high"),
        app_commands.Choice(name="🔴 Extreme (30s)", value="extreme")
    ])
    @app_commands.default_permissions(administrator=True)
    async def reglement_setup(self, interaction: discord.Interaction,
                             template: str,
                             rules_channel: discord.TextChannel,
                             member_role: Optional[discord.Role] = None,
                             create_role: bool = False,
                             role_name: str = "Membre",
                             log_channel: Optional[discord.TextChannel] = None,
                             verification_level: str = "medium"):
        """Configuration ultra-complète en une commande avec gestion intelligente des rôles !"""
        
        await interaction.response.defer()
        
        config = await self.get_config(interaction.guild.id)
        
        # Gestion intelligente des rôles
        final_role = None
        role_info = ""
        
        if member_role:
            # Utiliser le rôle existant
            final_role = member_role
            role_info = f"🔄 **Rôle existant utilisé:** {member_role.mention}"
        elif create_role:
            # Créer un nouveau rôle automatiquement
            try:
                final_role = await interaction.guild.create_role(
                    name=role_name,
                    color=discord.Color.green(),
                    reason="Rôle membre créé automatiquement par Arsenal",
                    mentionable=True,
                    hoist=True  # Affiche séparément des autres rôles
                )
                role_info = f"✨ **Nouveau rôle créé:** {final_role.mention}"
                
                # Positionner le rôle au bon endroit (pas tout en haut)
                try:
                    bot_member = interaction.guild.get_member(self.bot.user.id)
                    if bot_member and bot_member.top_role.position > 1:
                        await final_role.edit(position=bot_member.top_role.position - 1)
                except:
                    pass
                    
            except Exception as e:
                await interaction.followup.send(f"❌ Impossible de créer le rôle: {e}", ephemeral=True)
                return
        else:
            role_info = "⚠️ **Aucun rôle configuré** - Les utilisateurs n'auront pas de rôle spécial"
        
        # Appliquer les délais selon le niveau
        kick_delays = {"low": 600, "medium": 300, "high": 120, "extreme": 30}
        
        config.update({
            "enabled": True,
            "rules_channel": rules_channel.id,
            "log_channel": log_channel.id if log_channel else None,
            "member_role": final_role.id if final_role else None,
            "verification_level": verification_level,
            "kick_delay": kick_delays[verification_level],
            "auto_kick": True
        })
        
        # Appliquer le template
        if template != "custom" and template in config["templates"]:
            config["rules"] = config["templates"][template].copy()
        
        await self.save_config(interaction.guild.id, config)
        
        # Embed de confirmation ultra-détaillé
        level_names = {"low": "🟢 Faible", "medium": "🟡 Standard", "high": "🟠 Strict", "extreme": "🔴 Maximum"}
        template_names = {"gaming": "🎮 Gaming", "community": "👥 Community", "basic": "📝 Basic", "custom": "🛠️ Custom"}
        
        embed = discord.Embed(
            title="✅ **RÈGLEMENT DRAFTBOT CONFIGURÉ !**",
            description=f"**Configuration ultra-complète activée !**\n\n"
                       f"📋 **Salon règlement:** {rules_channel.mention}\n"
                       f"{role_info}\n"
                       f"📝 **Salon logs:** {log_channel.mention if log_channel else '❌ Non configuré'}\n"
                       f"🔒 **Niveau sécurité:** {level_names[verification_level]}\n"
                       f"⏰ **Délai expulsion:** {kick_delays[verification_level]}s\n"
                       f"📊 **Template appliqué:** {template_names[template]}",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🚀 **FONCTIONNALITÉS ACTIVES**",
            value="• ✅ Auto-kick intelligent\n"
                  "• 📊 Statistiques complètes\n"
                  "• 📝 Logs détaillés\n"
                  "• 🔔 Notifications auto\n"
                  "• 💌 Messages privés\n"
                  "• 🎯 Interface moderne",
            inline=True
        )
        
        embed.add_field(
            name="📝 **COMMANDES**",
            value="• `/reglement_show` - Afficher\n"
                  "• `/reglement_stats` - Stats\n"
                  "• `/reglement_logs` - Logs\n"
                  "• `/reglement_edit` - Modifier\n"
                  "• `/reglement_test` - Test",
            inline=True
        )
        
        embed.set_footer(text="Arsenal • DraftBot Style", icon_url=self.bot.user.avatar.url)
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="reglement_show", description="📋 Afficher le règlement avec interface complète")
    @app_commands.default_permissions(administrator=True)
    async def reglement_show(self, interaction: discord.Interaction):
        """Affiche le règlement avec toutes les fonctionnalités DraftBot"""
        
        config = await self.get_config(interaction.guild.id)
        if not config.get("enabled"):
            await interaction.response.send_message("❌ Configurez d'abord avec `/reglement_setup` !", ephemeral=True)
            return
        
        # Embed ultra-complet
        level_names = {"low": "🟢 Standard", "medium": "🟡 Renforcé", "high": "🟠 Strict", "extreme": "🔴 Maximum"}
        level = config.get("verification_level", "medium")
        
        embed = discord.Embed(
            title="📜 **RÈGLEMENT OFFICIEL DU SERVEUR**",
            description=f"**{interaction.guild.name}**\n\n"
                       f"**⚠️ ACCEPTATION OBLIGATOIRE ⚠️**\n\n"
                       f"🔒 **Sécurité:** {level_names[level]}\n"
                       f"⏰ **Limite:** {config.get('kick_delay', 300)}s\n"
                       f"📊 **{len(config.get('rules', []))} règles** à respecter",
            color=0xff0000,
            timestamp=datetime.now()
        )
        
        # Ajouter les règles
        if config.get("rules"):
            rules_text = ""
            for i, rule in enumerate(config["rules"][:8], 1):
                emoji = rule.get("emoji", "📝")
                title = rule.get("title", f"Règle {i}")
                desc = rule.get("desc", "Description")
                rules_text += f"{emoji} **{i}. {title}**\n{desc}\n\n"
            
            embed.add_field(
                name="📋 **RÈGLES À RESPECTER**",
                value=rules_text,
                inline=False
            )
        
        # Sanctions
        embed.add_field(
            name="⚖️ **SANCTIONS AUTOMATIQUES**",
            value="🟡 **1ère fois:** Avertissement\n"
                  "🟠 **2ème fois:** Timeout 1h\n"
                  "🔴 **3ème fois:** Timeout 24h\n"
                  "⚫ **Grave:** Expulsion immédiate",
            inline=True
        )
        
        # Aide
        embed.add_field(
            name="🆘 **AIDE ET SUPPORT**",
            value="• 📞 Contactez un **@Modérateur**\n"
                  "• 🎫 Ouvrez un **ticket**\n"
                  "• 📧 Salons d'**aide**\n"
                  "• ⏰ Soyez **patients** !",
            inline=True
        )
        
        # Stats serveur
        embed.add_field(
            name="📊 **STATISTIQUES**",
            value=f"👥 **Membres:** {len(interaction.guild.members)}\n"
                  f"🤖 **Bots:** {len([m for m in interaction.guild.members if m.bot])}\n"
                  f"📅 **Créé:** {interaction.guild.created_at.strftime('%d/%m/%Y')}\n"
                  f"🔐 **Niveau:** {interaction.guild.verification_level.name.title()}",
            inline=True
        )
        
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
        
        embed.set_footer(
            text=f"Arsenal • DraftBot Style • {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            icon_url=self.bot.user.avatar.url
        )
        
        # Envoyer dans le salon
        rules_channel = self.bot.get_channel(config["rules_channel"])
        if not rules_channel:
            await interaction.response.send_message("❌ Salon introuvable !", ephemeral=True)
            return
        
        view = ReglementDraftBotView()
        
        try:
            await rules_channel.send(embed=embed, view=view)
            
            confirm_embed = discord.Embed(
                title="✅ **RÈGLEMENT PUBLIÉ !**",
                description=f"**Interface DraftBot affichée dans {rules_channel.mention}**\n\n"
                           f"🎯 **Fonctionnalités actives:**\n"
                           f"• Auto-kick après {config.get('kick_delay', 300)}s\n"
                           f"• Interface à boutons moderne\n"
                           f"• Logs automatiques complets\n"
                           f"• Statistiques en temps réel\n"
                           f"• Messages privés intelligents",
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=confirm_embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @app_commands.command(name="reglement_stats", description="📊 Statistiques complètes du règlement")
    @app_commands.default_permissions(manage_guild=True)
    async def reglement_stats(self, interaction: discord.Interaction):
        """Statistiques style DraftBot"""
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Compter les acceptations
                async with db.execute("SELECT COUNT(*) FROM user_accepts WHERE guild_id = ?", (interaction.guild.id,)) as cursor:
                    total_accepts = (await cursor.fetchone())[0]
                
                # Compter les actions
                async with db.execute("SELECT COUNT(*) FROM action_logs WHERE guild_id = ? AND action = 'auto_kick'", (interaction.guild.id,)) as cursor:
                    total_kicks = (await cursor.fetchone())[0]
                
                # Acceptations récentes
                async with db.execute("""
                    SELECT COUNT(*) FROM user_accepts 
                    WHERE guild_id = ? AND DATE(accepted_at) = DATE('now')
                """, (interaction.guild.id,)) as cursor:
                    today_accepts = (await cursor.fetchone())[0]
            
            embed = discord.Embed(
                title="📊 **STATISTIQUES RÈGLEMENT**",
                description=f"**{interaction.guild.name}**\n\n"
                           f"Rapport complet du système de règlement",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="✅ **ACCEPTATIONS**",
                value=f"**Total:** {total_accepts}\n"
                      f"**Aujourd'hui:** {today_accepts}\n"
                      f"**Taux:** {(total_accepts/len(interaction.guild.members)*100):.1f}%",
                inline=True
            )
            
            embed.add_field(
                name="❌ **EXPULSIONS**",
                value=f"**Total:** {total_kicks}\n"
                      f"**Auto-kick:** {total_kicks}\n"
                      f"**Taux refus:** {(total_kicks/(total_accepts+total_kicks)*100) if (total_accepts+total_kicks) > 0 else 0:.1f}%",
                inline=True
            )
            
            embed.add_field(
                name="📈 **PERFORMANCE**",
                value=f"**Membres:** {len(interaction.guild.members)}\n"
                      f"**Vérifiés:** {total_accepts}\n"
                      f"**En attente:** {len(interaction.guild.members) - total_accepts}",
                inline=True
            )
            
            embed.set_footer(text="Arsenal • Statistiques DraftBot Style", icon_url=self.bot.user.avatar.url)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur stats: {e}", ephemeral=True)


class ReglementDraftBotView(discord.ui.View):
    """Interface à boutons style DraftBot ultra-complète"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="✅ J'ACCEPTE LE RÈGLEMENT", style=discord.ButtonStyle.success, custom_id="accept_rules", emoji="✅", row=0)
    async def accept_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton d'acceptation principal"""
        
        cog = interaction.client.get_cog("ReglementDraftBot")
        if not cog:
            await interaction.response.send_message("❌ Système indisponible !", ephemeral=True)
            return
        
        # Vérifier si déjà accepté
        if await cog.is_user_accepted(interaction.guild.id, interaction.user.id):
            embed = discord.Embed(
                title="ℹ️ **DÉJÀ ACCEPTÉ**",
                description=f"**{interaction.user.mention}**\n\n"
                           f"✅ **Vous avez déjà accepté le règlement !**\n"
                           f"🎉 **Bienvenue sur le serveur !**",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Enregistrer l'acceptation
        success = await cog.record_acceptance(interaction.guild.id, interaction.user.id, str(interaction.user))
        if not success:
            await interaction.response.send_message("❌ Erreur technique !", ephemeral=True)
            return
        
        # Donner le rôle membre
        config = await cog.get_config(interaction.guild.id)
        if config.get("member_role"):
            role = interaction.guild.get_role(config["member_role"])
            if role:
                try:
                    await interaction.user.add_roles(role, reason="Acceptation du règlement")
                except:
                    pass
        
        # Log de l'action
        await cog.log_action(interaction.guild.id, interaction.user.id, "accept", "Règlement accepté")
        
        # Confirmation complète
        embed = discord.Embed(
            title="🎉 **RÈGLEMENT ACCEPTÉ AVEC SUCCÈS !**",
            description=f"**Félicitations {interaction.user.mention} !**\n\n"
                       f"✅ **Vous êtes maintenant membre officiel !**\n"
                       f"🔓 **Accès complet au serveur déverrouillé**\n"
                       f"🎯 **Tous les salons sont maintenant accessibles**\n\n"
                       f"🤝 **Respectez les règles et amusez-vous bien !**",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🎁 **AVANTAGES DÉBLOQUÉS**",
            value="• 💬 **Accès aux salons** de discussion\n"
                  "• 🎮 **Participation aux événements**\n"
                  "• 🏆 **Système de niveaux** et récompenses\n"
                  "• 🎵 **Commandes musicales** disponibles",
            inline=True
        )
        
        embed.add_field(
            name="🆘 **BESOIN D'AIDE ?**",
            value="• 📞 Mentionnez un **@Modérateur**\n"
                  "• 🎫 Ouvrez un **ticket de support**\n"
                  "• 📚 Consultez le **#help** ou **#faq**\n"
                  "• 🤖 Utilisez les **commandes du bot**",
            inline=True
        )
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="Arsenal • Bienvenue officielle !", icon_url=interaction.client.user.avatar.url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="❌ JE REFUSE", style=discord.ButtonStyle.danger, custom_id="refuse_rules", emoji="❌", row=0)
    async def refuse_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton de refus avec confirmation"""
        
        embed = discord.Embed(
            title="⚠️ **CONFIRMATION DE REFUS**",
            description=f"**{interaction.user.mention}**\n\n"
                       f"❌ **Vous êtes sur le point de refuser le règlement.**\n"
                       f"⚠️ **Cela entraînera votre expulsion automatique.**\n\n"
                       f"🔄 **Êtes-vous certain de votre choix ?**",
            color=discord.Color.orange()
        )
        
        view = RefuseConfirmView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="📊 MES INFORMATIONS", style=discord.ButtonStyle.secondary, custom_id="my_info", emoji="📊", row=1)
    async def my_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Informations personnelles complètes"""
        
        cog = interaction.client.get_cog("ReglementDraftBot")
        if not cog:
            await interaction.response.send_message("❌ Système indisponible !", ephemeral=True)
            return
        
        is_accepted = await cog.is_user_accepted(interaction.guild.id, interaction.user.id)
        
        embed = discord.Embed(
            title="📊 **VOS INFORMATIONS COMPLÈTES**",
            description=f"**Profil de {interaction.user.mention}**\n\n"
                       f"Toutes les informations relatives à votre statut",
            color=discord.Color.green() if is_accepted else discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="✅ **STATUT RÈGLEMENT**",
            value=f"**État:** {'✅ Accepté' if is_accepted else '❌ Non accepté'}\n"
                  f"**Accès:** {'🔓 Complet' if is_accepted else '🔒 Restreint'}\n"
                  f"**Permissions:** {'👥 Membre' if is_accepted else '👤 Visiteur'}",
            inline=True
        )
        
        embed.add_field(
            name="📅 **DATES IMPORTANTES**",
            value=f"**Arrivée:** {interaction.user.joined_at.strftime('%d/%m/%Y à %H:%M') if interaction.user.joined_at else 'Inconnue'}\n"
                  f"**Compte créé:** {interaction.user.created_at.strftime('%d/%m/%Y')}\n"
                  f"**Ancienneté:** {(datetime.now() - interaction.user.created_at.replace(tzinfo=None)).days} jours",
            inline=True
        )
        
        embed.add_field(
            name="🔧 **DONNÉES TECHNIQUES**",
            value=f"**ID:** `{interaction.user.id}`\n"
                  f"**Tag:** {interaction.user.discriminator}\n"
                  f"**Bot:** {'🤖 Oui' if interaction.user.bot else '👤 Non'}",
            inline=True
        )
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="Arsenal • Informations Personnelles", icon_url=interaction.client.user.avatar.url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📋 RELIRE LE RÈGLEMENT", style=discord.ButtonStyle.secondary, custom_id="reread_rules", emoji="📋", row=1)
    async def reread_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Relire le règlement en détail"""
        
        cog = interaction.client.get_cog("ReglementDraftBot")
        if not cog:
            await interaction.response.send_message("❌ Système indisponible !", ephemeral=True)
            return
        
        config = await cog.get_config(interaction.guild.id)
        rules = config.get("rules", [])
        
        if not rules:
            await interaction.response.send_message("❌ Aucune règle configurée !", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📋 **RÈGLEMENT DÉTAILLÉ**",
            description=f"**{interaction.guild.name}** • Lecture complète\n\n"
                       f"📚 **{len(rules)} règles** à retenir absolument",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        for i, rule in enumerate(rules[:10], 1):
            emoji = rule.get("emoji", "📝")
            title = rule.get("title", f"Règle {i}")
            desc = rule.get("desc", "Description non définie")
            
            embed.add_field(
                name=f"{emoji} **{i}. {title}**",
                value=desc,
                inline=False
            )
        
        embed.set_footer(text="Arsenal • Règlement Complet", icon_url=interaction.client.user.avatar.url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🆘 AIDE ET SUPPORT", style=discord.ButtonStyle.secondary, custom_id="help_support", emoji="🆘", row=2)
    async def help_support(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Aide et support complet"""
        
        embed = discord.Embed(
            title="🆘 **AIDE ET SUPPORT COMPLET**",
            description=f"**{interaction.guild.name}** • Centre d'aide\n\n"
                       f"🎯 **Toutes les ressources pour vous aider**",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="👥 **CONTACTER L'ÉQUIPE**",
            value="• 🛡️ **@Modérateurs** - Questions générales\n"
                  "• 👑 **@Administrateurs** - Problèmes techniques\n"
                  "• 🤖 **@Support Bot** - Aide avec les commandes\n"
                  "• 📧 **Messages privés** - Questions privées",
            inline=False
        )
        
        embed.add_field(
            name="📚 **RESSOURCES UTILES**",
            value="• 📖 **#règles** - Règlement complet\n"
                  "• ❓ **#faq** - Questions fréquentes\n"
                  "• 🆘 **#aide** - Support communautaire\n"
                  "• 📢 **#annonces** - Informations importantes",
            inline=True
        )
        
        embed.add_field(
            name="🎫 **SYSTÈME DE TICKETS**",
            value="• 🎟️ **Ticket général** - Questions diverses\n"
                  "• 🔧 **Ticket technique** - Problèmes bot\n"
                  "• 🚨 **Ticket urgent** - Signalement\n"
                  "• 💡 **Ticket suggestion** - Idées",
            inline=True
        )
        
        embed.add_field(
            name="⚡ **RÉPONSE RAPIDE**",
            value="• 🏃‍♂️ **Temps moyen:** 5-15 minutes\n"
                  "• ⏰ **Horaires:** 24h/24, 7j/7\n"
                  "• 🌍 **Langues:** Français, Anglais\n"
                  "• 🎯 **Efficacité:** 98% de résolution",
            inline=False
        )
        
        embed.set_footer(text="Arsenal • Centre d'Aide", icon_url=interaction.client.user.avatar.url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class RefuseConfirmView(discord.ui.View):
    """Confirmation de refus avec double vérification"""
    
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.button(label="✅ OUI, JE CONFIRME LE REFUS", style=discord.ButtonStyle.danger, emoji="✅")
    async def confirm_refuse(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Confirmation définitive du refus"""
        
        embed = discord.Embed(
            title="❌ **RÈGLEMENT REFUSÉ DÉFINITIVEMENT**",
            description=f"**{interaction.user.mention}**\n\n"
                       f"❌ **Vous avez officiellement refusé le règlement.**\n"
                       f"⚠️ **Expulsion automatique dans 10 secondes.**\n\n"
                       f"🔄 **Pour revenir, vous devrez accepter les règles.**",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        
        embed.set_footer(text="Arsenal • Expulsion Automatique", icon_url=interaction.client.user.avatar.url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Log et auto-kick
        cog = interaction.client.get_cog("ReglementDraftBot")
        if cog:
            await cog.log_action(interaction.guild.id, interaction.user.id, "refuse", "Refus confirmé")
            
            await asyncio.sleep(10)
            try:
                await interaction.user.kick(reason="Refus confirmé du règlement")
            except:
                pass
    
    @discord.ui.button(label="🔄 NON, JE RECONSIDÈRE", style=discord.ButtonStyle.secondary, emoji="🔄")
    async def cancel_refuse(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Annulation du refus"""
        
        embed = discord.Embed(
            title="🔄 **REFUS ANNULÉ**",
            description=f"**{interaction.user.mention}**\n\n"
                       f"✅ **Sage décision !**\n"
                       f"📋 **Prenez le temps de relire le règlement.**\n"
                       f"🎯 **Acceptez-le quand vous êtes prêt !**",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    """Charge le module ReglementDraftBot"""
    await bot.add_cog(ReglementSystem(bot))
    print("🚀 [OK] ReglementDraftBot chargé - Interface ultra-complète style DraftBot !")
