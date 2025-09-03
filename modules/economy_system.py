"""
Arsenal Economy & Level System V4.5.2
Système complet d'économie et de nivellement avec autosave
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import sqlite3
import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import random

logger = logging.getLogger(__name__)

class EconomyDatabase:
    """Base de données économie et niveaux"""
    
    def __init__(self, db_path: str = "arsenal_economy_complete.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialise toutes les tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table utilisateurs (économie + level)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    balance INTEGER DEFAULT 0,
                    bank INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    xp INTEGER DEFAULT 0,
                    total_xp INTEGER DEFAULT 0,
                    messages INTEGER DEFAULT 0,
                    voice_time INTEGER DEFAULT 0,
                    last_daily TIMESTAMP,
                    last_message TIMESTAMP,
                    last_voice TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            
            # Table configuration serveur
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS guild_config (
                    guild_id INTEGER PRIMARY KEY,
                    economy_enabled INTEGER DEFAULT 1,
                    level_enabled INTEGER DEFAULT 1,
                    daily_amount INTEGER DEFAULT 100,
                    xp_per_message INTEGER DEFAULT 15,
                    xp_per_minute_voice INTEGER DEFAULT 5,
                    level_up_bonus INTEGER DEFAULT 50,
                    level_roles TEXT,
                    economy_channels TEXT,
                    level_channels TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table transactions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    description TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ Base de données Economy & Level initialisée")
            
        except Exception as e:
            logger.error(f"Erreur init database: {e}")
    
    def get_user_data(self, guild_id: int, user_id: int) -> Dict[str, Any]:
        """Récupère les données utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM users WHERE guild_id = ? AND user_id = ?
            """, (guild_id, user_id))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return dict(result)
            else:
                # Créer un nouvel utilisateur
                self.create_user(guild_id, user_id)
                return self.get_user_data(guild_id, user_id)
                
        except Exception as e:
            logger.error(f"Erreur get_user_data: {e}")
            return {}
    
    def create_user(self, guild_id: int, user_id: int):
        """Crée un nouvel utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO users (guild_id, user_id) VALUES (?, ?)
            """, (guild_id, user_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur create_user: {e}")
    
    def update_user_balance(self, guild_id: int, user_id: int, amount: int, transaction_type: str = "admin"):
        """Met à jour le solde utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Mettre à jour le solde
            cursor.execute("""
                UPDATE users SET balance = balance + ?, updated_at = CURRENT_TIMESTAMP
                WHERE guild_id = ? AND user_id = ?
            """, (amount, guild_id, user_id))
            
            # Enregistrer la transaction
            cursor.execute("""
                INSERT INTO transactions (guild_id, user_id, type, amount, description)
                VALUES (?, ?, ?, ?, ?)
            """, (guild_id, user_id, transaction_type, amount, f"{transaction_type} transaction"))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur update_balance: {e}")
    
    def add_xp(self, guild_id: int, user_id: int, xp: int) -> tuple:
        """Ajoute de l'XP et retourne (nouveau_level, level_up)"""
        try:
            user_data = self.get_user_data(guild_id, user_id)
            current_level = user_data.get('level', 1)
            current_xp = user_data.get('xp', 0)
            total_xp = user_data.get('total_xp', 0)
            
            new_xp = current_xp + xp
            new_total_xp = total_xp + xp
            
            # Calculer le niveau requis
            xp_for_next = current_level * 100
            new_level = current_level
            level_up = False
            
            while new_xp >= xp_for_next:
                new_xp -= xp_for_next
                new_level += 1
                level_up = True
                xp_for_next = new_level * 100
            
            # Sauvegarder
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET level = ?, xp = ?, total_xp = ?, updated_at = CURRENT_TIMESTAMP
                WHERE guild_id = ? AND user_id = ?
            """, (new_level, new_xp, new_total_xp, guild_id, user_id))
            
            conn.commit()
            conn.close()
            
            return (new_level, level_up)
            
        except Exception as e:
            logger.error(f"Erreur add_xp: {e}")
            return (1, False)

class EconomyLevelManager:
    """Gestionnaire principal économie & niveaux"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = EconomyDatabase()
        self.auto_save.start()  # Auto-save toutes les minutes
        
    @tasks.loop(minutes=1)
    async def auto_save(self):
        """Auto-sauvegarde toutes les minutes"""
        try:
            # Force la sauvegarde de la base
            conn = sqlite3.connect(self.db.db_path)
            conn.execute("PRAGMA wal_checkpoint(FULL)")
            conn.close()
            logger.debug("💾 Auto-save economy database completed")
        except Exception as e:
            logger.error(f"Erreur auto-save: {e}")
    
    async def on_message_xp(self, guild_id: int, user_id: int):
        """Gère l'XP des messages"""
        try:
            config = self.get_guild_config(guild_id)
            if not config.get('level_enabled', True):
                return
                
            xp_gain = config.get('xp_per_message', 15)
            new_level, level_up = self.db.add_xp(guild_id, user_id, xp_gain)
            
            if level_up:
                # Bonus économique pour level up
                bonus = config.get('level_up_bonus', 50)
                self.db.update_user_balance(guild_id, user_id, bonus, "level_bonus")
                return new_level
                
        except Exception as e:
            logger.error(f"Erreur on_message_xp: {e}")
        return None
    
    def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """Récupère la config du serveur"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM guild_config WHERE guild_id = ?", (guild_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return dict(result)
            else:
                # Créer config par défaut
                self.create_guild_config(guild_id)
                return self.get_guild_config(guild_id)
                
        except Exception as e:
            logger.error(f"Erreur get_guild_config: {e}")
            return {}
    
    def create_guild_config(self, guild_id: int):
        """Crée une config serveur par défaut"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO guild_config (guild_id) VALUES (?)
            """, (guild_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur create_guild_config: {e}")

class EconomyLevelCog(commands.Cog):
    """Cog principal Economy & Level"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = EconomyLevelManager(bot)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Gère l'XP des messages"""
        if message.author.bot or not message.guild:
            return
            
        # Cooldown anti-spam
        now = time.time()
        user_key = f"{message.guild.id}_{message.author.id}"
        
        if not hasattr(self, '_message_cooldowns'):
            self._message_cooldowns = {}
            
        if user_key in self._message_cooldowns:
            if now - self._message_cooldowns[user_key] < 60:  # 1 minute cooldown
                return
        
        self._message_cooldowns[user_key] = now
        
        # Donner XP
        new_level = await self.manager.on_message_xp(message.guild.id, message.author.id)
        
        if new_level:
            embed = discord.Embed(
                title="🎉 Level Up !",
                description=f"{message.author.mention} est maintenant niveau **{new_level}** !",
                color=0x00FF00
            )
            try:
                await message.channel.send(embed=embed, delete_after=10)
            except:
                pass
    
    @app_commands.command(name="balance", description="💰 Voir votre solde")
    async def balance_command(self, interaction: discord.Interaction, user: discord.Member = None):
        """Affiche le solde d'un utilisateur"""
        target = user or interaction.user
        data = self.manager.db.get_user_data(interaction.guild.id, target.id)
        
        embed = discord.Embed(
            title=f"💰 Portefeuille de {target.display_name}",
            color=0x00FF00
        )
        embed.add_field(name="💵 Argent", value=f"`{data.get('balance', 0):,}` coins", inline=True)
        embed.add_field(name="🏦 Banque", value=f"`{data.get('bank', 0):,}` coins", inline=True)
        embed.add_field(name="📈 Niveau", value=f"`{data.get('level', 1)}`", inline=True)
        embed.add_field(name="⭐ XP", value=f"`{data.get('xp', 0)}`/`{data.get('level', 1) * 100}`", inline=True)
        embed.add_field(name="💬 Messages", value=f"`{data.get('messages', 0):,}`", inline=True)
        embed.add_field(name="🎤 Temps vocal", value=f"`{data.get('voice_time', 0):,}` min", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="daily", description="💰 Récupérer votre bonus quotidien")
    async def daily_command(self, interaction: discord.Interaction):
        """Bonus quotidien"""
        user_data = self.manager.db.get_user_data(interaction.guild.id, interaction.user.id)
        config = self.manager.get_guild_config(interaction.guild.id)
        
        last_daily = user_data.get('last_daily')
        if last_daily:
            last_time = datetime.fromisoformat(last_daily)
            if datetime.now() - last_time < timedelta(hours=24):
                next_time = last_time + timedelta(hours=24)
                wait_time = next_time - datetime.now()
                hours = int(wait_time.total_seconds() // 3600)
                minutes = int((wait_time.total_seconds() % 3600) // 60)
                
                embed = discord.Embed(
                    title="⏰ Patience !",
                    description=f"Votre prochain daily sera disponible dans **{hours}h {minutes}m**",
                    color=0xFF9900
                )
                await interaction.response.send_message(embed=embed)
                return
        
        # Donner le daily
        daily_amount = config.get('daily_amount', 100)
        bonus = random.randint(int(daily_amount * 0.8), int(daily_amount * 1.2))
        
        self.manager.db.update_user_balance(interaction.guild.id, interaction.user.id, bonus, "daily")
        
        # Mettre à jour la date
        conn = sqlite3.connect(self.manager.db.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET last_daily = CURRENT_TIMESTAMP 
            WHERE guild_id = ? AND user_id = ?
        """, (interaction.guild.id, interaction.user.id))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="💰 Daily récupéré !",
            description=f"Vous avez reçu **{bonus:,}** coins !",
            color=0x00FF00
        )
        await interaction.response.send_message(embed=embed)

# Instance globale
_economy_manager = None

def get_economy_manager():
    return _economy_manager

def set_economy_manager(manager):
    global _economy_manager
    _economy_manager = manager

async def setup(bot: commands.Bot):
    """Setup function"""
    cog = EconomyLevelCog(bot)
    await bot.add_cog(cog)
    set_economy_manager(cog.manager)
    logger.info("✅ Arsenal Economy & Level System V4.5.2 chargé")

async def teardown(bot: commands.Bot):
    """Teardown function"""
    if _economy_manager:
        _economy_manager.auto_save.cancel()
    logger.info("🔄 Arsenal Economy & Level System déchargé")
