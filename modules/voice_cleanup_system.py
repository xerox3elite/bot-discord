"""
Arsenal Voice Cleanup System V4.5.2  
Nettoyage automatique des salons vocaux temporaires vides
"""

import discord
from discord.ext import commands, tasks
import logging
import json
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class VoiceCleanupManager:
    """Gestionnaire de nettoyage vocal"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.temp_channels_file = "temp_voice_channels.json"
        self.load_temp_channels()
        self.cleanup_task.start()
    
    def load_temp_channels(self):
        """Charge la liste des salons temporaires"""
        try:
            if os.path.exists(self.temp_channels_file):
                with open(self.temp_channels_file, 'r', encoding='utf-8') as f:
                    self.temp_channels = json.load(f)
            else:
                self.temp_channels = {}
            logger.info(f"📂 {len(self.temp_channels)} salons temporaires chargés")
        except Exception as e:
            logger.error(f"Erreur chargement temp channels: {e}")
            self.temp_channels = {}
    
    def save_temp_channels(self):
        """Sauvegarde la liste des salons temporaires"""
        try:
            with open(self.temp_channels_file, 'w', encoding='utf-8') as f:
                json.dump(self.temp_channels, f, indent=2)
        except Exception as e:
            logger.error(f"Erreur sauvegarde temp channels: {e}")
    
    def add_temp_channel(self, channel_id: int, guild_id: int, creator_id: int):
        """Ajoute un salon temporaire"""
        self.temp_channels[str(channel_id)] = {
            "guild_id": guild_id,
            "creator_id": creator_id,
            "created_at": datetime.now().isoformat(),
            "last_check": datetime.now().isoformat()
        }
        self.save_temp_channels()
        logger.info(f"➕ Salon temporaire ajouté: {channel_id}")
    
    def remove_temp_channel(self, channel_id: int):
        """Supprime un salon temporaire de la liste"""
        channel_str = str(channel_id)
        if channel_str in self.temp_channels:
            del self.temp_channels[channel_str]
            self.save_temp_channels()
            logger.info(f"➖ Salon temporaire retiré: {channel_id}")
    
    @tasks.loop(minutes=5)  # Vérification toutes les 5 minutes
    async def cleanup_task(self):
        """Tâche de nettoyage automatique"""
        try:
            channels_to_remove = []
            
            for channel_id_str, data in list(self.temp_channels.items()):
                try:
                    channel_id = int(channel_id_str)
                    guild_id = data.get("guild_id")
                    
                    # Trouver le serveur
                    guild = self.bot.get_guild(guild_id)
                    if not guild:
                        channels_to_remove.append(channel_id)
                        logger.warning(f"🔍 Serveur {guild_id} introuvable pour salon {channel_id}")
                        continue
                    
                    # Trouver le salon
                    channel = guild.get_channel(channel_id)
                    if not channel:
                        channels_to_remove.append(channel_id)
                        logger.warning(f"🔍 Salon {channel_id} introuvable")
                        continue
                    
                    # Vérifier si c'est un salon vocal
                    if not isinstance(channel, discord.VoiceChannel):
                        channels_to_remove.append(channel_id)
                        continue
                    
                    # Vérifier si le salon est vide
                    if len(channel.members) == 0:
                        # Salon vide depuis au moins 2 minutes
                        created_at = datetime.fromisoformat(data.get("created_at"))
                        if datetime.now() - created_at > timedelta(minutes=2):
                            try:
                                await channel.delete(reason="Salon vocal temporaire vide - nettoyage automatique")
                                channels_to_remove.append(channel_id)
                                logger.info(f"🧹 Salon temporaire {channel.name} ({channel_id}) supprimé - vide")
                            except discord.Forbidden:
                                logger.warning(f"❌ Permissions insuffisantes pour supprimer {channel_id}")
                            except discord.NotFound:
                                channels_to_remove.append(channel_id)
                                logger.info(f"🔍 Salon {channel_id} déjà supprimé")
                            except Exception as e:
                                logger.error(f"Erreur suppression salon {channel_id}: {e}")
                    else:
                        # Mettre à jour la dernière vérification
                        self.temp_channels[channel_id_str]["last_check"] = datetime.now().isoformat()
                        
                except Exception as e:
                    logger.error(f"Erreur traitement salon {channel_id_str}: {e}")
                    channels_to_remove.append(int(channel_id_str))
            
            # Nettoyer les salons supprimés de la liste
            for channel_id in channels_to_remove:
                self.remove_temp_channel(channel_id)
            
            if channels_to_remove:
                logger.info(f"🧹 Nettoyage terminé: {len(channels_to_remove)} salons supprimés")
            
        except Exception as e:
            logger.error(f"Erreur task cleanup: {e}")
    
    @cleanup_task.before_loop
    async def before_cleanup(self):
        """Attendre que le bot soit prêt"""
        await self.bot.wait_until_ready()
        logger.info("🧹 Système de nettoyage vocal démarré")
    
    async def startup_cleanup(self):
        """Nettoyage au démarrage du bot"""
        try:
            logger.info("🧹 Démarrage du nettoyage vocal au startup...")
            
            # Analyser tous les serveurs
            total_cleaned = 0
            for guild in self.bot.guilds:
                try:
                    for channel in guild.voice_channels:
                        # Vérifier si c'est un salon temporaire (par nom ou ID)
                        channel_id_str = str(channel.id)
                        
                        if channel_id_str in self.temp_channels:
                            # Salon temporaire connu
                            if len(channel.members) == 0:
                                try:
                                    await channel.delete(reason="Nettoyage startup - salon temporaire vide")
                                    self.remove_temp_channel(channel.id)
                                    total_cleaned += 1
                                    logger.info(f"🧹 [STARTUP] Salon {channel.name} supprimé du serveur {guild.name}")
                                except Exception as e:
                                    logger.error(f"Erreur suppression startup {channel.id}: {e}")
                        
                        # Détection par nom (salons commençant par "🎤 " ou contenant "Temp")
                        elif (channel.name.startswith("🎤 ") or "Temp" in channel.name or "temp" in channel.name):
                            if len(channel.members) == 0:
                                try:
                                    await channel.delete(reason="Nettoyage startup - salon temporaire détecté vide")
                                    total_cleaned += 1
                                    logger.info(f"🧹 [STARTUP] Salon détecté {channel.name} supprimé du serveur {guild.name}")
                                except Exception as e:
                                    logger.error(f"Erreur suppression détecté {channel.id}: {e}")
                
                except Exception as e:
                    logger.error(f"Erreur analyse serveur {guild.name}: {e}")
            
            logger.info(f"✅ Nettoyage startup terminé: {total_cleaned} salons supprimés")
            
        except Exception as e:
            logger.error(f"Erreur startup_cleanup: {e}")

class VoiceCleanupCog(commands.Cog):
    """Cog pour le nettoyage vocal"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cleanup_manager = VoiceCleanupManager(bot)
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Nettoyage au démarrage"""
        await self.cleanup_manager.startup_cleanup()
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Surveille les changements d'état vocal"""
        try:
            # Si quelqu'un quitte un salon temporaire
            if before.channel and not after.channel:
                channel_id_str = str(before.channel.id)
                if channel_id_str in self.cleanup_manager.temp_channels:
                    # Vérifier si le salon est maintenant vide
                    if len(before.channel.members) == 0:
                        # Attendre 30 secondes avant de supprimer
                        await asyncio.sleep(30)
                        
                        # Re-vérifier si toujours vide
                        fresh_channel = self.bot.get_channel(before.channel.id)
                        if fresh_channel and len(fresh_channel.members) == 0:
                            try:
                                await fresh_channel.delete(reason="Salon vocal temporaire vide")
                                self.cleanup_manager.remove_temp_channel(before.channel.id)
                                logger.info(f"🧹 Salon temporaire {fresh_channel.name} supprimé après départ")
                            except Exception as e:
                                logger.error(f"Erreur suppression après départ: {e}")
        
        except Exception as e:
            logger.error(f"Erreur voice_state_update: {e}")

# Instance globale
_voice_cleanup_manager = None

def get_voice_cleanup_manager():
    return _voice_cleanup_manager

def set_voice_cleanup_manager(manager):
    global _voice_cleanup_manager
    _voice_cleanup_manager = manager

async def setup(bot: commands.Bot):
    """Setup function"""
    cog = VoiceCleanupCog(bot)
    await bot.add_cog(cog)
    set_voice_cleanup_manager(cog.cleanup_manager)
    logger.info("✅ Arsenal Voice Cleanup System V4.5.2 chargé")

async def teardown(bot: commands.Bot):
    """Teardown function"""
    if _voice_cleanup_manager:
        _voice_cleanup_manager.cleanup_task.cancel()
    logger.info("🔄 Arsenal Voice Cleanup System déchargé")
