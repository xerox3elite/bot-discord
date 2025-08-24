#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎵 Arsenal V4 - Hub Vocal Temporaire
Système de vocaux temporaires avec auto-gestion
Développé par XeRoX - Arsenal Bot V4.5.2
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiosqlite
import json
import asyncio
from datetime import datetime, timedelta, timezone
import os
from typing import Optional, Dict, List
import logging

class HubVocal(commands.Cog):
    """Hub vocal temporaire complet style DraftBot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/hub_vocal.db"
        self.config_file = "hub_config.json"
        
        # Configuration par défaut
        self.default_config = {
            "category_id": None,
            "hub_channel_id": None,
            "channel_limit": 99,
            "default_name": "Vocal de {}",
            "auto_delete": True,
            "enabled": False,
            "temp_channels": {},
            "channel_counter": 0
        }
        
        # Démarrer les tâches
        self.auto_save.start()
        self.cleanup_empty_channels.start()

    async def cog_load(self):
        """Charge la configuration au démarrage du cog"""
        await self.init_database()
        await self.load_config()

    async def init_database(self):
        """Initialise la base de données"""
        os.makedirs('data', exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS server_config (
                    guild_id INTEGER PRIMARY KEY,
                    config TEXT NOT NULL
                )
            ''')
            await db.commit()
    
    async def get_config(self, guild_id: int) -> dict:
        """Récupère la configuration d'un serveur"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT config FROM server_config WHERE guild_id = ?",
                (guild_id,)
            )
            result = await cursor.fetchone()
            
            if result:
                return json.loads(result[0])
            else:
                # Retourne la config par défaut si pas trouvée
                return self.default_config.copy()
    
    async def save_config(self, guild_id: int, config: dict):
        """Sauvegarde la configuration d'un serveur"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO server_config (guild_id, config) VALUES (?, ?)",
                (guild_id, json.dumps(config))
            )
            await db.commit()

    async def load_config(self):
        """Charge la configuration depuis le fichier JSON au démarrage"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                # Charger les configs dans la base pour chaque serveur
                for guild_id_str, config in config_data.items():
                    guild_id = int(guild_id_str)
                    await self.save_config(guild_id, config)
                    
                logging.info(f"🧠 Configuration Hub Vocal restaurée depuis {self.config_file}")
            else:
                logging.warning("🧠 Aucun fichier hub_config.json détecté pour restaurer les vocaux.")
        except Exception as e:
            logging.error(f"❌ Erreur lors du chargement de la config: {e}")

    @tasks.loop(minutes=5.0)
    async def auto_save(self):
        """Sauvegarde automatique de la configuration"""
        try:
            save_data = {}
            
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT guild_id, config FROM server_config")
                results = await cursor.fetchall()
                
                for guild_id, config_str in results:
                    save_data[str(guild_id)] = json.loads(config_str)
            
            # Écrire dans le fichier JSON
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logging.error(f"❌ Erreur auto-save hub vocal: {e}")

    @auto_save.before_loop
    async def before_auto_save(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=1.0)
    async def cleanup_empty_channels(self):
        """Nettoie les canaux vocaux vides"""
        try:
            for guild in self.bot.guilds:
                config = await self.get_config(guild.id)
                if not config.get('enabled', False):
                    continue
                
                temp_channels = config.get('temp_channels', {})
                channels_to_remove = []
                
                for channel_id_str, creator_id in temp_channels.items():
                    try:
                        channel_id = int(channel_id_str)
                        channel = guild.get_channel(channel_id)
                        
                        if not channel or len(channel.members) == 0:
                            # Canal vide ou inexistant
                            if channel:
                                await channel.delete(reason="Canal vocal temporaire vide")
                            channels_to_remove.append(channel_id_str)
                    except Exception as e:
                        logging.error(f"Erreur cleanup canal {channel_id_str}: {e}")
                        channels_to_remove.append(channel_id_str)
                
                # Nettoyer la config si nécessaire
                if channels_to_remove:
                    for channel_id_str in channels_to_remove:
                        temp_channels.pop(channel_id_str, None)
                    config['temp_channels'] = temp_channels
                    await self.save_config(guild.id, config)
                    
        except Exception as e:
            logging.error(f"❌ Erreur cleanup_empty_channels: {e}")

    @cleanup_empty_channels.before_loop
    async def before_cleanup(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Gère la création/suppression des canaux temporaires"""
        try:
            guild = member.guild
            config = await self.get_config(guild.id)
            
            if not config.get('enabled', False):
                return
            
            hub_channel_id = config.get('hub_channel_id')
            if not hub_channel_id:
                return
                
            # Utilisateur rejoint le hub
            if after.channel and after.channel.id == hub_channel_id:
                await self.create_temp_channel(member, config)
            
            # Utilisateur quitte un canal temporaire
            if before.channel and str(before.channel.id) in config.get('temp_channels', {}):
                if len(before.channel.members) == 0:
                    await before.channel.delete(reason="Canal vocal temporaire vide")
                    # Retirer de la config
                    temp_channels = config.get('temp_channels', {})
                    temp_channels.pop(str(before.channel.id), None)
                    config['temp_channels'] = temp_channels
                    await self.save_config(guild.id, config)
                    
        except Exception as e:
            logging.error(f"❌ Erreur on_voice_state_update: {e}")

    async def create_temp_channel(self, member, config):
        """Crée un canal vocal temporaire"""
        try:
            guild = member.guild
            category_id = config.get('category_id')
            category = guild.get_channel(category_id) if category_id else None
            
            # Nom du canal
            channel_name = config.get('default_name', 'Vocal de {}').format(member.display_name)
            
            # Créer le canal
            temp_channel = await guild.create_voice_channel(
                name=channel_name,
                category=category,
                user_limit=config.get('channel_limit', 99)
            )
            
            # Donner les permissions au créateur
            await temp_channel.set_permissions(
                member, 
                manage_channels=True, 
                manage_permissions=True, 
                move_members=True
            )
            
            # Déplacer l'utilisateur
            await member.move_to(temp_channel)
            
            # Créer le panneau de configuration
            await self.send_control_panel(temp_channel, member)
            
            # Sauvegarder dans la config
            temp_channels = config.get('temp_channels', {})
            temp_channels[str(temp_channel.id)] = member.id
            config['temp_channels'] = temp_channels
            config['channel_counter'] = config.get('channel_counter', 0) + 1
            await self.save_config(guild.id, config)
            
            logging.info(f"🎵 Canal temporaire créé: {channel_name} pour {member.display_name}")
            
        except Exception as e:
            logging.error(f"❌ Erreur création canal temporaire: {e}")

    async def send_control_panel(self, channel, owner):
        """Envoie le panneau de contrôle dans le salon temporaire"""
        try:
            embed = discord.Embed(
                title="🎵 Panneau de Contrôle - Salon Temporaire",
                description=f"**Propriétaire:** {owner.mention}\n"
                           f"**Salon:** {channel.name}\n\n"
                           "Utilisez les boutons ci-dessous pour gérer votre salon !",
                color=0x00ff88
            )
            embed.add_field(
                name="🔧 Commandes disponibles",
                value="• **Renommer** - Changer le nom du salon\n"
                      "• **Limite** - Modifier la limite d'utilisateurs\n" 
                      "• **Privé** - Rendre le salon privé\n"
                      "• **Public** - Rendre le salon public\n"
                      "• **Expulser** - Expulser un membre\n"
                      "• **Supprimer** - Supprimer le salon",
                inline=False
            )
            
            view = VocalControlView(owner.id, channel.id)
            message = await channel.send(embed=embed, view=view)
            
            # Épingler le message
            await message.pin()
            
        except Exception as e:
            logging.error(f"❌ Erreur envoi panneau contrôle: {e}")


class VocalControlView(discord.ui.View):
    """Vue avec boutons pour contrôler le salon vocal temporaire"""
    
    def __init__(self, owner_id: int, channel_id: int):
        super().__init__(timeout=None)
        self.owner_id = owner_id
        self.channel_id = channel_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Vérifie si l'utilisateur peut utiliser les boutons"""
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.response.send_message("❌ Ce salon n'existe plus!", ephemeral=True)
            return False
            
        # Soit le propriétaire, soit un admin peut utiliser
        if interaction.user.id == self.owner_id or interaction.user.guild_permissions.manage_channels:
            return True
        else:
            await interaction.response.send_message("❌ Seul le propriétaire du salon peut utiliser ces boutons!", ephemeral=True)
            return False

    @discord.ui.button(label="🏷️ Renommer", style=discord.ButtonStyle.primary)
    async def rename_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Renommer le salon"""
        modal = RenameModal(self.channel_id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="👥 Limite", style=discord.ButtonStyle.primary)
    async def change_limit(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Changer la limite d'utilisateurs"""
        modal = LimitModal(self.channel_id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🔒 Privé", style=discord.ButtonStyle.secondary)
    async def make_private(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Rendre le salon privé"""
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.response.send_message("❌ Salon introuvable!", ephemeral=True)
            return
            
        await channel.set_permissions(interaction.guild.default_role, connect=False)
        await interaction.response.send_message("🔒 Salon rendu privé!", ephemeral=True)

    @discord.ui.button(label="🔓 Public", style=discord.ButtonStyle.secondary) 
    async def make_public(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Rendre le salon public"""
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.response.send_message("❌ Salon introuvable!", ephemeral=True)
            return
            
        await channel.set_permissions(interaction.guild.default_role, connect=True)
        await interaction.response.send_message("🔓 Salon rendu public!", ephemeral=True)

    @discord.ui.button(label="👢 Expulser", style=discord.ButtonStyle.danger)
    async def kick_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Interface pour expulser un utilisateur"""
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel or len(channel.members) <= 1:
            await interaction.response.send_message("❌ Aucun membre à expulser!", ephemeral=True)
            return
            
        # Créer un select avec les membres
        options = []
        for member in channel.members:
            if member.id != self.owner_id:  # Ne pas inclure le propriétaire
                options.append(discord.SelectOption(
                    label=member.display_name,
                    description=f"Expulser {member.display_name}",
                    value=str(member.id)
                ))
        
        if not options:
            await interaction.response.send_message("❌ Aucun membre à expulser!", ephemeral=True)
            return
            
        view = discord.ui.View()
        select = KickSelect(self.channel_id, options)
        view.add_item(select)
        
        await interaction.response.send_message("👢 Sélectionnez le membre à expulser:", view=view, ephemeral=True)

    @discord.ui.button(label="🗑️ Supprimer", style=discord.ButtonStyle.danger)
    async def delete_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Supprimer le salon"""
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.response.send_message("❌ Salon introuvable!", ephemeral=True)
            return
            
        await interaction.response.send_message("🗑️ Salon supprimé dans 5 secondes...", ephemeral=True)
        await asyncio.sleep(5)
        await channel.delete(reason="Suppression demandée par le propriétaire")


class RenameModal(discord.ui.Modal, title="🏷️ Renommer le salon"):
    """Modal pour renommer le salon"""
    
    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id
        
    name = discord.ui.TextInput(
        label="Nouveau nom du salon",
        placeholder="Entrez le nouveau nom...",
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.response.send_message("❌ Salon introuvable!", ephemeral=True)
            return
            
        try:
            await channel.edit(name=self.name.value)
            await interaction.response.send_message(f"✅ Salon renommé en **{self.name.value}**!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors du renommage: {e}", ephemeral=True)


class LimitModal(discord.ui.Modal, title="👥 Changer la limite"):
    """Modal pour changer la limite d'utilisateurs"""
    
    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id
        
    limit = discord.ui.TextInput(
        label="Nouvelle limite (0-99, 0 = illimitée)",
        placeholder="Entrez un nombre entre 0 et 99...",
        max_length=2
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.response.send_message("❌ Salon introuvable!", ephemeral=True)
            return
            
        try:
            limit_value = int(self.limit.value)
            if limit_value < 0 or limit_value > 99:
                await interaction.response.send_message("❌ La limite doit être entre 0 et 99!", ephemeral=True)
                return
                
            await channel.edit(user_limit=limit_value)
            limit_text = "illimitée" if limit_value == 0 else str(limit_value)
            await interaction.response.send_message(f"✅ Limite changée à **{limit_text}**!", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Veuillez entrer un nombre valide!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors du changement: {e}", ephemeral=True)


class KickSelect(discord.ui.Select):
    """Select pour choisir qui expulser"""
    
    def __init__(self, channel_id: int, options: list):
        super().__init__(placeholder="Choisir le membre à expulser...", options=options)
        self.channel_id = channel_id
    
    async def callback(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(self.channel_id)
        member_id = int(self.values[0])
        member = interaction.guild.get_member(member_id)
        
        if not channel or not member:
            await interaction.response.send_message("❌ Salon ou membre introuvable!", ephemeral=True)
            return
            
        try:
            await member.move_to(None)
            await interaction.response.send_message(f"👢 **{member.display_name}** a été expulsé du salon!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors de l'expulsion: {e}", ephemeral=True)
            temp_channels[str(temp_channel.id)] = member.id
            config['temp_channels'] = temp_channels
            config['channel_counter'] = config.get('channel_counter', 0) + 1
            await self.save_config(guild.id, config)
            
            logging.info(f"🎵 Canal temporaire créé: {channel_name} pour {member.display_name}")
            
        except Exception as e:
            logging.error(f"❌ Erreur création canal temporaire: {e}")

    # Groupe de commandes hub vocal
    hub_group = app_commands.Group(name="hub", description="🎤 Système de salons vocaux temporaires")

    @hub_group.command(name="config", description="⚙️ Configurer le système de hub vocal")
    @app_commands.describe(
        channel="Canal vocal à utiliser comme hub",
        category="Catégorie où créer les canaux temporaires",
        limit="Limite d'utilisateurs par canal (1-99)"
    )
    async def hub_config(
        self, 
        interaction: discord.Interaction, 
        channel: discord.VoiceChannel,
        category: Optional[discord.CategoryChannel] = None,
        limit: Optional[int] = None
    ):
        """Configure le système de hub vocal"""
        
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Vous devez avoir la permission de gérer les canaux!", ephemeral=True)
            return
        
        config = await self.get_config(interaction.guild.id)
        
        config['hub_channel_id'] = channel.id
        if category:
            config['category_id'] = category.id
        if limit and 1 <= limit <= 99:
            config['channel_limit'] = limit
        
        await self.save_config(interaction.guild.id, config)
        await interaction.response.send_message(f"✅ Hub vocal configuré avec le canal {channel.mention}!", ephemeral=True)

    @hub_group.command(name="enable", description="✅ Activer le système de hub vocal")
    async def hub_enable(self, interaction: discord.Interaction):
        """Activer le hub vocal"""
        
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Vous devez avoir la permission de gérer les canaux!", ephemeral=True)
            return
        
        config = await self.get_config(interaction.guild.id)
        
        if not config.get('hub_channel_id'):
            await interaction.response.send_message("❌ Vous devez d'abord configurer un canal hub avec `/hub config`!", ephemeral=True)
            return
        
        config['enabled'] = True
        await self.save_config(interaction.guild.id, config)
        await interaction.response.send_message("✅ Hub vocal activé!", ephemeral=True)

    @hub_group.command(name="disable", description="❌ Désactiver le système de hub vocal")
    async def hub_disable(self, interaction: discord.Interaction):
        """Désactiver le hub vocal"""
        
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Vous devez avoir la permission de gérer les canaux!", ephemeral=True)
            return
        
        config = await self.get_config(interaction.guild.id)
        config['enabled'] = False
        await self.save_config(interaction.guild.id, config)
        await interaction.response.send_message("❌ Hub vocal désactivé!", ephemeral=True)

    @hub_group.command(name="status", description="📊 Voir le status du hub vocal")
    async def hub_status(self, interaction: discord.Interaction):
        """Status du hub vocal"""
        
        config = await self.get_config(interaction.guild.id)
        hub_channel = interaction.guild.get_channel(config.get('hub_channel_id')) if config.get('hub_channel_id') else None
        category = interaction.guild.get_channel(config.get('category_id')) if config.get('category_id') else None
        
        embed = discord.Embed(title="🎵 Status Hub Vocal", color=0x00ff00 if config.get('enabled') else 0xff0000)
        embed.add_field(name="État", value="✅ Activé" if config.get('enabled') else "❌ Désactivé", inline=True)
        embed.add_field(name="Canal Hub", value=hub_channel.mention if hub_channel else "❌ Non configuré", inline=True)
        embed.add_field(name="Catégorie", value=category.name if category else "Aucune", inline=True)
        embed.add_field(name="Limite par canal", value=config.get('channel_limit', 99), inline=True)
        embed.add_field(name="Canaux temporaires actifs", value=len(config.get('temp_channels', {})), inline=True)
        embed.add_field(name="Total créés", value=config.get('channel_counter', 0), inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def send_control_panel(self, temp_channel: discord.VoiceChannel, owner: discord.Member):
        """Envoie le panneau de contrôle dans le chat du salon temporaire"""
        try:
            # Trouver un salon textuel dans la même catégorie ou utiliser le général
            text_channels = [ch for ch in temp_channel.guild.text_channels if ch.category == temp_channel.category]
            if not text_channels:
                text_channels = temp_channel.guild.text_channels
            
            if not text_channels:
                return
            
            target_channel = text_channels[0]  # Premier salon textuel disponible
            
            embed = discord.Embed(
                title="🎵 Panneau de Contrôle - Salon Temporaire",
                description=f"**{temp_channel.name}** créé par {owner.mention}",
                color=0x00ff00
            )
            
            embed.add_field(
                name="🔧 Actions disponibles",
                value="• 🔒 Verrouiller/déverrouiller le salon\n• ✏️ Renommer le salon\n• 👥 Gérer la limite d'utilisateurs\n• 👁️ Rendre invisible/visible\n• 📋 Gérer whitelist/blacklist\n• ❌ Supprimer le salon",
                inline=False
            )
            
            embed.add_field(
                name="ℹ️ Informations",
                value=f"**Propriétaire:** {owner.mention}\n**Salon:** {temp_channel.mention}\n**Créé:** <t:{int(temp_channel.created_at.timestamp())}:R>",
                inline=False
            )
            
            view = TempChannelControlView(self, temp_channel.id, owner.id)
            
            await target_channel.send(embed=embed, view=view)
            
        except Exception as e:
            logging.error(f"❌ Erreur envoi panneau contrôle: {e}")

    def cog_unload(self):
        """Nettoie les tâches à l'arrêt"""
        self.auto_save.cancel()
        self.cleanup_empty_channels.cancel()


class TempChannelControlView(discord.ui.View):
    """Panneau de contrôle pour les salons vocaux temporaires"""
    
    def __init__(self, cog, channel_id: int, owner_id: int):
        super().__init__(timeout=None)
        self.cog = cog
        self.channel_id = channel_id
        self.owner_id = owner_id

    @discord.ui.button(label="🔒", style=discord.ButtonStyle.secondary, custom_id="lock_unlock")
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
            return await interaction.response.send_message("❌ Salon introuvable", ephemeral=True)
        
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

    @discord.ui.button(label="✏️", style=discord.ButtonStyle.primary, custom_id="rename")
    async def rename_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Renommer le salon"""
        
        if interaction.user.id != self.owner_id:
            embed = discord.Embed(
                title="❌ Permission refusée",
                description="Seul le propriétaire peut contrôler ce salon",
                color=0xff0000
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            return await interaction.response.send_message("❌ Salon introuvable", ephemeral=True)
        
        # Créer une modal pour le nom
        modal = RenameChannelModal(channel)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="👥", style=discord.ButtonStyle.green, custom_id="user_limit")
    async def change_user_limit(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Changer la limite d'utilisateurs"""
        
        if interaction.user.id != self.owner_id:
            embed = discord.Embed(
                title="❌ Permission refusée",
                description="Seul le propriétaire peut contrôler ce salon",
                color=0xff0000
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            return await interaction.response.send_message("❌ Salon introuvable", ephemeral=True)
        
        # Créer une modal pour la limite
        modal = UserLimitModal(channel)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="👁️", style=discord.ButtonStyle.secondary, custom_id="toggle_invisible")
    async def toggle_invisible(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Rendre le salon invisible/visible"""
        
        if interaction.user.id != self.owner_id:
            embed = discord.Embed(
                title="❌ Permission refusée",
                description="Seul le propriétaire peut contrôler ce salon",
                color=0xff0000
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            return await interaction.response.send_message("❌ Salon introuvable", ephemeral=True)
        
        # Toggle visibility
        current_perms = channel.overwrites_for(interaction.guild.default_role)
        is_visible = current_perms.view_channel is not False
        
        await channel.set_permissions(
            interaction.guild.default_role,
            view_channel=not is_visible,
            connect=None if not is_visible else False  # Si invisible, on peut pas se connecter non plus
        )
        
        embed = discord.Embed(
            title=f"{'👁️ Salon visible' if not is_visible else '🫥 Salon invisible'}",
            description=f"Le salon **{channel.name}** est maintenant {'visible' if not is_visible else 'invisible'} pour les autres",
            color=0x00ff00 if not is_visible else 0x666666
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="📋", style=discord.ButtonStyle.blurple, custom_id="manage_access")
    async def manage_access(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gérer whitelist/blacklist du salon"""
        
        if interaction.user.id != self.owner_id:
            embed = discord.Embed(
                title="❌ Permission refusée",
                description="Seul le propriétaire peut contrôler ce salon",
                color=0xff0000
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            return await interaction.response.send_message("❌ Salon introuvable", ephemeral=True)
        
        # Créer la vue de gestion d'accès
        view = AccessManagementView(channel, interaction.user)
        
        embed = discord.Embed(
            title="📋 Gestion des Accès",
            description=f"Gérez les accès au salon **{channel.name}**",
            color=0x5865f2
        )
        
        # Afficher les utilisateurs ayant des permissions spéciales
        whitelist_users = []
        blacklist_users = []
        
        for target, perms in channel.overwrites.items():
            if isinstance(target, discord.Member):
                if perms.connect is True:
                    whitelist_users.append(target.mention)
                elif perms.connect is False:
                    blacklist_users.append(target.mention)
        
        if whitelist_users:
            embed.add_field(
                name="✅ Whitelist",
                value="\n".join(whitelist_users[:5]) + (f"\n... et {len(whitelist_users)-5} autres" if len(whitelist_users) > 5 else ""),
                inline=True
            )
        
        if blacklist_users:
            embed.add_field(
                name="❌ Blacklist", 
                value="\n".join(blacklist_users[:5]) + (f"\n... et {len(blacklist_users)-5} autres" if len(blacklist_users) > 5 else ""),
                inline=True
            )
        
        if not whitelist_users and not blacklist_users:
            embed.add_field(
                name="ℹ️ Info",
                value="Aucune restriction d'accès définie",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="❌", style=discord.ButtonStyle.danger, custom_id="delete")
    async def delete_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Supprimer le salon"""
        
        if interaction.user.id != self.owner_id:
            embed = discord.Embed(
                title="❌ Permission refusée",
                description="Seul le propriétaire peut contrôler ce salon",
                color=0xff0000
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            return await interaction.response.send_message("❌ Salon introuvable", ephemeral=True)
        
        # Confirmation
        embed = discord.Embed(
            title="⚠️ Confirmation",
            description=f"Voulez-vous vraiment supprimer le salon **{channel.name}** ?",
            color=0xff9900
        )
        
        view = ConfirmDeleteView(channel, interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class RenameChannelModal(discord.ui.Modal):
    """Modal pour renommer un salon"""
    
    def __init__(self, channel: discord.VoiceChannel):
        self.channel = channel
        super().__init__(title=f"Renommer {channel.name}")
        
        self.name_input = discord.ui.TextInput(
            label="Nouveau nom du salon",
            placeholder=channel.name,
            default=channel.name,
            max_length=100
        )
        self.add_item(self.name_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        new_name = self.name_input.value.strip()
        
        if not new_name:
            return await interaction.response.send_message("❌ Le nom ne peut pas être vide!", ephemeral=True)
        
        try:
            old_name = self.channel.name
            await self.channel.edit(name=new_name)
            
            embed = discord.Embed(
                title="✅ Salon renommé",
                description=f"**{old_name}** → **{new_name}**",
                color=0x00ff00
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logging.error(f"❌ Erreur renommage salon: {e}")
            await interaction.response.send_message("❌ Erreur lors du renommage", ephemeral=True)


class UserLimitModal(discord.ui.Modal):
    """Modal pour changer la limite d'utilisateurs"""
    
    def __init__(self, channel: discord.VoiceChannel):
        self.channel = channel
        super().__init__(title=f"Limite - {channel.name}")
        
        self.limit_input = discord.ui.TextInput(
            label="Nouvelle limite d'utilisateurs",
            placeholder=str(channel.user_limit or 0),
            default=str(channel.user_limit or 0),
            max_length=2
        )
        self.add_item(self.limit_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            new_limit = int(self.limit_input.value)
            if new_limit < 0 or new_limit > 99:
                return await interaction.response.send_message("❌ La limite doit être entre 0 et 99!", ephemeral=True)
            
            await self.channel.edit(user_limit=new_limit if new_limit > 0 else None)
            
            embed = discord.Embed(
                title="✅ Limite modifiée",
                description=f"Nouvelle limite: **{new_limit if new_limit > 0 else 'Aucune'}**",
                color=0x00ff00
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Veuillez entrer un nombre valide!", ephemeral=True)
        except Exception as e:
            logging.error(f"❌ Erreur modification limite: {e}")
            await interaction.response.send_message("❌ Erreur lors de la modification", ephemeral=True)


class ConfirmDeleteView(discord.ui.View):
    """Vue de confirmation pour supprimer un salon"""
    
    def __init__(self, channel: discord.VoiceChannel, user: discord.Member):
        super().__init__(timeout=30)
        self.channel = channel
        self.user = user
    
    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.danger)
    async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ Seul le propriétaire peut confirmer", ephemeral=True)
        
        try:
            channel_name = self.channel.name
            await self.channel.delete(reason=f"Suppression demandée par {self.user}")
            
            embed = discord.Embed(
                title="✅ Salon supprimé",
                description=f"Le salon **{channel_name}** a été supprimé",
                color=0x00ff00
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logging.error(f"❌ Erreur suppression salon: {e}")
            await interaction.response.send_message("❌ Erreur lors de la suppression", ephemeral=True)
    
    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
    async def cancel_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ Seul le propriétaire peut annuler", ephemeral=True)
        
        embed = discord.Embed(
            title="❌ Suppression annulée",
            description="Le salon n'a pas été supprimé",
            color=0xff9900
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class AccessManagementView(discord.ui.View):
    """Vue pour gérer les accès (whitelist/blacklist) du salon"""
    
    def __init__(self, channel: discord.VoiceChannel, owner: discord.Member):
        super().__init__(timeout=300)  # 5 minutes
        self.channel = channel
        self.owner = owner
    
    @discord.ui.button(label="➕ Autoriser un utilisateur", style=discord.ButtonStyle.green)
    async def add_to_whitelist(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Ajouter un utilisateur à la whitelist"""
        
        if interaction.user.id != self.owner.id:
            return await interaction.response.send_message("❌ Seul le propriétaire peut gérer les accès", ephemeral=True)
        
        modal = UserAccessModal(self.channel, "whitelist", self.owner)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="➖ Interdire un utilisateur", style=discord.ButtonStyle.red)
    async def add_to_blacklist(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Ajouter un utilisateur à la blacklist"""
        
        if interaction.user.id != self.owner.id:
            return await interaction.response.send_message("❌ Seul le propriétaire peut gérer les accès", ephemeral=True)
        
        modal = UserAccessModal(self.channel, "blacklist", self.owner)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🧹 Nettoyer les accès", style=discord.ButtonStyle.secondary)
    async def clear_access(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Supprimer toutes les restrictions d'accès"""
        
        if interaction.user.id != self.owner.id:
            return await interaction.response.send_message("❌ Seul le propriétaire peut gérer les accès", ephemeral=True)
        
        # Confirmation
        embed = discord.Embed(
            title="⚠️ Confirmation",
            description="Voulez-vous supprimer toutes les restrictions d'accès ?",
            color=0xff9900
        )
        
        view = ConfirmClearAccessView(self.channel, self.owner)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class UserAccessModal(discord.ui.Modal):
    """Modal pour ajouter/retirer un utilisateur des listes d'accès"""
    
    def __init__(self, channel: discord.VoiceChannel, action_type: str, owner: discord.Member):
        self.channel = channel
        self.action_type = action_type  # "whitelist" ou "blacklist"
        self.owner = owner
        
        title = f"{'Autoriser' if action_type == 'whitelist' else 'Interdire'} un utilisateur"
        super().__init__(title=title)
        
        self.user_input = discord.ui.TextInput(
            label="Nom ou ID de l'utilisateur",
            placeholder="@utilisateur ou 123456789",
            max_length=100
        )
        self.add_item(self.user_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        user_input = self.user_input.value.strip()
        
        # Chercher l'utilisateur
        user = None
        
        # Par mention
        if user_input.startswith('<@') and user_input.endswith('>'):
            user_id = user_input.strip('<@!>')
            try:
                user = interaction.guild.get_member(int(user_id))
            except ValueError:
                pass
        
        # Par ID
        elif user_input.isdigit():
            user = interaction.guild.get_member(int(user_input))
        
        # Par nom d'utilisateur
        else:
            user = discord.utils.find(
                lambda m: m.display_name.lower() == user_input.lower() or m.name.lower() == user_input.lower(),
                interaction.guild.members
            )
        
        if not user:
            return await interaction.response.send_message("❌ Utilisateur introuvable!", ephemeral=True)
        
        if user.id == self.owner.id:
            return await interaction.response.send_message("❌ Vous ne pouvez pas vous restreindre vous-même!", ephemeral=True)
        
        try:
            if self.action_type == "whitelist":
                await self.channel.set_permissions(user, connect=True, view_channel=True)
                action_text = "autorisé à rejoindre"
                color = 0x00ff00
                emoji = "✅"
            else:  # blacklist
                await self.channel.set_permissions(user, connect=False, view_channel=True)
                # Expulser l'utilisateur s'il est dans le salon
                if user in self.channel.members:
                    await user.move_to(None, reason="Ajouté à la blacklist")
                action_text = "interdit de rejoindre"
                color = 0xff0000
                emoji = "❌"
            
            embed = discord.Embed(
                title=f"{emoji} Accès modifié",
                description=f"**{user.display_name}** est maintenant {action_text} le salon **{self.channel.name}**",
                color=color
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logging.error(f"❌ Erreur modification accès: {e}")
            await interaction.response.send_message("❌ Erreur lors de la modification des permissions", ephemeral=True)


class ConfirmClearAccessView(discord.ui.View):
    """Vue de confirmation pour nettoyer tous les accès"""
    
    def __init__(self, channel: discord.VoiceChannel, owner: discord.Member):
        super().__init__(timeout=30)
        self.channel = channel
        self.owner = owner
    
    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.danger)
    async def confirm_clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner.id:
            return await interaction.response.send_message("❌ Seul le propriétaire peut confirmer", ephemeral=True)
        
        try:
            # Supprimer toutes les permissions spécifiques aux membres
            for target, perms in list(self.channel.overwrites.items()):
                if isinstance(target, discord.Member) and target.id != self.owner.id:
                    await self.channel.set_permissions(target, overwrite=None)
            
            embed = discord.Embed(
                title="🧹 Accès nettoyés",
                description=f"Toutes les restrictions d'accès ont été supprimées du salon **{self.channel.name}**",
                color=0x00ff00
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logging.error(f"❌ Erreur nettoyage accès: {e}")
            await interaction.response.send_message("❌ Erreur lors du nettoyage", ephemeral=True)
    
    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
    async def cancel_clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner.id:
            return await interaction.response.send_message("❌ Seul le propriétaire peut annuler", ephemeral=True)
        
        embed = discord.Embed(
            title="❌ Nettoyage annulé",
            description="Les restrictions d'accès n'ont pas été modifiées",
            color=0xff9900
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(HubVocal(bot))

