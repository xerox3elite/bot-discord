"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🎯 ARSENAL LEVEL SYSTEM V4 - COMPLET                     ║
║                     Système de niveaux et XP avancé                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import sqlite3
import asyncio
import json
import math
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import aiofiles
import os

class LevelDB:
    """Gestionnaire de base de données pour le système de niveaux"""
    
    def __init__(self):
        self.db_path = "arsenal_levels.db"
        self.init_database()
    
    def init_database(self):
        """Initialise toutes les tables de la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table principale des utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_levels (
                user_id TEXT PRIMARY KEY,
                guild_id TEXT NOT NULL,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 0,
                messages INTEGER DEFAULT 0,
                voice_minutes INTEGER DEFAULT 0,
                last_xp_gain TEXT,
                total_xp INTEGER DEFAULT 0,
                prestige INTEGER DEFAULT 0,
                boost_multiplier REAL DEFAULT 1.0,
                boost_expires TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des configurations de guild
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS level_config (
                guild_id TEXT PRIMARY KEY,
                enabled BOOLEAN DEFAULT 1,
                xp_per_message INTEGER DEFAULT 15,
                xp_per_voice_minute INTEGER DEFAULT 5,
                xp_cooldown INTEGER DEFAULT 60,
                level_up_channel TEXT,
                level_up_message TEXT DEFAULT "🎉 {user} vient d'atteindre le niveau **{level}** ! 🎯",
                no_xp_channels TEXT DEFAULT "[]",
                no_xp_roles TEXT DEFAULT "[]",
                bonus_channels TEXT DEFAULT "{}",
                bonus_roles TEXT DEFAULT "{}",
                prestige_enabled BOOLEAN DEFAULT 1,
                prestige_level INTEGER DEFAULT 100,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des récompenses de niveau
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS level_rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                level INTEGER NOT NULL,
                reward_type TEXT NOT NULL,
                reward_data TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des boosts XP temporaires
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS xp_boosts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                guild_id TEXT NOT NULL,
                multiplier REAL NOT NULL,
                duration_minutes INTEGER NOT NULL,
                expires_at TEXT NOT NULL,
                active BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des statistiques
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS level_stats (
                guild_id TEXT PRIMARY KEY,
                total_users INTEGER DEFAULT 0,
                total_messages INTEGER DEFAULT 0,
                total_xp_given INTEGER DEFAULT 0,
                last_reset TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user_level(self, user_id: str, guild_id: str) -> Dict:
        """Récupère les données de niveau d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_levels WHERE user_id = ? AND guild_id = ?
        ''', (user_id, guild_id))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, result))
        else:
            return self.create_user(user_id, guild_id)
    
    def create_user(self, user_id: str, guild_id: str) -> Dict:
        """Crée un nouvel utilisateur dans la base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_levels (user_id, guild_id, xp, level, messages, voice_minutes, 
                                   total_xp, prestige, created_at, updated_at)
            VALUES (?, ?, 0, 0, 0, 0, 0, 0, ?, ?)
        ''', (user_id, guild_id, datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return {
            'user_id': user_id,
            'guild_id': guild_id,
            'xp': 0,
            'level': 0,
            'messages': 0,
            'voice_minutes': 0,
            'total_xp': 0,
            'prestige': 0,
            'boost_multiplier': 1.0,
            'boost_expires': None
        }
    
    def add_xp(self, user_id: str, guild_id: str, xp_amount: int, source: str = "message") -> Tuple[bool, int, int]:
        """Ajoute de l'XP et retourne (level_up, old_level, new_level)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Récupère les données actuelles
        user_data = self.get_user_level(user_id, guild_id)
        old_level = user_data['level']
        new_xp = user_data['xp'] + xp_amount
        new_total_xp = user_data['total_xp'] + xp_amount
        
        # Calcule le nouveau niveau
        new_level = self.calculate_level(new_xp)
        level_up = new_level > old_level
        
        # Met à jour les données
        if source == "message":
            cursor.execute('''
                UPDATE user_levels 
                SET xp = ?, level = ?, messages = messages + 1, total_xp = ?, 
                    last_xp_gain = ?, updated_at = ?
                WHERE user_id = ? AND guild_id = ?
            ''', (new_xp, new_level, new_total_xp, datetime.now().isoformat(), 
                  datetime.now().isoformat(), user_id, guild_id))
        else:  # voice
            cursor.execute('''
                UPDATE user_levels 
                SET xp = ?, level = ?, voice_minutes = voice_minutes + 1, total_xp = ?, 
                    last_xp_gain = ?, updated_at = ?
                WHERE user_id = ? AND guild_id = ?
            ''', (new_xp, new_level, new_total_xp, datetime.now().isoformat(), 
                  datetime.now().isoformat(), user_id, guild_id))
        
        conn.commit()
        conn.close()
        
        return level_up, old_level, new_level
    
    def calculate_level(self, xp: int) -> int:
        """Calcule le niveau basé sur l'XP (formule progressive)"""
        if xp < 100:
            return 0
        
        # Formule: niveau = sqrt(xp / 100)
        return int(math.sqrt(xp / 100))
    
    def xp_for_level(self, level: int) -> int:
        """Calcule l'XP requis pour un niveau donné"""
        return level * level * 100
    
    def get_leaderboard(self, guild_id: str, limit: int = 10) -> List[Dict]:
        """Récupère le classement des utilisateurs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_levels 
            WHERE guild_id = ? 
            ORDER BY total_xp DESC, level DESC, xp DESC
            LIMIT ?
        ''', (guild_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        leaderboard = []
        for i, result in enumerate(results):
            columns = [desc[0] for desc in cursor.description]
            data = dict(zip(columns, result))
            data['rank'] = i + 1
            leaderboard.append(data)
        
        return leaderboard
    
    def get_guild_config(self, guild_id: str) -> Dict:
        """Récupère la configuration du serveur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM level_config WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()
        
        if result:
            columns = [desc[0] for desc in cursor.description]
            config = dict(zip(columns, result))
        else:
            # Crée la config par défaut
            cursor.execute('''
                INSERT INTO level_config (guild_id) VALUES (?)
            ''', (guild_id,))
            conn.commit()
            config = {
                'guild_id': guild_id,
                'enabled': True,
                'xp_per_message': 15,
                'xp_per_voice_minute': 5,
                'xp_cooldown': 60,
                'level_up_channel': None,
                'level_up_message': "🎉 {user} vient d'atteindre le niveau **{level}** ! 🎯",
                'no_xp_channels': "[]",
                'no_xp_roles': "[]",
                'bonus_channels': "{}",
                'bonus_roles': "{}",
                'prestige_enabled': True,
                'prestige_level': 100
            }
        
        conn.close()
        return config

class LevelReward:
    """Gestionnaire des récompenses de niveau"""
    
    def __init__(self, db: LevelDB):
        self.db = db
    
    def add_reward(self, guild_id: str, level: int, reward_type: str, reward_data: Dict):
        """Ajoute une récompense de niveau"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO level_rewards (guild_id, level, reward_type, reward_data)
            VALUES (?, ?, ?, ?)
        ''', (guild_id, level, reward_type, json.dumps(reward_data)))
        
        conn.commit()
        conn.close()
    
    def get_rewards(self, guild_id: str, level: int) -> List[Dict]:
        """Récupère les récompenses pour un niveau donné"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM level_rewards WHERE guild_id = ? AND level = ?
        ''', (guild_id, level))
        
        results = cursor.fetchall()
        conn.close()
        
        rewards = []
        for result in results:
            columns = [desc[0] for desc in cursor.description]
            reward = dict(zip(columns, result))
            reward['reward_data'] = json.loads(reward['reward_data'])
            rewards.append(reward)
        
        return rewards
    
    async def apply_rewards(self, guild: discord.Guild, user: discord.Member, level: int):
        """Applique les récompenses d'un niveau"""
        rewards = self.get_rewards(str(guild.id), level)
        
        for reward in rewards:
            try:
                if reward['reward_type'] == 'role':
                    role_id = reward['reward_data']['role_id']
                    role = guild.get_role(int(role_id))
                    if role:
                        await user.add_roles(role, reason=f"Récompense niveau {level}")
                
                elif reward['reward_type'] == 'coins':
                    # Intégration avec le système d'économie
                    amount = reward['reward_data']['amount']
                    # Logique pour ajouter des coins (à implémenter)
                    pass
                
            except Exception as e:
                print(f"Erreur application récompense: {e}")

class LevelManager:
    """Gestionnaire principal du système de niveaux"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = LevelDB()
        self.rewards = LevelReward(self.db)
        self.xp_cooldowns = {}  # user_id: timestamp
    
    def can_gain_xp(self, user_id: str, guild_id: str) -> bool:
        """Vérifie si l'utilisateur peut gagner de l'XP"""
        config = self.db.get_guild_config(guild_id)
        cooldown = config.get('xp_cooldown', 60)
        
        key = f"{user_id}_{guild_id}"
        now = datetime.now().timestamp()
        
        if key in self.xp_cooldowns:
            if now - self.xp_cooldowns[key] < cooldown:
                return False
        
        self.xp_cooldowns[key] = now
        return True
    
    async def process_message_xp(self, message: discord.Message):
        """Traite l'XP d'un message"""
        if message.author.bot:
            return
        
        guild_id = str(message.guild.id)
        user_id = str(message.author.id)
        
        # Vérifie la configuration
        config = self.db.get_guild_config(guild_id)
        if not config.get('enabled', True):
            return
        
        # Vérifie le cooldown
        if not self.can_gain_xp(user_id, guild_id):
            return
        
        # Vérifie les canaux/rôles exclus
        no_xp_channels = json.loads(config.get('no_xp_channels', '[]'))
        if str(message.channel.id) in no_xp_channels:
            return
        
        no_xp_roles = json.loads(config.get('no_xp_roles', '[]'))
        user_role_ids = [str(role.id) for role in message.author.roles]
        if any(role_id in no_xp_roles for role_id in user_role_ids):
            return
        
        # Calcule l'XP à donner
        base_xp = config.get('xp_per_message', 15)
        xp_amount = random.randint(base_xp - 5, base_xp + 10)
        
        # Applique les bonus
        xp_amount = await self.apply_bonuses(message.author, message.channel, xp_amount, config)
        
        # Ajoute l'XP
        level_up, old_level, new_level = self.db.add_xp(user_id, guild_id, xp_amount)
        
        if level_up:
            await self.handle_level_up(message.guild, message.author, old_level, new_level, message.channel)
    
    async def apply_bonuses(self, user: discord.Member, channel: discord.TextChannel, base_xp: int, config: Dict) -> int:
        """Applique les bonus d'XP"""
        multiplier = 1.0
        
        # Bonus de canal
        bonus_channels = json.loads(config.get('bonus_channels', '{}'))
        if str(channel.id) in bonus_channels:
            multiplier *= bonus_channels[str(channel.id)]
        
        # Bonus de rôle
        bonus_roles = json.loads(config.get('bonus_roles', '{}'))
        for role in user.roles:
            if str(role.id) in bonus_roles:
                multiplier *= bonus_roles[str(role.id)]
        
        # Bonus personnel de l'utilisateur
        user_data = self.db.get_user_level(str(user.id), str(user.guild.id))
        if user_data.get('boost_expires'):
            boost_expires = datetime.fromisoformat(user_data['boost_expires'])
            if datetime.now() < boost_expires:
                multiplier *= user_data.get('boost_multiplier', 1.0)
        
        return int(base_xp * multiplier)
    
    async def handle_level_up(self, guild: discord.Guild, user: discord.Member, old_level: int, new_level: int, channel: discord.TextChannel):
        """Gère les montées de niveau"""
        config = self.db.get_guild_config(str(guild.id))
        
        # Message de niveau
        level_up_message = config.get('level_up_message', "🎉 {user} vient d'atteindre le niveau **{level}** ! 🎯")
        formatted_message = level_up_message.format(user=user.mention, level=new_level, old_level=old_level)
        
        # Canal de niveau
        level_up_channel_id = config.get('level_up_channel')
        if level_up_channel_id:
            level_channel = guild.get_channel(int(level_up_channel_id))
            if level_channel:
                channel = level_channel
        
        # Envoie le message
        embed = discord.Embed(
            title="🎯 Niveau Supérieur !",
            description=formatted_message,
            color=0x00ff00
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Niveau précédent", value=f"**{old_level}**", inline=True)
        embed.add_field(name="Nouveau niveau", value=f"**{new_level}**", inline=True)
        
        # Calcule l'XP pour le prochain niveau
        next_level_xp = self.db.xp_for_level(new_level + 1)
        current_xp = self.db.get_user_level(str(user.id), str(guild.id))['xp']
        remaining_xp = next_level_xp - current_xp
        embed.add_field(name="XP jusqu'au prochain niveau", value=f"**{remaining_xp:,}**", inline=True)
        
        await channel.send(embed=embed)
        
        # Applique les récompenses
        await self.rewards.apply_rewards(guild, user, new_level)

# Interface utilisateur pour la configuration
class LevelConfigView(discord.ui.View):
    """Interface de configuration du système de niveaux"""
    
    def __init__(self, db: LevelDB, guild_id: str):
        super().__init__(timeout=300)
        self.db = db
        self.guild_id = guild_id
    
    @discord.ui.button(label="⚙️ Config Générale", style=discord.ButtonStyle.primary)
    async def general_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GeneralConfigModal(self.db, self.guild_id))
    
    @discord.ui.button(label="🎁 Récompenses", style=discord.ButtonStyle.success)
    async def rewards_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RewardsConfigModal(self.db, self.guild_id))
    
    @discord.ui.button(label="🚫 Exclusions", style=discord.ButtonStyle.danger)
    async def exclusions_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ExclusionsConfigModal(self.db, self.guild_id))
    
    @discord.ui.button(label="⚡ Bonus", style=discord.ButtonStyle.secondary)
    async def bonus_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BonusConfigModal(self.db, self.guild_id))

class GeneralConfigModal(discord.ui.Modal):
    def __init__(self, db: LevelDB, guild_id: str):
        super().__init__(title="⚙️ Configuration Générale")
        self.db = db
        self.guild_id = guild_id
        
        config = db.get_guild_config(guild_id)
        
        self.xp_per_message = discord.ui.TextInput(
            label="XP par message",
            placeholder="15",
            default=str(config.get('xp_per_message', 15)),
            max_length=3
        )
        
        self.xp_cooldown = discord.ui.TextInput(
            label="Cooldown XP (secondes)",
            placeholder="60",
            default=str(config.get('xp_cooldown', 60)),
            max_length=4
        )
        
        self.level_up_message = discord.ui.TextInput(
            label="Message de niveau",
            placeholder="🎉 {user} niveau {level} !",
            default=config.get('level_up_message', "🎉 {user} niveau {level} !"),
            style=discord.TextStyle.paragraph,
            max_length=500
        )
        
        self.add_item(self.xp_per_message)
        self.add_item(self.xp_cooldown)
        self.add_item(self.level_up_message)
    
    async def on_submit(self, interaction: discord.Interaction):
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE level_config 
            SET xp_per_message = ?, xp_cooldown = ?, level_up_message = ?, updated_at = ?
            WHERE guild_id = ?
        ''', (
            int(self.xp_per_message.value),
            int(self.xp_cooldown.value),
            self.level_up_message.value,
            datetime.now().isoformat(),
            self.guild_id
        ))
        
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="✅ Configuration Mise à Jour",
            description="Les paramètres généraux ont été sauvegardés !",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class RewardsConfigModal(discord.ui.Modal):
    def __init__(self, db: LevelDB, guild_id: str):
        super().__init__(title="🎁 Configuration des Récompenses")
        self.db = db
        self.guild_id = guild_id
        
        self.level = discord.ui.TextInput(
            label="Niveau pour la récompense",
            placeholder="10",
            max_length=3
        )
        
        self.role_id = discord.ui.TextInput(
            label="ID du rôle à donner",
            placeholder="123456789012345678",
            max_length=20
        )
        
        self.add_item(self.level)
        self.add_item(self.role_id)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            level = int(self.level.value)
            role_id = self.role_id.value
            
            # Vérifie que le rôle existe
            guild = interaction.guild
            role = guild.get_role(int(role_id))
            if not role:
                await interaction.response.send_message("❌ Rôle introuvable !", ephemeral=True)
                return
            
            # Ajoute la récompense
            reward_data = {"role_id": role_id, "role_name": role.name}
            
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO level_rewards (guild_id, level, reward_type, reward_data)
                VALUES (?, ?, ?, ?)
            ''', (self.guild_id, level, "role", json.dumps(reward_data)))
            conn.commit()
            conn.close()
            
            embed = discord.Embed(
                title="✅ Récompense Ajoutée",
                description=f"Le rôle **{role.name}** sera donné au niveau **{level}** !",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Valeurs invalides !", ephemeral=True)

class ExclusionsConfigModal(discord.ui.Modal):
    def __init__(self, db: LevelDB, guild_id: str):
        super().__init__(title="🚫 Configuration des Exclusions")
        self.db = db
        self.guild_id = guild_id
        
        config = db.get_guild_config(guild_id)
        no_xp_channels = json.loads(config.get('no_xp_channels', '[]'))
        no_xp_roles = json.loads(config.get('no_xp_roles', '[]'))
        
        self.no_xp_channels = discord.ui.TextInput(
            label="Canaux sans XP (IDs séparés par des virgules)",
            placeholder="123456789,987654321",
            default=','.join(no_xp_channels),
            style=discord.TextStyle.paragraph,
            max_length=1000
        )
        
        self.no_xp_roles = discord.ui.TextInput(
            label="Rôles sans XP (IDs séparés par des virgules)",
            placeholder="123456789,987654321",
            default=','.join(no_xp_roles),
            style=discord.TextStyle.paragraph,
            max_length=1000
        )
        
        self.add_item(self.no_xp_channels)
        self.add_item(self.no_xp_roles)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Parse les IDs
        channel_ids = [id.strip() for id in self.no_xp_channels.value.split(',') if id.strip()]
        role_ids = [id.strip() for id in self.no_xp_roles.value.split(',') if id.strip()]
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE level_config 
            SET no_xp_channels = ?, no_xp_roles = ?, updated_at = ?
            WHERE guild_id = ?
        ''', (
            json.dumps(channel_ids),
            json.dumps(role_ids),
            datetime.now().isoformat(),
            self.guild_id
        ))
        
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="✅ Exclusions Mises à Jour",
            description="Les canaux et rôles exclus ont été sauvegardés !",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class BonusConfigModal(discord.ui.Modal):
    def __init__(self, db: LevelDB, guild_id: str):
        super().__init__(title="⚡ Configuration des Bonus")
        self.db = db
        self.guild_id = guild_id
        
        self.channel_id = discord.ui.TextInput(
            label="ID du canal à bonifier",
            placeholder="123456789012345678",
            max_length=20
        )
        
        self.multiplier = discord.ui.TextInput(
            label="Multiplicateur (ex: 1.5 pour +50%)",
            placeholder="1.5",
            max_length=5
        )
        
        self.add_item(self.channel_id)
        self.add_item(self.multiplier)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            channel_id = self.channel_id.value
            multiplier = float(self.multiplier.value)
            
            # Vérifie le canal
            guild = interaction.guild
            channel = guild.get_channel(int(channel_id))
            if not channel:
                await interaction.response.send_message("❌ Canal introuvable !", ephemeral=True)
                return
            
            # Met à jour les bonus
            config = self.db.get_guild_config(self.guild_id)
            bonus_channels = json.loads(config.get('bonus_channels', '{}'))
            bonus_channels[channel_id] = multiplier
            
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE level_config 
                SET bonus_channels = ?, updated_at = ?
                WHERE guild_id = ?
            ''', (
                json.dumps(bonus_channels),
                datetime.now().isoformat(),
                self.guild_id
            ))
            
            conn.commit()
            conn.close()
            
            embed = discord.Embed(
                title="✅ Bonus Ajouté",
                description=f"Le canal **{channel.name}** aura un multiplicateur de **x{multiplier}** !",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Valeurs invalides !", ephemeral=True)

# Commandes principales
class LevelSystem(commands.Cog):
    """🎯 Système de niveaux et XP complet pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.manager = LevelManager(bot)
        self.voice_tracking = {}  # user_id: join_time
        self.voice_xp_task.start()
    
    def cog_unload(self):
        self.voice_xp_task.cancel()
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listener pour les messages"""
        if message.guild:
            await self.manager.process_message_xp(message)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Listener pour le vocal"""
        if member.bot:
            return
        
        user_id = str(member.id)
        
        # Utilisateur rejoint un canal
        if before.channel is None and after.channel is not None:
            self.voice_tracking[user_id] = datetime.now()
        
        # Utilisateur quitte un canal
        elif before.channel is not None and after.channel is None:
            if user_id in self.voice_tracking:
                # Calcule le temps passé
                join_time = self.voice_tracking.pop(user_id)
                duration = datetime.now() - join_time
                minutes = int(duration.total_seconds() / 60)
                
                if minutes > 0:
                    # Donne de l'XP vocal
                    config = self.manager.db.get_guild_config(str(member.guild.id))
                    xp_per_minute = config.get('xp_per_voice_minute', 5)
                    total_xp = minutes * xp_per_minute
                    
                    level_up, old_level, new_level = self.manager.db.add_xp(
                        str(member.id), str(member.guild.id), total_xp, "voice"
                    )
                    
                    if level_up:
                        await self.manager.handle_level_up(
                            member.guild, member, old_level, new_level, 
                            member.guild.system_channel or member.guild.text_channels[0]
                        )
    
    @tasks.loop(minutes=1)
    async def voice_xp_task(self):
        """Donne de l'XP toutes les minutes pour les utilisateurs en vocal"""
        for user_id, join_time in list(self.voice_tracking.items()):
            try:
                # Trouve l'utilisateur
                user = self.bot.get_user(int(user_id))
                if not user:
                    continue
                
                # Trouve le serveur (suppose qu'il n'est que dans un seul vocal à la fois)
                for guild in self.bot.guilds:
                    member = guild.get_member(int(user_id))
                    if member and member.voice and member.voice.channel:
                        config = self.manager.db.get_guild_config(str(guild.id))
                        if config.get('enabled', True):
                            xp_amount = config.get('xp_per_voice_minute', 5)
                            
                            level_up, old_level, new_level = self.manager.db.add_xp(
                                user_id, str(guild.id), xp_amount, "voice"
                            )
                            
                            if level_up:
                                channel = member.voice.channel if hasattr(member.voice.channel, 'send') else guild.system_channel or guild.text_channels[0]
                                await self.manager.handle_level_up(guild, member, old_level, new_level, channel)
                        break
            except Exception as e:
                print(f"Erreur XP vocal: {e}")
    
    @app_commands.command(name="level", description="🎯 Affiche votre niveau ou celui d'un utilisateur")
    async def level(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        target = user or interaction.user
        
        if target.bot:
            await interaction.response.send_message("❌ Les bots n'ont pas de niveau !", ephemeral=True)
            return
        
        user_data = self.manager.db.get_user_level(str(target.id), str(interaction.guild.id))
        
        # Calcule les informations de niveau
        current_level = user_data['level']
        current_xp = user_data['xp']
        total_xp = user_data['total_xp']
        
        current_level_xp = self.manager.db.xp_for_level(current_level)
        next_level_xp = self.manager.db.xp_for_level(current_level + 1)
        xp_for_next = next_level_xp - current_xp
        progress = ((current_xp - current_level_xp) / (next_level_xp - current_level_xp)) * 100
        
        # Calcule le rang
        leaderboard = self.manager.db.get_leaderboard(str(interaction.guild.id), 1000)
        rank = next((i+1 for i, user in enumerate(leaderboard) if user['user_id'] == str(target.id)), "N/A")
        
        # Crée l'embed
        embed = discord.Embed(
            title=f"🎯 Niveau de {target.display_name}",
            color=0x00ff00 if target == interaction.user else 0x3498db
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        
        embed.add_field(name="📊 Niveau Actuel", value=f"**{current_level}**", inline=True)
        embed.add_field(name="⭐ Total XP", value=f"**{total_xp:,}**", inline=True)
        embed.add_field(name="🏆 Classement", value=f"**#{rank}**", inline=True)
        
        embed.add_field(name="🎯 XP Actuel", value=f"**{current_xp:,}**", inline=True)
        embed.add_field(name="🎯 Prochain Niveau", value=f"**{xp_for_next:,}** XP", inline=True)
        embed.add_field(name="📈 Progression", value=f"**{progress:.1f}%**", inline=True)
        
        embed.add_field(name="💬 Messages", value=f"**{user_data['messages']:,}**", inline=True)
        embed.add_field(name="🎤 Minutes Vocal", value=f"**{user_data['voice_minutes']:,}**", inline=True)
        embed.add_field(name="🎖️ Prestige", value=f"**{user_data['prestige']}**", inline=True)
        
        # Barre de progression
        bar_length = 20
        filled = int((progress / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        embed.add_field(name="Progression vers niveau suivant", value=f"`{bar}` {progress:.1f}%", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leaderboard", description="🏆 Affiche le classement des niveaux")
    async def leaderboard(self, interaction: discord.Interaction, page: Optional[int] = 1):
        if page < 1:
            page = 1
        
        limit = 10
        offset = (page - 1) * limit
        
        leaderboard = self.manager.db.get_leaderboard(str(interaction.guild.id), offset + limit)
        
        if not leaderboard:
            await interaction.response.send_message("❌ Aucune donnée de niveau trouvée !", ephemeral=True)
            return
        
        # Filtre pour la page
        page_data = leaderboard[offset:offset + limit]
        
        embed = discord.Embed(
            title=f"🏆 Classement des Niveaux - Page {page}",
            color=0xffd700
        )
        
        description = ""
        for i, user_data in enumerate(page_data):
            rank = offset + i + 1
            user = self.bot.get_user(int(user_data['user_id']))
            username = user.display_name if user else f"Utilisateur {user_data['user_id']}"
            
            if rank == 1:
                medal = "🥇"
            elif rank == 2:
                medal = "🥈"
            elif rank == 3:
                medal = "🥉"
            else:
                medal = f"**#{rank}**"
            
            description += f"{medal} {username} - **Niveau {user_data['level']}** ({user_data['total_xp']:,} XP)\n"
        
        embed.description = description
        
        # Navigation
        view = LeaderboardView(self.manager.db, interaction.guild.id, page)
        
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="level_config", description="⚙️ Configuration du système de niveaux (Admin)")
    @app_commands.describe(action="Action de configuration à effectuer")
    @app_commands.choices(action=[
        app_commands.Choice(name="Configuration générale", value="general"),
        app_commands.Choice(name="Récompenses", value="rewards"),
        app_commands.Choice(name="Exclusions", value="exclusions"),
        app_commands.Choice(name="Bonus", value="bonus"),
        app_commands.Choice(name="Activer/Désactiver", value="toggle")
    ])
    async def level_config(self, interaction: discord.Interaction, action: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Vous devez être administrateur !", ephemeral=True)
            return
        
        guild_id = str(interaction.guild.id)
        
        if action == "toggle":
            config = self.manager.db.get_guild_config(guild_id)
            new_status = not config.get('enabled', True)
            
            conn = sqlite3.connect(self.manager.db.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE level_config SET enabled = ?, updated_at = ? WHERE guild_id = ?
            ''', (new_status, datetime.now().isoformat(), guild_id))
            conn.commit()
            conn.close()
            
            status_text = "activé" if new_status else "désactivé"
            embed = discord.Embed(
                title=f"✅ Système {status_text}",
                description=f"Le système de niveaux a été {status_text} !",
                color=0x00ff00 if new_status else 0xff0000
            )
            await interaction.response.send_message(embed=embed)
        
        else:
            view = LevelConfigView(self.manager.db, guild_id)
            embed = discord.Embed(
                title="⚙️ Configuration du Système de Niveaux",
                description="Choisissez l'élément à configurer :",
                color=0x3498db
            )
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="givexp", description="⭐ Donner de l'XP à un utilisateur (Admin)")
    async def givexp(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Vous devez être administrateur !", ephemeral=True)
            return
        
        if user.bot:
            await interaction.response.send_message("❌ Impossible de donner de l'XP à un bot !", ephemeral=True)
            return
        
        if amount <= 0:
            await interaction.response.send_message("❌ Le montant doit être positif !", ephemeral=True)
            return
        
        level_up, old_level, new_level = self.manager.db.add_xp(
            str(user.id), str(interaction.guild.id), amount
        )
        
        embed = discord.Embed(
            title="⭐ XP Accordé",
            description=f"**{amount:,} XP** donné à {user.mention}",
            color=0x00ff00
        )
        
        if level_up:
            embed.add_field(
                name="🎉 Niveau Supérieur !",
                value=f"Niveau {old_level} → **{new_level}**",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
        
        if level_up:
            await self.manager.handle_level_up(interaction.guild, user, old_level, new_level, interaction.channel)
    
    @app_commands.command(name="xpboost", description="⚡ Donner un boost XP temporaire à un utilisateur (Admin)")
    async def xpboost(self, interaction: discord.Interaction, user: discord.Member, multiplier: float, duration_minutes: int):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Vous devez être administrateur !", ephemeral=True)
            return
        
        if user.bot:
            await interaction.response.send_message("❌ Impossible de donner un boost à un bot !", ephemeral=True)
            return
        
        if multiplier <= 0 or duration_minutes <= 0:
            await interaction.response.send_message("❌ Les valeurs doivent être positives !", ephemeral=True)
            return
        
        # Calcule l'expiration
        expires_at = datetime.now() + timedelta(minutes=duration_minutes)
        
        # Met à jour la base
        conn = sqlite3.connect(self.manager.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_levels 
            SET boost_multiplier = ?, boost_expires = ?, updated_at = ?
            WHERE user_id = ? AND guild_id = ?
        ''', (multiplier, expires_at.isoformat(), datetime.now().isoformat(), 
              str(user.id), str(interaction.guild.id)))
        
        # Ajoute dans la table des boosts
        cursor.execute('''
            INSERT INTO xp_boosts (user_id, guild_id, multiplier, duration_minutes, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (str(user.id), str(interaction.guild.id), multiplier, duration_minutes, expires_at.isoformat()))
        
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="⚡ Boost XP Accordé",
            description=f"Boost **x{multiplier}** donné à {user.mention} pour **{duration_minutes} minutes** !",
            color=0xffd700
        )
        embed.add_field(name="Expire le", value=f"<t:{int(expires_at.timestamp())}:F>", inline=False)
        
        await interaction.response.send_message(embed=embed)

class LeaderboardView(discord.ui.View):
    """Interface de navigation du leaderboard"""
    
    def __init__(self, db: LevelDB, guild_id: str, current_page: int = 1):
        super().__init__(timeout=300)
        self.db = db
        self.guild_id = guild_id
        self.current_page = current_page
    
    @discord.ui.button(label="⬅️ Précédent", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            embed = await self.get_leaderboard_embed(interaction.client)
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="➡️ Suivant", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        embed = await self.get_leaderboard_embed(interaction.client)
        if embed:
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            self.current_page -= 1  # Revient en arrière si pas de données
            await interaction.response.defer()
    
    async def get_leaderboard_embed(self, bot) -> Optional[discord.Embed]:
        limit = 10
        offset = (self.current_page - 1) * limit
        
        leaderboard = self.db.get_leaderboard(self.guild_id, offset + limit)
        page_data = leaderboard[offset:offset + limit]
        
        if not page_data:
            return None
        
        embed = discord.Embed(
            title=f"🏆 Classement des Niveaux - Page {self.current_page}",
            color=0xffd700
        )
        
        description = ""
        for i, user_data in enumerate(page_data):
            rank = offset + i + 1
            user = bot.get_user(int(user_data['user_id']))
            username = user.display_name if user else f"Utilisateur {user_data['user_id']}"
            
            if rank == 1:
                medal = "🥇"
            elif rank == 2:
                medal = "🥈"
            elif rank == 3:
                medal = "🥉"
            else:
                medal = f"**#{rank}**"
            
            description += f"{medal} {username} - **Niveau {user_data['level']}** ({user_data['total_xp']:,} XP)\n"
        
        embed.description = description
        return embed

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))

