"""
Arsenal Bot Status System - Système de statut dynamique avec keepalive
Maintient le bot en ligne sur Render et affiche des statuts rotatifs
"""
import asyncio
import random
import aiohttp
from datetime import datetime, timezone
from discord.ext import tasks
from core.logger import get_logger

log = get_logger(__name__)

class ArsenalStatusSystem:
    def __init__(self, bot):
        self.bot = bot
        self.current_status_index = 0
        self.status_messages = [
            # Statuts généraux
            "🚀 Arsenal V4.5.0 | /help",
            "💎 ArsenalCoin actif | /balance",
            "⚙️ 150+ commandes | /config", 
            "🛍️ Boutique Arsenal | /shop",
            "📈 Système XP | /level",
            "🎵 Musique HD | /play",
            "🎮 Jeux intégrés | /games",
            "🔧 Configuration facile | /config",
            
            # Statuts économiques
            "💰 Gagnez des ArsenalCoins quotidiens !",
            "🏪 Nouvelle boutique serveur disponible",
            "💸 Transférez vos AC avec /pay",
            "📊 Consultez le top richesse | /leaderboard money",
            
            # Statuts communautaires  
            "👥 {member_count} membres connectés",
            "🌟 Niveau up avec les messages !",
            "🎯 Créez des sondages | /poll",
            "📝 Suggestions ouvertes | /suggest",
            
            # Statuts techniques
            "⚡ Hébergé sur Render Cloud",
            "🔄 Mise à jour automatique active",
            "🛡️ Sécurité Arsenal maximale", 
            "📡 Latence optimisée",
            
            # Statuts spéciaux
            "🎉 Merci pour votre confiance !",
            "🚀 Arsenal Bot - By xerox3elite",
            "💫 L'avenir du Discord français",
            "🏆 #1 Bot multifonctionnel FR"
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

    @tasks.loop(seconds=45)  # Change le statut toutes les 45 secondes
    async def status_rotation(self):
        """Fait tourner les statuts du bot"""
        try:
            if not self.bot.is_ready():
                return
                
            # Sélectionne le statut suivant
            status_text = self.status_messages[self.current_status_index]
            
            # Remplace les variables dynamiques
            if "{member_count}" in status_text:
                member_count = sum(guild.member_count or 0 for guild in self.bot.guilds)
                status_text = status_text.replace("{member_count}", str(member_count))
            
            # Change le statut
            import discord
            activity = discord.Game(name=status_text)
            await self.bot.change_presence(
                status=discord.Status.online, 
                activity=activity
            )
            
            # Passe au statut suivant
            self.current_status_index = (self.current_status_index + 1) % len(self.status_messages)
            
            log.debug(f"📱 [STATUS] Statut changé: {status_text}")
            
        except Exception as e:
            log.error(f"❌ [STATUS] Erreur rotation statut: {e}")

    @tasks.loop(seconds=300)  # Ping toutes les 5 minutes
    async def render_keepalive(self):
        """Maintient le service Render actif avec des requêtes régulières"""
        try:
            async with aiohttp.ClientSession() as session:
                # Ping de la route health
                async with session.get(f"{self.render_url}/health", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        log.debug(f"💚 [KEEPALIVE] Health check OK: {data.get('status', 'unknown')}")
                    else:
                        log.warning(f"⚠️ [KEEPALIVE] Health check failed: {response.status}")
                
                # Ping de la route principale
                await asyncio.sleep(2)
                async with session.get(self.render_url, timeout=10) as response:
                    if response.status == 200:
                        log.debug("💚 [KEEPALIVE] Main route ping successful")
                    else:
                        log.warning(f"⚠️ [KEEPALIVE] Main route ping failed: {response.status}")
                        
        except asyncio.TimeoutError:
            log.warning("⏰ [KEEPALIVE] Timeout lors du ping keepalive")
        except Exception as e:
            log.error(f"❌ [KEEPALIVE] Erreur keepalive: {e}")

    @status_rotation.before_loop
    async def before_status_rotation(self):
        """Attend que le bot soit prêt avant de commencer la rotation"""
        await self.bot.wait_until_ready()
        
    @render_keepalive.before_loop  
    async def before_keepalive(self):
        """Attend que le bot soit prêt avant de commencer le keepalive"""
        await self.bot.wait_until_ready()
        await asyncio.sleep(30)  # Attend 30s après le démarrage

    def add_custom_status(self, status: str):
        """Ajoute un statut personnalisé à la liste"""
        if status not in self.status_messages:
            self.status_messages.append(status)
            log.info(f"➕ [STATUS] Statut ajouté: {status}")

    def remove_custom_status(self, status: str):
        """Supprime un statut personnalisé"""
        if status in self.status_messages:
            self.status_messages.remove(status)
            log.info(f"➖ [STATUS] Statut supprimé: {status}")

    def get_status_info(self):
        """Retourne les informations sur le système de statut"""
        return {
            "total_statuses": len(self.status_messages),
            "current_index": self.current_status_index,
            "current_status": self.status_messages[self.current_status_index],
            "rotation_active": self.status_rotation.is_running(),
            "keepalive_active": self.render_keepalive.is_running(),
            "next_rotation": "45 secondes",
            "next_keepalive": "5 minutes"
        }

# Instance globale pour l'import facile
status_system = None

def get_status_system():
    """Retourne l'instance du système de statut"""
    return status_system

def initialize_status_system(bot):
    """Initialise le système de statut"""
    global status_system
    status_system = ArsenalStatusSystem(bot)
    return status_system
