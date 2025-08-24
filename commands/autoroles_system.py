"""
🎭 ARSENAL AUTOROLES SYSTEM V2.0
Système modulaire de rôles automatiques

Fonctionnalités:
- Attribution automatique à l'arrivée
- Rôles basés sur l'activité/niveaux
- Rôles temporaires et conditions
- Gestion par règles et triggers
- Interface de configuration avancée

Author: Arsenal Bot Team
Version: 2.0.0
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
import sqlite3
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# BASE DE DONNÉES AUTORÔLES
# =============================================================================

class AutoRolesDB:
    """Gestionnaire de base de données pour les rôles automatiques"""
    
    def __init__(self, db_path: str = "arsenal_autoroles.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des règles d'auto-rôles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS autorole_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    rule_name TEXT NOT NULL,
                    rule_type TEXT NOT NULL, -- 'join', 'level', 'activity', 'time', 'custom'
                    target_role_id INTEGER NOT NULL,
                    conditions TEXT NOT NULL, -- JSON des conditions
                    priority INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_removable BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des attributions d'auto-rôles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS autorole_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    rule_id INTEGER NOT NULL,
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NULL,
                    assignment_reason TEXT,
                    FOREIGN KEY (rule_id) REFERENCES autorole_rules (id)
                )
            ''')
            
            # Table de configuration des auto-rôles par serveur
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS autorole_config (
                    guild_id INTEGER PRIMARY KEY,
                    welcome_roles TEXT, -- JSON array des rôles de bienvenue
                    bot_roles TEXT, -- JSON array des rôles pour les bots
                    default_permissions TEXT, -- JSON des permissions par défaut
                    join_delay INTEGER DEFAULT 0, -- Délai avant attribution (secondes)
                    enable_logging BOOLEAN DEFAULT TRUE,
                    log_channel_id INTEGER NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des statistiques d'auto-rôles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS autorole_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    rule_id INTEGER NOT NULL,
                    assignments_total INTEGER DEFAULT 0,
                    assignments_today INTEGER DEFAULT 0,
                    last_assignment TIMESTAMP NULL,
                    success_rate REAL DEFAULT 100.0,
                    FOREIGN KEY (rule_id) REFERENCES autorole_rules (id)
                )
            ''')
            
            conn.commit()
    
    def get_guild_config(self, guild_id: int) -> Optional[Dict[str, Any]]:
        """Récupère la configuration d'auto-rôles d'un serveur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM autorole_config WHERE guild_id = ?
            ''', (guild_id,))
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                config = dict(zip(columns, row))
                
                # Parser les JSON
                config['welcome_roles'] = json.loads(config['welcome_roles']) if config['welcome_roles'] else []
                config['bot_roles'] = json.loads(config['bot_roles']) if config['bot_roles'] else []
                config['default_permissions'] = json.loads(config['default_permissions']) if config['default_permissions'] else {}
                
                return config
            return None
    
    def save_guild_config(self, guild_id: int, config: Dict[str, Any]) -> bool:
        """Sauvegarde la configuration d'auto-rôles"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO autorole_config 
                    (guild_id, welcome_roles, bot_roles, default_permissions, join_delay, enable_logging, log_channel_id, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    guild_id,
                    json.dumps(config.get('welcome_roles', [])),
                    json.dumps(config.get('bot_roles', [])),
                    json.dumps(config.get('default_permissions', {})),
                    config.get('join_delay', 0),
                    config.get('enable_logging', True),
                    config.get('log_channel_id')
                ))
                
                conn.commit()
                return True
                
            except Exception as e:
                logger.error(f"Erreur sauvegarde config auto-rôles {guild_id}: {e}")
                return False
    
    def create_autorole_rule(self, guild_id: int, rule_data: Dict[str, Any]) -> Optional[int]:
        """Crée une nouvelle règle d'auto-rôle"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO autorole_rules 
                    (guild_id, rule_name, rule_type, target_role_id, conditions, priority, is_active, is_removable)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    guild_id,
                    rule_data['rule_name'],
                    rule_data['rule_type'],
                    rule_data['target_role_id'],
                    json.dumps(rule_data['conditions']),
                    rule_data.get('priority', 0),
                    rule_data.get('is_active', True),
                    rule_data.get('is_removable', False)
                ))
                
                rule_id = cursor.lastrowid
                
                # Créer les stats pour cette règle
                cursor.execute('''
                    INSERT INTO autorole_stats (guild_id, rule_id)
                    VALUES (?, ?)
                ''', (guild_id, rule_id))
                
                conn.commit()
                return rule_id
                
            except Exception as e:
                logger.error(f"Erreur création règle auto-rôle: {e}")
                return None
    
    def get_autorole_rules(self, guild_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
        """Récupère toutes les règles d'auto-rôles d'un serveur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT r.*, s.assignments_total, s.assignments_today, s.success_rate
                FROM autorole_rules r
                LEFT JOIN autorole_stats s ON r.id = s.rule_id
                WHERE r.guild_id = ?
            '''
            
            params = [guild_id]
            if active_only:
                query += ' AND r.is_active = TRUE'
            
            query += ' ORDER BY r.priority DESC, r.created_at ASC'
            
            cursor.execute(query, params)
            
            rules = []
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                rule = dict(zip(columns, row))
                rule['conditions'] = json.loads(rule['conditions'])
                rules.append(rule)
            
            return rules
    
    def assign_role(self, guild_id: int, user_id: int, role_id: int, rule_id: int, reason: str = None, expires_at: datetime = None) -> bool:
        """Enregistre une attribution d'auto-rôle"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO autorole_assignments 
                    (guild_id, user_id, role_id, rule_id, assignment_reason, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (guild_id, user_id, role_id, rule_id, reason, expires_at))
                
                # Mettre à jour les stats
                cursor.execute('''
                    UPDATE autorole_stats 
                    SET assignments_total = assignments_total + 1,
                        assignments_today = assignments_today + 1,
                        last_assignment = CURRENT_TIMESTAMP
                    WHERE guild_id = ? AND rule_id = ?
                ''', (guild_id, rule_id))
                
                conn.commit()
                return True
                
            except Exception as e:
                logger.error(f"Erreur enregistrement attribution rôle: {e}")
                return False
    
    def get_user_autoroles(self, guild_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Récupère tous les auto-rôles d'un utilisateur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.*, r.rule_name, r.rule_type
                FROM autorole_assignments a
                JOIN autorole_rules r ON a.rule_id = r.id
                WHERE a.guild_id = ? AND a.user_id = ?
                ORDER BY a.assigned_at DESC
            ''', (guild_id, user_id))
            
            assignments = []
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                assignments.append(dict(zip(columns, row)))
            
            return assignments
    
    def get_expired_roles(self) -> List[Dict[str, Any]]:
        """Récupère tous les rôles expirés à retirer"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM autorole_assignments 
                WHERE expires_at IS NOT NULL AND expires_at <= CURRENT_TIMESTAMP
            ''')
            
            expired = []
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                expired.append(dict(zip(columns, row)))
            
            return expired
    
    def remove_assignment(self, assignment_id: int) -> bool:
        """Supprime une attribution d'auto-rôle"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('DELETE FROM autorole_assignments WHERE id = ?', (assignment_id,))
                conn.commit()
                return cursor.rowcount > 0
                
            except Exception as e:
                logger.error(f"Erreur suppression attribution: {e}")
                return False


# =============================================================================
# LOGIQUE D'ATTRIBUTION DES RÔLES
# =============================================================================

class AutoRoleManager:
    """Gestionnaire principal des attributions d'auto-rôles"""
    
    def __init__(self, bot, db: AutoRolesDB):
        self.bot = bot
        self.db = db
    
    async def process_member_join(self, member: discord.Member):
        """Traite l'arrivée d'un nouveau membre"""
        config = self.db.get_guild_config(member.guild.id)
        
        if not config:
            return
        
        # Délai avant attribution si configuré
        if config['join_delay'] > 0:
            await asyncio.sleep(config['join_delay'])
        
        # Rôles pour les bots
        if member.bot and config['bot_roles']:
            await self._assign_bot_roles(member, config['bot_roles'])
        
        # Rôles de bienvenue pour les humains
        if not member.bot and config['welcome_roles']:
            await self._assign_welcome_roles(member, config['welcome_roles'])
        
        # Traiter les règles d'auto-rôles
        rules = self.db.get_autorole_rules(member.guild.id)
        
        for rule in rules:
            if rule['rule_type'] == 'join':
                if await self._check_rule_conditions(member, rule):
                    await self._assign_rule_role(member, rule)
    
    async def _assign_welcome_roles(self, member: discord.Member, role_ids: List[int]):
        """Attribue les rôles de bienvenue"""
        for role_id in role_ids:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role, reason="Auto-rôle de bienvenue")
                    logger.info(f"Rôle de bienvenue {role.name} attribué à {member}")
                except discord.Forbidden:
                    logger.warning(f"Permission manquante pour attribuer le rôle {role.name}")
                except Exception as e:
                    logger.error(f"Erreur attribution rôle bienvenue: {e}")
    
    async def _assign_bot_roles(self, member: discord.Member, role_ids: List[int]):
        """Attribue les rôles aux bots"""
        for role_id in role_ids:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role, reason="Auto-rôle pour bot")
                    logger.info(f"Rôle bot {role.name} attribué à {member}")
                except Exception as e:
                    logger.error(f"Erreur attribution rôle bot: {e}")
    
    async def _check_rule_conditions(self, member: discord.Member, rule: Dict[str, Any]) -> bool:
        """Vérifie si les conditions d'une règle sont remplies"""
        conditions = rule['conditions']
        
        # Conditions de base
        if conditions.get('is_bot') is not None:
            if conditions['is_bot'] != member.bot:
                return False
        
        if conditions.get('account_age_days'):
            account_age = (datetime.now(timezone.utc) - member.created_at).days
            if account_age < conditions['account_age_days']:
                return False
        
        if conditions.get('required_roles'):
            member_role_ids = [role.id for role in member.roles]
            required_roles = conditions['required_roles']
            if not any(role_id in member_role_ids for role_id in required_roles):
                return False
        
        if conditions.get('excluded_roles'):
            member_role_ids = [role.id for role in member.roles]
            excluded_roles = conditions['excluded_roles']
            if any(role_id in member_role_ids for role_id in excluded_roles):
                return False
        
        # Conditions spécifiques par type de règle
        if rule['rule_type'] == 'level':
            # Intégration avec système de niveaux (à implémenter)
            user_level = await self._get_user_level(member)
            if user_level < conditions.get('min_level', 0):
                return False
        
        elif rule['rule_type'] == 'activity':
            # Vérifier l'activité récente
            if not await self._check_user_activity(member, conditions):
                return False
        
        elif rule['rule_type'] == 'time':
            # Vérifier la présence depuis X temps
            if not await self._check_member_time(member, conditions):
                return False
        
        return True
    
    async def _assign_rule_role(self, member: discord.Member, rule: Dict[str, Any]):
        """Attribue un rôle basé sur une règle"""
        role = member.guild.get_role(rule['target_role_id'])
        
        if not role:
            logger.warning(f"Rôle {rule['target_role_id']} introuvable pour la règle {rule['rule_name']}")
            return
        
        try:
            await member.add_roles(role, reason=f"Auto-rôle: {rule['rule_name']}")
            
            # Enregistrer l'attribution
            expires_at = None
            if rule['conditions'].get('duration_hours'):
                expires_at = datetime.now(timezone.utc) + timedelta(hours=rule['conditions']['duration_hours'])
            
            self.db.assign_role(
                guild_id=member.guild.id,
                user_id=member.id,
                role_id=role.id,
                rule_id=rule['id'],
                reason=rule['rule_name'],
                expires_at=expires_at
            )
            
            logger.info(f"Auto-rôle {role.name} attribué à {member} via la règle {rule['rule_name']}")
            
        except discord.Forbidden:
            logger.warning(f"Permission manquante pour attribuer le rôle {role.name}")
        except Exception as e:
            logger.error(f"Erreur attribution auto-rôle: {e}")
    
    async def _get_user_level(self, member: discord.Member) -> int:
        """Récupère le niveau d'un utilisateur (à intégrer avec le système de niveaux)"""
        # TODO: Intégration avec le système de niveaux Arsenal
        return 1
    
    async def _check_user_activity(self, member: discord.Member, conditions: Dict[str, Any]) -> bool:
        """Vérifie l'activité d'un utilisateur"""
        # TODO: Implémenter la vérification d'activité
        return True
    
    async def _check_member_time(self, member: discord.Member, conditions: Dict[str, Any]) -> bool:
        """Vérifie depuis combien de temps le membre est sur le serveur"""
        if not member.joined_at:
            return False
        
        member_time = (datetime.now(timezone.utc) - member.joined_at).total_seconds()
        required_time = conditions.get('min_member_hours', 0) * 3600
        
        return member_time >= required_time


# =============================================================================
# VUES DISCORD UI POUR LA CONFIGURATION
# =============================================================================

class AutoRolesSetupView(discord.ui.View):
    """Vue principale de configuration des auto-rôles"""
    
    def __init__(self, guild_id: int, db: AutoRolesDB):
        super().__init__(timeout=600)
        self.guild_id = guild_id
        self.db = db
    
    @discord.ui.button(label="🎯 Rôles de Bienvenue", style=discord.ButtonStyle.primary, emoji="🎯")
    async def welcome_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = WelcomeRolesModal(self.guild_id, self.db)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🤖 Rôles pour Bots", style=discord.ButtonStyle.secondary, emoji="🤖")
    async def bot_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = BotRolesModal(self.guild_id, self.db)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="⚙️ Règles Avancées", style=discord.ButtonStyle.success, emoji="⚙️")
    async def advanced_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = AdvancedRulesView(self.guild_id, self.db)
        embed = discord.Embed(
            title="⚙️ Règles d'Auto-Rôles Avancées",
            description="Créez des règles personnalisées pour l'attribution automatique de rôles",
            color=0x00FF88
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="📊 Statistiques", style=discord.ButtonStyle.secondary, emoji="📊")
    async def show_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._show_autoroles_stats(interaction)
    
    async def _show_autoroles_stats(self, interaction: discord.Interaction):
        """Affiche les statistiques des auto-rôles"""
        rules = self.db.get_autorole_rules(self.guild_id, active_only=False)
        config = self.db.get_guild_config(self.guild_id)
        
        embed = discord.Embed(
            title="📊 Statistiques Auto-Rôles",
            color=0xFFD700
        )
        
        if config:
            embed.add_field(
                name="⚙️ Configuration Actuelle",
                value=f"**Rôles de bienvenue:** {len(config['welcome_roles'])}\n"
                      f"**Rôles bots:** {len(config['bot_roles'])}\n"
                      f"**Délai d'attribution:** {config['join_delay']}s\n"
                      f"**Logging activé:** {'Oui' if config['enable_logging'] else 'Non'}",
                inline=True
            )
        
        embed.add_field(
            name="📋 Règles Actives",
            value=f"**Total:** {len([r for r in rules if r['is_active']])}\n"
                  f"**Inactives:** {len([r for r in rules if not r['is_active']])}\n"
                  f"**Types:** Join, Level, Activity, Time",
            inline=True
        )
        
        if rules:
            total_assignments = sum(r.get('assignments_total', 0) for r in rules)
            today_assignments = sum(r.get('assignments_today', 0) for r in rules)
            
            embed.add_field(
                name="🎯 Attributions",
                value=f"**Total:** {total_assignments}\n"
                      f"**Aujourd'hui:** {today_assignments}\n"
                      f"**Taux de succès moyen:** {sum(r.get('success_rate', 100) for r in rules) / len(rules):.1f}%",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class AdvancedRulesView(discord.ui.View):
    """Vue pour gérer les règles avancées d'auto-rôles"""
    
    def __init__(self, guild_id: int, db: AutoRolesDB):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.db = db
    
    @discord.ui.button(label="➕ Créer Règle", style=discord.ButtonStyle.success, emoji="➕")
    async def create_rule(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CreateRuleModal(self.guild_id, self.db)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 Voir Règles", style=discord.ButtonStyle.primary, emoji="📋")
    async def list_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        rules = self.db.get_autorole_rules(self.guild_id, active_only=False)
        
        embed = discord.Embed(
            title="📋 Règles d'Auto-Rôles",
            color=0x3366FF
        )
        
        if not rules:
            embed.description = "Aucune règle configurée."
        else:
            for rule in rules[:10]:  # Limiter à 10 pour l'affichage
                status = "🟢" if rule['is_active'] else "🔴"
                role = interaction.guild.get_role(rule['target_role_id'])
                role_name = role.name if role else f"Rôle supprimé ({rule['target_role_id']})"
                
                embed.add_field(
                    name=f"{status} {rule['rule_name']}",
                    value=f"**Type:** {rule['rule_type']}\n"
                          f"**Rôle:** {role_name}\n"
                          f"**Attributions:** {rule.get('assignments_total', 0)}",
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


# =============================================================================
# MODALS POUR LA CONFIGURATION
# =============================================================================

class WelcomeRolesModal(discord.ui.Modal):
    """Modal pour configurer les rôles de bienvenue"""
    
    def __init__(self, guild_id: int, db: AutoRolesDB):
        super().__init__(title="🎯 Configuration Rôles de Bienvenue", timeout=300)
        self.guild_id = guild_id
        self.db = db
        
        # Récupérer la config actuelle
        config = db.get_guild_config(guild_id)
        current_roles = config['welcome_roles'] if config else []
        
        self.roles_input = discord.ui.TextInput(
            label="IDs des rôles de bienvenue",
            placeholder="123456789 987654321 (séparés par des espaces)",
            default=" ".join(str(role_id) for role_id in current_roles),
            max_length=200,
            required=False
        )
        
        self.delay_input = discord.ui.TextInput(
            label="Délai avant attribution (secondes)",
            placeholder="0 (immédiat)",
            default=str(config['join_delay']) if config else "0",
            max_length=10,
            required=False
        )
        
        self.add_item(self.roles_input)
        self.add_item(self.delay_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Parser les IDs de rôles
            role_ids = []
            if self.roles_input.value.strip():
                role_ids = [int(role_id) for role_id in self.roles_input.value.split()]
            
            # Parser le délai
            delay = int(self.delay_input.value) if self.delay_input.value else 0
            
            # Récupérer la config actuelle ou créer une nouvelle
            config = self.db.get_guild_config(self.guild_id) or {}
            
            # Mettre à jour
            config['welcome_roles'] = role_ids
            config['join_delay'] = delay
            
            # Sauvegarder
            success = self.db.save_guild_config(self.guild_id, config)
            
            if success:
                embed = discord.Embed(
                    title="✅ Rôles de Bienvenue Configurés",
                    description=f"Configuration mise à jour avec succès !",
                    color=0x00FF88
                )
                
                if role_ids:
                    role_mentions = []
                    for role_id in role_ids:
                        role = interaction.guild.get_role(role_id)
                        role_mentions.append(role.mention if role else f"Rôle {role_id} (introuvable)")
                    
                    embed.add_field(
                        name="🎯 Rôles configurés",
                        value="\n".join(role_mentions),
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="🎯 Rôles de bienvenue",
                        value="Aucun rôle configuré",
                        inline=False
                    )
                
                embed.add_field(
                    name="⏱️ Délai d'attribution",
                    value=f"{delay} secondes" if delay > 0 else "Immédiat",
                    inline=True
                )
                
            else:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Une erreur s'est produite lors de la sauvegarde.",
                    color=0xFF0000
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Erreur de Format",
                description="Vérifiez que les IDs de rôles sont des nombres valides.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


class BotRolesModal(discord.ui.Modal):
    """Modal pour configurer les rôles pour les bots"""
    
    def __init__(self, guild_id: int, db: AutoRolesDB):
        super().__init__(title="🤖 Configuration Rôles pour Bots", timeout=300)
        self.guild_id = guild_id
        self.db = db
        
        config = db.get_guild_config(guild_id)
        current_roles = config['bot_roles'] if config else []
        
        self.roles_input = discord.ui.TextInput(
            label="IDs des rôles pour les bots",
            placeholder="123456789 987654321 (séparés par des espaces)",
            default=" ".join(str(role_id) for role_id in current_roles),
            max_length=200,
            required=False
        )
        
        self.add_item(self.roles_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            role_ids = []
            if self.roles_input.value.strip():
                role_ids = [int(role_id) for role_id in self.roles_input.value.split()]
            
            config = self.db.get_guild_config(self.guild_id) or {}
            config['bot_roles'] = role_ids
            
            success = self.db.save_guild_config(self.guild_id, config)
            
            if success:
                embed = discord.Embed(
                    title="✅ Rôles pour Bots Configurés",
                    color=0x00FF88
                )
                
                if role_ids:
                    role_mentions = []
                    for role_id in role_ids:
                        role = interaction.guild.get_role(role_id)
                        role_mentions.append(role.mention if role else f"Rôle {role_id} (introuvable)")
                    
                    embed.add_field(
                        name="🤖 Rôles configurés",
                        value="\n".join(role_mentions),
                        inline=False
                    )
                else:
                    embed.description = "Aucun rôle configuré pour les bots"
                
            else:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Erreur lors de la sauvegarde.",
                    color=0xFF0000
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Erreur de Format",
                description="Vérifiez les IDs de rôles.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


class CreateRuleModal(discord.ui.Modal):
    """Modal pour créer une règle d'auto-rôle avancée"""
    
    def __init__(self, guild_id: int, db: AutoRolesDB):
        super().__init__(title="➕ Créer une Règle d'Auto-Rôle", timeout=300)
        self.guild_id = guild_id
        self.db = db
        
        self.name_input = discord.ui.TextInput(
            label="Nom de la règle",
            placeholder="ex: Rôle niveau 10",
            max_length=50,
            required=True
        )
        
        self.type_input = discord.ui.TextInput(
            label="Type de règle",
            placeholder="join, level, activity, time",
            max_length=20,
            required=True
        )
        
        self.role_input = discord.ui.TextInput(
            label="ID du rôle à attribuer",
            placeholder="123456789",
            max_length=20,
            required=True
        )
        
        self.conditions_input = discord.ui.TextInput(
            label="Conditions (JSON)",
            placeholder='{"min_level": 10, "account_age_days": 7}',
            style=discord.TextStyle.long,
            max_length=500,
            required=True
        )
        
        self.add_item(self.name_input)
        self.add_item(self.type_input)
        self.add_item(self.role_input)
        self.add_item(self.conditions_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Validation des données
            rule_type = self.type_input.value.lower()
            if rule_type not in ['join', 'level', 'activity', 'time', 'custom']:
                raise ValueError("Type de règle invalide")
            
            role_id = int(self.role_input.value)
            role = interaction.guild.get_role(role_id)
            if not role:
                raise ValueError("Rôle introuvable")
            
            conditions = json.loads(self.conditions_input.value)
            
            # Créer la règle
            rule_data = {
                'rule_name': self.name_input.value,
                'rule_type': rule_type,
                'target_role_id': role_id,
                'conditions': conditions,
                'priority': 0,
                'is_active': True,
                'is_removable': True
            }
            
            rule_id = self.db.create_autorole_rule(self.guild_id, rule_data)
            
            if rule_id:
                embed = discord.Embed(
                    title="✅ Règle Créée",
                    description=f"La règle **{self.name_input.value}** a été créée avec succès !",
                    color=0x00FF88
                )
                
                embed.add_field(
                    name="📋 Détails",
                    value=f"**Type:** {rule_type}\n"
                          f"**Rôle:** {role.mention}\n"
                          f"**ID règle:** {rule_id}",
                    inline=False
                )
            else:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Erreur lors de la création de la règle.",
                    color=0xFF0000
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except json.JSONDecodeError:
            embed = discord.Embed(
                title="❌ Erreur JSON",
                description="Le format des conditions n'est pas valide.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except (ValueError, TypeError) as e:
            embed = discord.Embed(
                title="❌ Erreur de Validation",
                description=f"Erreur: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


# =============================================================================
# COMMANDES PRINCIPALES DU SYSTÈME AUTO-RÔLES
# =============================================================================

class AutoRolesSystem(commands.Cog):
    """🎭 Système modulaire d'auto-rôles Arsenal"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = AutoRolesDB()
        self.manager = AutoRoleManager(bot, self.db)
        
        # Démarrer la tâche de nettoyage des rôles expirés
        self.cleanup_expired_roles.start()
    
    def cog_unload(self):
        self.cleanup_expired_roles.cancel()
    
    @app_commands.command(name="autoroles", description="🎭 Configuration des rôles automatiques")
    @app_commands.describe(action="Action à effectuer")
    @app_commands.choices(action=[
        app_commands.Choice(name="setup - Configuration générale", value="setup"),
        app_commands.Choice(name="welcome - Rôles de bienvenue", value="welcome"),
        app_commands.Choice(name="bots - Rôles pour bots", value="bots"),
        app_commands.Choice(name="rules - Règles avancées", value="rules"),
        app_commands.Choice(name="stats - Statistiques", value="stats")
    ])
    async def autoroles(self, interaction: discord.Interaction, action: str = "setup"):
        """Commande principale de gestion des auto-rôles"""
        
        if not interaction.user.guild_permissions.manage_roles:
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes",
                description="Seuls les membres avec la permission **Gérer les rôles** peuvent utiliser cette commande.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if action == "setup":
            await self.setup_autoroles(interaction)
        elif action == "welcome":
            modal = WelcomeRolesModal(interaction.guild_id, self.db)
            await interaction.response.send_modal(modal)
        elif action == "bots":
            modal = BotRolesModal(interaction.guild_id, self.db)
            await interaction.response.send_modal(modal)
        elif action == "rules":
            view = AdvancedRulesView(interaction.guild_id, self.db)
            embed = discord.Embed(
                title="⚙️ Règles d'Auto-Rôles Avancées",
                description="Gérez les règles personnalisées d'attribution automatique",
                color=0x00FF88
            )
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        elif action == "stats":
            view = AutoRolesSetupView(interaction.guild_id, self.db)
            await view._show_autoroles_stats(interaction)
    
    async def setup_autoroles(self, interaction: discord.Interaction):
        """Configuration initiale des auto-rôles"""
        embed = discord.Embed(
            title="🎭 Système d'Auto-Rôles Arsenal",
            description="""
**Bienvenue dans le système d'auto-rôles le plus avancé !**

🔧 **Fonctionnalités principales :**
• **Rôles de bienvenue** - Attribution automatique à l'arrivée
• **Rôles pour bots** - Gestion spécifique des bots
• **Règles avancées** - Conditions personnalisées (niveau, activité, temps)
• **Rôles temporaires** - Attribution avec expiration automatique
• **Statistiques** - Suivi détaillé des attributions

🎯 **Types de règles disponibles :**
• **Join** - À l'arrivée sur le serveur
• **Level** - Basé sur le système de niveaux
• **Activity** - Selon l'activité de l'utilisateur  
• **Time** - Après un certain temps sur le serveur
• **Custom** - Conditions personnalisées avancées

Configurez chaque aspect selon vos besoins !
            """,
            color=0x3366FF
        )
        
        view = AutoRolesSetupView(interaction.guild_id, self.db)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Gestion de l'arrivée d'un membre"""
        try:
            await self.manager.process_member_join(member)
        except Exception as e:
            logger.error(f"Erreur traitement arrivée membre {member}: {e}")
    
    @tasks.loop(minutes=30)
    async def cleanup_expired_roles(self):
        """Tâche de nettoyage des rôles expirés"""
        try:
            expired_assignments = self.db.get_expired_roles()
            
            for assignment in expired_assignments:
                guild = self.bot.get_guild(assignment['guild_id'])
                if not guild:
                    continue
                
                member = guild.get_member(assignment['user_id'])
                role = guild.get_role(assignment['role_id'])
                
                if member and role and role in member.roles:
                    try:
                        await member.remove_roles(role, reason="Auto-rôle expiré")
                        logger.info(f"Rôle expiré {role.name} retiré de {member}")
                    except Exception as e:
                        logger.error(f"Erreur retrait rôle expiré: {e}")
                
                # Supprimer l'assignment de la base
                self.db.remove_assignment(assignment['id'])
                
        except Exception as e:
            logger.error(f"Erreur nettoyage rôles expirés: {e}")
    
    @cleanup_expired_roles.before_loop
    async def before_cleanup_expired_roles(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    """Setup function pour charger le système d'auto-rôles"""
    await bot.add_cog(AutoRolesSystem(bot))
    logger.info("🎭 Système d'Auto-Rôles Arsenal chargé avec succès!")
    print("✅ AutoRoles System - Système modulaire prêt!")
    print("🎯 Types: Join, Level, Activity, Time, Custom")
    print("🎭 Commande: /autoroles [setup|welcome|bots|rules|stats]")

