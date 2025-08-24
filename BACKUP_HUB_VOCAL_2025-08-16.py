#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎵 BACKUP Arsenal V4 - Hub Vocal Temporaire
SAUVEGARDE COMPLÈTE DU SYSTÈME VOCAL - 16 Août 2025
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
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS hub_config (
                        guild_id INTEGER PRIMARY KEY,
                        config TEXT
                    )
                ''')
                
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS temp_channels (
                        guild_id INTEGER,
                        channel_id INTEGER,
                        owner_id INTEGER,
                        created_at TEXT,
                        data TEXT,
                        PRIMARY KEY (guild_id, channel_id)
                    )
                ''')
                
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS vocal_stats (
                        guild_id INTEGER,
                        user_id INTEGER,
                        total_time INTEGER DEFAULT 0,
                        sessions INTEGER DEFAULT 0,
                        channels_created INTEGER DEFAULT 0,
                        PRIMARY KEY (guild_id, user_id)
                    )
                ''')
                
                await db.commit()
                
        except Exception as e:
            print(f"[ERROR] Hub Vocal DB Setup: {e}")

    async def get_config(self, guild_id: int) -> dict:
        """Récupérer la configuration du hub vocal"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT config FROM hub_config WHERE guild_id = ?",
                    (guild_id,)
                )
                row = await cursor.fetchone()
                
                if row:
                    config = json.loads(row[0])
                    # Merger avec la config par défaut
                    for key, value in self.default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
                else:
                    return self.default_config.copy()
                    
        except Exception as e:
            print(f"[ERROR] Get Config: {e}")
            return self.default_config.copy()

    async def save_config(self, guild_id: int, config: dict):
        """Sauvegarder la configuration"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT OR REPLACE INTO hub_config (guild_id, config) VALUES (?, ?)",
                    (guild_id, json.dumps(config))
                )
                await db.commit()
        except Exception as e:
            print(f"[ERROR] Save Config: {e}")

    @app_commands.command(name="hub_vocal", description="🎤 Configuration du hub vocal temporaire")
    @app_commands.describe(action="Action à effectuer")
    @app_commands.choices(action=[
        app_commands.Choice(name="🎛️ Configuration", value="config"),
        app_commands.Choice(name="📊 Statistiques", value="stats"),
        app_commands.Choice(name="🔧 Réinitialiser", value="reset"),
        app_commands.Choice(name="❓ Aide", value="help")
    ])
    async def hub_vocal(self, interaction: discord.Interaction, action: str = "config"):
        """Gestion du hub vocal"""
        
        if not interaction.user.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="❌ Permission insuffisante",
                description="Vous avez besoin de la permission **Gérer les salons**",
                color=0xff0000
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        config = await self.get_config(interaction.guild_id)
        
        if action == "config":
            await self.show_config_panel(interaction, config)
        elif action == "stats":
            await self.show_stats(interaction, config)
        elif action == "reset":
            await self.reset_config(interaction, config)
        elif action == "help":
            await self.show_help(interaction)

    async def show_config_panel(self, interaction: discord.Interaction, config: dict):
        """Panneau de configuration principal"""
        
        embed = discord.Embed(
            title="🎤 Configuration Hub Vocal",
            description="Configurez votre système de salons temporaires",
            color=0x00ff00 if config["enabled"] else 0xff9900
        )
        
        # Status
        embed.add_field(
            name="📊 Status",
            value=f"{'✅ Activé' if config['enabled'] else '❌ Désactivé'}",
            inline=True
        )
        
        # Hub channel
        hub_channel = interaction.guild.get_channel(config["hub_channel"]) if config["hub_channel"] else None
        embed.add_field(
            name="🎯 Salon Hub",
            value=f"{hub_channel.mention if hub_channel else '❌ Non configuré'}",
            inline=True
        )
        
        # Vocal role
        vocal_role = interaction.guild.get_role(config["vocal_role"]) if config["vocal_role"] else None
        embed.add_field(
            name="🎭 Rôle Vocal",
            value=f"{vocal_role.mention if vocal_role else '❌ Non configuré'}",
            inline=True
        )
        
        # Category
        category = interaction.guild.get_channel(config["category"]) if config["category"] else None
        embed.add_field(
            name="📁 Catégorie",
            value=f"{category.name if category else '❌ Non configurée'}",
            inline=True
        )
        
        # Salons actifs
        active_channels = len(config.get("temp_channels", {}))
        embed.add_field(
            name="🔊 Salons Actifs",
            value=f"{active_channels} salon(s)",
            inline=True
        )
        
        # Auto create role
        embed.add_field(
            name="⚙️ Création Auto Rôle",
            value=f"{'✅ Oui' if config.get('auto_create_role', True) else '❌ Non'}",
            inline=True
        )
        
        view = HubVocalConfigView(self, config)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def show_stats(self, interaction: discord.Interaction, config: dict):
        """Afficher les statistiques"""
        embed = discord.Embed(
            title="📊 Statistiques Hub Vocal",
            color=0x00ff00
        )
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Total des salons créés
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM temp_channels WHERE guild_id = ?",
                    (interaction.guild_id,)
                )
                total_channels = (await cursor.fetchone())[0]
                
                # Utilisateurs actifs
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM vocal_stats WHERE guild_id = ? AND total_time > 0",
                    (interaction.guild_id,)
                )
                active_users = (await cursor.fetchone())[0]
                
                # Top 5 utilisateurs
                cursor = await db.execute(
                    """SELECT user_id, total_time, sessions, channels_created 
                       FROM vocal_stats 
                       WHERE guild_id = ? 
                       ORDER BY total_time DESC LIMIT 5""",
                    (interaction.guild_id,)
                )
                top_users = await cursor.fetchall()
                
                embed.add_field(
                    name="🎯 Statistiques Générales",
                    value=f"**Salons créés:** {total_channels}\n**Utilisateurs actifs:** {active_users}",
                    inline=False
                )
                
                if top_users:
                    top_text = ""
                    for i, (user_id, total_time, sessions, channels_created) in enumerate(top_users, 1):
                        user = interaction.guild.get_member(user_id)
                        if user:
                            hours = total_time // 3600
                            minutes = (total_time % 3600) // 60
                            top_text += f"**{i}.** {user.display_name}\n"
                            top_text += f"└ ⏱️ {hours}h {minutes}m • 📊 {sessions} sessions • 🎤 {channels_created} salons\n\n"
                    
                    embed.add_field(
                        name="🏆 Top Utilisateurs",
                        value=top_text if top_text else "Aucune donnée",
                        inline=False
                    )
                
        except Exception as e:
            embed.add_field(
                name="❌ Erreur",
                value=f"Impossible de charger les stats: {e}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def show_help(self, interaction: discord.Interaction):
        """Afficher l'aide"""
        embed = discord.Embed(
            title="❓ Aide Hub Vocal",
            description="Guide complet d'utilisation",
            color=0x00ffff
        )
        
        embed.add_field(
            name="🎯 Concept",
            value="Le hub vocal permet de créer des salons vocaux temporaires automatiquement",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Configuration requise",
            value="• Un salon principal (hub)\n• Une catégorie pour les salons temporaires\n• Un rôle vocal (optionnel)",
            inline=False
        )
        
        embed.add_field(
            name="🔄 Fonctionnement",
            value="1. L'utilisateur rejoint le salon hub\n2. Un salon temporaire est créé automatiquement\n3. L'utilisateur est déplacé dans son salon\n4. Le salon est supprimé quand il est vide",
            inline=False
        )
        
        embed.add_field(
            name="🎛️ Contrôles disponibles",
            value="• Verrouiller/déverrouiller le salon\n• Changer le nom\n• Gérer les permissions\n• Inviter des membres\n• Statistiques personnelles",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Gestion des événements vocaux"""
        try:
            config = await self.get_config(member.guild.id)
            
            if not config["enabled"]:
                return
            
            # Rejoindre le hub vocal
            if after.channel and after.channel.id == config["hub_channel"]:
                await self.create_temp_channel(member, config)
            
            # Quitter un salon temporaire
            if before.channel and str(before.channel.id) in config.get("temp_channels", {}):
                if len(before.channel.members) == 0:
                    await self.delete_temp_channel(before.channel, config)
                    
            # Gestion du rôle vocal
            if config["vocal_role"]:
                vocal_role = member.guild.get_role(config["vocal_role"])
                if vocal_role:
                    if after.channel and not before.channel:
                        # Utilisateur rejoint un vocal
                        await member.add_roles(vocal_role)
                    elif before.channel and not after.channel:
                        # Utilisateur quitte tous les vocaux
                        await member.remove_roles(vocal_role)
                        
        except Exception as e:
            print(f"[ERROR] Voice State Update: {e}")

    async def create_temp_channel(self, member: discord.Member, config: dict):
        """Créer un salon temporaire"""
        try:
            guild = member.guild
            category = guild.get_channel(config["category"]) if config["category"] else None
            
            # Nom du salon
            channel_name = f"🎤 {member.display_name}"
            
            # Permissions
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=True, connect=True),
                member: discord.PermissionOverwrite(
                    manage_channels=True,
                    manage_permissions=True,
                    move_members=True,
                    mute_members=True,
                    deafen_members=True
                )
            }
            
            # Créer le salon
            temp_channel = await guild.create_voice_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites
            )
            
            # Déplacer l'utilisateur
            await member.move_to(temp_channel)
            
            # Sauvegarder dans la config
            config["temp_channels"][str(temp_channel.id)] = {
                "owner_id": member.id,
                "created_at": datetime.now().isoformat(),
                "name": channel_name
            }
            await self.save_config(guild.id, config)
            
            # Créer le panel de contrôle
            await self.create_control_panel(temp_channel, member)
            
            # Stats
            await self.update_user_stats(guild.id, member.id, "channel_created")
            
            print(f"[HUB_VOCAL] Salon temporaire créé: {temp_channel.name} pour {member}")
            
        except Exception as e:
            print(f"[ERROR] Create Temp Channel: {e}")

    async def create_control_panel(self, channel: discord.VoiceChannel, owner: discord.Member):
        """Créer le panel de contrôle du salon"""
        try:
            embed = discord.Embed(
                title=f"🎛️ Contrôle du salon vocal",
                description=f"Panel de contrôle pour **{channel.name}**\nPropriétaire: {owner.mention}",
                color=0x00ff00
            )
            
            embed.add_field(
                name="🔧 Actions disponibles",
                value="• 🔒 Verrouiller/déverrouiller\n• ✏️ Renommer\n• 👥 Gérer les accès\n• 📊 Statistiques",
                inline=False
            )
            
            view = TempChannelControlView(self, channel.id, owner.id)
            
            # Envoyer dans le salon textuel correspondant ou créer un salon temporaire
            text_channels = [ch for ch in channel.guild.text_channels if ch.category == channel.category]
            if text_channels:
                target_channel = text_channels[0]
            else:
                target_channel = channel.guild.system_channel or channel.guild.text_channels[0]
            
            if target_channel:
                message = await target_channel.send(embed=embed, view=view)
                
                # Sauvegarder l'ID du message de contrôle
                self.temp_channels_data[channel.id] = {
                    "owner_id": owner.id,
                    "control_message": message.id,
                    "control_channel": target_channel.id
                }
                
        except Exception as e:
            print(f"[ERROR] Create Control Panel: {e}")

    async def delete_temp_channel(self, channel: discord.VoiceChannel, config: dict):
        """Supprimer un salon temporaire"""
        try:
            channel_id_str = str(channel.id)
            
            if channel_id_str in config["temp_channels"]:
                # Supprimer de la config
                owner_id = config["temp_channels"][channel_id_str]["owner_id"]
                del config["temp_channels"][channel_id_str]
                await self.save_config(channel.guild.id, config)
                
                # Nettoyer les données temporaires
                if channel.id in self.temp_channels_data:
                    del self.temp_channels_data[channel.id]
                
                # Supprimer le salon
                await channel.delete(reason="Salon temporaire vide")
                
                print(f"[HUB_VOCAL] Salon temporaire supprimé: {channel.name}")
                
        except Exception as e:
            print(f"[ERROR] Delete Temp Channel: {e}")

    async def update_user_stats(self, guild_id: int, user_id: int, stat_type: str):
        """Mettre à jour les statistiques utilisateur"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Créer l'entrée si elle n'existe pas
                await db.execute(
                    """INSERT OR IGNORE INTO vocal_stats 
                       (guild_id, user_id, total_time, sessions, channels_created) 
                       VALUES (?, ?, 0, 0, 0)""",
                    (guild_id, user_id)
                )
                
                # Mettre à jour selon le type
                if stat_type == "channel_created":
                    await db.execute(
                        "UPDATE vocal_stats SET channels_created = channels_created + 1 WHERE guild_id = ? AND user_id = ?",
                        (guild_id, user_id)
                    )
                elif stat_type == "session_start":
                    await db.execute(
                        "UPDATE vocal_stats SET sessions = sessions + 1 WHERE guild_id = ? AND user_id = ?",
                        (guild_id, user_id)
                    )
                
                await db.commit()
                
        except Exception as e:
            print(f"[ERROR] Update User Stats: {e}")

    @tasks.loop(minutes=5)
    async def cleanup_empty_channels(self):
        """Nettoyer les salons vides périodiquement"""
        try:
            for guild in self.bot.guilds:
                config = await self.get_config(guild.id)
                
                if not config["enabled"]:
                    continue
                
                channels_to_remove = []
                for channel_id_str, data in config["temp_channels"].items():
                    try:
                        channel = guild.get_channel(int(channel_id_str))
                        if not channel or len(channel.members) == 0:
                            channels_to_remove.append(channel_id_str)
                            if channel:
                                await channel.delete(reason="Salon temporaire vide (nettoyage automatique)")
                    except Exception as e:
                        print(f"[ERROR] Cleanup channel {channel_id_str}: {e}")
                        channels_to_remove.append(channel_id_str)
                
                # Nettoyer la config
                if channels_to_remove:
                    for channel_id_str in channels_to_remove:
                        if channel_id_str in config["temp_channels"]:
                            del config["temp_channels"][channel_id_str]
                    await self.save_config(guild.id, config)
                    
        except Exception as e:
            print(f"[ERROR] Cleanup Task: {e}")

class HubVocalConfigView(discord.ui.View):
    """Vue de configuration du hub vocal"""
    
    def __init__(self, cog: HubVocal, config: dict):
        super().__init__(timeout=300)
        self.cog = cog
        self.config = config

    @discord.ui.button(label="🎯 Salon Hub", style=discord.ButtonStyle.primary)
    async def set_hub_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Définir le salon hub"""
        
        modal = HubChannelModal(self.cog, self.config)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="📁 Catégorie", style=discord.ButtonStyle.primary)
    async def set_category(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Définir la catégorie"""
        
        modal = CategoryModal(self.cog, self.config)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🎭 Rôle Vocal", style=discord.ButtonStyle.primary)
    async def set_vocal_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Définir le rôle vocal"""
        
        modal = VocalRoleModal(self.cog, self.config)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="⚙️ Options", style=discord.ButtonStyle.secondary)
    async def toggle_options(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Options avancées"""
        
        modal = OptionsModal(self.cog, self.config)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="✅ Activer" if not config.get("enabled") else "❌ Désactiver", 
                      style=discord.ButtonStyle.success if not config.get("enabled") else discord.ButtonStyle.danger)
    async def toggle_system(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Activer/désactiver le système"""
        
        self.config["enabled"] = not self.config["enabled"]
        await self.cog.save_config(interaction.guild_id, self.config)
        
        embed = discord.Embed(
            title=f"{'✅ Hub Vocal Activé' if self.config['enabled'] else '❌ Hub Vocal Désactivé'}",
            color=0x00ff00 if self.config["enabled"] else 0xff0000
        )
        
        await interaction.response.edit_message(embed=embed, view=self)

class HubChannelModal(discord.ui.Modal, title="🎯 Configuration Salon Hub"):
    def __init__(self, cog: HubVocal, config: dict):
        super().__init__()
        self.cog = cog
        self.config = config

    channel_input = discord.ui.TextInput(
        label="ID du salon hub vocal",
        placeholder="Collez l'ID du salon vocal principal...",
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            channel_id = int(self.channel_input.value)
            channel = interaction.guild.get_channel(channel_id)
            
            if not channel or not isinstance(channel, discord.VoiceChannel):
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Ce salon n'existe pas ou n'est pas un salon vocal",
                    color=0xff0000
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            self.config["hub_channel"] = channel_id
            await self.cog.save_config(interaction.guild_id, self.config)
            
            embed = discord.Embed(
                title="✅ Salon Hub Configuré",
                description=f"Salon hub défini: {channel.mention}",
                color=0x00ff00
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Erreur",
                description="ID de salon invalide",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

class CategoryModal(discord.ui.Modal, title="📁 Configuration Catégorie"):
    def __init__(self, cog: HubVocal, config: dict):
        super().__init__()
        self.cog = cog
        self.config = config

    category_input = discord.ui.TextInput(
        label="ID de la catégorie",
        placeholder="Collez l'ID de la catégorie pour les salons temporaires...",
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            category_id = int(self.category_input.value)
            category = interaction.guild.get_channel(category_id)
            
            if not category or not isinstance(category, discord.CategoryChannel):
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Cette catégorie n'existe pas",
                    color=0xff0000
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            self.config["category"] = category_id
            await self.cog.save_config(interaction.guild_id, self.config)
            
            embed = discord.Embed(
                title="✅ Catégorie Configurée",
                description=f"Catégorie définie: **{category.name}**",
                color=0x00ff00
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Erreur",
                description="ID de catégorie invalide",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

class VocalRoleModal(discord.ui.Modal, title="🎭 Configuration Rôle Vocal"):
    def __init__(self, cog: HubVocal, config: dict):
        super().__init__()
        self.cog = cog
        self.config = config

    role_input = discord.ui.TextInput(
        label="ID du rôle vocal (optionnel)",
        placeholder="Collez l'ID du rôle ou laissez vide...",
        required=False,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            if not self.role_input.value.strip():
                # Créer automatiquement le rôle
                if self.config.get("auto_create_role", True):
                    role = await interaction.guild.create_role(
                        name=self.config.get("role_name", "🎤 En Vocal"),
                        color=0x00ff00,
                        reason="Rôle vocal automatique du Hub Vocal"
                    )
                    self.config["vocal_role"] = role.id
                else:
                    self.config["vocal_role"] = None
            else:
                role_id = int(self.role_input.value)
                role = interaction.guild.get_role(role_id)
                
                if not role:
                    embed = discord.Embed(
                        title="❌ Erreur",
                        description="Ce rôle n'existe pas",
                        color=0xff0000
                    )
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
                
                self.config["vocal_role"] = role_id
            
            await self.cog.save_config(interaction.guild_id, self.config)
            
            role = interaction.guild.get_role(self.config["vocal_role"]) if self.config["vocal_role"] else None
            
            embed = discord.Embed(
                title="✅ Rôle Vocal Configuré",
                description=f"Rôle vocal: {role.mention if role else '❌ Aucun'}",
                color=0x00ff00
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Erreur",
                description="ID de rôle invalide",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

class OptionsModal(discord.ui.Modal, title="⚙️ Options Avancées"):
    def __init__(self, cog: HubVocal, config: dict):
        super().__init__()
        self.cog = cog
        self.config = config

    role_name_input = discord.ui.TextInput(
        label="Nom du rôle vocal",
        placeholder="🎤 En Vocal",
        default=config.get("role_name", "🎤 En Vocal"),
        required=False,
        max_length=50
    )

    auto_create_input = discord.ui.TextInput(
        label="Créer automatiquement le rôle (oui/non)",
        placeholder="oui",
        default="oui" if config.get("auto_create_role", True) else "non",
        required=False,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Nom du rôle
        if self.role_name_input.value.strip():
            self.config["role_name"] = self.role_name_input.value.strip()
        
        # Création automatique
        auto_create = self.auto_create_input.value.lower().strip() in ["oui", "yes", "true", "1"]
        self.config["auto_create_role"] = auto_create
        
        await self.cog.save_config(interaction.guild_id, self.config)
        
        embed = discord.Embed(
            title="✅ Options Sauvegardées",
            description=f"**Nom du rôle:** {self.config['role_name']}\n**Création auto:** {'✅ Oui' if auto_create else '❌ Non'}",
            color=0x00ff00
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class TempChannelControlView(discord.ui.View):
    """Panel de contrôle pour les salons temporaires"""
    
    def __init__(self, cog: HubVocal, channel_id: int, owner_id: int):
        super().__init__(timeout=None)
        self.cog = cog
        self.channel_id = channel_id
        self.owner_id = owner_id

    @discord.ui.button(label="🔒", style=discord.ButtonStyle.secondary)
    async def lock_unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Verrouiller/déverrouiller le salon"""
        
        if interaction.user.id != self.owner_id:
            embed = discord.Embed(
                title="❌ Permission refusée",
                description="Seul le propriétaire peut contrôler ce salon",
                color=0xff0000
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            return
        
        # Toggle lock
        current_perms = channel.overwrites_for(interaction.guild.default_role)
        is_locked = current_perms.connect is False
        
        await channel.set_permissions(
            interaction.guild.default_role,
            connect=is_locked,  # Inverse the lock
            view_channel=True
        )
        
        embed = discord.Embed(
            title=f"{'🔓 Salon déverrouillé' if is_locked else '🔒 Salon verrouillé'}",
            description=f"Le salon **{channel.name}** a été {'déverrouillé' if is_locked else 'verrouillé'}",
            color=0x00ff00 if is_locked else 0xff9900
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="✏️", style=discord.ButtonStyle.primary)
    async def rename_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Renommer le salon"""
        
        if interaction.user.id != self.owner_id:
            embed = discord.Embed(
                title="❌ Permission refusée",
                description="Seul le propriétaire peut contrôler ce salon",
                color=0xff0000
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        modal = RenameChannelModal(self.channel_id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="👥", style=discord.ButtonStyle.success)
    async def manage_access(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gérer les accès"""
        
        if interaction.user.id != self.owner_id:
            embed = discord.Embed(
                title="❌ Permission refusée",
                description="Seul le propriétaire peut contrôler ce salon",
                color=0xff0000
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        modal = ManageAccessModal(self.channel_id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="📊", style=discord.ButtonStyle.secondary)
    async def show_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Afficher les stats du salon"""
        
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            return
        
        embed = discord.Embed(
            title="📊 Statistiques du salon",
            description=f"Informations sur **{channel.name}**",
            color=0x00ffff
        )
        
        embed.add_field(
            name="👤 Propriétaire",
            value=f"<@{self.owner_id}>",
            inline=True
        )
        
        embed.add_field(
            name="👥 Membres connectés",
            value=f"{len(channel.members)}",
            inline=True
        )
        
        embed.add_field(
            name="🔒 Status",
            value="Verrouillé" if channel.overwrites_for(interaction.guild.default_role).connect is False else "Ouvert",
            inline=True
        )
        
        if channel.members:
            members_list = "\n".join([f"• {member.display_name}" for member in channel.members[:10]])
            if len(channel.members) > 10:
                members_list += f"\n... et {len(channel.members) - 10} autres"
            
            embed.add_field(
                name="👥 Membres présents",
                value=members_list,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class RenameChannelModal(discord.ui.Modal, title="✏️ Renommer le salon"):
    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id

    name_input = discord.ui.TextInput(
        label="Nouveau nom du salon",
        placeholder="Entrez le nouveau nom...",
        required=True,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            channel = interaction.guild.get_channel(self.channel_id)
            if not channel:
                return
            
            old_name = channel.name
            await channel.edit(name=self.name_input.value)
            
            embed = discord.Embed(
                title="✅ Salon renommé",
                description=f"**{old_name}** → **{channel.name}**",
                color=0x00ff00
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Impossible de renommer: {e}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

class ManageAccessModal(discord.ui.Modal, title="👥 Gérer les accès"):
    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id

    user_input = discord.ui.TextInput(
        label="ID utilisateur à inviter/bannir",
        placeholder="Collez l'ID de l'utilisateur...",
        required=True,
        max_length=20
    )

    action_input = discord.ui.TextInput(
        label="Action (invite/ban)",
        placeholder="invite ou ban",
        required=True,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            channel = interaction.guild.get_channel(self.channel_id)
            if not channel:
                return
            
            user_id = int(self.user_input.value)
            user = interaction.guild.get_member(user_id)
            
            if not user:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Utilisateur non trouvé",
                    color=0xff0000
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            action = self.action_input.value.lower()
            
            if action == "invite":
                await channel.set_permissions(user, connect=True, view_channel=True)
                embed = discord.Embed(
                    title="✅ Utilisateur invité",
                    description=f"{user.mention} peut maintenant rejoindre le salon",
                    color=0x00ff00
                )
            elif action == "ban":
                await channel.set_permissions(user, connect=False, view_channel=False)
                if user in channel.members:
                    await user.move_to(None)
                embed = discord.Embed(
                    title="✅ Utilisateur banni",
                    description=f"{user.mention} ne peut plus accéder au salon",
                    color=0xff0000
                )
            else:
                embed = discord.Embed(
                    title="❌ Action invalide",
                    description="Utilisez 'invite' ou 'ban'",
                    color=0xff0000
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Erreur",
                description="ID utilisateur invalide",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Impossible de modifier les permissions: {e}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HubVocal(bot))
    print("🎤 [OK] Hub Vocal - Système complet de salons temporaires avec contrôle !")

