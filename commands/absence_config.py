#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 ARSENAL ABSENCE CONFIG - CONFIGURATION SYSTÈME D'ABSENCE
Interface complète pour configurer le système de tickets d'absence
Par xerox3elite - Arsenal V4.5.2 ULTIMATE
"""

import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional

class AbsenceConfigModal(discord.ui.Modal):
    """Modal pour configurer les paramètres d'absence"""
    def __init__(self, bot, config_type: str, current_config: Dict):
        self.bot = bot
        self.config_type = config_type
        self.current_config = current_config
        
        titles = {
            "channels": "🏷️ Configuration des Canaux",
            "roles": "👥 Configuration des Rôles", 
            "settings": "⚙️ Paramètres Généraux"
        }
        
        super().__init__(title=titles.get(config_type, "Configuration"))
        
        # Ajouter champs selon le type
        if config_type == "channels":
            self.setup_channel_fields()
        elif config_type == "roles":
            self.setup_role_fields()
        elif config_type == "settings":
            self.setup_settings_fields()
    
    def setup_channel_fields(self):
        """Configuration des canaux"""
        self.category_id = discord.ui.TextInput(
            label="ID Catégorie Tickets",
            placeholder="ID de la catégorie où créer les tickets d'absence",
            default=str(self.current_config.get("ticket_category_id", "")),
            required=False,
            max_length=25
        )
        self.add_item(self.category_id)
        
        self.log_channel_id = discord.ui.TextInput(
            label="ID Canal Logs",
            placeholder="ID du canal pour les logs d'absence",
            default=str(self.current_config.get("log_channel_id", "")),
            required=False,
            max_length=25
        )
        self.add_item(self.log_channel_id)
    
    def setup_role_fields(self):
        """Configuration des rôles"""
        self.absence_role_id = discord.ui.TextInput(
            label="ID Rôle Absence",
            placeholder="ID du rôle à attribuer pendant l'absence",
            default=str(self.current_config.get("absence_role_id", "")),
            required=False,
            max_length=25
        )
        self.add_item(self.absence_role_id)
        
        self.moderator_role_ids = discord.ui.TextInput(
            label="IDs Rôles Modérateurs",
            placeholder="IDs des rôles modérateurs (séparés par des virgules)",
            default=",".join(map(str, self.current_config.get("moderator_role_ids", []))),
            required=False,
            max_length=200,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.moderator_role_ids)
    
    def setup_settings_fields(self):
        """Configuration des paramètres généraux"""
        self.max_duration_days = discord.ui.TextInput(
            label="Durée Maximum (jours)",
            placeholder="Nombre maximum de jours d'absence autorisés",
            default=str(self.current_config.get("max_duration_days", 365)),
            required=False,
            max_length=4
        )
        self.add_item(self.max_duration_days)
        
        self.auto_approve = discord.ui.TextInput(
            label="Approbation Auto (true/false)",
            placeholder="Approuver automatiquement les tickets",
            default=str(self.current_config.get("auto_approve", False)).lower(),
            required=False,
            max_length=5
        )
        self.add_item(self.auto_approve)
        
        self.notification_days = discord.ui.TextInput(
            label="Notification Retour (jours)",
            placeholder="Notifier X jours avant la fin d'absence",
            default=str(self.current_config.get("notification_days_before", 1)),
            required=False,
            max_length=2
        )
        self.add_item(self.notification_days)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            # Récupérer config actuelle
            config = await self.load_guild_config(interaction.guild.id)
            
            # Mettre à jour selon le type
            if self.config_type == "channels":
                await self.update_channel_config(config, interaction.guild)
            elif self.config_type == "roles":
                await self.update_role_config(config, interaction.guild)
            elif self.config_type == "settings":
                await self.update_settings_config(config)
            
            # Sauvegarder
            await self.save_guild_config(interaction.guild.id, config)
            
            # Confirmation
            embed = discord.Embed(
                title="✅ Configuration Mise à Jour",
                description=f"La configuration **{self.config_type}** a été mise à jour avec succès !",
                color=0x00ff00,
                timestamp=datetime.now(timezone.utc)
            )
            
            await interaction.edit_original_response(embed=embed)
            
        except Exception as e:
            print(f"❌ [ABSENCE CONFIG] Erreur sauvegarde: {e}")
            await interaction.edit_original_response(content=f"❌ Erreur lors de la sauvegarde: {str(e)}")
    
    async def update_channel_config(self, config: Dict, guild: discord.Guild):
        """Met à jour la config des canaux"""
        if self.category_id.value.strip():
            try:
                category_id = int(self.category_id.value.strip())
                category = guild.get_channel(category_id)
                if category and isinstance(category, discord.CategoryChannel):
                    config["ticket_category_id"] = category_id
                else:
                    raise ValueError("Catégorie introuvable")
            except ValueError:
                raise ValueError("ID catégorie invalide")
        
        if self.log_channel_id.value.strip():
            try:
                log_id = int(self.log_channel_id.value.strip())
                log_channel = guild.get_channel(log_id)
                if log_channel and isinstance(log_channel, discord.TextChannel):
                    config["log_channel_id"] = log_id
                else:
                    raise ValueError("Canal de logs introuvable")
            except ValueError:
                raise ValueError("ID canal de logs invalide")
    
    async def update_role_config(self, config: Dict, guild: discord.Guild):
        """Met à jour la config des rôles"""
        if self.absence_role_id.value.strip():
            try:
                role_id = int(self.absence_role_id.value.strip())
                role = guild.get_role(role_id)
                if role:
                    config["absence_role_id"] = role_id
                else:
                    raise ValueError("Rôle d'absence introuvable")
            except ValueError:
                raise ValueError("ID rôle d'absence invalide")
        
        if self.moderator_role_ids.value.strip():
            try:
                role_ids = []
                for role_id_str in self.moderator_role_ids.value.split(","):
                    role_id = int(role_id_str.strip())
                    role = guild.get_role(role_id)
                    if role:
                        role_ids.append(role_id)
                    else:
                        print(f"⚠️ Rôle {role_id} introuvable")
                
                config["moderator_role_ids"] = role_ids
            except ValueError:
                raise ValueError("IDs rôles modérateurs invalides")
    
    async def update_settings_config(self, config: Dict):
        """Met à jour les paramètres généraux"""
        if self.max_duration_days.value.strip():
            try:
                max_days = int(self.max_duration_days.value.strip())
                if 1 <= max_days <= 365:
                    config["max_duration_days"] = max_days
                else:
                    raise ValueError("Durée doit être entre 1 et 365 jours")
            except ValueError:
                raise ValueError("Durée maximum invalide")
        
        if self.auto_approve.value.strip().lower() in ["true", "false"]:
            config["auto_approve"] = self.auto_approve.value.strip().lower() == "true"
        
        if self.notification_days.value.strip():
            try:
                notif_days = int(self.notification_days.value.strip())
                if 0 <= notif_days <= 30:
                    config["notification_days_before"] = notif_days
                else:
                    raise ValueError("Notification doit être entre 0 et 30 jours")
            except ValueError:
                raise ValueError("Jours de notification invalides")
    
    async def load_guild_config(self, guild_id: int) -> Dict:
        """Charge la config du serveur"""
        try:
            async with aiosqlite.connect("data/absence_config.db") as db:
                cursor = await db.execute(
                    "SELECT config FROM guild_configs WHERE guild_id = ?",
                    (guild_id,)
                )
                result = await cursor.fetchone()
                if result:
                    return json.loads(result[0])
        except Exception as e:
            print(f"❌ [ABSENCE CONFIG] Erreur chargement config: {e}")
        
        # Config par défaut
        return {
            "ticket_category_id": None,
            "log_channel_id": None,
            "absence_role_id": None,
            "moderator_role_ids": [],
            "max_duration_days": 365,
            "auto_approve": False,
            "notification_days_before": 1
        }
    
    async def save_guild_config(self, guild_id: int, config: Dict):
        """Sauvegarde la config du serveur"""
        async with aiosqlite.connect("data/absence_config.db") as db:
            await db.execute("""
                INSERT OR REPLACE INTO guild_configs (guild_id, config, updated_at)
                VALUES (?, ?, ?)
            """, (guild_id, json.dumps(config), datetime.now(timezone.utc).isoformat()))
            await db.commit()

class AbsenceConfigView(discord.ui.View):
    """Vue principale de configuration d'absence"""
    def __init__(self, bot, user_id: int, current_config: Dict):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_config = current_config
    
    @discord.ui.button(label="🏷️ Canaux", style=discord.ButtonStyle.primary, emoji="🏷️")
    async def config_channels(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut utiliser ce bouton.", ephemeral=True)
            return
        
        modal = AbsenceConfigModal(self.bot, "channels", self.current_config)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="👥 Rôles", style=discord.ButtonStyle.secondary, emoji="👥")
    async def config_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut utiliser ce bouton.", ephemeral=True)
            return
        
        modal = AbsenceConfigModal(self.bot, "roles", self.current_config)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="⚙️ Paramètres", style=discord.ButtonStyle.success, emoji="⚙️")
    async def config_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut utiliser ce bouton.", ephemeral=True)
            return
        
        modal = AbsenceConfigModal(self.bot, "settings", self.current_config)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📊 Voir Config", style=discord.ButtonStyle.secondary, emoji="📊")
    async def view_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut utiliser ce bouton.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Recharger config actuelle
        config = await self.load_current_config(interaction.guild.id)
        
        embed = discord.Embed(
            title="📊 Configuration Actuelle",
            description="**Voici la configuration actuelle du système d'absence**",
            color=0x3498db,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Canaux
        channels_info = ""
        if config.get("ticket_category_id"):
            category = interaction.guild.get_channel(config["ticket_category_id"])
            channels_info += f"**Catégorie:** {category.name if category else 'Introuvable'}\n"
        else:
            channels_info += "**Catégorie:** Non configurée\n"
        
        if config.get("log_channel_id"):
            log_channel = interaction.guild.get_channel(config["log_channel_id"])
            channels_info += f"**Logs:** {log_channel.mention if log_channel else 'Introuvable'}\n"
        else:
            channels_info += "**Logs:** Non configuré\n"
        
        embed.add_field(name="🏷️ **Canaux**", value=channels_info, inline=False)
        
        # Rôles
        roles_info = ""
        if config.get("absence_role_id"):
            absence_role = interaction.guild.get_role(config["absence_role_id"])
            roles_info += f"**Absence:** {absence_role.mention if absence_role else 'Introuvable'}\n"
        else:
            roles_info += "**Absence:** Non configuré\n"
        
        mod_roles = []
        for role_id in config.get("moderator_role_ids", []):
            role = interaction.guild.get_role(role_id)
            if role:
                mod_roles.append(role.mention)
        
        roles_info += f"**Modérateurs:** {', '.join(mod_roles) if mod_roles else 'Aucun'}\n"
        
        embed.add_field(name="👥 **Rôles**", value=roles_info, inline=False)
        
        # Paramètres
        settings_info = f"**Durée max:** {config.get('max_duration_days', 365)} jours\n"
        settings_info += f"**Auto-approbation:** {'Oui' if config.get('auto_approve', False) else 'Non'}\n"
        settings_info += f"**Notification:** {config.get('notification_days_before', 1)} jour(s) avant\n"
        
        embed.add_field(name="⚙️ **Paramètres**", value=settings_info, inline=False)
        
        embed.set_footer(text="Utilisez les boutons pour modifier la configuration")
        
        await interaction.edit_original_response(embed=embed)
    
    async def load_current_config(self, guild_id: int) -> Dict:
        """Recharge la config actuelle"""
        try:
            async with aiosqlite.connect("data/absence_config.db") as db:
                cursor = await db.execute(
                    "SELECT config FROM guild_configs WHERE guild_id = ?",
                    (guild_id,)
                )
                result = await cursor.fetchone()
                if result:
                    return json.loads(result[0])
        except:
            pass
        
        return {
            "ticket_category_id": None,
            "log_channel_id": None,
            "absence_role_id": None,
            "moderator_role_ids": [],
            "max_duration_days": 365,
            "auto_approve": False,
            "notification_days_before": 1
        }

class AbsenceStatsView(discord.ui.View):
    """Vue des statistiques d'absence"""
    def __init__(self, bot, user_id: int, guild_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.guild_id = guild_id
    
    @discord.ui.button(label="📈 Stats Générales", style=discord.ButtonStyle.primary, emoji="📈")
    async def general_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut utiliser ce bouton.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            async with aiosqlite.connect("data/absence_tickets.db") as db:
                # Statistiques générales
                cursor = await db.execute(
                    "SELECT status, COUNT(*) FROM tickets WHERE guild_id = ? GROUP BY status",
                    (self.guild_id,)
                )
                stats = await cursor.fetchall()
                
                # Tickets actifs
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM tickets WHERE guild_id = ? AND status = 'active'",
                    (self.guild_id,)
                )
                active_count = await cursor.fetchone()
                
                # Tickets ce mois
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM tickets WHERE guild_id = ? AND created_at >= date('now', '-30 days')",
                    (self.guild_id,)
                )
                month_count = await cursor.fetchone()
            
            embed = discord.Embed(
                title="📈 Statistiques Générales",
                description="**Aperçu complet du système d'absence**",
                color=0x3498db,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Répartition par statut
            stats_text = ""
            total_tickets = 0
            for status, count in stats:
                status_emoji = {
                    'active': '🟢',
                    'approved': '✅',
                    'rejected': '❌',
                    'closed': '📝',
                    'expired': '⏰'
                }
                stats_text += f"{status_emoji.get(status, '📊')} **{status.title()}:** {count}\n"
                total_tickets += count
            
            if not stats_text:
                stats_text = "Aucun ticket créé"
            
            embed.add_field(name="📊 **Répartition des Tickets**", value=stats_text, inline=True)
            
            # Résumé
            summary = f"**Total:** {total_tickets} tickets\n"
            summary += f"**Actifs:** {active_count[0] if active_count else 0}\n"
            summary += f"**Ce mois:** {month_count[0] if month_count else 0}"
            
            embed.add_field(name="📋 **Résumé**", value=summary, inline=True)
            
            await interaction.edit_original_response(embed=embed)
            
        except Exception as e:
            print(f"❌ [ABSENCE STATS] Erreur: {e}")
            await interaction.edit_original_response(content="❌ Erreur lors du chargement des statistiques")
    
    @discord.ui.button(label="👤 Stats Utilisateurs", style=discord.ButtonStyle.secondary, emoji="👤")
    async def user_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut utiliser ce bouton.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            async with aiosqlite.connect("data/absence_tickets.db") as db:
                # Top utilisateurs
                cursor = await db.execute("""
                    SELECT user_id, COUNT(*) as ticket_count 
                    FROM tickets 
                    WHERE guild_id = ? 
                    GROUP BY user_id 
                    ORDER BY ticket_count DESC 
                    LIMIT 10
                """, (self.guild_id,))
                top_users = await cursor.fetchall()
            
            embed = discord.Embed(
                title="👤 Statistiques Utilisateurs",
                description="**Top 10 des utilisateurs par nombre de tickets**",
                color=0xe74c3c,
                timestamp=datetime.now(timezone.utc)
            )
            
            if top_users:
                users_text = ""
                for i, (user_id, count) in enumerate(top_users, 1):
                    user = interaction.guild.get_member(user_id)
                    user_name = user.display_name if user else f"Utilisateur {user_id}"
                    users_text += f"**{i}.** {user_name}: {count} ticket(s)\n"
                
                embed.add_field(name="🏆 **Classement**", value=users_text, inline=False)
            else:
                embed.add_field(name="📋 **Aucune donnée**", value="Aucun ticket créé pour le moment", inline=False)
            
            await interaction.edit_original_response(embed=embed)
            
        except Exception as e:
            print(f"❌ [ABSENCE USER STATS] Erreur: {e}")
            await interaction.edit_original_response(content="❌ Erreur lors du chargement des statistiques utilisateurs")

async def setup_absence_config_db():
    """Initialise la base de données de configuration"""
    async with aiosqlite.connect("data/absence_config.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_configs (
                guild_id INTEGER PRIMARY KEY,
                config TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        await db.commit()
        print("✅ [ABSENCE CONFIG] Base de données initialisée")
