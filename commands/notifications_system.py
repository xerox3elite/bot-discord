# 🚀 Arsenal V4 - Système Notifications & Webhooks
"""
Système avancé de notifications pour Arsenal V4:
- Webhooks Discord configurable
- Notifications serveur en temps réel  
- Alertes pour modération
- Messages automatiques/programmés
- Logging avancé des événements
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import json
import asyncio
from datetime import datetime, timedelta
import os
from typing import Optional, Dict, List, Union
import sqlite3
import uuid

class NotificationSystem(commands.Cog):
    """Système de notifications avancé pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/notifications.db"
        self.webhooks_config = "data/webhooks.json"
        self.active_notifications = {}
        self.init_database()
        self.load_webhooks_config()
        self.notification_checker.start()

    def init_database(self):
        """Initialise la base de données des notifications"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_notifications (
                id TEXT PRIMARY KEY,
                guild_id INTEGER,
                channel_id INTEGER,
                message TEXT,
                send_time TEXT,
                repeat_interval TEXT,
                is_active INTEGER DEFAULT 1,
                created_by INTEGER,
                created_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhook_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                webhook_name TEXT,
                event_type TEXT,
                guild_id INTEGER,
                payload TEXT,
                status TEXT,
                timestamp TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_settings (
                guild_id INTEGER PRIMARY KEY,
                welcome_enabled INTEGER DEFAULT 0,
                leave_enabled INTEGER DEFAULT 0,
                moderation_enabled INTEGER DEFAULT 1,
                level_up_enabled INTEGER DEFAULT 0,
                custom_events TEXT DEFAULT '{}'
            )
        ''')
        
        conn.commit()
        conn.close()

    def load_webhooks_config(self):
        """Charge la configuration des webhooks"""
        if not os.path.exists(self.webhooks_config):
            os.makedirs(os.path.dirname(self.webhooks_config), exist_ok=True)
            default_config = {
                "webhooks": {},
                "templates": {
                    "welcome": "🎉 **{user}** a rejoint le serveur !",
                    "leave": "😢 **{user}** a quitté le serveur...",
                    "ban": "🔨 **{user}** a été banni par {moderator}",
                    "kick": "👢 **{user}** a été expulsé par {moderator}"
                }
            }
            
            with open(self.webhooks_config, 'w') as f:
                json.dump(default_config, f, indent=2)
        
        try:
            with open(self.webhooks_config, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {"webhooks": {}, "templates": {}}

    def save_webhooks_config(self):
        """Sauvegarde la configuration des webhooks"""
        with open(self.webhooks_config, 'w') as f:
            json.dump(self.config, f, indent=2)

    @app_commands.command(name="notification", description="📢 Système de notifications Arsenal")
    async def notification_menu(self, interaction: discord.Interaction):
        """Menu principal des notifications"""
        embed = discord.Embed(
            title="📢 Système de Notifications Arsenal",
            description="Gérez vos notifications et webhooks",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="⚙️ Configuration",
            value=(
                "`/webhook setup` - Configurer webhooks\n"
                "`/schedule message` - Programmer message\n" 
                "`/notify settings` - Paramètres serveur"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📨 Actions Rapides", 
            value=(
                "`/announce` - Annonce serveur\n"
                "`/alert` - Alerte modération\n"
                "`/remind` - Rappel programmé"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="webhook", description="🔗 Gestion des webhooks")
    @app_commands.describe(action="Action à effectuer", name="Nom du webhook", url="URL du webhook")
    async def webhook_management(self, interaction: discord.Interaction, 
                               action: str, name: Optional[str] = None, 
                               url: Optional[str] = None):
        """Gestion des webhooks Discord"""
        
        if not interaction.user.guild_permissions.manage_webhooks:
            await interaction.response.send_message("❌ Permission 'Gérer les webhooks' requise !", ephemeral=True)
            return
        
        guild_id = str(interaction.guild.id)
        
        if action == "list":
            webhooks = self.config["webhooks"].get(guild_id, {})
            if not webhooks:
                await interaction.response.send_message("📭 Aucun webhook configuré", ephemeral=True)
                return
            
            embed = discord.Embed(title="🔗 Webhooks Configurés", color=discord.Color.blue())
            for wh_name, wh_data in webhooks.items():
                embed.add_field(
                    name=f"📌 {wh_name}",
                    value=f"Canal: <#{wh_data['channel_id']}>\nEvénements: {', '.join(wh_data.get('events', []))}",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        elif action == "add":
            if not name or not url:
                await interaction.response.send_message("❌ Nom et URL requis !", ephemeral=True)
                return
            
            if guild_id not in self.config["webhooks"]:
                self.config["webhooks"][guild_id] = {}
            
            self.config["webhooks"][guild_id][name] = {
                "url": url,
                "channel_id": interaction.channel.id,
                "events": ["welcome", "leave", "moderation"],
                "active": True
            }
            
            self.save_webhooks_config()
            
            embed = discord.Embed(
                title="✅ Webhook Ajouté",
                description=f"Webhook **{name}** configuré avec succès !",
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="announce", description="📣 Annonce serveur")
    @app_commands.describe(message="Message à annoncer", channel="Canal de destination")
    async def server_announce(self, interaction: discord.Interaction, 
                            message: str, channel: Optional[discord.TextChannel] = None):
        """Créer une annonce serveur"""
        
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ Permission 'Gérer les messages' requise !", ephemeral=True)
            return
        
        target_channel = channel or interaction.channel
        
        embed = discord.Embed(
            title="📣 Annonce Officielle",
            description=message,
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.avatar.url if interaction.user.avatar else None
        )
        
        embed.set_footer(text=f"Arsenal V4 • Serveur: {interaction.guild.name}")
        
        try:
            await target_channel.send(embed=embed)
            
            # Log dans webhook si configuré
            await self.send_webhook_notification(
                interaction.guild.id,
                "announcement",
                {
                    "title": "📣 Nouvelle Annonce",
                    "description": f"**{interaction.user.mention}** a fait une annonce dans {target_channel.mention}",
                    "message": message
                }
            )
            
            await interaction.response.send_message(f"✅ Annonce envoyée dans {target_channel.mention} !", ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)

    @app_commands.command(name="schedule", description="⏰ Programmer un message")
    @app_commands.describe(
        message="Message à programmer",
        delay_minutes="Délai en minutes",
        channel="Canal de destination"
    )
    async def schedule_message(self, interaction: discord.Interaction, 
                             message: str, delay_minutes: int,
                             channel: Optional[discord.TextChannel] = None):
        """Programmer un message"""
        
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ Permission requise !", ephemeral=True)
            return
        
        if delay_minutes < 1 or delay_minutes > 10080:  # Max 1 semaine
            await interaction.response.send_message("❌ Délai entre 1 minute et 1 semaine !", ephemeral=True)
            return
        
        target_channel = channel or interaction.channel
        send_time = datetime.now() + timedelta(minutes=delay_minutes)
        notification_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scheduled_notifications 
            (id, guild_id, channel_id, message, send_time, repeat_interval, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            notification_id,
            interaction.guild.id,
            target_channel.id,
            message,
            send_time.isoformat(),
            "none",
            interaction.user.id,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="⏰ Message Programmé",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📝 Message",
            value=message[:100] + ("..." if len(message) > 100 else ""),
            inline=False
        )
        
        embed.add_field(
            name="📅 Envoi prévu",
            value=f"<t:{int(send_time.timestamp())}:F>",
            inline=True
        )
        
        embed.add_field(
            name="📍 Canal",
            value=target_channel.mention,
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @tasks.loop(minutes=1)
    async def notification_checker(self):
        """Vérifie les notifications programmées"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute('''
                SELECT * FROM scheduled_notifications 
                WHERE send_time <= ? AND is_active = 1
            ''', (now,))
            
            notifications = cursor.fetchall()
            
            for notif in notifications:
                await self.send_scheduled_notification(notif)
                
                # Marquer comme envoyée
                cursor.execute('''
                    UPDATE scheduled_notifications 
                    SET is_active = 0 WHERE id = ?
                ''', (notif[0],))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erreur notification checker: {e}")

    async def send_scheduled_notification(self, notification_data):
        """Envoie une notification programmée"""
        try:
            guild = self.bot.get_guild(notification_data[1])
            if not guild:
                return
            
            channel = guild.get_channel(notification_data[2])
            if not channel:
                return
            
            embed = discord.Embed(
                title="⏰ Message Programmé",
                description=notification_data[3],
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.set_footer(text="Arsenal V4 • Notification Système")
            
            await channel.send(embed=embed)
            
        except Exception as e:
            print(f"Erreur envoi notification: {e}")

    async def send_webhook_notification(self, guild_id: int, event_type: str, data: Dict):
        """Envoie une notification via webhook"""
        try:
            guild_webhooks = self.config["webhooks"].get(str(guild_id), {})
            
            for webhook_name, webhook_data in guild_webhooks.items():
                if not webhook_data.get("active", True):
                    continue
                
                if event_type not in webhook_data.get("events", []):
                    continue
                
                webhook_url = webhook_data["url"]
                
                embed_data = {
                    "title": data.get("title", "Arsenal V4 Notification"),
                    "description": data.get("description", ""),
                    "color": 0x00FF00,
                    "timestamp": datetime.now().isoformat()
                }
                
                payload = {
                    "username": "Arsenal V4",
                    "embeds": [embed_data]
                }
                
                async with aiohttp.ClientSession() as session:
                    await session.post(webhook_url, json=payload)
                
                # Log webhook
                self.log_webhook_activity(webhook_name, event_type, guild_id, payload, "success")
                
        except Exception as e:
            print(f"Erreur webhook: {e}")
            self.log_webhook_activity(webhook_name, event_type, guild_id, {}, f"error: {e}")

    def log_webhook_activity(self, webhook_name: str, event_type: str, guild_id: int, payload: Dict, status: str):
        """Log l'activité des webhooks"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO webhook_logs 
                (webhook_name, event_type, guild_id, payload, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                webhook_name,
                event_type, 
                guild_id,
                json.dumps(payload),
                status,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erreur log webhook: {e}")

    @notification_checker.before_loop
    async def before_notification_checker(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(NotificationSystem(bot))
    print("📢 [Notification System] Module chargé avec succès!")

