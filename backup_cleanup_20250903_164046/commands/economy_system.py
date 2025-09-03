"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   💰 ARSENAL ECONOMY SYSTEM V4 - COMPLET                    ║
║                    Système d'économie et argent avancé                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import sqlite3
import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Union
import aiofiles
import os

class EconomyDB:
    """Gestionnaire de base de données pour le système d'économie"""
    
    def __init__(self):
        self.db_path = "arsenal_economy.db"
        self.init_database()
    
    def init_database(self):
        """Initialise toutes les tables de la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table principale des utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_economy (
                user_id TEXT PRIMARY KEY,
                guild_id TEXT NOT NULL,
                balance INTEGER DEFAULT 1000,
                bank INTEGER DEFAULT 0,
                bank_limit INTEGER DEFAULT 10000,
                daily_streak INTEGER DEFAULT 0,
                last_daily TEXT,
                last_work TEXT,
                last_crime TEXT,
                total_earned INTEGER DEFAULT 1000,
                total_spent INTEGER DEFAULT 0,
                job TEXT DEFAULT NULL,
                job_level INTEGER DEFAULT 1,
                job_xp INTEGER DEFAULT 0,
                prestige INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des configurations de guild
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS economy_config (
                guild_id TEXT PRIMARY KEY,
                enabled BOOLEAN DEFAULT 1,
                currency_name TEXT DEFAULT "Arsenal Coins",
                currency_symbol TEXT DEFAULT "🪙",
                starting_balance INTEGER DEFAULT 1000,
                daily_amount INTEGER DEFAULT 500,
                daily_streak_bonus INTEGER DEFAULT 100,
                max_daily_streak INTEGER DEFAULT 30,
                work_cooldown INTEGER DEFAULT 3600,
                crime_cooldown INTEGER DEFAULT 7200,
                work_min_reward INTEGER DEFAULT 100,
                work_max_reward INTEGER DEFAULT 500,
                crime_min_reward INTEGER DEFAULT 200,
                crime_max_reward INTEGER DEFAULT 1000,
                crime_fail_rate INTEGER DEFAULT 30,
                bank_interest_rate REAL DEFAULT 0.02,
                shop_tax_rate REAL DEFAULT 0.05,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des objets du shop
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price INTEGER NOT NULL,
                item_type TEXT NOT NULL,
                item_data TEXT DEFAULT "{}",
                stock INTEGER DEFAULT -1,
                max_per_user INTEGER DEFAULT -1,
                role_required TEXT,
                level_required INTEGER DEFAULT 0,
                available BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des inventaires utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                guild_id TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                acquired_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES shop_items (id)
            )
        ''')
        
        # Table des transactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                guild_id TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                description TEXT,
                reference_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des emplois
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                base_salary INTEGER NOT NULL,
                level_multiplier REAL DEFAULT 1.1,
                xp_required INTEGER DEFAULT 1000,
                requirements TEXT DEFAULT "{}",
                available BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des paris/jeux
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gambling_stats (
                user_id TEXT PRIMARY KEY,
                guild_id TEXT NOT NULL,
                games_played INTEGER DEFAULT 0,
                total_bet INTEGER DEFAULT 0,
                total_won INTEGER DEFAULT 0,
                biggest_win INTEGER DEFAULT 0,
                biggest_loss INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des statistiques globales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS economy_stats (
                guild_id TEXT PRIMARY KEY,
                total_users INTEGER DEFAULT 0,
                total_transactions INTEGER DEFAULT 0,
                total_money_circulation INTEGER DEFAULT 0,
                total_shop_sales INTEGER DEFAULT 0,
                last_reset TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user_economy(self, user_id: str, guild_id: str) -> Dict:
        """Récupère les données économiques d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_economy WHERE user_id = ? AND guild_id = ?
        ''', (user_id, guild_id))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, result))
        else:
            return self.create_user_economy(user_id, guild_id)
    
    def create_user_economy(self, user_id: str, guild_id: str) -> Dict:
        """Crée un nouvel utilisateur économique"""
        config = self.get_guild_config(guild_id)
        starting_balance = config.get('starting_balance', 1000)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_economy (user_id, guild_id, balance, total_earned, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, guild_id, starting_balance, starting_balance, 
              datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return {
            'user_id': user_id,
            'guild_id': guild_id,
            'balance': starting_balance,
            'bank': 0,
            'bank_limit': 10000,
            'daily_streak': 0,
            'total_earned': starting_balance,
            'total_spent': 0,
            'job': None,
            'job_level': 1,
            'job_xp': 0,
            'prestige': 0
        }
    
    def update_balance(self, user_id: str, guild_id: str, amount: int, transaction_type: str, description: str = None) -> bool:
        """Met à jour le solde d'un utilisateur et enregistre la transaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Récupère le solde actuel
        user_data = self.get_user_economy(user_id, guild_id)
        new_balance = user_data['balance'] + amount
        
        if new_balance < 0:
            conn.close()
            return False
        
        # Met à jour le solde
        if amount > 0:
            cursor.execute('''
                UPDATE user_economy 
                SET balance = ?, total_earned = total_earned + ?, updated_at = ?
                WHERE user_id = ? AND guild_id = ?
            ''', (new_balance, amount, datetime.now().isoformat(), user_id, guild_id))
        else:
            cursor.execute('''
                UPDATE user_economy 
                SET balance = ?, total_spent = total_spent + ?, updated_at = ?
                WHERE user_id = ? AND guild_id = ?
            ''', (new_balance, abs(amount), datetime.now().isoformat(), user_id, guild_id))
        
        # Enregistre la transaction
        cursor.execute('''
            INSERT INTO transactions (user_id, guild_id, transaction_type, amount, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, guild_id, transaction_type, amount, description))
        
        conn.commit()
        conn.close()
        return True
    
    def get_guild_config(self, guild_id: str) -> Dict:
        """Récupère la configuration économique du serveur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM economy_config WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()
        
        if result:
            columns = [desc[0] for desc in cursor.description]
            config = dict(zip(columns, result))
        else:
            # Crée la config par défaut
            cursor.execute('''
                INSERT INTO economy_config (guild_id) VALUES (?)
            ''', (guild_id,))
            conn.commit()
            config = {
                'guild_id': guild_id,
                'enabled': True,
                'currency_name': 'Arsenal Coins',
                'currency_symbol': '🪙',
                'starting_balance': 1000,
                'daily_amount': 500,
                'daily_streak_bonus': 100,
                'max_daily_streak': 30,
                'work_cooldown': 3600,
                'crime_cooldown': 7200,
                'work_min_reward': 100,
                'work_max_reward': 500,
                'crime_min_reward': 200,
                'crime_max_reward': 1000,
                'crime_fail_rate': 30,
                'bank_interest_rate': 0.02,
                'shop_tax_rate': 0.05
            }
        
        conn.close()
        return config
    
    def get_leaderboard(self, guild_id: str, order_by: str = "balance", limit: int = 10) -> List[Dict]:
        """Récupère le classement économique"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        valid_orders = ["balance", "bank", "total_earned", "total_spent"]
        if order_by not in valid_orders:
            order_by = "balance"
        
        cursor.execute(f'''
            SELECT * FROM user_economy 
            WHERE guild_id = ? 
            ORDER BY {order_by} DESC, balance DESC
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

class ShopManager:
    """Gestionnaire du système de boutique"""
    
    def __init__(self, db: EconomyDB):
        self.db = db
    
    def add_item(self, guild_id: str, name: str, description: str, price: int, 
                item_type: str, item_data: Dict = None, stock: int = -1) -> int:
        """Ajoute un objet au shop"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO shop_items (guild_id, name, description, price, item_type, item_data, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (guild_id, name, description, price, item_type, 
              json.dumps(item_data or {}), stock))
        
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return item_id
    
    def get_shop_items(self, guild_id: str, available_only: bool = True) -> List[Dict]:
        """Récupère les objets du shop"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM shop_items WHERE guild_id = ?'
        params = [guild_id]
        
        if available_only:
            query += ' AND available = 1'
        
        query += ' ORDER BY price ASC'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        items = []
        for result in results:
            columns = [desc[0] for desc in cursor.description]
            item = dict(zip(columns, result))
            item['item_data'] = json.loads(item['item_data'])
            items.append(item)
        
        return items
    
    def buy_item(self, user_id: str, guild_id: str, item_id: int, quantity: int = 1) -> Tuple[bool, str]:
        """Achète un objet du shop"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Récupère l'objet
        cursor.execute('SELECT * FROM shop_items WHERE id = ? AND guild_id = ?', (item_id, guild_id))
        item_result = cursor.fetchone()
        
        if not item_result:
            conn.close()
            return False, "Objet introuvable"
        
        columns = [desc[0] for desc in cursor.description]
        item = dict(zip(columns, item_result))
        
        if not item['available']:
            conn.close()
            return False, "Objet non disponible"
        
        # Vérifie le stock
        if item['stock'] != -1 and item['stock'] < quantity:
            conn.close()
            return False, f"Stock insuffisant ({item['stock']} disponible)"
        
        # Calcule le prix total
        total_price = item['price'] * quantity
        config = self.db.get_guild_config(guild_id)
        tax = int(total_price * config.get('shop_tax_rate', 0.05))
        final_price = total_price + tax
        
        # Vérifie le solde
        user_data = self.db.get_user_economy(user_id, guild_id)
        if user_data['balance'] < final_price:
            conn.close()
            return False, f"Solde insuffisant (besoin de {final_price:,})"
        
        # Effectue l'achat
        success = self.db.update_balance(user_id, guild_id, -final_price, "shop_purchase", 
                                       f"Achat: {item['name']} x{quantity}")
        
        if not success:
            conn.close()
            return False, "Erreur lors de l'achat"
        
        # Met à jour le stock
        if item['stock'] != -1:
            cursor.execute('UPDATE shop_items SET stock = stock - ? WHERE id = ?', (quantity, item_id))
        
        # Ajoute à l'inventaire
        cursor.execute('''
            INSERT INTO user_inventory (user_id, guild_id, item_id, quantity)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, guild_id, item_id) DO UPDATE SET
            quantity = quantity + ?
        ''', (user_id, guild_id, item_id, quantity, quantity))
        
        conn.commit()
        conn.close()
        
        return True, f"Achat réussi ! ({final_price:,} payé, taxe: {tax:,})"
    
    def get_user_inventory(self, user_id: str, guild_id: str) -> List[Dict]:
        """Récupère l'inventaire d'un utilisateur"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ui.*, si.name, si.description, si.price, si.item_type, si.item_data
            FROM user_inventory ui
            JOIN shop_items si ON ui.item_id = si.id
            WHERE ui.user_id = ? AND ui.guild_id = ?
            ORDER BY ui.acquired_at DESC
        ''', (user_id, guild_id))
        
        results = cursor.fetchall()
        conn.close()
        
        inventory = []
        for result in results:
            columns = [desc[0] for desc in cursor.description]
            item = dict(zip(columns, result))
            item['item_data'] = json.loads(item['item_data'])
            inventory.append(item)
        
        return inventory

class JobManager:
    """Gestionnaire du système d'emplois"""
    
    def __init__(self, db: EconomyDB):
        self.db = db
        self.init_default_jobs()
    
    def init_default_jobs(self):
        """Initialise les emplois par défaut"""
        default_jobs = [
            {"name": "Livreur", "description": "Livraison de paquets", "base_salary": 200, "xp_required": 0},
            {"name": "Vendeur", "description": "Vente en magasin", "base_salary": 300, "xp_required": 500},
            {"name": "Développeur", "description": "Programmation", "base_salary": 500, "xp_required": 1500},
            {"name": "Manager", "description": "Gestion d'équipe", "base_salary": 800, "xp_required": 3000},
            {"name": "CEO", "description": "Direction générale", "base_salary": 1500, "xp_required": 10000}
        ]
        
        # Pour chaque serveur, ajoute les jobs s'ils n'existent pas
        # (sera fait lors de la première utilisation)
    
    def get_jobs(self, guild_id: str) -> List[Dict]:
        """Récupère tous les emplois disponibles"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM jobs WHERE guild_id = ? AND available = 1
            ORDER BY base_salary ASC
        ''', (guild_id,))
        
        results = cursor.fetchall()
        
        # Si aucun job, crée les jobs par défaut
        if not results:
            self.create_default_jobs(guild_id)
            cursor.execute('''
                SELECT * FROM jobs WHERE guild_id = ? AND available = 1
                ORDER BY base_salary ASC
            ''', (guild_id,))
            results = cursor.fetchall()
        
        conn.close()
        
        jobs = []
        for result in results:
            columns = [desc[0] for desc in cursor.description]
            job = dict(zip(columns, result))
            job['requirements'] = json.loads(job['requirements'])
            jobs.append(job)
        
        return jobs
    
    def create_default_jobs(self, guild_id: str):
        """Crée les emplois par défaut pour un serveur"""
        default_jobs = [
            {"name": "Livreur", "description": "Livraison de paquets", "base_salary": 200, "xp_required": 0},
            {"name": "Vendeur", "description": "Vente en magasin", "base_salary": 300, "xp_required": 500},
            {"name": "Développeur", "description": "Programmation", "base_salary": 500, "xp_required": 1500},
            {"name": "Manager", "description": "Gestion d'équipe", "base_salary": 800, "xp_required": 3000},
            {"name": "CEO", "description": "Direction générale", "base_salary": 1500, "xp_required": 10000}
        ]
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        for job in default_jobs:
            cursor.execute('''
                INSERT INTO jobs (guild_id, name, description, base_salary, xp_required)
                VALUES (?, ?, ?, ?, ?)
            ''', (guild_id, job['name'], job['description'], job['base_salary'], job['xp_required']))
        
        conn.commit()
        conn.close()
    
    def apply_job(self, user_id: str, guild_id: str, job_id: int) -> Tuple[bool, str]:
        """Postule pour un emploi"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Récupère le job
        cursor.execute('SELECT * FROM jobs WHERE id = ? AND guild_id = ?', (job_id, guild_id))
        job_result = cursor.fetchone()
        
        if not job_result:
            conn.close()
            return False, "Emploi introuvable"
        
        columns = [desc[0] for desc in cursor.description]
        job = dict(zip(columns, job_result))
        
        # Vérifie les prérequis
        user_data = self.db.get_user_economy(user_id, guild_id)
        
        if user_data['job'] == job['name']:
            conn.close()
            return False, "Vous avez déjà cet emploi"
        
        # Met à jour l'emploi
        cursor.execute('''
            UPDATE user_economy 
            SET job = ?, job_level = 1, job_xp = 0, updated_at = ?
            WHERE user_id = ? AND guild_id = ?
        ''', (job['name'], datetime.now().isoformat(), user_id, guild_id))
        
        conn.commit()
        conn.close()
        
        return True, f"Félicitations ! Vous êtes maintenant {job['name']}"
    
    def work(self, user_id: str, guild_id: str) -> Tuple[bool, str, int]:
        """Effectue une session de travail"""
        user_data = self.db.get_user_economy(user_id, guild_id)
        
        if not user_data['job']:
            return False, "Vous devez d'abord avoir un emploi", 0
        
        # Vérifie le cooldown
        config = self.db.get_guild_config(guild_id)
        cooldown = config.get('work_cooldown', 3600)
        
        if user_data['last_work']:
            last_work = datetime.fromisoformat(user_data['last_work'])
            if datetime.now() - last_work < timedelta(seconds=cooldown):
                remaining = cooldown - (datetime.now() - last_work).seconds
                return False, f"Vous devez attendre encore {remaining//60} minutes", 0
        
        # Calcule la récompense
        jobs = self.get_jobs(guild_id)
        user_job = next((j for j in jobs if j['name'] == user_data['job']), None)
        
        if not user_job:
            base_reward = random.randint(200, 400)
        else:
            base_salary = user_job['base_salary']
            level_bonus = base_salary * (user_data['job_level'] * 0.1)
            base_reward = int(base_salary + level_bonus)
        
        # Bonus aléatoire
        bonus_multiplier = random.uniform(0.8, 1.3)
        final_reward = int(base_reward * bonus_multiplier)
        
        # Ajoute l'argent
        success = self.db.update_balance(user_id, guild_id, final_reward, "work", 
                                       f"Travail: {user_data['job']}")
        
        if success:
            # Met à jour les données de travail
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            new_job_xp = user_data['job_xp'] + random.randint(10, 50)
            new_level = user_data['job_level']
            
            # Vérifie la montée de niveau
            xp_needed = new_level * 1000
            if new_job_xp >= xp_needed:
                new_level += 1
                new_job_xp = 0
            
            cursor.execute('''
                UPDATE user_economy 
                SET last_work = ?, job_xp = ?, job_level = ?, updated_at = ?
                WHERE user_id = ? AND guild_id = ?
            ''', (datetime.now().isoformat(), new_job_xp, new_level,
                  datetime.now().isoformat(), user_id, guild_id))
            
            conn.commit()
            conn.close()
            
            result_msg = f"Travail terminé ! +{final_reward:,} {config['currency_symbol']}"
            if new_level > user_data['job_level']:
                result_msg += f"\n🎉 Promotion ! Niveau {new_level} atteint !"
            
            return True, result_msg, final_reward
        
        return False, "Erreur lors du travail", 0

class GamblingManager:
    """Gestionnaire des jeux d'argent"""
    
    def __init__(self, db: EconomyDB):
        self.db = db
    
    def coinflip(self, user_id: str, guild_id: str, bet_amount: int, choice: str) -> Tuple[bool, str, int]:
        """Jeu de pile ou face"""
        user_data = self.db.get_user_economy(user_id, guild_id)
        
        if user_data['balance'] < bet_amount:
            return False, "Solde insuffisant", 0
        
        if bet_amount <= 0:
            return False, "Mise invalide", 0
        
        # Lance la pièce
        result = random.choice(['pile', 'face'])
        won = (choice.lower() == result)
        
        if won:
            winnings = bet_amount  # Gagne le même montant
            self.db.update_balance(user_id, guild_id, winnings, "gambling_win", 
                                 f"Coinflip gagné: {choice}")
            self.update_gambling_stats(user_id, guild_id, bet_amount, winnings)
            return True, f"🎉 {result.title()} ! Vous gagnez {winnings:,} !", winnings
        else:
            self.db.update_balance(user_id, guild_id, -bet_amount, "gambling_loss", 
                                 f"Coinflip perdu: {choice}")
            self.update_gambling_stats(user_id, guild_id, bet_amount, 0)
            return False, f"💸 {result.title()} ! Vous perdez {bet_amount:,} !", -bet_amount
    
    def dice_roll(self, user_id: str, guild_id: str, bet_amount: int, prediction: int) -> Tuple[bool, str, int]:
        """Jeu de dé (1-6)"""
        user_data = self.db.get_user_economy(user_id, guild_id)
        
        if user_data['balance'] < bet_amount:
            return False, "Solde insuffisant", 0
        
        if not 1 <= prediction <= 6:
            return False, "Prédiction invalide (1-6)", 0
        
        # Lance le dé
        result = random.randint(1, 6)
        
        if result == prediction:
            winnings = bet_amount * 5  # Gain x5 si exact
            self.db.update_balance(user_id, guild_id, winnings, "gambling_win", 
                                 f"Dé exact: {prediction}")
            self.update_gambling_stats(user_id, guild_id, bet_amount, winnings)
            return True, f"🎯 Dé: {result} ! Prédiction exacte ! +{winnings:,} !", winnings
        else:
            self.db.update_balance(user_id, guild_id, -bet_amount, "gambling_loss", 
                                 f"Dé raté: {prediction} vs {result}")
            self.update_gambling_stats(user_id, guild_id, bet_amount, 0)
            return False, f"🎲 Dé: {result} (prédit: {prediction}). -{bet_amount:,} !", -bet_amount
    
    def slots(self, user_id: str, guild_id: str, bet_amount: int) -> Tuple[bool, str, int]:
        """Machine à sous"""
        user_data = self.db.get_user_economy(user_id, guild_id)
        
        if user_data['balance'] < bet_amount:
            return False, "Solde insuffisant", 0
        
        # Symboles et leurs probabilités
        symbols = ['🍒', '🍋', '🍊', '🍇', '⭐', '💎']
        weights = [30, 25, 20, 15, 8, 2]  # Plus rare = plus de gains
        
        # Tire 3 symboles
        slot1 = random.choices(symbols, weights=weights)[0]
        slot2 = random.choices(symbols, weights=weights)[0]
        slot3 = random.choices(symbols, weights=weights)[0]
        
        result_display = f"{slot1} | {slot2} | {slot3}"
        
        # Calcule les gains
        winnings = 0
        
        # Trois identiques
        if slot1 == slot2 == slot3:
            multipliers = {'🍒': 3, '🍋': 4, '🍊': 5, '🍇': 8, '⭐': 15, '💎': 50}
            winnings = bet_amount * multipliers.get(slot1, 3)
        
        # Deux identiques
        elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
            winnings = int(bet_amount * 0.5)
        
        if winnings > 0:
            self.db.update_balance(user_id, guild_id, winnings, "gambling_win", "Slots")
            self.update_gambling_stats(user_id, guild_id, bet_amount, winnings)
            return True, f"🎰 {result_display}\n🎉 Vous gagnez {winnings:,} !", winnings
        else:
            self.db.update_balance(user_id, guild_id, -bet_amount, "gambling_loss", "Slots")
            self.update_gambling_stats(user_id, guild_id, bet_amount, 0)
            return False, f"🎰 {result_display}\n💸 Vous perdez {bet_amount:,} !", -bet_amount
    
    def update_gambling_stats(self, user_id: str, guild_id: str, bet: int, winnings: int):
        """Met à jour les statistiques de jeu"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO gambling_stats (user_id, guild_id, games_played, total_bet, total_won, 
                                      biggest_win, biggest_loss)
            VALUES (?, ?, 1, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            games_played = games_played + 1,
            total_bet = total_bet + ?,
            total_won = total_won + ?,
            biggest_win = MAX(biggest_win, ?),
            biggest_loss = MAX(biggest_loss, ?),
            win_rate = CAST(total_won AS REAL) / CAST(total_bet AS REAL),
            updated_at = ?
        ''', (user_id, guild_id, bet, winnings, winnings, bet if winnings == 0 else 0,
              bet, winnings, winnings, bet if winnings == 0 else 0, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()

# Interfaces utilisateur
class EconomyConfigView(discord.ui.View):
    """Interface de configuration économique"""
    
    def __init__(self, db: EconomyDB, guild_id: str):
        super().__init__(timeout=300)
        self.db = db
        self.guild_id = guild_id
    
    @discord.ui.button(label="💰 Config Générale", style=discord.ButtonStyle.primary)
    async def general_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EconomyGeneralModal(self.db, self.guild_id))
    
    @discord.ui.button(label="🏪 Gérer Shop", style=discord.ButtonStyle.success)
    async def shop_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ShopAddItemModal(self.db, self.guild_id))
    
    @discord.ui.button(label="💼 Gérer Emplois", style=discord.ButtonStyle.secondary)
    async def job_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(JobAddModal(self.db, self.guild_id))

class EconomyGeneralModal(discord.ui.Modal):
    def __init__(self, db: EconomyDB, guild_id: str):
        super().__init__(title="💰 Configuration Économie")
        self.db = db
        self.guild_id = guild_id
        
        config = db.get_guild_config(guild_id)
        
        self.currency_name = discord.ui.TextInput(
            label="Nom de la monnaie",
            placeholder="Arsenal Coins",
            default=config.get('currency_name', 'Arsenal Coins'),
            max_length=50
        )
        
        self.currency_symbol = discord.ui.TextInput(
            label="Symbole de la monnaie",
            placeholder="🪙",
            default=config.get('currency_symbol', '🪙'),
            max_length=5
        )
        
        self.daily_amount = discord.ui.TextInput(
            label="Montant daily",
            placeholder="500",
            default=str(config.get('daily_amount', 500)),
            max_length=6
        )
        
        self.add_item(self.currency_name)
        self.add_item(self.currency_symbol)
        self.add_item(self.daily_amount)
    
    async def on_submit(self, interaction: discord.Interaction):
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE economy_config 
            SET currency_name = ?, currency_symbol = ?, daily_amount = ?, updated_at = ?
            WHERE guild_id = ?
        ''', (
            self.currency_name.value,
            self.currency_symbol.value,
            int(self.daily_amount.value),
            datetime.now().isoformat(),
            self.guild_id
        ))
        
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="✅ Configuration Mise à Jour",
            description="Les paramètres économiques ont été sauvegardés !",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ShopView(discord.ui.View):
    """Interface de navigation du shop"""
    
    def __init__(self, shop_manager: ShopManager, guild_id: str, current_page: int = 0):
        super().__init__(timeout=300)
        self.shop_manager = shop_manager
        self.guild_id = guild_id
        self.current_page = current_page
        self.items_per_page = 5
    
    @discord.ui.button(label="⬅️ Précédent", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            embed = await self.get_shop_embed(interaction.client)
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="➡️ Suivant", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        items = self.shop_manager.get_shop_items(self.guild_id)
        max_pages = (len(items) - 1) // self.items_per_page
        
        if self.current_page < max_pages:
            self.current_page += 1
            embed = await self.get_shop_embed(interaction.client)
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="💳 Acheter", style=discord.ButtonStyle.success)
    async def buy_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BuyItemModal(self.shop_manager, self.guild_id))
    
    async def get_shop_embed(self, bot) -> discord.Embed:
        items = self.shop_manager.get_shop_items(self.guild_id)
        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_items = items[start_idx:end_idx]
        
        embed = discord.Embed(
            title="🏪 Boutique Arsenal",
            description=f"Page {self.current_page + 1}/{((len(items) - 1) // self.items_per_page) + 1}",
            color=0x3498db
        )
        
        for item in page_items:
            stock_text = f"Stock: {item['stock']}" if item['stock'] != -1 else "Stock: ∞"
            embed.add_field(
                name=f"{item['name']} (ID: {item['id']})",
                value=f"{item['description']}\n💰 **{item['price']:,}** | {stock_text}",
                inline=False
            )
        
        if not page_items:
            embed.description = "Aucun objet en vente"
        
        return embed

class BuyItemModal(discord.ui.Modal):
    def __init__(self, shop_manager: ShopManager, guild_id: str):
        super().__init__(title="💳 Acheter un Objet")
        self.shop_manager = shop_manager
        self.guild_id = guild_id
        
        self.item_id = discord.ui.TextInput(
            label="ID de l'objet",
            placeholder="1",
            max_length=10
        )
        
        self.quantity = discord.ui.TextInput(
            label="Quantité",
            placeholder="1",
            default="1",
            max_length=5
        )
        
        self.add_item(self.item_id)
        self.add_item(self.quantity)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            item_id = int(self.item_id.value)
            quantity = int(self.quantity.value)
            
            success, message = self.shop_manager.buy_item(
                str(interaction.user.id), self.guild_id, item_id, quantity
            )
            
            embed = discord.Embed(
                title="🏪 Résultat d'Achat",
                description=message,
                color=0x00ff00 if success else 0xff0000
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Valeurs invalides !", ephemeral=True)

# Commandes principales
class EconomySystem(commands.Cog):
    """💰 Système d'économie et argent complet pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = EconomyDB()
        self.shop_manager = ShopManager(self.db)
        self.job_manager = JobManager(self.db)
        self.gambling_manager = GamblingManager(self.db)
        self.daily_interest.start()
    
    def cog_unload(self):
        self.daily_interest.cancel()
    
    @tasks.loop(hours=24)
    async def daily_interest(self):
        """Applique les intérêts bancaires quotidiens"""
        # À implémenter pour tous les utilisateurs
        pass
    
    @app_commands.command(name="balance", description="💰 Affiche votre solde ou celui d'un utilisateur")
    async def balance(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        target = user or interaction.user
        
        if target.bot:
            await interaction.response.send_message("❌ Les bots n'ont pas de solde !", ephemeral=True)
            return
        
        user_data = self.db.get_user_economy(str(target.id), str(interaction.guild.id))
        config = self.db.get_guild_config(str(interaction.guild.id))
        
        embed = discord.Embed(
            title=f"💰 Portefeuille de {target.display_name}",
            color=0x00ff00
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # Solde principal
        embed.add_field(
            name=f"{config['currency_symbol']} Portefeuille",
            value=f"**{user_data['balance']:,}** {config['currency_name']}",
            inline=True
        )
        
        # Banque
        embed.add_field(
            name="🏦 Banque",
            value=f"**{user_data['bank']:,}** / {user_data['bank_limit']:,}",
            inline=True
        )
        
        # Net worth
        net_worth = user_data['balance'] + user_data['bank']
        embed.add_field(
            name="💎 Valeur Totale",
            value=f"**{net_worth:,}**",
            inline=True
        )
        
        # Statistiques
        embed.add_field(name="📈 Total Gagné", value=f"{user_data['total_earned']:,}", inline=True)
        embed.add_field(name="📉 Total Dépensé", value=f"{user_data['total_spent']:,}", inline=True)
        embed.add_field(name="💼 Emploi", value=user_data['job'] or "Aucun", inline=True)
        
        if user_data['job']:
            embed.add_field(name="🎯 Niveau Job", value=f"**{user_data['job_level']}**", inline=True)
            embed.add_field(name="⭐ XP Job", value=f"{user_data['job_xp']:,}", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="daily", description="🎁 Récupère votre récompense quotidienne")
    async def daily(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)
        
        user_data = self.db.get_user_economy(user_id, guild_id)
        config = self.db.get_guild_config(guild_id)
        
        # Vérifie le cooldown
        if user_data['last_daily']:
            last_daily = datetime.fromisoformat(user_data['last_daily'])
            if datetime.now() - last_daily < timedelta(hours=20):  # 20h pour être sûr
                next_daily = last_daily + timedelta(hours=24)
                await interaction.response.send_message(
                    f"⏰ Prochaine récompense quotidienne: <t:{int(next_daily.timestamp())}:R>",
                    ephemeral=True
                )
                return
        
        # Calcule la récompense
        base_amount = config.get('daily_amount', 500)
        streak = user_data['daily_streak']
        max_streak = config.get('max_daily_streak', 30)
        
        # Bonus de série
        streak_bonus = min(streak, max_streak) * config.get('daily_streak_bonus', 100)
        total_reward = base_amount + streak_bonus
        
        # Ajoute l'argent
        success = self.db.update_balance(user_id, guild_id, total_reward, "daily", 
                                       f"Récompense quotidienne (série: {streak + 1})")
        
        if success:
            # Met à jour les données daily
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            new_streak = streak + 1
            cursor.execute('''
                UPDATE user_economy 
                SET last_daily = ?, daily_streak = ?, updated_at = ?
                WHERE user_id = ? AND guild_id = ?
            ''', (datetime.now().isoformat(), new_streak, datetime.now().isoformat(),
                  user_id, guild_id))
            
            conn.commit()
            conn.close()
            
            embed = discord.Embed(
                title="🎁 Récompense Quotidienne",
                description=f"Vous avez reçu **{total_reward:,}** {config['currency_symbol']} !",
                color=0x00ff00
            )
            embed.add_field(name="💰 Base", value=f"{base_amount:,}", inline=True)
            embed.add_field(name="🔥 Bonus Série", value=f"{streak_bonus:,}", inline=True)
            embed.add_field(name="🎯 Série Actuelle", value=f"**{new_streak}** jour(s)", inline=True)
            
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="work", description="💼 Travaillez pour gagner de l'argent")
    async def work(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)
        
        success, message, reward = self.job_manager.work(user_id, guild_id)
        
        embed = discord.Embed(
            title="💼 Travail",
            description=message,
            color=0x00ff00 if success else 0xff0000
        )
        
        if success:
            config = self.db.get_guild_config(guild_id)
            embed.add_field(name="Gain", value=f"+{reward:,} {config['currency_symbol']}", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="jobs", description="💼 Affiche les emplois disponibles")
    async def jobs(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        jobs = self.job_manager.get_jobs(guild_id)
        
        embed = discord.Embed(
            title="💼 Emplois Disponibles",
            color=0x3498db
        )
        
        for job in jobs:
            requirements = f"XP requis: {job['xp_required']:,}" if job['xp_required'] > 0 else "Aucun prérequis"
            embed.add_field(
                name=f"{job['name']} (ID: {job['id']})",
                value=f"{job['description']}\n💰 Salaire: {job['base_salary']:,}\n📋 {requirements}",
                inline=False
            )
        
        embed.set_footer(text="Utilisez /apply <id> pour postuler")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="apply", description="📋 Postuler pour un emploi")
    async def apply(self, interaction: discord.Interaction, job_id: int):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)
        
        success, message = self.job_manager.apply_job(user_id, guild_id, job_id)
        
        embed = discord.Embed(
            title="📋 Candidature",
            description=message,
            color=0x00ff00 if success else 0xff0000
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="shop", description="🏪 Affiche la boutique")
    async def shop(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        view = ShopView(self.shop_manager, guild_id)
        embed = await view.get_shop_embed(self.bot)
        
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="inventory", description="🎒 Affiche votre inventaire")
    async def inventory(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        target = user or interaction.user
        
        if target.bot:
            await interaction.response.send_message("❌ Les bots n'ont pas d'inventaire !", ephemeral=True)
            return
        
        inventory = self.shop_manager.get_user_inventory(str(target.id), str(interaction.guild.id))
        
        embed = discord.Embed(
            title=f"🎒 Inventaire de {target.display_name}",
            color=0x3498db
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        
        if not inventory:
            embed.description = "Inventaire vide"
        else:
            for item in inventory[:25]:  # Limite Discord
                embed.add_field(
                    name=f"{item['name']} x{item['quantity']}",
                    value=f"{item['description'][:50]}...",
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="pay", description="💸 Transférer de l'argent à un utilisateur")
    async def pay(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if user.bot:
            await interaction.response.send_message("❌ Impossible de payer un bot !", ephemeral=True)
            return
        
        if user == interaction.user:
            await interaction.response.send_message("❌ Vous ne pouvez pas vous payer vous-même !", ephemeral=True)
            return
        
        if amount <= 0:
            await interaction.response.send_message("❌ Le montant doit être positif !", ephemeral=True)
            return
        
        sender_id = str(interaction.user.id)
        receiver_id = str(user.id)
        guild_id = str(interaction.guild.id)
        
        # Vérifie le solde
        sender_data = self.db.get_user_economy(sender_id, guild_id)
        if sender_data['balance'] < amount:
            await interaction.response.send_message("❌ Solde insuffisant !", ephemeral=True)
            return
        
        # Effectue le transfert
        sender_success = self.db.update_balance(sender_id, guild_id, -amount, "transfer_sent", 
                                              f"Transfert vers {user.display_name}")
        receiver_success = self.db.update_balance(receiver_id, guild_id, amount, "transfer_received", 
                                                f"Transfert de {interaction.user.display_name}")
        
        if sender_success and receiver_success:
            config = self.db.get_guild_config(guild_id)
            embed = discord.Embed(
                title="💸 Transfert Réussi",
                description=f"**{amount:,}** {config['currency_symbol']} transféré à {user.mention}",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Erreur lors du transfert !", ephemeral=True)
    
    @app_commands.command(name="coinflip", description="🪙 Pile ou face")
    async def coinflip(self, interaction: discord.Interaction, bet: int, choice: str):
        if choice.lower() not in ['pile', 'face']:
            await interaction.response.send_message("❌ Choix invalide ! Utilisez 'pile' ou 'face'", ephemeral=True)
            return
        
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)
        
        success, message, result = self.gambling_manager.coinflip(user_id, guild_id, bet, choice)
        
        embed = discord.Embed(
            title="🪙 Pile ou Face",
            description=message,
            color=0x00ff00 if success else 0xff0000
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="dice", description="🎲 Pariez sur un dé (1-6)")
    async def dice(self, interaction: discord.Interaction, bet: int, prediction: int):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)
        
        success, message, result = self.gambling_manager.dice_roll(user_id, guild_id, bet, prediction)
        
        embed = discord.Embed(
            title="🎲 Dé",
            description=message,
            color=0x00ff00 if success else 0xff0000
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="slots", description="🎰 Machine à sous")
    async def slots(self, interaction: discord.Interaction, bet: int):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)
        
        success, message, result = self.gambling_manager.slots(user_id, guild_id, bet)
        
        embed = discord.Embed(
            title="🎰 Machine à Sous",
            description=message,
            color=0x00ff00 if success else 0xff0000
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leaderboard_money", description="🏆 Classement économique")
    @app_commands.describe(category="Catégorie de classement")
    @app_commands.choices(category=[
        app_commands.Choice(name="Balance", value="balance"),
        app_commands.Choice(name="Banque", value="bank"),
        app_commands.Choice(name="Total gagné", value="total_earned"),
        app_commands.Choice(name="Total dépensé", value="total_spent")
    ])
    async def leaderboard_money(self, interaction: discord.Interaction, category: str = "balance"):
        guild_id = str(interaction.guild.id)
        leaderboard = self.db.get_leaderboard(guild_id, category)
        config = self.db.get_guild_config(guild_id)
        
        embed = discord.Embed(
            title=f"🏆 Classement - {category.title()}",
            color=0xffd700
        )
        
        description = ""
        for user_data in leaderboard:
            user = self.bot.get_user(int(user_data['user_id']))
            username = user.display_name if user else f"Utilisateur {user_data['user_id']}"
            
            rank = user_data['rank']
            value = user_data[category]
            
            if rank == 1:
                medal = "🥇"
            elif rank == 2:
                medal = "🥈"
            elif rank == 3:
                medal = "🥉"
            else:
                medal = f"**#{rank}**"
            
            description += f"{medal} {username} - **{value:,}** {config['currency_symbol']}\n"
        
        embed.description = description or "Aucune donnée"
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="economy_config", description="⚙️ Configuration du système économique (Admin)")
    async def economy_config(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Vous devez être administrateur !", ephemeral=True)
            return
        
        guild_id = str(interaction.guild.id)
        view = EconomyConfigView(self.db, guild_id)
        
        embed = discord.Embed(
            title="⚙️ Configuration Économique",
            description="Choisissez l'élément à configurer :",
            color=0x3498db
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(EconomySystem(bot))

