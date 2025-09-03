# 🚀 Arsenal V4 - Système KeepAlive pour Render
"""
Système KeepAlive avancé pour maintenir le bot actif sur Render:
- Auto-ping intelligent pour éviter l'hibernation
- Monitoring de santé du bot
- Statistiques d'uptime
- Notifications de status
- Optimisations pour hébergement gratuit
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
import psutil
import time

class KeepAliveSystem(commands.Cog):
    """Système KeepAlive pour maintenir le bot actif"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "data/keepalive_config.json"
        self.stats_file = "data/uptime_stats.json"
        self.start_time = datetime.now()
        self.last_ping = datetime.now()
        self.ping_count = 0
        self.load_config()
        self.load_stats()
        
        # Démarrage automatique des tâches
        self.keepalive_task.start()
        self.health_monitor.start()
        self.stats_updater.start()

    def load_config(self):
        """Charge la configuration KeepAlive"""
        if not os.path.exists(self.config_file):
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            default_config = {
                "enabled": True,
                "ping_interval": 300,  # 5 minutes
                "ping_url": f"https://{os.getenv('RENDER_SERVICE_NAME', 'arsenal-bot')}.onrender.com",
                "health_checks": {
                    "memory_threshold": 80,  # %
                    "response_time_threshold": 5000  # ms
                },
                "notification_channel": None,
                "auto_restart": False
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
        
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {"enabled": True, "ping_interval": 300}

    def save_config(self):
        """Sauvegarde la configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def load_stats(self):
        """Charge les statistiques d'uptime"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            except:
                self.stats = self.init_stats()
        else:
            self.stats = self.init_stats()

    def init_stats(self):
        """Initialise les statistiques par défaut"""
        return {
            "total_uptime": 0,
            "total_pings": 0,
            "successful_pings": 0,
            "failed_pings": 0,
            "last_restart": datetime.now().isoformat(),
            "restart_count": 0,
            "average_response_time": 0,
            "health_score": 100
        }

    def save_stats(self):
        """Sauvegarde les statistiques"""
        os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

    @app_commands.command(name="keepalive", description="🔄 Gestion système KeepAlive")
    async def keepalive_menu(self, interaction: discord.Interaction):
        """Menu principal du système KeepAlive"""
        
        uptime = datetime.now() - self.start_time
        uptime_str = str(uptime).split('.')[0]
        
        embed = discord.Embed(
            title="🔄 Système KeepAlive Arsenal",
            description="Surveillance et maintien de l'activité du bot",
            color=discord.Color.green()
        )
        
        # Status principal
        status_emoji = "🟢" if self.config.get("enabled") else "🔴"
        embed.add_field(
            name=f"{status_emoji} Status",
            value=f"**Actif:** {self.config.get('enabled', False)}\n**Uptime:** {uptime_str}\n**Pings:** {self.ping_count}",
            inline=True
        )
        
        # Santé système
        try:
            memory_percent = psutil.virtual_memory().percent
            cpu_percent = psutil.cpu_percent()
            
            health_emoji = "🟢" if memory_percent < 70 else "🟡" if memory_percent < 85 else "🔴"
            embed.add_field(
                name=f"{health_emoji} Santé Système",
                value=f"**RAM:** {memory_percent:.1f}%\n**CPU:** {cpu_percent:.1f}%\n**Score:** {self.stats.get('health_score', 100)}/100",
                inline=True
            )
        except:
            embed.add_field(
                name="⚠️ Santé Système", 
                value="Données indisponibles",
                inline=True
            )
        
        # Configuration
        ping_interval = self.config.get("ping_interval", 300) // 60
        embed.add_field(
            name="⚙️ Configuration",
            value=f"**Intervalle:** {ping_interval} min\n**Auto-restart:** {self.config.get('auto_restart', False)}\n**Dernier ping:** <t:{int(self.last_ping.timestamp())}:R>",
            inline=False
        )
        
        embed.set_footer(text="Arsenal V4 KeepAlive • Pour Render.com")
        
        view = KeepAliveView(self)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="uptime", description="📊 Statistiques d'uptime")
    async def uptime_stats(self, interaction: discord.Interaction):
        """Affiche les statistiques détaillées d'uptime"""
        
        current_uptime = datetime.now() - self.start_time
        total_uptime_hours = self.stats.get("total_uptime", 0) + (current_uptime.total_seconds() / 3600)
        
        embed = discord.Embed(
            title="📊 Statistiques Arsenal KeepAlive",
            color=discord.Color.blue()
        )
        
        # Uptime
        embed.add_field(
            name="⏰ Temps de fonctionnement",
            value=f"**Session actuelle:** {str(current_uptime).split('.')[0]}\n**Total:** {total_uptime_hours:.1f}h\n**Dernière interruption:** <t:{int(datetime.fromisoformat(self.stats.get('last_restart', datetime.now().isoformat())).timestamp())}:R>",
            inline=False
        )
        
        # Statistiques pings
        total_pings = self.stats.get("total_pings", 0)
        success_pings = self.stats.get("successful_pings", 0)
        success_rate = (success_pings / total_pings * 100) if total_pings > 0 else 100
        
        embed.add_field(
            name="📡 Pings KeepAlive",
            value=f"**Total:** {total_pings}\n**Réussis:** {success_pings}\n**Taux de réussite:** {success_rate:.1f}%",
            inline=True
        )
        
        # Performance
        avg_response = self.stats.get("average_response_time", 0)
        health_score = self.stats.get("health_score", 100)
        
        embed.add_field(
            name="🎯 Performance",
            value=f"**Temps de réponse:** {avg_response:.0f}ms\n**Score de santé:** {health_score}/100\n**Redémarrages:** {self.stats.get('restart_count', 0)}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

    @tasks.loop(minutes=1)  # Réduire à 1 minute pour plus de stabilité
    async def keepalive_task(self):
        """Tâche principale de KeepAlive - Version optimisée"""
        if not self.config.get("enabled", True):
            return
        
        try:
            self.last_ping = datetime.now()
            self.ping_count += 1
            
            # Simple ping interne au lieu de requête HTTP externe
            latency = self.bot.latency * 1000  # Latency Discord en ms
            
            if latency < 1000:  # Si la latence est correcte
                self.stats["successful_pings"] = self.stats.get("successful_pings", 0) + 1
                print(f"🔄 [KeepAlive] Ping #{self.ping_count} - Latence: {latency:.0f}ms ✅")
            else:
                self.stats["failed_pings"] = self.stats.get("failed_pings", 0) + 1
                print(f"⚠️ [KeepAlive] Ping #{self.ping_count} - Latence élevée: {latency:.0f}ms")
            
            self.stats["total_pings"] = self.stats.get("total_pings", 0) + 1
            self.stats["average_response_time"] = latency
            
            # Sauvegarde légère toutes les 10 pings
            if self.ping_count % 10 == 0:
                self.save_stats()
                
        except Exception as e:
            print(f"❌ [KeepAlive] Erreur dans keepalive_task: {e}")
            self.stats["failed_pings"] = self.stats.get("failed_pings", 0) + 1
        
        try:
            ping_url = self.config.get("ping_url")
            if not ping_url:
                return
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(ping_url, timeout=5) as response:  # Réduire timeout
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status == 200:
                            self.ping_count += 1
                            self.last_ping = datetime.now()
                            self.stats["successful_pings"] += 1
                            
                            # Mettre à jour temps de réponse moyen
                            current_avg = self.stats.get("average_response_time", 0)
                            total_pings = self.stats.get("total_pings", 0)
                            self.stats["average_response_time"] = ((current_avg * total_pings) + response_time) / (total_pings + 1)
                        else:
                            self.stats["failed_pings"] += 1
                            
                except asyncio.TimeoutError:
                    self.stats["failed_pings"] += 1
                except Exception as e:
                    print(f"Erreur ping: {e}")
                    self.stats["failed_pings"] += 1
                
                self.stats["total_pings"] += 1
                
        except Exception as e:
            print(f"Erreur KeepAlive: {e}")
            self.stats["failed_pings"] += 1

    @tasks.loop(minutes=10)  # Réduire fréquence pour stabilité
    async def health_monitor(self):
        """Surveille la santé du système - Version simplifiée"""
        try:
            # Vérifications simplifiées sans psutil qui peut planter
            latency = self.bot.latency * 1000
            
            # Calcul score de santé basé sur la latence Discord
            health_score = 100
            
            if latency > 1000:  # > 1 seconde
                health_score -= 30
            elif latency > 500:  # > 500ms
                health_score -= 15
                
            # Vérifier si le bot répond
            if not self.bot.is_ready():
                health_score -= 50
                
            self.stats["health_score"] = max(0, health_score)
            
            print(f"🏥 [Health] Score: {health_score}/100 - Latence: {latency:.0f}ms")
                
        except Exception as e:
            print(f"❌ [Health] Erreur health monitor: {e}")
            self.stats["health_score"] = 50  # Score neutre en cas d'erreur

    @tasks.loop(minutes=30)  # Réduire fréquence pour éviter les erreurs
    async def stats_updater(self):
        """Met à jour les statistiques - Version simplifiée"""
        try:
            # Mise à jour simple sans calculs complexes
            current_uptime = (datetime.now() - self.start_time).total_seconds() / 3600
            self.stats["total_uptime"] = current_uptime
            
            # Sauvegarde toutes les 30 minutes au lieu de 15
            self.save_stats()
            print(f"💾 [Stats] Uptime: {current_uptime:.1f}h - Pings: {self.ping_count}")
            
        except Exception as e:
            print(f"❌ [Stats] Erreur stats_updater: {e}")
            
        except Exception as e:
            print(f"Erreur stats updater: {e}")

    async def emergency_restart(self):
        """Redémarrage d'urgence du bot"""
        try:
            self.stats["restart_count"] += 1
            self.stats["last_restart"] = datetime.now().isoformat()
            self.save_stats()
            
            # Notification si canal configuré
            channel_id = self.config.get("notification_channel")
            if channel_id:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    embed = discord.Embed(
                        title="🚨 Redémarrage d'Urgence",
                        description="Le bot redémarre pour maintenir les performances",
                        color=discord.Color.orange()
                    )
                    await channel.send(embed=embed)
            
            # Redémarrer (nécessite implémentation spécifique)
            print("🚨 Redémarrage d'urgence initié")
            
        except Exception as e:
            print(f"Erreur emergency restart: {e}")

class KeepAliveView(discord.ui.View):
    def __init__(self, keepalive_cog):
        super().__init__(timeout=60)
        self.keepalive = keepalive_cog

    @discord.ui.button(label="▶️ Activer", style=discord.ButtonStyle.success)
    async def toggle_on(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.keepalive.config["enabled"] = True
        self.keepalive.save_config()
        
        embed = discord.Embed(
            title="✅ KeepAlive Activé",
            description="Le système de maintien d'activité est maintenant actif",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="⏸️ Désactiver", style=discord.ButtonStyle.secondary)
    async def toggle_off(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.keepalive.config["enabled"] = False
        self.keepalive.save_config()
        
        embed = discord.Embed(
            title="⏸️ KeepAlive Désactivé",
            description="Le système de maintien d'activité est maintenant inactif",
            color=discord.Color.orange()
        )
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="🔄 Ping Manuel", style=discord.ButtonStyle.primary)
    async def manual_ping(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Ping manuel
        ping_url = self.keepalive.config.get("ping_url")
        if ping_url:
            try:
                start_time = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.get(ping_url, timeout=10) as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status == 200:
                            embed = discord.Embed(
                                title="✅ Ping Réussi",
                                description=f"Temps de réponse: {response_time:.0f}ms",
                                color=discord.Color.green()
                            )
                        else:
                            embed = discord.Embed(
                                title="❌ Ping Échoué",
                                description=f"Code: {response.status}",
                                color=discord.Color.red()
                            )
            except Exception as e:
                embed = discord.Embed(
                    title="❌ Erreur Ping",
                    description=f"Erreur: {str(e)}",
                    color=discord.Color.red()
                )
        else:
            embed = discord.Embed(
                title="⚠️ Pas d'URL",
                description="URL de ping non configurée",
                color=discord.Color.orange()
            )
        
        await interaction.followup.edit_message(interaction.message.id, embed=embed, view=None)

async def setup(bot):
    await bot.add_cog(KeepAliveSystem(bot))
    print("🔄 [KeepAlive System] Module chargé avec succès!")

