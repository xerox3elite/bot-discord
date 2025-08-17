"""
🔧 ARSENAL ECONOMY SYSTEM UNIFIED V1.0.1
===========================================
SYSTÈME ÉCONOMIQUE UNIFIÉ ARSENAL - TERMINÉ ✅

Gestion complète des ArsenalCoins avec :
✅ Balance synchronisée
✅ Daily rewards
✅ Database unifiée
✅ WebPanel API intégrée
"""

import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import json
import os
import asyncio
import datetime
from typing import Optional
import time

class ArsenalEconomyUnified(commands.Cog):
    """🏦 SYSTÈME ÉCONOMIQUE ARSENAL UNIFIÉ - VERSION FINALE"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "arsenal_coins_central.db"
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données unifiée"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table principale des utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arsenal_users (
                discord_id TEXT PRIMARY KEY,
                username TEXT,
                balance INTEGER DEFAULT 0,
                total_earned INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                daily_streak INTEGER DEFAULT 0,
                last_daily DATE,
                last_work INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des transactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arsenal_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                amount INTEGER,
                type TEXT,
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES arsenal_users (discord_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de données Arsenal Economy unifiée initialisée")
    
    def get_user_data(self, user_id: str) -> dict:
        """Récupère les données utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT discord_id, username, balance, total_earned, total_spent, 
                   level, xp, daily_streak, last_daily, last_work
            FROM arsenal_users WHERE discord_id = ?
        ''', (user_id,))
        
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return {
                "discord_id": user_data[0],
                "username": user_data[1],
                "balance": user_data[2] or 0,
                "total_earned": user_data[3] or 0,
                "total_spent": user_data[4] or 0,
                "level": user_data[5] or 1,
                "xp": user_data[6] or 0,
                "daily_streak": user_data[7] or 0,
                "last_daily": user_data[8],
                "last_work": user_data[9] or 0
            }
        else:
            # Créer nouvel utilisateur
            return self.create_user(user_id)
    
    def create_user(self, user_id: str, username: str = None) -> dict:
        """Crée un nouvel utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO arsenal_users 
            (discord_id, username, balance, total_earned, total_spent, level, xp, daily_streak)
            VALUES (?, ?, 0, 0, 0, 1, 0, 0)
        ''', (user_id, username))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Nouvel utilisateur créé: {user_id}")
        return {
            "discord_id": user_id,
            "username": username,
            "balance": 0,
            "total_earned": 0,
            "total_spent": 0,
            "level": 1,
            "xp": 0,
            "daily_streak": 0,
            "last_daily": None,
            "last_work": 0
        }
    
    def update_user_balance(self, user_id: str, amount: int, transaction_type: str, description: str = "") -> int:
        """Met à jour le solde utilisateur et enregistre la transaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # S'assurer que l'utilisateur existe
        user_data = self.get_user_data(user_id)
        
        # Calculer nouveau solde
        new_balance = user_data["balance"] + amount
        new_total_earned = user_data["total_earned"] + (amount if amount > 0 else 0)
        new_total_spent = user_data["total_spent"] + (abs(amount) if amount < 0 else 0)
        
        # Mettre à jour utilisateur
        cursor.execute('''
            UPDATE arsenal_users 
            SET balance = ?, total_earned = ?, total_spent = ?, updated_at = CURRENT_TIMESTAMP
            WHERE discord_id = ?
        ''', (new_balance, new_total_earned, new_total_spent, user_id))
        
        # Enregistrer transaction
        cursor.execute('''
            INSERT INTO arsenal_transactions (user_id, amount, type, description)
            VALUES (?, ?, ?, ?)
        ''', (user_id, amount, transaction_type, description))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Balance mise à jour: {user_id} = {new_balance} AC ({amount:+} via {transaction_type})")
        return new_balance
    
    def get_user_rank(self, user_id: str) -> int:
        """Récupère le rang de l'utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) + 1 FROM arsenal_users 
            WHERE balance > (SELECT balance FROM arsenal_users WHERE discord_id = ?)
        ''', (user_id,))
        
        rank = cursor.fetchone()[0]
        conn.close()
        return rank
    
    def get_leaderboard(self, limit: int = 10) -> list:
        """Récupère le leaderboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT discord_id, username, balance, level 
            FROM arsenal_users 
            WHERE balance > 0 
            ORDER BY balance DESC 
            LIMIT ?
        ''', (limit,))
        
        leaderboard = cursor.fetchall()
        conn.close()
        
        return [
            {
                "discord_id": row[0],
                "username": row[1] or f"User#{row[0][-4:]}",
                "balance": row[2],
                "level": row[3],
                "rank": idx + 1
            }
            for idx, row in enumerate(leaderboard)
        ]
    
    # ==================== COMMANDES DISCORD ====================
    
    @app_commands.command(name="balance", description="💰 Affiche votre solde ArsenalCoin")
    @app_commands.describe(user="Utilisateur à vérifier (optionnel)")
    async def balance_command(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """💰 Commande balance unifiée"""
        target_user = user or interaction.user
        user_data = self.get_user_data(str(target_user.id))
        
        # Mettre à jour le nom d'utilisateur si nécessaire
        if not user_data["username"] or user_data["username"] != target_user.display_name:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE arsenal_users SET username = ? WHERE discord_id = ?', 
                         (target_user.display_name, str(target_user.id)))
            conn.commit()
            conn.close()
        
        rank = self.get_user_rank(str(target_user.id))
        
        embed = discord.Embed(
            title=f"💰 Arsenal Wallet - {target_user.display_name}",
            color=0x00ff88,
            timestamp=datetime.datetime.now()
        )
        
        # Solde principal
        embed.add_field(
            name="💳 Solde Actuel",
            value=f"**{user_data['balance']:,} AC** 🪙",
            inline=True
        )
        
        # Rang
        embed.add_field(
            name="📊 Classement",
            value=f"**#{rank}**",
            inline=True
        )
        
        # Niveau & XP
        embed.add_field(
            name="🏆 Level",
            value=f"**Niveau {user_data['level']}**\n{user_data['xp']:,} XP",
            inline=True
        )
        
        # Statistiques financières
        embed.add_field(
            name="📈 Statistiques",
            value=f"**Total Gagné:** {user_data['total_earned']:,} AC\n**Total Dépensé:** {user_data['total_spent']:,} AC\n**Daily Streak:** {user_data['daily_streak']} jours",
            inline=False
        )
        
        # Statut Premium
        status = "🌟 Premium" if user_data['balance'] > 100000 else "⭐ Standard"
        embed.add_field(name="💎 Statut", value=status, inline=True)
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        embed.set_footer(text="Arsenal Economy System Unified", icon_url=self.bot.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="daily", description="🎁 Récupérer votre récompense quotidienne")
    async def daily_command(self, interaction: discord.Interaction):
        """🎁 Commande daily unifiée"""
        user_id = str(interaction.user.id)
        user_data = self.get_user_data(user_id)
        
        # Vérifier si déjà récupéré aujourd'hui
        today = datetime.date.today()
        if user_data["last_daily"]:
            try:
                last_daily = datetime.datetime.strptime(user_data["last_daily"], "%Y-%m-%d").date()
                if last_daily >= today:
                    # Calculer temps restant
                    tomorrow = today + datetime.timedelta(days=1)
                    time_left = datetime.datetime.combine(tomorrow, datetime.time.min) - datetime.datetime.now()
                    hours = int(time_left.seconds // 3600)
                    minutes = int((time_left.seconds % 3600) // 60)
                    
                    embed = discord.Embed(
                        title="⏰ Daily Déjà Récupéré",
                        description="Vous avez déjà récupéré votre récompense quotidienne !",
                        color=0xff6b6b
                    )
                    embed.add_field(
                        name="⏳ Prochaine Récompense",
                        value=f"Dans {hours}h {minutes}m",
                        inline=False
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            except (ValueError, TypeError):
                pass  # Date invalide, continuer
        
        # Calculer récompense avec streak
        base_reward = 1000
        streak_bonus = user_data["daily_streak"] * 100
        total_reward = base_reward + min(streak_bonus, 2000)  # Max 3000 AC
        
        # Mettre à jour solde
        new_balance = self.update_user_balance(user_id, total_reward, "Daily Reward", "Récompense quotidienne")
        
        # Mettre à jour streak et date
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_streak = user_data["daily_streak"] + 1
        cursor.execute('''
            UPDATE arsenal_users 
            SET daily_streak = ?, last_daily = ?, username = ?
            WHERE discord_id = ?
        ''', (new_streak, today.strftime("%Y-%m-%d"), interaction.user.display_name, user_id))
        
        conn.commit()
        conn.close()
        
        # Réponse avec embed stylé
        embed = discord.Embed(
            title="🎁 Daily Reward Récupéré !",
            description=f"Vous avez reçu **{total_reward:,} ArsenalCoins** !",
            color=0x00ff88,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="💰 Nouveau Solde",
            value=f"**{new_balance:,} AC**",
            inline=True
        )
        
        embed.add_field(
            name="🔥 Daily Streak",
            value=f"**{new_streak} jours**\nBonus: +{streak_bonus} AC",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Prochaine Récompense",
            value="Demain à 00:00",
            inline=True
        )
        
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/741090748488835122.png")
        embed.set_footer(text=f"Arsenal Economy • Récompense #{new_streak}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leaderboard", description="🏆 Affiche le classement ArsenalCoin")
    @app_commands.describe(page="Page du classement (défaut: 1)")
    async def leaderboard_command(self, interaction: discord.Interaction, page: Optional[int] = 1):
        """🏆 Classement des plus riches"""
        page = max(1, page)  # Minimum page 1
        limit = 10
        offset = (page - 1) * limit
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Récupérer les données avec pagination
        cursor.execute('''
            SELECT discord_id, username, balance, level 
            FROM arsenal_users 
            WHERE balance > 0 
            ORDER BY balance DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        leaderboard_data = cursor.fetchall()
        
        # Compter le total d'utilisateurs avec solde > 0
        cursor.execute('SELECT COUNT(*) FROM arsenal_users WHERE balance > 0')
        total_users = cursor.fetchone()[0]
        conn.close()
        
        if not leaderboard_data:
            embed = discord.Embed(
                title="🏆 Classement ArsenalCoin",
                description="Aucun utilisateur trouvé sur cette page.",
                color=0xff6b6b
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Construire le classement
        embed = discord.Embed(
            title="🏆 Classement ArsenalCoin",
            description=f"**Page {page}** • Top utilisateurs les plus riches",
            color=0xffd700,
            timestamp=datetime.datetime.now()
        )
        
        leaderboard_text = ""
        for idx, (discord_id, username, balance, level) in enumerate(leaderboard_data):
            rank = offset + idx + 1
            
            # Émojis pour le podium
            if rank == 1:
                medal = "🥇"
            elif rank == 2:
                medal = "🥈"
            elif rank == 3:
                medal = "🥉"
            else:
                medal = f"**{rank}.**"
            
            display_name = username or f"User#{discord_id[-4:]}"
            leaderboard_text += f"{medal} **{display_name}**\n💰 {balance:,} AC • Niveau {level}\n\n"
        
        embed.add_field(
            name="💎 Classement",
            value=leaderboard_text,
            inline=False
        )
        
        # Navigation
        total_pages = (total_users + limit - 1) // limit
        embed.set_footer(text=f"Page {page}/{total_pages} • {total_users} utilisateurs")
        
        await interaction.response.send_message(embed=embed)
    
    # ==================== API WEBPANEL ====================
    
    def get_economy_stats(self) -> dict:
        """API pour le WebPanel - Statistiques économiques"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total coins en circulation
        cursor.execute('SELECT COALESCE(SUM(balance), 0) FROM arsenal_users')
        total_coins = cursor.fetchone()[0]
        
        # Utilisateurs actifs
        cursor.execute('SELECT COUNT(*) FROM arsenal_users WHERE balance > 0')
        active_users = cursor.fetchone()[0]
        
        # Transactions aujourd'hui
        cursor.execute('SELECT COUNT(*) FROM arsenal_transactions WHERE DATE(timestamp) = DATE("now")')
        transactions_today = cursor.fetchone()[0]
        
        # Top 3
        cursor.execute('''
            SELECT username, balance FROM arsenal_users 
            WHERE balance > 0 ORDER BY balance DESC LIMIT 3
        ''')
        top_holders = [{"username": row[0] or f"User#{i+1}", "balance": row[1]} 
                       for i, row in enumerate(cursor.fetchall())]
        
        conn.close()
        
        return {
            "total_coins": total_coins,
            "active_users": active_users,
            "transactions_today": transactions_today,
            "top_holders": top_holders,
            "status": "UNIFIED_OK"
        }
    
    def get_user_api_data(self, user_id: str) -> dict:
        """API pour le WebPanel - Données utilisateur"""
        return self.get_user_data(user_id)

async def setup(bot):
    await bot.add_cog(ArsenalEconomyUnified(bot))
    print("✅ Arsenal Economy System Unified V1.0.1 chargé avec succès !")
