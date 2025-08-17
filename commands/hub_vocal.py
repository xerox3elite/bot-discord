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
from datetime import datetime, timedelta
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
            
            # Déplacer l'utilisateur
            await member.move_to(temp_channel)
            
            # Sauvegarder dans la config
            temp_channels = config.get('temp_channels', {})
            temp_channels[str(temp_channel.id)] = member.id
            config['temp_channels'] = temp_channels
            config['channel_counter'] = config.get('channel_counter', 0) + 1
            await self.save_config(guild.id, config)
            
            logging.info(f"🎵 Canal temporaire créé: {channel_name} pour {member.display_name}")
            
        except Exception as e:
            logging.error(f"❌ Erreur création canal temporaire: {e}")

    @app_commands.command(name="hub_vocal", description="Configure le système de hub vocal temporaire")
    @app_commands.describe(
        action="Action à effectuer",
        channel="Canal vocal à utiliser comme hub",
        category="Catégorie où créer les canaux temporaires",
        limit="Limite d'utilisateurs par canal (1-99)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="activer", value="enable"),
        app_commands.Choice(name="désactiver", value="disable"),
        app_commands.Choice(name="configurer", value="setup"),
        app_commands.Choice(name="status", value="status")
    ])
    async def hub_vocal(
        self, 
        interaction: discord.Interaction, 
        action: app_commands.Choice[str],
        channel: Optional[discord.VoiceChannel] = None,
        category: Optional[discord.CategoryChannel] = None,
        limit: Optional[int] = None
    ):
        """Commande principale pour configurer le hub vocal"""
        
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Vous devez avoir la permission de gérer les canaux!", ephemeral=True)
            return
        
        config = await self.get_config(interaction.guild.id)
        
        if action.value == "enable":
            if not config.get('hub_channel_id'):
                await interaction.response.send_message("❌ Vous devez d'abord configurer un canal hub avec `/hub_vocal setup`!", ephemeral=True)
                return
            
            config['enabled'] = True
            await self.save_config(interaction.guild.id, config)
            await interaction.response.send_message("✅ Hub vocal activé!", ephemeral=True)
            
        elif action.value == "disable":
            config['enabled'] = False
            await self.save_config(interaction.guild.id, config)
            await interaction.response.send_message("❌ Hub vocal désactivé!", ephemeral=True)
            
        elif action.value == "setup":
            if not channel:
                await interaction.response.send_message("❌ Vous devez spécifier un canal vocal pour le hub!", ephemeral=True)
                return
            
            config['hub_channel_id'] = channel.id
            if category:
                config['category_id'] = category.id
            if limit and 1 <= limit <= 99:
                config['channel_limit'] = limit
            
            await self.save_config(interaction.guild.id, config)
            await interaction.response.send_message(f"✅ Hub vocal configuré avec le canal {channel.mention}!", ephemeral=True)
            
        elif action.value == "status":
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

    def cog_unload(self):
        """Nettoie les tâches à l'arrêt"""
        self.auto_save.cancel()
        self.cleanup_empty_channels.cancel()

async def setup(bot):
    await bot.add_cog(HubVocal(bot))
