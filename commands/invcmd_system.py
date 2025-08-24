"""
🖥️ ARSENAL INVCMD MONITORING SYSTEM V1.0
Système de monitoring et terminal de débogage

Fonctionnalités:
- Terminal intégré pour surveillance bot
- Logs en temps réel des commandes
- Monitoring des erreurs et exceptions
- Interface de débogage avancée
- Commandes créateurs uniquement

Author: Arsenal Bot Team
Version: 1.0.0
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import logging
import traceback
import sys
import os
import subprocess
import psutil
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import json

# Configuration des créateurs autorisés
CREATOR_IDS = [
    # Ajoutez vos IDs Discord ici
    123456789012345678,  # Remplacez par votre véritable ID
]

logger = logging.getLogger(__name__)

# =============================================================================
# GESTIONNAIRE DE MONITORING
# =============================================================================

class MonitoringManager:
    """Gestionnaire principal du système de monitoring"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_sessions = {}  # Sessions de monitoring actives
        self.command_logs = []  # Historique des commandes
        self.error_logs = []   # Historique des erreurs
        self.max_logs = 1000   # Limite des logs en mémoire
        
        # Configurer le logging personnalisé
        self.setup_custom_logging()
    
    def setup_custom_logging(self):
        """Configure le système de logging personnalisé"""
        # Handler personnalisé pour capturer les logs
        self.log_handler = MonitoringLogHandler(self)
        self.log_handler.setLevel(logging.INFO)
        
        # Format des logs
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        )
        self.log_handler.setFormatter(formatter)
        
        # Ajouter le handler au logger racine
        logging.getLogger().addHandler(self.log_handler)
    
    def log_command(self, ctx: commands.Context, command_name: str, success: bool, error: str = None):
        """Enregistre l'exécution d'une commande"""
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'guild_id': ctx.guild.id if ctx.guild else None,
            'guild_name': ctx.guild.name if ctx.guild else 'DM',
            'channel_id': ctx.channel.id,
            'user_id': ctx.author.id,
            'user_name': str(ctx.author),
            'command': command_name,
            'success': success,
            'error': error
        }
        
        self.command_logs.append(log_entry)
        
        # Limiter la taille des logs
        if len(self.command_logs) > self.max_logs:
            self.command_logs = self.command_logs[-self.max_logs:]
        
        # Notifier les sessions actives
        asyncio.create_task(self.notify_sessions('command', log_entry))
    
    def log_error(self, error: Exception, context: str = None):
        """Enregistre une erreur"""
        error_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        self.error_logs.append(error_entry)
        
        # Limiter la taille des logs
        if len(self.error_logs) > self.max_logs:
            self.error_logs = self.error_logs[-self.max_logs:]
        
        # Notifier les sessions actives
        asyncio.create_task(self.notify_sessions('error', error_entry))
    
    async def notify_sessions(self, log_type: str, log_entry: Dict[str, Any]):
        """Notifie toutes les sessions actives d'un nouveau log"""
        if not self.active_sessions:
            return
        
        # Format du message selon le type
        if log_type == 'command':
            status_emoji = "✅" if log_entry['success'] else "❌"
            message = f"{status_emoji} **{log_entry['command']}** par {log_entry['user_name']} dans {log_entry['guild_name']}"
            if not log_entry['success'] and log_entry['error']:
                message += f"\n```{log_entry['error'][:200]}```"
        
        elif log_type == 'error':
            message = f"🚨 **{log_entry['error_type']}**: {log_entry['error_message']}"
            if log_entry['context']:
                message += f"\n📍 **Contexte**: {log_entry['context']}"
        
        else:
            message = f"📝 **Log**: {log_entry}"
        
        # Envoyer à toutes les sessions actives
        for user_id, session in self.active_sessions.items():
            try:
                if session['channel'] and not session['channel'].is_closed():
                    embed = discord.Embed(
                        description=message,
                        color=0x00FF00 if log_type == 'command' and log_entry.get('success') else 0xFF0000,
                        timestamp=datetime.now(timezone.utc)
                    )
                    await session['channel'].send(embed=embed)
            except Exception as e:
                logger.error(f"Erreur notification session {user_id}: {e}")
    
    async def start_monitoring_session(self, user: discord.User) -> discord.DMChannel:
        """Démarre une session de monitoring pour un utilisateur"""
        if user.id in self.active_sessions:
            return self.active_sessions[user.id]['channel']
        
        # Créer le canal DM
        dm_channel = await user.create_dm()
        
        # Enregistrer la session
        self.active_sessions[user.id] = {
            'channel': dm_channel,
            'started_at': datetime.now(timezone.utc),
            'user': user
        }
        
        # Message de bienvenue
        embed = discord.Embed(
            title="🖥️ Session de Monitoring Arsenal",
            description="""
**Terminal de débogage activé !**

Vous recevrez désormais :
• ✅ Logs des commandes exécutées
• 🚨 Erreurs et exceptions
• 📊 Statistiques en temps réel
• 🔧 Informations de débogage

**Commandes disponibles :**
• `!logs` - Historique des logs récents
• `!errors` - Historique des erreurs
• `!stats` - Statistiques du bot
• `!stop` - Arrêter le monitoring
            """,
            color=0x00FF88
        )
        
        await dm_channel.send(embed=embed)
        
        return dm_channel
    
    def stop_monitoring_session(self, user_id: int) -> bool:
        """Arrête une session de monitoring"""
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]
            return True
        return False
    
    def get_recent_logs(self, count: int = 10) -> List[Dict[str, Any]]:
        """Récupère les logs récents"""
        return self.command_logs[-count:] if self.command_logs else []
    
    def get_recent_errors(self, count: int = 10) -> List[Dict[str, Any]]:
        """Récupère les erreurs récentes"""
        return self.error_logs[-count:] if self.error_logs else []
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques système"""
        process = psutil.Process(os.getpid())
        
        return {
            'bot_uptime': str(datetime.now(timezone.utc) - self.bot.start_time) if hasattr(self.bot, 'start_time') else 'Inconnue',
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': process.memory_percent(),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'guilds_count': len(self.bot.guilds),
            'users_count': len(set(self.bot.get_all_members())),
            'commands_today': len([log for log in self.command_logs if log['timestamp'].startswith(datetime.now().strftime('%Y-%m-%d'))]),
            'errors_today': len([error for error in self.error_logs if error['timestamp'].startswith(datetime.now().strftime('%Y-%m-%d'))]),
            'active_sessions': len(self.active_sessions)
        }


class MonitoringLogHandler(logging.Handler):
    """Handler personnalisé pour capturer les logs"""
    
    def __init__(self, monitoring_manager: MonitoringManager):
        super().__init__()
        self.monitoring_manager = monitoring_manager
    
    def emit(self, record):
        """Traite un enregistrement de log"""
        try:
            # Ignorer les logs de discord.py trop verbeux
            if record.name.startswith('discord.') and record.levelno < logging.WARNING:
                return
            
            # Créer l'entrée de log
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module if hasattr(record, 'module') else 'Unknown'
            }
            
            # Notifier les sessions actives pour les logs importants
            if record.levelno >= logging.WARNING:
                asyncio.create_task(
                    self.monitoring_manager.notify_sessions('log', log_entry)
                )
                
        except Exception:
            self.handleError(record)


# =============================================================================
# COMMANDES DE MONITORING
# =============================================================================

class InvcmdSystem(commands.Cog):
    """🖥️ Système de monitoring et terminal de débogage Arsenal"""
    
    def __init__(self, bot):
        self.bot = bot
        self.monitoring = MonitoringManager(bot)
        
        # Enregistrer l'heure de démarrage du bot
        if not hasattr(bot, 'start_time'):
            bot.start_time = datetime.now(timezone.utc)
    
    def is_creator(self, user_id: int) -> bool:
        """Vérifie si l'utilisateur est un créateur autorisé"""
        return user_id in CREATOR_IDS
    
    @app_commands.command(name="invcmd", description="🖥️ Terminal de monitoring et débogage (créateurs uniquement)")
    async def invcmd(self, interaction: discord.Interaction):
        """Commande principale de monitoring"""
        
        if not self.is_creator(interaction.user.id):
            embed = discord.Embed(
                title="❌ Accès Refusé",
                description="Cette commande est réservée aux créateurs du bot.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Démarrer la session de monitoring
        try:
            dm_channel = await self.monitoring.start_monitoring_session(interaction.user)
            
            embed = discord.Embed(
                title="✅ Terminal Activé",
                description=f"Le terminal de monitoring a été ouvert dans vos messages privés.\n"
                           f"Vérifiez {dm_channel.mention if hasattr(dm_channel, 'mention') else 'vos MPs'}.",
                color=0x00FF88
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Erreur d'Accès",
                description="Impossible d'ouvrir un canal privé avec vous. Vérifiez vos paramètres de confidentialité.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        """Événement déclenché lors de l'exécution d'une commande"""
        self.monitoring.log_command(ctx, ctx.command.name, True)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Événement déclenché lors d'une erreur de commande"""
        self.monitoring.log_command(ctx, ctx.command.name if ctx.command else 'Unknown', False, str(error))
        self.monitoring.log_error(error, f"Commande: {ctx.command}")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Écoute les messages dans les sessions de monitoring actives"""
        if message.author.bot:
            return
        
        # Vérifier si c'est une session de monitoring active
        if message.author.id not in self.monitoring.active_sessions:
            return
        
        # Vérifier si c'est un canal DM
        if not isinstance(message.channel, discord.DMChannel):
            return
        
        content = message.content.lower().strip()
        
        try:
            if content == '!logs':
                await self._send_recent_logs(message.channel)
            elif content == '!errors':
                await self._send_recent_errors(message.channel)
            elif content == '!stats':
                await self._send_system_stats(message.channel)
            elif content == '!stop':
                await self._stop_monitoring_session(message.author, message.channel)
            elif content == '!help':
                await self._send_help(message.channel)
                
        except Exception as e:
            logger.error(f"Erreur traitement commande monitoring: {e}")
    
    async def _send_recent_logs(self, channel: discord.DMChannel):
        """Envoie les logs récents"""
        logs = self.monitoring.get_recent_logs(10)
        
        if not logs:
            embed = discord.Embed(
                title="📝 Logs Récents",
                description="Aucun log récent disponible.",
                color=0x888888
            )
        else:
            embed = discord.Embed(
                title="📝 10 Derniers Logs",
                color=0x3366FF
            )
            
            for log in logs[-5:]:  # Afficher seulement les 5 derniers pour éviter le spam
                status = "✅" if log['success'] else "❌"
                timestamp = log['timestamp'][:19].replace('T', ' ')
                
                embed.add_field(
                    name=f"{status} {log['command']}",
                    value=f"**Utilisateur**: {log['user_name']}\n"
                          f"**Serveur**: {log['guild_name']}\n"
                          f"**Heure**: {timestamp}",
                    inline=True
                )
        
        await channel.send(embed=embed)
    
    async def _send_recent_errors(self, channel: discord.DMChannel):
        """Envoie les erreurs récentes"""
        errors = self.monitoring.get_recent_errors(5)
        
        if not errors:
            embed = discord.Embed(
                title="🚨 Erreurs Récentes",
                description="Aucune erreur récente. Le bot fonctionne correctement !",
                color=0x00FF88
            )
        else:
            embed = discord.Embed(
                title="🚨 5 Dernières Erreurs",
                color=0xFF0000
            )
            
            for error in errors:
                timestamp = error['timestamp'][:19].replace('T', ' ')
                
                embed.add_field(
                    name=f"🔥 {error['error_type']}",
                    value=f"**Message**: {error['error_message'][:100]}...\n"
                          f"**Contexte**: {error['context'] or 'Aucun'}\n"
                          f"**Heure**: {timestamp}",
                    inline=False
                )
        
        await channel.send(embed=embed)
    
    async def _send_system_stats(self, channel: discord.DMChannel):
        """Envoie les statistiques système"""
        stats = await self.monitoring.get_system_stats()
        
        embed = discord.Embed(
            title="📊 Statistiques Système",
            color=0xFFD700,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(
            name="🤖 Bot",
            value=f"**Uptime**: {stats['bot_uptime']}\n"
                  f"**Serveurs**: {stats['guilds_count']}\n"
                  f"**Utilisateurs**: {stats['users_count']}",
            inline=True
        )
        
        embed.add_field(
            name="💻 Système",
            value=f"**CPU**: {stats['cpu_percent']:.1f}%\n"
                  f"**RAM**: {stats['memory_percent']:.1f}%\n"
                  f"**RAM MB**: {stats['memory_mb']:.1f}",
            inline=True
        )
        
        embed.add_field(
            name="📈 Activité Aujourd'hui",
            value=f"**Commandes**: {stats['commands_today']}\n"
                  f"**Erreurs**: {stats['errors_today']}\n"
                  f"**Sessions actives**: {stats['active_sessions']}",
            inline=True
        )
        
        await channel.send(embed=embed)
    
    async def _stop_monitoring_session(self, user: discord.User, channel: discord.DMChannel):
        """Arrête une session de monitoring"""
        success = self.monitoring.stop_monitoring_session(user.id)
        
        if success:
            embed = discord.Embed(
                title="✅ Session Fermée",
                description="La session de monitoring a été fermée avec succès.",
                color=0x00FF88
            )
        else:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Aucune session active trouvée.",
                color=0xFF0000
            )
        
        await channel.send(embed=embed)
    
    async def _send_help(self, channel: discord.DMChannel):
        """Envoie l'aide des commandes de monitoring"""
        embed = discord.Embed(
            title="🖥️ Commandes du Terminal",
            description="Voici toutes les commandes disponibles dans le terminal de monitoring :",
            color=0x3366FF
        )
        
        embed.add_field(
            name="📝 Commandes de Logs",
            value="`!logs` - Affiche les 10 derniers logs\n"
                  "`!errors` - Affiche les 5 dernières erreurs\n"
                  "`!stats` - Statistiques système complètes",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Commandes de Contrôle",
            value="`!stop` - Ferme la session de monitoring\n"
                  "`!help` - Affiche cette aide",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Informations",
            value="• Les logs s'affichent automatiquement en temps réel\n"
                  "• Les erreurs sont signalées immédiatement\n"
                  "• Une seule session par créateur autorisée",
            inline=False
        )
        
        await channel.send(embed=embed)


async def setup(bot):
    """Setup function pour charger le système de monitoring"""
    await bot.add_cog(InvcmdSystem(bot))
    logger.info("🖥️ Système de Monitoring INVCMD chargé avec succès!")
    print("✅ INVCMD System - Terminal de monitoring prêt!")
    print("🖥️ Commande: /invcmd (créateurs uniquement)")
    print(f"👑 Créateurs autorisés: {len(CREATOR_IDS)}")

