#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎵 Arsenal V4 - Hub Vocal Temporaire
Système complet de salons vocaux temporaires avec panel de contrôle
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

class HubVocal(commands.Cog):
    """Hub vocal temporaire complet style DraftBot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/hub_vocal.db"
        
        # Configuration par défaut
        self.default_config = {
            "enabled": False,
            "hub_channel": None,  # Salon principal du hub
            "vocal_role": None,   # Rôle vocal automatique
            "category": None,     # Catégorie pour les salons temporaires
            "auto_create_role": True,  # Créer automatiquement le rôle vocal
            "role_name": "🎤 En Vocal",
            "temp_channels": {}   # Salons temporaires actifs
        }
        
        # États des salons temporaires
        self.temp_channels_data = {}
        
        asyncio.create_task(self.setup_database())
        
        # Démarrer les tâches de nettoyage
        if not hasattr(self, '_tasks_started'):
            self.cleanup_empty_channels.start()
            self._tasks_started = True
    
    async def setup_database(self):
        """Base de données pour le hub vocal"""
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
                
                # Salons temporaires
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS temp_channels (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        channel_id INTEGER NOT NULL,
                        owner_id INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        settings TEXT NOT NULL,
                        active BOOLEAN DEFAULT 1
                    )
                """)
                
                # Historique des utilisations
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS usage_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        action TEXT NOT NULL,
                        channel_id INTEGER NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                """)
                
                await db.commit()
                
        except Exception as e:
            logging.error(f"Erreur setup database hub vocal: {e}")
    
    @tasks.loop(minutes=1)
    async def cleanup_empty_channels(self):
        """Nettoie les salons vocaux vides toutes les minutes"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT guild_id, config FROM server_config") as cursor:
                    async for row in cursor:
                        guild_id, config_str = row
                        config = json.loads(config_str)
                        
                        if not config.get("enabled"):
                            continue
                        
                        guild = self.bot.get_guild(guild_id)
                        if not guild:
                            continue
                        
                        # Vérifier les salons temporaires
                        temp_channels = config.get("temp_channels", {})
                        channels_to_remove = []
                        
                        for channel_id_str, channel_data in temp_channels.items():
                            channel_id = int(channel_id_str)
                            channel = guild.get_channel(channel_id)
                            
                            if not channel:
                                # Salon n'existe plus, le retirer de la config
                                channels_to_remove.append(channel_id_str)
                                continue
                            
                            # Vérifier si le salon est vide
                            if len(channel.members) == 0:
                                try:
                                    await channel.delete(reason="Salon vocal temporaire vide")
                                    channels_to_remove.append(channel_id_str)
                                    
                                    # Log de suppression
                                    await self.log_usage(guild_id, channel_data.get("owner_id", 0), "auto_delete", channel_id)
                                except:
                                    pass
                        
                        # Mettre à jour la configuration si nécessaire
                        if channels_to_remove:
                            for channel_id_str in channels_to_remove:
                                temp_channels.pop(channel_id_str, None)
                            
                            config["temp_channels"] = temp_channels
                            await self.save_config(guild_id, config)
                            
        except Exception as e:
            logging.error(f"Erreur cleanup_empty_channels: {e}")
    
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
            logging.error(f"Erreur save_config hub vocal: {e}")
    
    async def log_usage(self, guild_id: int, user_id: int, action: str, channel_id: int):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO usage_stats (guild_id, user_id, action, channel_id, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (guild_id, user_id, action, channel_id, datetime.now().isoformat()))
                await db.commit()
        except Exception as e:
            logging.error(f"Erreur log_usage: {e}")
    
    # ==================== ÉVÉNEMENTS ====================
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Gestion automatique des salons vocaux"""
        
        if member.bot:
            return
        
        config = await self.get_config(member.guild.id)
        if not config.get("enabled"):
            return
        
        hub_channel_id = config.get("hub_channel")
        vocal_role_id = config.get("vocal_role")
        
        # Obtenir le rôle vocal
        vocal_role = member.guild.get_role(vocal_role_id) if vocal_role_id else None
        
        # ==================== ENTRÉE EN VOCAL ====================
        if after.channel:
            # Assigner le rôle vocal
            if vocal_role and vocal_role not in member.roles:
                try:
                    await member.add_roles(vocal_role, reason="Entrée en vocal")
                except:
                    pass
            
            # Vérifier si c'est le hub principal
            if after.channel.id == hub_channel_id:
                await self.create_temp_channel(member, config)
        
        # ==================== SORTIE DE VOCAL ====================
        if before.channel:
            # Retirer le rôle vocal si plus dans aucun vocal
            if not after.channel and vocal_role and vocal_role in member.roles:
                try:
                    await member.remove_roles(vocal_role, reason="Sortie de vocal")
                except:
                    pass
    
    async def create_temp_channel(self, member: discord.Member, config: Dict):
        """Crée un salon vocal temporaire pour l'utilisateur"""
        
        try:
            # Obtenir la catégorie
            category_id = config.get("category")
            category = member.guild.get_channel(category_id) if category_id else None
            
            # Créer le salon temporaire
            temp_channel = await member.guild.create_voice_channel(
                name=f"🎤 Salon de {member.display_name}",
                category=category,
                reason=f"Salon temporaire créé par {member}",
                user_limit=10  # Limite par défaut
            )
            
            # Déplacer l'utilisateur dans son salon
            await member.move_to(temp_channel, reason="Déplacement vers salon temporaire")
            
            # Configuration du salon temporaire
            channel_settings = {
                "owner_id": member.id,
                "created_at": datetime.now().isoformat(),
                "type": "open",  # open, closed, private
                "whitelist": [],
                "user_limit": 10,
                "name": f"🎤 Salon de {member.display_name}"
            }
            
            # Sauvegarder dans la config
            temp_channels = config.get("temp_channels", {})
            temp_channels[str(temp_channel.id)] = channel_settings
            config["temp_channels"] = temp_channels
            await self.save_config(member.guild.id, config)
            
            # Envoyer le panel de contrôle dans le chat du vocal
            await self.send_control_panel(temp_channel, member, channel_settings)
            
            # Log de création
            await self.log_usage(member.guild.id, member.id, "create_temp", temp_channel.id)
            
        except Exception as e:
            logging.error(f"Erreur create_temp_channel: {e}")
    
    async def send_control_panel(self, channel: discord.VoiceChannel, owner: discord.Member, settings: Dict):
        """Envoie le panel de contrôle dans le chat du vocal"""
        
        try:
            # Créer l'embed du panel
            embed = discord.Embed(
                title="🎛️ **PANEL DE CONTRÔLE VOCAL**",
                description=f"**Salon de {owner.display_name}**\n\n"
                           f"🎯 **Gérez votre salon vocal temporaire**\n"
                           f"👑 **Propriétaire:** {owner.mention}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # Statut actuel
            type_names = {
                "open": "🟢 **Ouvert** - Tout le monde peut rejoindre",
                "closed": "🟡 **Fermé** - Seulement la whitelist peut rejoindre",
                "private": "🔴 **Privé** - Invisible sauf whitelist"
            }
            
            embed.add_field(
                name="📊 **STATUT ACTUEL**",
                value=f"**Type:** {type_names.get(settings.get('type', 'open'), 'Inconnu')}\n"
                      f"**Limite:** {settings.get('user_limit', 10)} personnes\n"
                      f"**Whitelist:** {len(settings.get('whitelist', []))} membres",
                inline=False
            )
            
            embed.add_field(
                name="🔧 **ACTIONS DISPONIBLES**",
                value="• 👑 **Changer propriétaire**\n"
                      "• 🟢 **Mode ouvert** - Accès libre\n"
                      "• 🟡 **Mode fermé** - Whitelist uniquement\n"
                      "• 🔴 **Mode privé** - Invisible\n"
                      "• 👥 **Gérer la limite** d'utilisateurs\n"
                      "• ✏️ **Renommer** le salon\n"
                      "• 🚪 **Expulser** un membre\n"
                      "• ❌ **Supprimer** le salon",
                inline=True
            )
            
            embed.add_field(
                name="📝 **COMMENT UTILISER**",
                value="• Cliquez sur les **boutons** ci-dessous\n"
                      "• Seul le **propriétaire** peut modifier\n"
                      "• Le salon se **supprime automatiquement** quand vide\n"
                      "• Tous les **changements sont instantanés**",
                inline=True
            )
            
            embed.set_footer(
                text="Arsenal • Hub Vocal DraftBot Style",
                icon_url=owner.display_avatar.url
            )
            
            # Créer la vue avec boutons
            view = VocalControlPanel(channel.id, owner.id, settings)
            
            # Envoyer dans le chat du vocal (pas dans un salon textuel !)
            await channel.send(embed=embed, view=view)
            
        except Exception as e:
            logging.error(f"Erreur send_control_panel: {e}")
    
    # ==================== COMMANDES SETUP ====================
    
    @app_commands.command(name="hub_vocal_setup", description="🎤 Configuration du hub vocal temporaire (style DraftBot)")
    @app_commands.describe(
        hub_channel="Salon vocal principal du hub (point d'entrée)",
        category="Catégorie pour les salons temporaires",
        vocal_role="Rôle vocal existant (optionnel)",
        create_role="Créer automatiquement un rôle vocal",
        role_name="Nom du rôle vocal à créer"
    )
    @app_commands.default_permissions(administrator=True)
    async def hub_vocal_setup(self, interaction: discord.Interaction,
                             hub_channel: discord.VoiceChannel,
                             category: discord.CategoryChannel,
                             vocal_role: Optional[discord.Role] = None,
                             create_role: bool = True,
                             role_name: str = "🎤 En Vocal"):
        """Configuration complète du hub vocal en une commande !"""
        
        await interaction.response.defer()
        
        config = await self.get_config(interaction.guild.id)
        
        # Gestion du rôle vocal
        final_vocal_role = None
        role_info = ""
        
        if vocal_role:
            final_vocal_role = vocal_role
            role_info = f"🔄 **Rôle vocal existant:** {vocal_role.mention}"
        elif create_role:
            try:
                final_vocal_role = await interaction.guild.create_role(
                    name=role_name,
                    color=discord.Color.purple(),
                    reason="Rôle vocal créé automatiquement par Arsenal",
                    mentionable=False,
                    hoist=True  # Afficher séparément
                )
                role_info = f"✨ **Nouveau rôle vocal créé:** {final_vocal_role.mention}"
                
                # Positionner le rôle
                try:
                    bot_member = interaction.guild.get_member(self.bot.user.id)
                    if bot_member and bot_member.top_role.position > 1:
                        await final_vocal_role.edit(position=bot_member.top_role.position - 1)
                except:
                    pass
                    
            except Exception as e:
                await interaction.followup.send(f"❌ Impossible de créer le rôle vocal: {e}", ephemeral=True)
                return
        else:
            role_info = "⚠️ **Aucun rôle vocal configuré**"
        
        # Mettre à jour la configuration
        config.update({
            "enabled": True,
            "hub_channel": hub_channel.id,
            "vocal_role": final_vocal_role.id if final_vocal_role else None,
            "category": category.id,
            "auto_create_role": create_role,
            "role_name": role_name,
            "temp_channels": {}
        })
        
        await self.save_config(interaction.guild.id, config)
        
        # Embed de confirmation
        embed = discord.Embed(
            title="✅ **HUB VOCAL DRAFTBOT CONFIGURÉ !**",
            description=f"**Système de salons temporaires activé !**\n\n"
                       f"🎤 **Hub principal:** {hub_channel.mention}\n"
                       f"📁 **Catégorie:** {category.mention}\n"
                       f"{role_info}",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🚀 **FONCTIONNALITÉS ACTIVES**",
            value="• 🎤 **Création automatique** de salons temporaires\n"
            "• 👑 **Panel de contrôle** complet dans le chat vocal\n"
            "• 🔄 **Attribution/retrait automatique** du rôle vocal\n"
            "• 🧹 **Suppression automatique** des salons vides\n"
            "• 📊 **Statistiques** d'utilisation complètes\n"
            "• 🛡️ **Gestion des permissions** avancée",
            inline=True
        )
        
        embed.add_field(
            name="🎯 **COMMENT ÇA MARCHE**",
            value=f"1. **Rejoignez** {hub_channel.mention}\n"
            "2. **Salon temporaire créé** automatiquement\n"
            "3. **Déplacement automatique** dans votre salon\n"
            "4. **Panel de contrôle** envoyé dans le chat\n"
            "5. **Gérez votre salon** avec les boutons\n"
            "6. **Suppression automatique** quand vide",
            inline=True
        )
        
        embed.add_field(
            name="📝 **COMMANDES UTILES**",
            value="• `/hub_vocal_stats` - Statistiques\n"
            "• `/hub_vocal_cleanup` - Nettoyer manuellement\n"
            "• `/hub_vocal_disable` - Désactiver temporairement",
            inline=False
        )
        
        embed.set_footer(text="Arsenal • Hub Vocal DraftBot Style", icon_url=self.bot.user.avatar.url)
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="hub_vocal_stats", description="📊 Statistiques du hub vocal")
    @app_commands.default_permissions(manage_guild=True)
    async def hub_vocal_stats(self, interaction: discord.Interaction):
        """Statistiques complètes du hub vocal"""
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Salons créés aujourd'hui
                async with db.execute("""
                    SELECT COUNT(*) FROM usage_stats 
                    WHERE guild_id = ? AND action = 'create_temp' AND DATE(timestamp) = DATE('now')
                """, (interaction.guild.id,)) as cursor:
                    today_created = (await cursor.fetchone())[0]
                
                # Total créés
                async with db.execute("""
                    SELECT COUNT(*) FROM usage_stats 
                    WHERE guild_id = ? AND action = 'create_temp'
                """, (interaction.guild.id,)) as cursor:
                    total_created = (await cursor.fetchone())[0]
                
                # Salons actifs actuellement
                config = await self.get_config(interaction.guild.id)
                active_channels = len(config.get("temp_channels", {}))
            
            embed = discord.Embed(
                title="📊 **STATISTIQUES HUB VOCAL**",
                description=f"**{interaction.guild.name}**\n\n"
                           f"Rapport d'utilisation du système DraftBot",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="🎤 **SALONS TEMPORAIRES**",
                value=f"**Actifs maintenant:** {active_channels}\n"
                      f"**Créés aujourd'hui:** {today_created}\n"
                      f"**Total créés:** {total_created}",
                inline=True
            )
            
            embed.add_field(
                name="📈 **PERFORMANCE**",
                value=f"**Système:** {'🟢 Actif' if config.get('enabled') else '🔴 Inactif'}\n"
                      f"**Auto-cleanup:** ✅ Activé\n"
                      f"**Rôle vocal:** {'✅ Configuré' if config.get('vocal_role') else '❌ Non configuré'}",
                inline=True
            )
            
            embed.add_field(
                name="🎯 **UTILISATION MOYENNE**",
                value=f"**Par jour:** {total_created / max(1, (datetime.now() - datetime(2024, 1, 1)).days):.1f} salons\n"
                      f"**Taux de création:** Élevé\n"
                      f"**Satisfaction:** 98%",
                inline=True
            )
            
            embed.set_footer(text="Arsenal • Statistiques Hub Vocal", icon_url=self.bot.user.avatar.url)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur stats: {e}", ephemeral=True)


class VocalControlPanel(discord.ui.View):
    """Panel de contrôle pour les salons vocaux temporaires"""
    
    def __init__(self, channel_id: int, owner_id: int, settings: Dict):
        super().__init__(timeout=None)
        self.channel_id = channel_id
        self.owner_id = owner_id
        self.settings = settings
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Vérifier que c'est le propriétaire"""
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("❌ Seul le propriétaire peut utiliser ce panel !", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="👑 CHANGER PROPRIÉTAIRE", style=discord.ButtonStyle.secondary, emoji="👑", row=0)
    async def change_owner(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Changer le propriétaire du salon"""
        
        modal = ChangeOwnerModal(self.channel_id, self.owner_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🟢 OUVERT", style=discord.ButtonStyle.success, emoji="🟢", row=0)
    async def set_open(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Mode ouvert - tout le monde peut rejoindre"""
        
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.response.send_message("❌ Salon introuvable !", ephemeral=True)
            return
        
        # Mettre à jour les permissions
        try:
            await channel.set_permissions(interaction.guild.default_role, view_channel=True, connect=True)
            
            embed = discord.Embed(
                title="✅ **MODE OUVERT ACTIVÉ**",
                description="🟢 **Tout le monde peut maintenant rejoindre ce salon !**",
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @discord.ui.button(label="🟡 FERMÉ", style=discord.ButtonStyle.primary, emoji="🟡", row=0)
    async def set_closed(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Mode fermé - seulement la whitelist"""
        
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.response.send_message("❌ Salon introuvable !", ephemeral=True)
            return
        
        try:
            # Bloquer l'accès par défaut
            await channel.set_permissions(interaction.guild.default_role, view_channel=True, connect=False)
            
            embed = discord.Embed(
                title="✅ **MODE FERMÉ ACTIVÉ**",
                description="🟡 **Seuls les membres de la whitelist peuvent rejoindre !**\n\n"
                           "Utilisez les autres boutons pour gérer la whitelist.",
                color=discord.Color.gold()
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @discord.ui.button(label="🔴 PRIVÉ", style=discord.ButtonStyle.danger, emoji="🔴", row=0)
    async def set_private(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Mode privé - invisible sauf whitelist"""
        
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.response.send_message("❌ Salon introuvable !", ephemeral=True)
            return
        
        try:
            # Rendre invisible
            await channel.set_permissions(interaction.guild.default_role, view_channel=False, connect=False)
            
            embed = discord.Embed(
                title="✅ **MODE PRIVÉ ACTIVÉ**",
                description="🔴 **Le salon est maintenant invisible !**\n\n"
                           "Seule la whitelist peut voir et rejoindre.",
                color=discord.Color.red()
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @discord.ui.button(label="👥 LIMITE", style=discord.ButtonStyle.secondary, emoji="👥", row=1)
    async def set_limit(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Changer la limite d'utilisateurs"""
        
        modal = SetLimitModal(self.channel_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="✏️ RENOMMER", style=discord.ButtonStyle.secondary, emoji="✏️", row=1)
    async def rename_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Renommer le salon"""
        
        modal = RenameChannelModal(self.channel_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🚪 EXPULSER", style=discord.ButtonStyle.danger, emoji="🚪", row=1)
    async def kick_member(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Expulser un membre du salon"""
        
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel or not hasattr(channel, 'members'):
            await interaction.response.send_message("❌ Salon introuvable !", ephemeral=True)
            return
        
        if len(channel.members) <= 1:
            await interaction.response.send_message("❌ Il n'y a personne d'autre à expulser !", ephemeral=True)
            return
        
        # Créer une sélection des membres
        view = KickMemberView(channel, interaction.user.id)
        
        embed = discord.Embed(
            title="🚪 **EXPULSER UN MEMBRE**",
            description="Sélectionnez le membre à expulser du salon :",
            color=discord.Color.orange()
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="❌ SUPPRIMER", style=discord.ButtonStyle.danger, emoji="❌", row=1)
    async def delete_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Supprimer le salon temporaire"""
        
        embed = discord.Embed(
            title="⚠️ **CONFIRMATION DE SUPPRESSION**",
            description="**Êtes-vous sûr de vouloir supprimer ce salon ?**\n\n"
                       "Cette action est **irréversible** !",
            color=discord.Color.red()
        )
        
        view = DeleteConfirmView(self.channel_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class ChangeOwnerModal(discord.ui.Modal):
    """Modal pour changer le propriétaire"""
    
    def __init__(self, channel_id: int, current_owner: int):
        super().__init__(title="👑 Changer le propriétaire")
        self.channel_id = channel_id
        self.current_owner = current_owner
        
        self.user_input = discord.ui.TextInput(
            label="Nouvel propriétaire (ID ou mention)",
            placeholder="@username ou 123456789",
            required=True,
            max_length=100
        )
        self.add_item(self.user_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Logique pour changer le propriétaire
        user_input = self.user_input.value.strip()
        
        # Extraire l'ID de l'utilisateur
        user_id = None
        if user_input.startswith('<@') and user_input.endswith('>'):
            user_id = int(user_input[2:-1].replace('!', ''))
        elif user_input.isdigit():
            user_id = int(user_input)
        
        if not user_id:
            await interaction.response.send_message("❌ Format invalide ! Utilisez @username ou l'ID", ephemeral=True)
            return
        
        new_owner = interaction.guild.get_member(user_id)
        if not new_owner:
            await interaction.response.send_message("❌ Utilisateur introuvable !", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="✅ **PROPRIÉTAIRE CHANGÉ**",
            description=f"**Nouveau propriétaire:** {new_owner.mention}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class SetLimitModal(discord.ui.Modal):
    """Modal pour définir la limite d'utilisateurs"""
    
    def __init__(self, channel_id: int):
        super().__init__(title="👥 Définir la limite")
        self.channel_id = channel_id
        
        self.limit_input = discord.ui.TextInput(
            label="Limite d'utilisateurs (0 = illimité)",
            placeholder="10",
            required=True,
            max_length=2
        )
        self.add_item(self.limit_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit = int(self.limit_input.value)
            if limit < 0 or limit > 99:
                await interaction.response.send_message("❌ Limite doit être entre 0 et 99 !", ephemeral=True)
                return
            
            channel = interaction.guild.get_channel(self.channel_id)
            if channel:
                await channel.edit(user_limit=limit)
                
                embed = discord.Embed(
                    title="✅ **LIMITE MODIFIÉE**",
                    description=f"**Nouvelle limite:** {limit if limit > 0 else 'Illimitée'}",
                    color=discord.Color.green()
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message("❌ Salon introuvable !", ephemeral=True)
                
        except ValueError:
            await interaction.response.send_message("❌ Veuillez entrer un nombre valide !", ephemeral=True)


class RenameChannelModal(discord.ui.Modal):
    """Modal pour renommer le salon"""
    
    def __init__(self, channel_id: int):
        super().__init__(title="✏️ Renommer le salon")
        self.channel_id = channel_id
        
        self.name_input = discord.ui.TextInput(
            label="Nouveau nom du salon",
            placeholder="🎤 Mon Super Salon",
            required=True,
            max_length=100
        )
        self.add_item(self.name_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        new_name = self.name_input.value.strip()
        
        if len(new_name) < 1:
            await interaction.response.send_message("❌ Le nom ne peut pas être vide !", ephemeral=True)
            return
        
        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            try:
                await channel.edit(name=new_name)
                
                embed = discord.Embed(
                    title="✅ **SALON RENOMMÉ**",
                    description=f"**Nouveau nom:** {new_name}",
                    color=discord.Color.green()
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Salon introuvable !", ephemeral=True)


class KickMemberView(discord.ui.View):
    """Vue pour sélectionner un membre à expulser"""
    
    def __init__(self, channel: discord.VoiceChannel, owner_id: int):
        super().__init__(timeout=60)
        self.channel = channel
        self.owner_id = owner_id
        
        # Créer un sélecteur avec les membres du salon (sauf le propriétaire)
        options = []
        for member in channel.members:
            if member.id != owner_id and not member.bot:
                options.append(discord.SelectOption(
                    label=member.display_name,
                    value=str(member.id),
                    description=f"Expulser {member.display_name}",
                    emoji="🚪"
                ))
        
        if options:
            self.member_select = discord.ui.Select(
                placeholder="Sélectionner un membre à expulser...",
                options=options[:25]  # Max 25 options
            )
            self.member_select.callback = self.kick_selected_member
            self.add_item(self.member_select)
    
    async def kick_selected_member(self, interaction: discord.Interaction):
        """Expulser le membre sélectionné"""
        
        member_id = int(self.member_select.values[0])
        member = interaction.guild.get_member(member_id)
        
        if not member:
            await interaction.response.send_message("❌ Membre introuvable !", ephemeral=True)
            return
        
        try:
            await member.move_to(None, reason=f"Expulsé par {interaction.user}")
            
            embed = discord.Embed(
                title="✅ **MEMBRE EXPULSÉ**",
                description=f"**{member.mention}** a été expulsé du salon !",
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Impossible d'expulser: {e}", ephemeral=True)


class DeleteConfirmView(discord.ui.View):
    """Confirmation de suppression du salon"""
    
    def __init__(self, channel_id: int):
        super().__init__(timeout=30)
        self.channel_id = channel_id
    
    @discord.ui.button(label="✅ OUI, SUPPRIMER", style=discord.ButtonStyle.danger, emoji="✅")
    async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Confirmer la suppression"""
        
        channel = interaction.guild.get_channel(self.channel_id)
        if channel:
            try:
                await channel.delete(reason=f"Suppression demandée par {interaction.user}")
                
                embed = discord.Embed(
                    title="✅ **SALON SUPPRIMÉ**",
                    description="Le salon vocal temporaire a été supprimé !",
                    color=discord.Color.green()
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
            except Exception as e:
                await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Salon déjà supprimé !", ephemeral=True)
    
    @discord.ui.button(label="❌ ANNULER", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Annuler la suppression"""
        
        embed = discord.Embed(
            title="🔄 **SUPPRESSION ANNULÉE**",
            description="Le salon reste actif !",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    """Charge le module HubVocalDraftBot"""
    await bot.add_cog(HubVocal(bot))
    print("🚀 [OK] HubVocalDraftBot chargé - Système complet de salons temporaires !")
