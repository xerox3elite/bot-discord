"""
Arsenal Bot - Status Loop System
Gestion du statut Discord avec keepalive et rotation d'activités
"""
import discord
import asyncio
import random
from datetime import datetime

class ArsenalStatusLoop:
    def __init__(self, bot):
        self.bot = bot
        self.current_status = 0
        
        # Statuts personnalisables
        self.status_list = [
            {"type": discord.ActivityType.playing, "name": "Arsenal V4.5.0 | /help"},
            {"type": discord.ActivityType.watching, "name": "{guilds} serveurs | 150+ commandes"},
            {"type": discord.ActivityType.listening, "name": "les commandes Arsenal"},
            {"type": discord.ActivityType.playing, "name": "ArsenalCoin Economy | /balance"},
            {"type": discord.ActivityType.watching, "name": "{users} utilisateurs"},
            {"type": discord.ActivityType.playing, "name": "/config pour tout configurer"},
            {"type": discord.ActivityType.listening, "name": "discord.gg/arsenal"},
            {"type": discord.ActivityType.playing, "name": "WebPanel disponible !"},
            {"type": discord.ActivityType.watching, "name": "Render Deploy Ready 🚀"},
        ]
        
        self.keepalive_interval = 30  # secondes entre chaque changement
        self.status_task = None
    
    async def start_status_loop(self):
        """Démarre la boucle de statut"""
        if self.status_task is not None:
            self.status_task.cancel()
        
        self.status_task = asyncio.create_task(self._status_loop())
        print("[STATUS] Boucle de statut Arsenal démarrée")
    
    async def stop_status_loop(self):
        """Arrête la boucle de statut"""
        if self.status_task:
            self.status_task.cancel()
            self.status_task = None
            print("[STATUS] Boucle de statut Arsenal arrêtée")
    
    async def _status_loop(self):
        """Boucle principale de changement de statut"""
        await self.bot.wait_until_ready()
        
        while not self.bot.is_closed():
            try:
                # Récupère le statut actuel
                status_data = self.status_list[self.current_status]
                
                # Remplace les variables dynamiques
                activity_name = self._replace_variables(status_data["name"])
                
                # Crée l'activité
                activity = discord.Activity(
                    type=status_data["type"],
                    name=activity_name
                )
                
                # Change le statut
                await self.bot.change_presence(
                    status=discord.Status.online,
                    activity=activity
                )
                
                print(f"[STATUS] Statut changé: {status_data['type'].name} {activity_name}")
                
                # Passe au statut suivant
                self.current_status = (self.current_status + 1) % len(self.status_list)
                
                # Keepalive pour Render
                await self._keepalive_ping()
                
                # Attendre avant le prochain changement
                await asyncio.sleep(self.keepalive_interval)
                
            except Exception as e:
                print(f"[STATUS ERROR] Erreur dans la boucle de statut: {e}")
                await asyncio.sleep(60)  # Attendre plus longtemps en cas d'erreur
    
    def _replace_variables(self, text):
        """Remplace les variables dynamiques dans le texte"""
        guild_count = len(self.bot.guilds)
        user_count = sum(guild.member_count or 0 for guild in self.bot.guilds)
        
        replacements = {
            "{guilds}": str(guild_count),
            "{users}": str(user_count),
            "{uptime}": self._get_uptime()
        }
        
        for var, value in replacements.items():
            text = text.replace(var, value)
        
        return text
    
    def _get_uptime(self):
        """Calcule l'uptime du bot"""
        if hasattr(self.bot, 'startup_time'):
            uptime = datetime.now(datetime.timezone.utc) - self.bot.startup_time
            hours = int(uptime.total_seconds() // 3600)
            minutes = int((uptime.total_seconds() % 3600) // 60)
            return f"{hours}h{minutes}m"
        return "N/A"
    
    async def _keepalive_ping(self):
        """Ping de keepalive pour maintenir la connexion Render"""
        try:
            # Simple ping pour maintenir l'activité
            latency = round(self.bot.latency * 1000, 2)
            if latency < 100:
                print(f"[KEEPALIVE] Latency: {latency}ms - Excellent")
            elif latency < 300:
                print(f"[KEEPALIVE] Latency: {latency}ms - Bon")
            else:
                print(f"[KEEPALIVE] Latency: {latency}ms - Lent")
                
        except Exception as e:
            print(f"[KEEPALIVE ERROR] {e}")
    
    def add_custom_status(self, activity_type, name):
        """Ajoute un statut personnalisé à la liste"""
        self.status_list.append({
            "type": activity_type,
            "name": name
        })
        print(f"[STATUS] Statut ajouté: {activity_type.name} {name}")
    
    def remove_status(self, index):
        """Supprime un statut de la liste"""
        if 0 <= index < len(self.status_list):
            removed = self.status_list.pop(index)
            print(f"[STATUS] Statut supprimé: {removed}")
        else:
            print("[STATUS ERROR] Index de statut invalide")
    
    def set_keepalive_interval(self, seconds):
        """Change l'intervalle de keepalive"""
        self.keepalive_interval = max(10, seconds)  # Minimum 10 secondes
        print(f"[STATUS] Intervalle keepalive changé: {self.keepalive_interval}s")
