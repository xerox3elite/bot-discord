#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arsenal V4.5.2 Ultimate - Système de Sanctions
==============================================
Auteur: Arsenal Studio
Description: Module de sanctions basique pour compatibilité
"""

import discord
from discord.ext import commands
import asyncio
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

logger = logging.getLogger('Arsenal.Sanctions')

class SanctionDatabase:
    """Gestionnaire de base de données pour les sanctions"""
    
    def __init__(self, db_path: str = "data/sanctions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données des sanctions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Table des sanctions
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sanctions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        moderator_id INTEGER NOT NULL,
                        sanction_type TEXT NOT NULL,
                        reason TEXT,
                        duration INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        evidence TEXT
                    )
                ''')
                
                # Table des infractions
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS infractions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        infraction_type TEXT NOT NULL,
                        severity INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        resolved BOOLEAN DEFAULT FALSE
                    )
                ''')
                
                conn.commit()
                logger.info("Base de données sanctions initialisée")
                
        except Exception as e:
            logger.error(f"Erreur initialisation DB sanctions: {e}")
    
    def add_sanction(self, guild_id: int, user_id: int, moderator_id: int, 
                    sanction_type: str, reason: str = None, duration: int = None) -> int:
        """Ajoute une sanction"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                expires_at = None
                if duration:
                    expires_at = datetime.now() + timedelta(seconds=duration)
                
                cursor.execute('''
                    INSERT INTO sanctions (guild_id, user_id, moderator_id, sanction_type, reason, duration, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (guild_id, user_id, moderator_id, sanction_type, reason, duration, expires_at))
                
                sanction_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Sanction ajoutée: ID {sanction_id} pour utilisateur {user_id}")
                return sanction_id
                
        except Exception as e:
            logger.error(f"Erreur ajout sanction: {e}")
            return 0
    
    def get_user_sanctions(self, guild_id: int, user_id: int) -> List[Dict]:
        """Récupère les sanctions d'un utilisateur"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM sanctions 
                    WHERE guild_id = ? AND user_id = ? 
                    ORDER BY created_at DESC
                ''', (guild_id, user_id))
                
                columns = [description[0] for description in cursor.description]
                sanctions = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                return sanctions
                
        except Exception as e:
            logger.error(f"Erreur récupération sanctions: {e}")
            return []

class SanctionManager:
    """Gestionnaire des sanctions"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = SanctionDatabase()
    
    async def warn_user(self, guild: discord.Guild, user: discord.Member, 
                       moderator: discord.Member, reason: str = None) -> int:
        """Avertir un utilisateur"""
        try:
            sanction_id = self.db.add_sanction(
                guild.id, user.id, moderator.id, "warn", reason
            )
            
            # Envoyer un message privé à l'utilisateur
            try:
                embed = discord.Embed(
                    title="⚠️ Avertissement",
                    description=f"Vous avez reçu un avertissement sur **{guild.name}**",
                    color=0xffaa00
                )
                embed.add_field(name="Raison", value=reason or "Non spécifiée", inline=False)
                embed.add_field(name="Modérateur", value=moderator.mention, inline=True)
                
                await user.send(embed=embed)
            except discord.Forbidden:
                logger.warning(f"Impossible d'envoyer un MP à {user.id}")
            
            logger.info(f"Utilisateur {user.id} averti par {moderator.id}")
            return sanction_id
            
        except Exception as e:
            logger.error(f"Erreur avertissement: {e}")
            return 0
    
    async def timeout_user(self, guild: discord.Guild, user: discord.Member,
                          moderator: discord.Member, duration: int, reason: str = None) -> int:
        """Mettre en timeout un utilisateur"""
        try:
            # Appliquer le timeout Discord
            timeout_until = datetime.now() + timedelta(seconds=duration)
            await user.timeout(timeout_until, reason=reason)
            
            # Enregistrer en base
            sanction_id = self.db.add_sanction(
                guild.id, user.id, moderator.id, "timeout", reason, duration
            )
            
            logger.info(f"Utilisateur {user.id} timeout par {moderator.id} pour {duration}s")
            return sanction_id
            
        except Exception as e:
            logger.error(f"Erreur timeout: {e}")
            return 0
    
    async def kick_user(self, guild: discord.Guild, user: discord.Member,
                       moderator: discord.Member, reason: str = None) -> int:
        """Expulser un utilisateur"""
        try:
            # Enregistrer avant d'expulser
            sanction_id = self.db.add_sanction(
                guild.id, user.id, moderator.id, "kick", reason
            )
            
            # Expulser
            await user.kick(reason=reason)
            
            logger.info(f"Utilisateur {user.id} expulsé par {moderator.id}")
            return sanction_id
            
        except Exception as e:
            logger.error(f"Erreur expulsion: {e}")
            return 0
    
    async def ban_user(self, guild: discord.Guild, user: discord.Member,
                      moderator: discord.Member, duration: int = None, reason: str = None) -> int:
        """Bannir un utilisateur"""
        try:
            # Enregistrer avant de bannir
            sanction_id = self.db.add_sanction(
                guild.id, user.id, moderator.id, "ban", reason, duration
            )
            
            # Bannir
            await user.ban(reason=reason, delete_message_days=1)
            
            logger.info(f"Utilisateur {user.id} banni par {moderator.id}")
            return sanction_id
            
        except Exception as e:
            logger.error(f"Erreur bannissement: {e}")
            return 0

# Instance globale pour compatibilité
sanctions_manager = None

def init_sanctions(bot):
    """Initialise le gestionnaire de sanctions"""
    global sanctions_manager
    sanctions_manager = SanctionManager(bot)
    return sanctions_manager

def get_sanctions_manager():
    """Retourne l'instance du gestionnaire de sanctions"""
    return sanctions_manager

# Classes et fonctions pour compatibilité
class Sanction:
    """Classe de compatibilité pour les sanctions"""
    
    def __init__(self, bot):
        self.bot = bot
        self.manager = SanctionManager(bot)
    
    async def warn(self, guild, user, moderator, reason=None):
        """Avertir un utilisateur"""
        return await self.manager.warn_user(guild, user, moderator, reason)
    
    async def timeout(self, guild, user, moderator, duration, reason=None):
        """Timeout un utilisateur"""
        return await self.manager.timeout_user(guild, user, moderator, duration, reason)
    
    async def kick(self, guild, user, moderator, reason=None):
        """Expulser un utilisateur"""
        return await self.manager.kick_user(guild, user, moderator, reason)
    
    async def ban(self, guild, user, moderator, duration=None, reason=None):
        """Bannir un utilisateur"""
        return await self.manager.ban_user(guild, user, moderator, duration, reason)
    
    def get_user_sanctions(self, guild_id, user_id):
        """Récupérer les sanctions d'un utilisateur"""
        return SanctionDatabase().get_user_sanctions(guild_id, user_id)

# Export pour compatibilité
__all__ = [
    'Sanction',
    'SanctionManager', 
    'SanctionDatabase',
    'init_sanctions',
    'get_sanctions_manager'
]
