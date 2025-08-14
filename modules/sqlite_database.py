"""
🗄️ Arsenal SQLite Database Manager
Système de gestion des bases de données SQLite centralisé
Développé par XeRoX - Arsenal Bot V4.5.0
"""

import sqlite3
import os
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import core.logger as logger

log = logger.log

class ArsenalDatabaseManager:
    """Gestionnaire centralisé des bases de données SQLite d'Arsenal"""
    
    def __init__(self):
        self.databases = {}
        self.db_path = "data/"
        os.makedirs(self.db_path, exist_ok=True)
        
        # Bases de données principales
        self.main_db = "arsenal_v4.db"
        self.profiles_db = "hunt_royal_profiles.db"
        self.auth_db = "hunt_royal_auth.db"
        self.coins_db = "arsenal_coins_central.db"
        self.suggestions_db = "suggestions.db"
        
        self._init_databases()
    
    def _init_databases(self):
        """Initialise toutes les bases de données"""
        try:
            # Arsenal principal
            self._init_main_database()
            
            # Profils utilisateurs
            self._init_profiles_database()
            
            # Authentification
            self._init_auth_database()
            
            # Système monétaire
            self._init_coins_database()
            
            # Suggestions
            self._init_suggestions_database()
            
            log.info("🗄️ [DATABASE] Toutes les bases de données initialisées")
            
        except Exception as e:
            log.error(f"❌ [DATABASE] Erreur initialisation: {e}")
    
    def _init_main_database(self):
        """Initialise la base de données principale"""
        with sqlite3.connect(self.main_db) as conn:
            cursor = conn.cursor()
            
            # Table de configuration serveur
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS server_config (
                    guild_id INTEGER PRIMARY KEY,
                    config_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table d'activité utilisateurs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    guild_id INTEGER,
                    activity_type TEXT,
                    activity_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table de statistiques
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stat_type TEXT,
                    stat_value TEXT,
                    guild_id INTEGER,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def _init_profiles_database(self):
        """Initialise la base des profils utilisateurs"""
        with sqlite3.connect(self.profiles_db) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    level INTEGER DEFAULT 1,
                    experience INTEGER DEFAULT 0,
                    coins INTEGER DEFAULT 0,
                    profile_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def _init_auth_database(self):
        """Initialise la base d'authentification"""
        with sqlite3.connect(self.auth_db) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    guild_id INTEGER,
                    auth_level INTEGER DEFAULT 0,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def _init_coins_database(self):
        """Initialise la base du système monétaire"""
        with sqlite3.connect(self.coins_db) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS arsenal_coins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    guild_id INTEGER,
                    balance INTEGER DEFAULT 0,
                    total_earned INTEGER DEFAULT 0,
                    total_spent INTEGER DEFAULT 0,
                    last_daily TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS coin_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    guild_id INTEGER,
                    transaction_type TEXT,
                    amount INTEGER,
                    description TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def _init_suggestions_database(self):
        """Initialise la base des suggestions"""
        with sqlite3.connect(self.suggestions_db) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    guild_id INTEGER,
                    suggestion TEXT,
                    status TEXT DEFAULT 'pending',
                    votes_up INTEGER DEFAULT 0,
                    votes_down INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def get_connection(self, db_name: str):
        """Obtient une connexion à une base de données"""
        try:
            if not db_name.endswith('.db'):
                db_name += '.db'
            
            return sqlite3.connect(db_name)
        except Exception as e:
            log.error(f"❌ [DATABASE] Erreur connexion {db_name}: {e}")
            return None
    
    def execute_query(self, db_name: str, query: str, params: tuple = None) -> Optional[List]:
        """Exécute une requête SQL"""
        try:
            with self.get_connection(db_name) as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().lower().startswith('select'):
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount
        except Exception as e:
            log.error(f"❌ [DATABASE] Erreur requête: {e}")
            return None
    
    def backup_database(self, db_name: str) -> bool:
        """Sauvegarde une base de données"""
        try:
            backup_dir = "backups/"
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{backup_dir}{db_name}_{timestamp}.backup"
            
            with sqlite3.connect(db_name) as source:
                with sqlite3.connect(backup_file) as backup:
                    source.backup(backup)
            
            log.info(f"💾 [DATABASE] Sauvegarde créée: {backup_file}")
            return True
            
        except Exception as e:
            log.error(f"❌ [DATABASE] Erreur sauvegarde: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Informations sur les bases de données"""
        info = {
            "databases": [],
            "total_size": 0,
            "status": "operational"
        }
        
        try:
            for db_file in [self.main_db, self.profiles_db, self.auth_db, self.coins_db, self.suggestions_db]:
                if os.path.exists(db_file):
                    size = os.path.getsize(db_file)
                    info["databases"].append({
                        "name": db_file,
                        "size": size,
                        "size_mb": round(size / 1024 / 1024, 2)
                    })
                    info["total_size"] += size
            
            info["total_size_mb"] = round(info["total_size"] / 1024 / 1024, 2)
            
        except Exception as e:
            log.error(f"❌ [DATABASE] Erreur info: {e}")
            info["status"] = "error"
        
        return info

# Instance globale
database_manager = ArsenalDatabaseManager()

def setup(bot):
    """Setup function pour le chargement du module"""
    log.info("🗄️ [DATABASE] Module SQLite Database Manager chargé")
    return database_manager
