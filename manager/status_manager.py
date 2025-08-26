"""
Arsenal Bot Status System - Système de statut dynamique avec keepalive
Maintient le bot en ligne sur Render et affiche des statuts rotatifs
"""
import asyncio
import random
import aiohttp
import discord
from discord.ext import tasks
import core.logger

log = core.logger.log

class ArsenalStatusSystem:
    def __init__(self, bot):
        self.bot = bot
        self.creator_name = "un développeur"  # Default value
        self.status_messages = [
            {'type': discord.ActivityType.watching, 'text': 'surveille {guild_count} serveurs.'},
            {'type': discord.ActivityType.watching, 'text': 'protège {member_count} utilisateurs.'},
            {'type': discord.ActivityType.playing, 'text': 'proposé par {creator_name}.'},
            {'type': discord.ActivityType.playing, 'text': '/help | Arsenal V4.5'},
        ]
        
        # Variables pour le keepalive
        self.render_url = "https://arsenal-bot-discord.onrender.com"
        self.keepalive_interval = 300  # 5 minutes
        
    async def start_status_rotation(self):
        """Démarre la rotation des statuts"""
        if not self.status_rotation.is_running():
            self.status_rotation.start()
            log.info("🔄 [STATUS] Rotation des statuts démarrée")
            
    async def start_keepalive(self):
        """Démarre le système keepalive pour Render"""
        if not self.render_keepalive.is_running():
            self.render_keepalive.start() 
            log.info("💚 [KEEPALIVE] Système keepalive Render démarré")

    @tasks.loop(seconds=15)  # Change le statut toutes les 15 secondes
    async def status_rotation(self):
        """Fait tourner les statuts du bot de manière aléatoire"""
        try:
            if not self.bot.is_ready():
                return
                
            # Sélectionne un statut au hasard
            status_info = random.choice(self.status_messages)
            status_text = status_info['text']
            activity_type = status_info['type']
            
            # Remplace les variables dynamiques
            if "{member_count}" in status_text:
                member_count = sum(guild.member_count or 0 for guild in self.bot.guilds)
                status_text = status_text.replace("{member_count}", str(member_count))
            if "{guild_count}" in status_text:
                guild_count = len(self.bot.guilds)
                status_text = status_text.replace("{guild_count}", str(guild_count))
            if "{creator_name}" in status_text:
                status_text = status_text.replace("{creator_name}", self.creator_name)
            
            activity = discord.Activity(
                type=activity_type,
                name=status_text
            )
            await self.bot.change_presence(status=discord.Status.online, activity=activity)
            
            log.debug(f"📱 [STATUS] Statut changé: {status_text}")
            
        except Exception as e:
            log.error(f"❌ [STATUS] Erreur rotation statut: {e}")

    @tasks.loop(seconds=300)  # Ping toutes les 5 minutes
    async def render_keepalive(self):
        """Maintient le service Render actif avec des requêtes régulières"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.render_url}/health", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        log.debug(f"💚 [KEEPALIVE] Health check OK: {data.get('status', 'unknown')}")
                    else:
                        log.warning(f"⚠️ [KEEPALIVE] Health check failed: {response.status}")
        except asyncio.TimeoutError:
            log.warning("⏰ [KEEPALIVE] Timeout lors du ping keepalive")
        except Exception as e:
            log.error(f"❌ [KEEPALIVE] Erreur keepalive: {e}")

    @status_rotation.before_loop
    async def before_status_rotation(self):
        """Attend que le bot soit prêt et récupère le nom du créateur"""
        await self.bot.wait_until_ready()
        try:
            creator_user = await self.bot.fetch_user(self.bot.creator_id)
            self.creator_name = creator_user.name
            log.info(f"[STATUS] Nom du créateur récupéré: {self.creator_name}")
        except Exception as e:
            log.error(f"[STATUS] Impossible de récupérer le nom du créateur: {e}")
        
    @render_keepalive.before_loop  
    async def before_keepalive(self):
        """Attend que le bot soit prêt avant de commencer le keepalive"""
        await self.bot.wait_until_ready()
        await asyncio.sleep(30)

# Instance globale pour l'import facile
status_system = None

def get_status_system():
    """Retourne l'instance du système de statut"""
    return status_system

def initialize_status_system(bot):
    """Initialise le système de statut"""
    global status_system
    if status_system is None:
        status_system = ArsenalStatusSystem(bot)
    return status_system
