"""
🎭 ARSENAL REACTION ROLES SYSTEM V2.0
Système modulaire de rôles par réactions

Fonctionnalités:
- Messages de réaction avec rôles multiples
- Panels personnalisables avec embeds
- Gestion des limites et exclusions
- Mode unique/multiple/toggle
- Interface de configuration complète

Author: Arsenal Bot Team
Version: 2.0.0
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
import sqlite3
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# BASE DE DONNÉES REACTION ROLES
# =============================================================================

class ReactionRolesDB:
    """Gestionnaire de base de données pour les rôles par réaction"""
    
    def __init__(self, db_path: str = "arsenal_reaction_roles.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des panels de rôles par réaction
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reaction_panels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    message_id INTEGER NOT NULL,
                    panel_name TEXT NOT NULL,
                    panel_type TEXT NOT NULL DEFAULT 'normal', -- 'normal', 'unique', 'toggle'
                    max_roles INTEGER DEFAULT -1, -- -1 = illimité
                    require_role INTEGER NULL, -- Rôle requis pour utiliser le panel
                    exclude_roles TEXT, -- JSON array des rôles exclus
                    embed_data TEXT, -- JSON de l'embed
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des rôles assignés aux réactions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reaction_role_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    panel_id INTEGER NOT NULL,
                    emoji TEXT NOT NULL,
                    role_id INTEGER NOT NULL,
                    role_name TEXT NOT NULL,
                    role_description TEXT,
                    position INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (panel_id) REFERENCES reaction_panels (id) ON DELETE CASCADE
                )
            ''')
            
            # Table des utilisateurs ayant des rôles par réaction
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reaction_role_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    panel_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (panel_id) REFERENCES reaction_panels (id) ON DELETE CASCADE
                )
            ''')
            
            # Table des statistiques des panels
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reaction_panel_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    panel_id INTEGER NOT NULL,
                    emoji TEXT NOT NULL,
                    role_id INTEGER NOT NULL,
                    total_reactions INTEGER DEFAULT 0,
                    unique_users INTEGER DEFAULT 0,
                    last_used TIMESTAMP NULL,
                    FOREIGN KEY (panel_id) REFERENCES reaction_panels (id) ON DELETE CASCADE
                )
            ''')
            
            # Table de configuration globale
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reaction_config (
                    guild_id INTEGER PRIMARY KEY,
                    log_channel_id INTEGER NULL,
                    enable_dm_notifications BOOLEAN DEFAULT TRUE,
                    auto_remove_reactions BOOLEAN DEFAULT FALSE,
                    reaction_cooldown INTEGER DEFAULT 0, -- En secondes
                    max_panels_per_guild INTEGER DEFAULT 10,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def create_panel(self, guild_id: int, channel_id: int, panel_data: Dict[str, Any]) -> Optional[int]:
        """Crée un nouveau panel de rôles par réaction"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO reaction_panels 
                    (guild_id, channel_id, message_id, panel_name, panel_type, max_roles, require_role, exclude_roles, embed_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    guild_id,
                    channel_id,
                    panel_data.get('message_id', 0),
                    panel_data['panel_name'],
                    panel_data.get('panel_type', 'normal'),
                    panel_data.get('max_roles', -1),
                    panel_data.get('require_role'),
                    json.dumps(panel_data.get('exclude_roles', [])),
                    json.dumps(panel_data.get('embed_data', {}))
                ))
                
                panel_id = cursor.lastrowid
                conn.commit()
                return panel_id
                
            except Exception as e:
                logger.error(f"Erreur création panel: {e}")
                return None
    
    def update_panel_message_id(self, panel_id: int, message_id: int) -> bool:
        """Met à jour l'ID du message d'un panel"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    UPDATE reaction_panels 
                    SET message_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (message_id, panel_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
            except Exception as e:
                logger.error(f"Erreur mise à jour message panel: {e}")
                return False
    
    def add_role_to_panel(self, panel_id: int, emoji: str, role_id: int, role_name: str, description: str = None) -> bool:
        """Ajoute un rôle à un panel"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                # Vérifier la position suivante
                cursor.execute('SELECT MAX(position) FROM reaction_role_mappings WHERE panel_id = ?', (panel_id,))
                max_pos = cursor.fetchone()[0] or 0
                
                cursor.execute('''
                    INSERT INTO reaction_role_mappings 
                    (panel_id, emoji, role_id, role_name, role_description, position)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (panel_id, emoji, role_id, role_name, description, max_pos + 1))
                
                # Créer les stats pour ce mapping
                cursor.execute('''
                    INSERT INTO reaction_panel_stats (panel_id, emoji, role_id)
                    VALUES (?, ?, ?)
                ''', (panel_id, emoji, role_id))
                
                conn.commit()
                return True
                
            except Exception as e:
                logger.error(f"Erreur ajout rôle au panel: {e}")
                return False
    
    def get_panel(self, panel_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un panel par son ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM reaction_panels WHERE id = ?', (panel_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                panel = dict(zip(columns, row))
                
                # Parser les JSON
                panel['exclude_roles'] = json.loads(panel['exclude_roles']) if panel['exclude_roles'] else []
                panel['embed_data'] = json.loads(panel['embed_data']) if panel['embed_data'] else {}
                
                return panel
            return None
    
    def get_panel_by_message(self, message_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un panel par l'ID de son message"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM reaction_panels WHERE message_id = ?', (message_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                panel = dict(zip(columns, row))
                
                panel['exclude_roles'] = json.loads(panel['exclude_roles']) if panel['exclude_roles'] else []
                panel['embed_data'] = json.loads(panel['embed_data']) if panel['embed_data'] else {}
                
                return panel
            return None
    
    def get_panel_roles(self, panel_id: int) -> List[Dict[str, Any]]:
        """Récupère tous les rôles d'un panel"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT m.*, s.total_reactions, s.unique_users, s.last_used
                FROM reaction_role_mappings m
                LEFT JOIN reaction_panel_stats s ON m.panel_id = s.panel_id AND m.emoji = s.emoji
                WHERE m.panel_id = ? AND m.is_active = TRUE
                ORDER BY m.position ASC
            ''', (panel_id,))
            
            roles = []
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                roles.append(dict(zip(columns, row)))
            
            return roles
    
    def get_guild_panels(self, guild_id: int) -> List[Dict[str, Any]]:
        """Récupère tous les panels d'un serveur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.*, COUNT(m.id) as role_count
                FROM reaction_panels p
                LEFT JOIN reaction_role_mappings m ON p.id = m.panel_id AND m.is_active = TRUE
                WHERE p.guild_id = ? AND p.is_active = TRUE
                GROUP BY p.id
                ORDER BY p.created_at DESC
            ''', (guild_id,))
            
            panels = []
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                panel = dict(zip(columns, row))
                panel['exclude_roles'] = json.loads(panel['exclude_roles']) if panel['exclude_roles'] else []
                panel['embed_data'] = json.loads(panel['embed_data']) if panel['embed_data'] else {}
                panels.append(panel)
            
            return panels
    
    def get_role_by_reaction(self, panel_id: int, emoji: str) -> Optional[Dict[str, Any]]:
        """Récupère un rôle par son emoji dans un panel"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM reaction_role_mappings 
                WHERE panel_id = ? AND emoji = ? AND is_active = TRUE
            ''', (panel_id, emoji))
            
            row = cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def log_role_assignment(self, guild_id: int, user_id: int, panel_id: int, role_id: int) -> bool:
        """Enregistre l'attribution d'un rôle par réaction"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO reaction_role_users (guild_id, user_id, panel_id, role_id)
                    VALUES (?, ?, ?, ?)
                ''', (guild_id, user_id, panel_id, role_id))
                
                conn.commit()
                return True
                
            except Exception as e:
                logger.error(f"Erreur log assignment: {e}")
                return False
    
    def remove_role_assignment(self, guild_id: int, user_id: int, panel_id: int, role_id: int) -> bool:
        """Supprime l'enregistrement d'un rôle par réaction"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    DELETE FROM reaction_role_users 
                    WHERE guild_id = ? AND user_id = ? AND panel_id = ? AND role_id = ?
                ''', (guild_id, user_id, panel_id, role_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
            except Exception as e:
                logger.error(f"Erreur suppression assignment: {e}")
                return False
    
    def update_reaction_stats(self, panel_id: int, emoji: str, role_id: int):
        """Met à jour les statistiques d'une réaction"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                # Compter les utilisateurs uniques pour cette réaction
                cursor.execute('''
                    SELECT COUNT(DISTINCT user_id) FROM reaction_role_users 
                    WHERE panel_id = ? AND role_id = ?
                ''', (panel_id, role_id))
                
                unique_users = cursor.fetchone()[0] or 0
                
                cursor.execute('''
                    UPDATE reaction_panel_stats 
                    SET total_reactions = total_reactions + 1,
                        unique_users = ?,
                        last_used = CURRENT_TIMESTAMP
                    WHERE panel_id = ? AND emoji = ? AND role_id = ?
                ''', (unique_users, panel_id, emoji, role_id))
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"Erreur mise à jour stats: {e}")


# =============================================================================
# GESTIONNAIRE DE RÔLES PAR RÉACTION
# =============================================================================

class ReactionRoleManager:
    """Gestionnaire principal des rôles par réaction"""
    
    def __init__(self, bot, db: ReactionRolesDB):
        self.bot = bot
        self.db = db
        self.cooldowns = {}  # Cooldowns des utilisateurs
    
    async def handle_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Gère l'ajout d'une réaction"""
        if payload.user_id == self.bot.user.id:
            return
        
        # Récupérer le panel
        panel = self.db.get_panel_by_message(payload.message_id)
        if not panel or not panel['is_active']:
            return
        
        # Vérifier le cooldown
        if not await self._check_cooldown(payload.user_id, payload.guild_id):
            return
        
        # Récupérer le rôle associé à cette réaction
        role_mapping = self.db.get_role_by_reaction(panel['id'], str(payload.emoji))
        if not role_mapping:
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        member = guild.get_member(payload.user_id)
        role = guild.get_role(role_mapping['role_id'])
        
        if not member or not role:
            return
        
        # Vérifier les permissions et conditions
        if not await self._check_user_permissions(member, panel):
            await self._remove_reaction_silent(payload)
            return
        
        # Gestion selon le type de panel
        await self._process_role_assignment(member, role, panel, role_mapping, payload)
    
    async def handle_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Gère la suppression d'une réaction"""
        if payload.user_id == self.bot.user.id:
            return
        
        panel = self.db.get_panel_by_message(payload.message_id)
        if not panel or panel['panel_type'] == 'toggle':
            return  # Ne pas retirer le rôle automatiquement sauf en mode toggle
        
        role_mapping = self.db.get_role_by_reaction(panel['id'], str(payload.emoji))
        if not role_mapping:
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        member = guild.get_member(payload.user_id)
        role = guild.get_role(role_mapping['role_id'])
        
        if not member or not role:
            return
        
        # Retirer le rôle si le membre l'a
        if role in member.roles:
            try:
                await member.remove_roles(role, reason=f"Réaction retirée - Panel: {panel['panel_name']}")
                self.db.remove_role_assignment(guild.id, member.id, panel['id'], role.id)
                
                # Notifier l'utilisateur si activé
                await self._notify_user_role_change(member, role, "removed", panel['panel_name'])
                
            except discord.Forbidden:
                logger.warning(f"Permission manquante pour retirer le rôle {role.name}")
            except Exception as e:
                logger.error(f"Erreur retrait rôle par réaction: {e}")
    
    async def _check_cooldown(self, user_id: int, guild_id: int) -> bool:
        """Vérifie le cooldown d'un utilisateur"""
        # TODO: Implémenter le système de cooldown
        return True
    
    async def _check_user_permissions(self, member: discord.Member, panel: Dict[str, Any]) -> bool:
        """Vérifie si un utilisateur peut utiliser le panel"""
        # Vérifier le rôle requis
        if panel['require_role']:
            required_role = member.guild.get_role(panel['require_role'])
            if not required_role or required_role not in member.roles:
                return False
        
        # Vérifier les rôles exclus
        if panel['exclude_roles']:
            member_role_ids = [role.id for role in member.roles]
            if any(role_id in member_role_ids for role_id in panel['exclude_roles']):
                return False
        
        return True
    
    async def _process_role_assignment(self, member: discord.Member, role: discord.Role, 
                                     panel: Dict[str, Any], role_mapping: Dict[str, Any], 
                                     payload: discord.RawReactionActionEvent):
        """Traite l'attribution d'un rôle selon le type de panel"""
        
        if panel['panel_type'] == 'unique':
            # Mode unique : retirer tous les autres rôles du panel
            await self._handle_unique_role(member, role, panel)
        
        elif panel['panel_type'] == 'toggle':
            # Mode toggle : ajouter/retirer selon l'état actuel
            await self._handle_toggle_role(member, role, panel, role_mapping, payload)
        
        else:
            # Mode normal : simplement ajouter le rôle
            await self._handle_normal_role(member, role, panel, role_mapping)
    
    async def _handle_normal_role(self, member: discord.Member, role: discord.Role, 
                                 panel: Dict[str, Any], role_mapping: Dict[str, Any]):
        """Gère l'attribution en mode normal"""
        if role in member.roles:
            return  # L'utilisateur a déjà ce rôle
        
        # Vérifier la limite de rôles
        if panel['max_roles'] > 0:
            user_panel_roles = await self._get_user_panel_roles(member, panel['id'])
            if len(user_panel_roles) >= panel['max_roles']:
                return
        
        try:
            await member.add_roles(role, reason=f"Rôle par réaction - Panel: {panel['panel_name']}")
            self.db.log_role_assignment(member.guild.id, member.id, panel['id'], role.id)
            self.db.update_reaction_stats(panel['id'], role_mapping['emoji'], role.id)
            
            await self._notify_user_role_change(member, role, "added", panel['panel_name'])
            
        except discord.Forbidden:
            logger.warning(f"Permission manquante pour attribuer le rôle {role.name}")
        except Exception as e:
            logger.error(f"Erreur attribution rôle normal: {e}")
    
    async def _handle_unique_role(self, member: discord.Member, role: discord.Role, panel: Dict[str, Any]):
        """Gère l'attribution en mode unique (un seul rôle du panel)"""
        panel_roles = self.db.get_panel_roles(panel['id'])
        roles_to_remove = []
        
        # Identifier les rôles du panel que l'utilisateur possède
        for panel_role in panel_roles:
            existing_role = member.guild.get_role(panel_role['role_id'])
            if existing_role and existing_role in member.roles and existing_role != role:
                roles_to_remove.append(existing_role)
        
        try:
            # Retirer les anciens rôles du panel
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove, reason=f"Mode unique - Panel: {panel['panel_name']}")
                for old_role in roles_to_remove:
                    self.db.remove_role_assignment(member.guild.id, member.id, panel['id'], old_role.id)
            
            # Ajouter le nouveau rôle s'il ne l'a pas déjà
            if role not in member.roles:
                await member.add_roles(role, reason=f"Rôle unique - Panel: {panel['panel_name']}")
                self.db.log_role_assignment(member.guild.id, member.id, panel['id'], role.id)
            
            await self._notify_user_role_change(member, role, "selected", panel['panel_name'])
            
        except discord.Forbidden:
            logger.warning(f"Permission manquante pour gérer les rôles uniques")
        except Exception as e:
            logger.error(f"Erreur gestion rôle unique: {e}")
    
    async def _handle_toggle_role(self, member: discord.Member, role: discord.Role, 
                                 panel: Dict[str, Any], role_mapping: Dict[str, Any], 
                                 payload: discord.RawReactionActionEvent):
        """Gère l'attribution en mode toggle"""
        try:
            if role in member.roles:
                # Retirer le rôle
                await member.remove_roles(role, reason=f"Toggle OFF - Panel: {panel['panel_name']}")
                self.db.remove_role_assignment(member.guild.id, member.id, panel['id'], role.id)
                
                await self._notify_user_role_change(member, role, "removed", panel['panel_name'])
            else:
                # Ajouter le rôle
                await member.add_roles(role, reason=f"Toggle ON - Panel: {panel['panel_name']}")
                self.db.log_role_assignment(member.guild.id, member.id, panel['id'], role.id)
                self.db.update_reaction_stats(panel['id'], role_mapping['emoji'], role.id)
                
                await self._notify_user_role_change(member, role, "added", panel['panel_name'])
                
            # Retirer la réaction pour clarifier l'état
            await self._remove_reaction_silent(payload)
            
        except discord.Forbidden:
            logger.warning(f"Permission manquante pour toggle le rôle {role.name}")
        except Exception as e:
            logger.error(f"Erreur toggle rôle: {e}")
    
    async def _get_user_panel_roles(self, member: discord.Member, panel_id: int) -> List[discord.Role]:
        """Récupère tous les rôles d'un panel que possède l'utilisateur"""
        panel_roles = self.db.get_panel_roles(panel_id)
        user_roles = []
        
        for panel_role in panel_roles:
            role = member.guild.get_role(panel_role['role_id'])
            if role and role in member.roles:
                user_roles.append(role)
        
        return user_roles
    
    async def _notify_user_role_change(self, member: discord.Member, role: discord.Role, 
                                      action: str, panel_name: str):
        """Notifie l'utilisateur d'un changement de rôle"""
        # TODO: Vérifier les préférences de notification
        try:
            action_text = {
                "added": f"✅ Vous avez obtenu le rôle **{role.name}**",
                "removed": f"❌ Le rôle **{role.name}** vous a été retiré", 
                "selected": f"🎯 Vous avez sélectionné le rôle **{role.name}**"
            }.get(action, f"Rôle **{role.name}** modifié")
            
            embed = discord.Embed(
                title="🎭 Rôle par Réaction",
                description=f"{action_text}\nPanel: **{panel_name}**",
                color=role.color if role.color.value else 0x3366FF
            )
            
            await member.send(embed=embed)
            
        except discord.Forbidden:
            # L'utilisateur n'accepte pas les MP
            pass
        except Exception as e:
            logger.error(f"Erreur notification utilisateur: {e}")
    
    async def _remove_reaction_silent(self, payload: discord.RawReactionActionEvent):
        """Retire silencieusement une réaction"""
        try:
            channel = self.bot.get_channel(payload.channel_id)
            if channel:
                message = await channel.fetch_message(payload.message_id)
                await message.remove_reaction(payload.emoji, payload.member or await self.bot.fetch_user(payload.user_id))
        except Exception:
            pass  # Ignorer les erreurs de suppression de réaction


# =============================================================================
# VUES DISCORD UI POUR LA CRÉATION DE PANELS
# =============================================================================

class ReactionRoleSetupView(discord.ui.View):
    """Vue principale de configuration des rôles par réaction"""
    
    def __init__(self, guild_id: int, db: ReactionRolesDB):
        super().__init__(timeout=600)
        self.guild_id = guild_id
        self.db = db
    
    @discord.ui.button(label="➕ Créer Panel", style=discord.ButtonStyle.success, emoji="➕")
    async def create_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CreatePanelModal(self.guild_id, self.db)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 Mes Panels", style=discord.ButtonStyle.primary, emoji="📋")
    async def list_panels(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._show_guild_panels(interaction)
    
    @discord.ui.button(label="⚙️ Gérer Panel", style=discord.ButtonStyle.secondary, emoji="⚙️")
    async def manage_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = PanelSelectionView(self.guild_id, self.db)
        embed = discord.Embed(
            title="⚙️ Gestion des Panels",
            description="Sélectionnez un panel à gérer",
            color=0xFF8800
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="📊 Statistiques", style=discord.ButtonStyle.secondary, emoji="📊")
    async def show_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._show_reaction_stats(interaction)
    
    async def _show_guild_panels(self, interaction: discord.Interaction):
        """Affiche tous les panels du serveur"""
        panels = self.db.get_guild_panels(self.guild_id)
        
        embed = discord.Embed(
            title="📋 Panels de Rôles par Réaction",
            color=0x3366FF
        )
        
        if not panels:
            embed.description = "Aucun panel configuré sur ce serveur."
        else:
            for panel in panels[:10]:
                channel = interaction.guild.get_channel(panel['channel_id'])
                channel_name = channel.mention if channel else f"Canal supprimé ({panel['channel_id']})"
                
                panel_type_emoji = {
                    'normal': '🔄',
                    'unique': '🎯',
                    'toggle': '🔘'
                }.get(panel['panel_type'], '📋')
                
                embed.add_field(
                    name=f"{panel_type_emoji} {panel['panel_name']}",
                    value=f"**Canal:** {channel_name}\n"
                          f"**Type:** {panel['panel_type']}\n"
                          f"**Rôles:** {panel['role_count']}\n"
                          f"**ID:** {panel['id']}",
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def _show_reaction_stats(self, interaction: discord.Interaction):
        """Affiche les statistiques des rôles par réaction"""
        panels = self.db.get_guild_panels(self.guild_id)
        
        embed = discord.Embed(
            title="📊 Statistiques Rôles par Réaction",
            color=0xFFD700
        )
        
        if not panels:
            embed.description = "Aucune donnée statistique disponible."
        else:
            total_panels = len(panels)
            total_roles = sum(panel['role_count'] for panel in panels)
            active_panels = len([p for p in panels if p['is_active']])
            
            embed.add_field(
                name="📈 Statistiques Générales",
                value=f"**Panels totaux:** {total_panels}\n"
                      f"**Panels actifs:** {active_panels}\n"
                      f"**Rôles configurés:** {total_roles}",
                inline=True
            )
            
            # Types de panels
            panel_types = {}
            for panel in panels:
                panel_type = panel['panel_type']
                panel_types[panel_type] = panel_types.get(panel_type, 0) + 1
            
            if panel_types:
                type_list = []
                for ptype, count in panel_types.items():
                    emoji = {'normal': '🔄', 'unique': '🎯', 'toggle': '🔘'}.get(ptype, '📋')
                    type_list.append(f"{emoji} {ptype.title()}: {count}")
                
                embed.add_field(
                    name="🎭 Types de Panels",
                    value="\n".join(type_list),
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class PanelSelectionView(discord.ui.View):
    """Vue pour sélectionner un panel à gérer"""
    
    def __init__(self, guild_id: int, db: ReactionRolesDB):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.db = db
        
        # Ajouter les panels dans un select menu
        panels = db.get_guild_panels(guild_id)
        
        if panels:
            options = []
            for panel in panels[:25]:  # Maximum 25 options
                options.append(discord.SelectOption(
                    label=panel['panel_name'],
                    description=f"Type: {panel['panel_type']} | Rôles: {panel['role_count']}",
                    value=str(panel['id'])
                ))
            
            if options:
                self.panel_select = discord.ui.Select(
                    placeholder="Choisir un panel à gérer...",
                    options=options
                )
                self.panel_select.callback = self.panel_selected
                self.add_item(self.panel_select)
    
    async def panel_selected(self, interaction: discord.Interaction):
        """Callback quand un panel est sélectionné"""
        panel_id = int(self.panel_select.values[0])
        view = PanelManagementView(panel_id, self.db)
        
        panel = self.db.get_panel(panel_id)
        embed = discord.Embed(
            title=f"⚙️ Gestion: {panel['panel_name']}",
            description=f"Gérez ce panel de rôles par réaction",
            color=0xFF8800
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class PanelManagementView(discord.ui.View):
    """Vue de gestion d'un panel spécifique"""
    
    def __init__(self, panel_id: int, db: ReactionRolesDB):
        super().__init__(timeout=300)
        self.panel_id = panel_id
        self.db = db
    
    @discord.ui.button(label="➕ Ajouter Rôle", style=discord.ButtonStyle.success, emoji="➕")
    async def add_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AddRoleToPanel(self.panel_id, self.db)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 Voir Rôles", style=discord.ButtonStyle.primary, emoji="📋")
    async def view_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._show_panel_roles(interaction)
    
    @discord.ui.button(label="🔄 Recréer Panel", style=discord.ButtonStyle.secondary, emoji="🔄")
    async def recreate_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._recreate_panel_message(interaction)
    
    async def _show_panel_roles(self, interaction: discord.Interaction):
        """Affiche tous les rôles du panel"""
        panel = self.db.get_panel(self.panel_id)
        roles = self.db.get_panel_roles(self.panel_id)
        
        embed = discord.Embed(
            title=f"📋 Rôles du Panel: {panel['panel_name']}",
            color=0x3366FF
        )
        
        if not roles:
            embed.description = "Aucun rôle configuré dans ce panel."
        else:
            for role_data in roles:
                guild_role = interaction.guild.get_role(role_data['role_id'])
                role_name = guild_role.name if guild_role else f"Rôle supprimé ({role_data['role_id']})"
                
                embed.add_field(
                    name=f"{role_data['emoji']} {role_name}",
                    value=f"**Description:** {role_data['role_description'] or 'Aucune'}\n"
                          f"**Utilisateurs:** {role_data['unique_users'] or 0}\n"
                          f"**Réactions totales:** {role_data['total_reactions'] or 0}",
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def _recreate_panel_message(self, interaction: discord.Interaction):
        """Recrée le message du panel"""
        panel = self.db.get_panel(self.panel_id)
        roles = self.db.get_panel_roles(self.panel_id)
        
        if not roles:
            embed = discord.Embed(
                title="❌ Panel Vide",
                description="Ce panel ne contient aucun rôle. Ajoutez des rôles avant de le créer.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Créer l'embed du panel
        panel_embed = self._create_panel_embed(panel, roles, interaction.guild)
        
        try:
            # Envoyer le message dans le canal configuré
            channel = interaction.guild.get_channel(panel['channel_id'])
            if not channel:
                embed = discord.Embed(
                    title="❌ Canal Introuvable",
                    description="Le canal configuré pour ce panel n'existe plus.",
                    color=0xFF0000
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            message = await channel.send(embed=panel_embed)
            
            # Ajouter toutes les réactions
            for role_data in roles:
                try:
                    await message.add_reaction(role_data['emoji'])
                except Exception as e:
                    logger.error(f"Erreur ajout réaction {role_data['emoji']}: {e}")
            
            # Mettre à jour l'ID du message
            self.db.update_panel_message_id(self.panel_id, message.id)
            
            embed = discord.Embed(
                title="✅ Panel Recréé",
                description=f"Le panel a été recréé dans {channel.mention}",
                color=0x00FF88
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes",
                description="Je n'ai pas les permissions pour envoyer des messages dans ce canal.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def _create_panel_embed(self, panel: Dict[str, Any], roles: List[Dict[str, Any]], 
                           guild: discord.Guild) -> discord.Embed:
        """Crée l'embed du panel"""
        embed_data = panel['embed_data']
        
        embed = discord.Embed(
            title=embed_data.get('title', panel['panel_name']),
            description=embed_data.get('description', "Cliquez sur les réactions pour obtenir les rôles !"),
            color=int(embed_data.get('color', '3366FF'), 16)
        )
        
        # Ajouter les rôles disponibles
        role_list = []
        for role_data in roles:
            guild_role = guild.get_role(role_data['role_id'])
            if guild_role:
                description = role_data['role_description'] or guild_role.name
                role_list.append(f"{role_data['emoji']} **{guild_role.name}** - {description}")
        
        if role_list:
            embed.add_field(
                name="🎭 Rôles Disponibles",
                value="\n".join(role_list),
                inline=False
            )
        
        # Informations sur le panel
        panel_info = []
        if panel['panel_type'] == 'unique':
            panel_info.append("🎯 **Mode Unique** - Un seul rôle à la fois")
        elif panel['panel_type'] == 'toggle':
            panel_info.append("🔘 **Mode Toggle** - Cliquez pour activer/désactiver")
        
        if panel['max_roles'] > 0:
            panel_info.append(f"📊 **Limite** - Maximum {panel['max_roles']} rôles")
        
        if panel_info:
            embed.add_field(
                name="ℹ️ Informations",
                value="\n".join(panel_info),
                inline=False
            )
        
        embed.set_footer(text=f"Panel ID: {panel['id']}")
        
        return embed


# =============================================================================
# MODALS POUR LA CONFIGURATION
# =============================================================================

class CreatePanelModal(discord.ui.Modal):
    """Modal pour créer un nouveau panel"""
    
    def __init__(self, guild_id: int, db: ReactionRolesDB):
        super().__init__(title="➕ Créer un Panel de Rôles", timeout=300)
        self.guild_id = guild_id
        self.db = db
        
        self.name_input = discord.ui.TextInput(
            label="Nom du panel",
            placeholder="ex: Rôles de couleur",
            max_length=50,
            required=True
        )
        
        self.channel_input = discord.ui.TextInput(
            label="ID du canal de destination",
            placeholder="123456789",
            max_length=20,
            required=True
        )
        
        self.type_input = discord.ui.TextInput(
            label="Type de panel",
            placeholder="normal, unique, toggle",
            max_length=10,
            default="normal",
            required=True
        )
        
        self.title_input = discord.ui.TextInput(
            label="Titre de l'embed",
            placeholder="Choisissez vos rôles !",
            max_length=100,
            required=False
        )
        
        self.description_input = discord.ui.TextInput(
            label="Description de l'embed",
            placeholder="Cliquez sur les réactions pour obtenir les rôles correspondants.",
            style=discord.TextStyle.long,
            max_length=500,
            required=False
        )
        
        self.add_item(self.name_input)
        self.add_item(self.channel_input)
        self.add_item(self.type_input)
        self.add_item(self.title_input)
        self.add_item(self.description_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Validation
            panel_type = self.type_input.value.lower()
            if panel_type not in ['normal', 'unique', 'toggle']:
                raise ValueError("Type de panel invalide")
            
            channel_id = int(self.channel_input.value)
            channel = interaction.guild.get_channel(channel_id)
            if not channel:
                raise ValueError("Canal introuvable")
            
            # Données du panel
            panel_data = {
                'panel_name': self.name_input.value,
                'panel_type': panel_type,
                'embed_data': {
                    'title': self.title_input.value or self.name_input.value,
                    'description': self.description_input.value or "Cliquez sur les réactions pour obtenir les rôles !",
                    'color': '3366FF'
                }
            }
            
            # Créer le panel
            panel_id = self.db.create_panel(self.guild_id, channel_id, panel_data)
            
            if panel_id:
                embed = discord.Embed(
                    title="✅ Panel Créé",
                    description=f"Le panel **{self.name_input.value}** a été créé avec succès !",
                    color=0x00FF88
                )
                
                embed.add_field(
                    name="📋 Détails",
                    value=f"**Canal:** {channel.mention}\n"
                          f"**Type:** {panel_type}\n"
                          f"**ID Panel:** {panel_id}",
                    inline=False
                )
                
                embed.add_field(
                    name="➡️ Prochaines Étapes",
                    value="1. Ajoutez des rôles au panel\n2. Générez le message du panel\n3. Les utilisateurs pourront réagir !",
                    inline=False
                )
                
                # Vue pour gérer le nouveau panel
                view = PanelManagementView(panel_id, self.db)
                
            else:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Erreur lors de la création du panel.",
                    color=0xFF0000
                )
                view = None
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except ValueError as e:
            embed = discord.Embed(
                title="❌ Erreur de Validation",
                description=f"Erreur: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


class AddRoleToPanel(discord.ui.Modal):
    """Modal pour ajouter un rôle à un panel"""
    
    def __init__(self, panel_id: int, db: ReactionRolesDB):
        super().__init__(title="➕ Ajouter un Rôle au Panel", timeout=300)
        self.panel_id = panel_id
        self.db = db
        
        self.emoji_input = discord.ui.TextInput(
            label="Emoji/Réaction",
            placeholder="🎨 ou :custom_emoji:",
            max_length=50,
            required=True
        )
        
        self.role_input = discord.ui.TextInput(
            label="ID du rôle",
            placeholder="123456789",
            max_length=20,
            required=True
        )
        
        self.description_input = discord.ui.TextInput(
            label="Description du rôle",
            placeholder="Rôle pour les artistes",
            max_length=100,
            required=False
        )
        
        self.add_item(self.emoji_input)
        self.add_item(self.role_input)
        self.add_item(self.description_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            role_id = int(self.role_input.value)
            role = interaction.guild.get_role(role_id)
            
            if not role:
                raise ValueError("Rôle introuvable")
            
            # Vérifier que l'emoji n'est pas déjà utilisé
            existing = self.db.get_role_by_reaction(self.panel_id, self.emoji_input.value)
            if existing:
                raise ValueError("Cette réaction est déjà utilisée dans ce panel")
            
            # Ajouter le rôle au panel
            success = self.db.add_role_to_panel(
                self.panel_id,
                self.emoji_input.value,
                role_id,
                role.name,
                self.description_input.value
            )
            
            if success:
                embed = discord.Embed(
                    title="✅ Rôle Ajouté",
                    description=f"Le rôle **{role.name}** a été ajouté au panel !",
                    color=0x00FF88
                )
                
                embed.add_field(
                    name="📋 Détails",
                    value=f"**Réaction:** {self.emoji_input.value}\n"
                          f"**Rôle:** {role.mention}\n"
                          f"**Description:** {self.description_input.value or 'Aucune'}",
                    inline=False
                )
            else:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Erreur lors de l'ajout du rôle.",
                    color=0xFF0000
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError as e:
            embed = discord.Embed(
                title="❌ Erreur de Validation",
                description=f"Erreur: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


# =============================================================================
# COMMANDES PRINCIPALES DU SYSTÈME REACTION ROLES
# =============================================================================

class ReactionRolesSystem(commands.Cog):
    """🎭 Système modulaire de rôles par réaction Arsenal"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = ReactionRolesDB()
        self.manager = ReactionRoleManager(bot, self.db)
    
    @app_commands.command(name="reactionroles", description="🎭 Configuration des rôles par réaction")
    @app_commands.describe(action="Action à effectuer")
    @app_commands.choices(action=[
        app_commands.Choice(name="setup - Configuration générale", value="setup"),
        app_commands.Choice(name="create - Créer un panel", value="create"),
        app_commands.Choice(name="manage - Gérer un panel", value="manage"),
        app_commands.Choice(name="list - Lister les panels", value="list"),
        app_commands.Choice(name="stats - Statistiques", value="stats")
    ])
    async def reactionroles(self, interaction: discord.Interaction, action: str = "setup"):
        """Commande principale de gestion des rôles par réaction"""
        
        if not interaction.user.guild_permissions.manage_roles:
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes",
                description="Seuls les membres avec la permission **Gérer les rôles** peuvent utiliser cette commande.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if action == "setup":
            await self.setup_reaction_roles(interaction)
        elif action == "create":
            modal = CreatePanelModal(interaction.guild_id, self.db)
            await interaction.response.send_modal(modal)
        elif action == "manage":
            view = PanelSelectionView(interaction.guild_id, self.db)
            embed = discord.Embed(
                title="⚙️ Gestion des Panels",
                description="Sélectionnez un panel à gérer",
                color=0xFF8800
            )
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        elif action == "list":
            view = ReactionRoleSetupView(interaction.guild_id, self.db)
            await view._show_guild_panels(interaction)
        elif action == "stats":
            view = ReactionRoleSetupView(interaction.guild_id, self.db)
            await view._show_reaction_stats(interaction)
    
    async def setup_reaction_roles(self, interaction: discord.Interaction):
        """Configuration initiale des rôles par réaction"""
        embed = discord.Embed(
            title="🎭 Système de Rôles par Réaction Arsenal",
            description="""
**Le système le plus avancé de rôles par réaction !**

🎯 **Fonctionnalités principales :**
• **Panels personnalisables** - Embeds sur-mesure
• **3 modes d'attribution** - Normal, Unique, Toggle
• **Gestion des limites** - Nombre maximum de rôles
• **Conditions d'accès** - Rôles requis ou exclus
• **Statistiques complètes** - Suivi des utilisations

🔄 **Modes disponibles :**
• **Normal** - Cumul de rôles autorisé
• **Unique** - Un seul rôle du panel à la fois  
• **Toggle** - Activation/désactivation par clic

⚙️ **Options avancées :**
• **Cooldowns** - Limitation des actions
• **Notifications** - Messages privés aux utilisateurs
• **Logs** - Historique des attributions
• **Auto-cleanup** - Gestion automatique des réactions

Créez vos premiers panels maintenant !
            """,
            color=0x9966FF
        )
        
        view = ReactionRoleSetupView(interaction.guild_id, self.db)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Gestion de l'ajout de réactions"""
        await self.manager.handle_reaction_add(payload)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Gestion de la suppression de réactions"""
        await self.manager.handle_reaction_remove(payload)


async def setup(bot):
    """Setup function pour charger le système de rôles par réaction"""
    await bot.add_cog(ReactionRolesSystem(bot))
    logger.info("🎭 Système de Rôles par Réaction Arsenal chargé avec succès!")
    print("✅ Reaction Roles System - Système modulaire prêt!")
    print("🎭 Modes: Normal, Unique, Toggle")
    print("🎯 Commande: /reactionroles [setup|create|manage|list|stats]")
