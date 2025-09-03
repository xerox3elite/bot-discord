"""
📢 ARSENAL ANNOUNCEMENTS SYSTEM V2.0
Système modulaire d'annonces et notifications

Fonctionnalités:
- Annonces programmées et instantanées
- Templates personnalisables
- Multi-canaux et mentions ciblées
- Système de validation et preview
- Historique et statistiques

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
import re

logger = logging.getLogger(__name__)

# =============================================================================
# BASE DE DONNÉES ANNONCES
# =============================================================================

class AnnouncementsDB:
    """Gestionnaire de base de données pour les annonces"""
    
    def __init__(self, get_cog=None, db_path: str = "arsenal_announcements.db"):
        self.db_path = db_path
        # get_cog peut être une callable (ex: bot.get_cog) ou None
        self.get_cog = get_cog
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des templates d'annonces
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS announcement_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    template_name TEXT NOT NULL,
                    template_type TEXT NOT NULL DEFAULT 'embed', -- 'embed', 'text', 'mixed'
                    embed_data TEXT, -- JSON des données embed
                    content_template TEXT, -- Template du contenu texte
                    mention_settings TEXT, -- JSON des paramètres de mention
                    image_url TEXT,
                    thumbnail_url TEXT,
                    footer_text TEXT,
                    color INTEGER DEFAULT 3447003, -- Couleur par défaut
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des annonces programmées
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_announcements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    template_id INTEGER,
                    announcement_title TEXT NOT NULL,
                    announcement_content TEXT NOT NULL,
                    target_channels TEXT NOT NULL, -- JSON array des canaux
                    mentions TEXT, -- JSON des mentions (roles, users, everyone)
                    embed_data TEXT, -- JSON des données embed complètes
                    scheduled_time TIMESTAMP NOT NULL,
                    repeat_settings TEXT, -- JSON pour répétitions (daily, weekly, etc.)
                    is_sent BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_by INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (template_id) REFERENCES announcement_templates (id)
                )
            ''')
            
            # Table de l'historique des annonces
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS announcement_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    scheduled_id INTEGER,
                    announcement_title TEXT NOT NULL,
                    announcement_content TEXT NOT NULL,
                    channels_sent TEXT NOT NULL, -- JSON des canaux où l'annonce a été envoyée
                    message_ids TEXT, -- JSON des IDs des messages envoyés
                    mentions_used TEXT, -- JSON des mentions utilisées
                    sent_by INTEGER NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reaction_stats TEXT, -- JSON des stats de réaction
                    FOREIGN KEY (scheduled_id) REFERENCES scheduled_announcements (id)
                )
            ''')
            
            # Table de configuration des annonces par serveur
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS announcement_config (
                    guild_id INTEGER PRIMARY KEY,
                    default_channel_id INTEGER, -- Canal par défaut
                    announcement_role_id INTEGER, -- Rôle pour recevoir les annonces
                    moderator_role_id INTEGER, -- Rôle pouvant créer des annonces
                    require_approval BOOLEAN DEFAULT FALSE,
                    approval_channel_id INTEGER,
                    max_daily_announcements INTEGER DEFAULT 5,
                    enable_auto_reactions BOOLEAN DEFAULT FALSE,
                    auto_reactions TEXT, -- JSON des réactions automatiques
                    log_channel_id INTEGER,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des approbations d'annonces
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS announcement_approvals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    scheduled_id INTEGER NOT NULL,
                    requested_by INTEGER NOT NULL,
                    approval_status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
                    approved_by INTEGER,
                    approval_reason TEXT,
                    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reviewed_at TIMESTAMP,
                    FOREIGN KEY (scheduled_id) REFERENCES scheduled_announcements (id)
                )
            ''')
            
            # Table des statistiques d'annonces
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS announcement_stats (
                    guild_id INTEGER PRIMARY KEY,
                    total_sent INTEGER DEFAULT 0,
                    sent_today INTEGER DEFAULT 0,
                    sent_this_week INTEGER DEFAULT 0,
                    sent_this_month INTEGER DEFAULT 0,
                    templates_created INTEGER DEFAULT 0,
                    avg_reactions REAL DEFAULT 0.0,
                    most_used_channel_id INTEGER,
                    last_announcement TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def create_template(self, guild_id: int, template_data: Dict[str, Any]) -> Optional[int]:
        """Crée un nouveau template d'annonce"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO announcement_templates 
                    (guild_id, template_name, template_type, embed_data, content_template, 
                     mention_settings, image_url, thumbnail_url, footer_text, color)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    guild_id,
                    template_data['template_name'],
                    template_data.get('template_type', 'embed'),
                    json.dumps(template_data.get('embed_data', {})),
                    template_data.get('content_template'),
                    json.dumps(template_data.get('mention_settings', {})),
                    template_data.get('image_url'),
                    template_data.get('thumbnail_url'),
                    template_data.get('footer_text'),
                    template_data.get('color', 3447003)
                ))
                
                template_id = cursor.lastrowid
                
                # Mettre à jour les stats
                cursor.execute('''
                    INSERT OR REPLACE INTO announcement_stats 
                    (guild_id, templates_created, updated_at)
                    VALUES (?, COALESCE((SELECT templates_created FROM announcement_stats WHERE guild_id = ?), 0) + 1, CURRENT_TIMESTAMP)
                ''', (guild_id, guild_id))
                
                conn.commit()
                return template_id
                
            except Exception as e:
                logger.error(f"Erreur création template: {e}")
                return None
    
    def get_templates(self, guild_id: int) -> List[Dict[str, Any]]:
        """Récupère tous les templates d'un serveur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM announcement_templates 
                WHERE guild_id = ? AND is_active = TRUE
                ORDER BY created_at DESC
            ''', (guild_id,))
            
            templates = []
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                template = dict(zip(columns, row))
                # Parser les JSON
                template['embed_data'] = json.loads(template['embed_data']) if template['embed_data'] else {}
                template['mention_settings'] = json.loads(template['mention_settings']) if template['mention_settings'] else {}
                templates.append(template)
            
            return templates
    
    def schedule_announcement(self, guild_id: int, announcement_data: Dict[str, Any], created_by: int) -> Optional[int]:
        """Programme une nouvelle annonce"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO scheduled_announcements 
                    (guild_id, template_id, announcement_title, announcement_content, 
                     target_channels, mentions, embed_data, scheduled_time, repeat_settings, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    guild_id,
                    announcement_data.get('template_id'),
                    announcement_data['announcement_title'],
                    announcement_data['announcement_content'],
                    json.dumps(announcement_data['target_channels']),
                    json.dumps(announcement_data.get('mentions', {})),
                    json.dumps(announcement_data.get('embed_data', {})),
                    announcement_data['scheduled_time'],
                    json.dumps(announcement_data.get('repeat_settings', {})),
                    created_by
                ))
                
                scheduled_id = cursor.lastrowid
                conn.commit()
                return scheduled_id
                
            except Exception as e:
                logger.error(f"Erreur programmation annonce: {e}")
                return None
    
    def get_pending_announcements(self) -> List[Dict[str, Any]]:
        """Récupère les annonces en attente d'envoi"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM scheduled_announcements 
                WHERE is_sent = FALSE AND is_active = TRUE 
                AND scheduled_time <= CURRENT_TIMESTAMP
                ORDER BY scheduled_time ASC
            ''', )
            
            announcements = []
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                announcement = dict(zip(columns, row))
                # Parser les JSON
                announcement['target_channels'] = json.loads(announcement['target_channels'])
                announcement['mentions'] = json.loads(announcement['mentions']) if announcement['mentions'] else {}
                announcement['embed_data'] = json.loads(announcement['embed_data']) if announcement['embed_data'] else {}
                announcement['repeat_settings'] = json.loads(announcement['repeat_settings']) if announcement['repeat_settings'] else {}
                announcements.append(announcement)
            
            return announcements
    
    def mark_announcement_sent(self, announcement_id: int, message_ids: List[int], channels_sent: List[int]) -> bool:
        """Marque une annonce comme envoyée"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    UPDATE scheduled_announcements 
                    SET is_sent = TRUE 
                    WHERE id = ?
                ''', (announcement_id,))
                
                # Récupérer les données de l'annonce
                cursor.execute('SELECT * FROM scheduled_announcements WHERE id = ?', (announcement_id,))
                row = cursor.fetchone()
                
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    announcement = dict(zip(columns, row))
                    
                    # Ajouter à l'historique
                    cursor.execute('''
                        INSERT INTO announcement_history 
                        (guild_id, scheduled_id, announcement_title, announcement_content,
                         channels_sent, message_ids, mentions_used, sent_by)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        announcement['guild_id'],
                        announcement_id,
                        announcement['announcement_title'],
                        announcement['announcement_content'],
                        json.dumps(channels_sent),
                        json.dumps(message_ids),
                        announcement['mentions'],
                        announcement['created_by']
                    ))
                    
                    # Mettre à jour les stats
                    self._update_guild_stats(announcement['guild_id'])
                
                conn.commit()
                return True
                
            except Exception as e:
                logger.error(f"Erreur marquage annonce envoyée: {e}")
                return False
    
    def get_guild_config(self, guild_id: int) -> Optional[Dict[str, Any]]:
        """Récupère la configuration d'annonces d'un serveur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM announcement_config WHERE guild_id = ?', (guild_id,))
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                config = dict(zip(columns, row))
                
                # Parser les JSON
                config['auto_reactions'] = json.loads(config['auto_reactions']) if config['auto_reactions'] else []
                
                return config
            return None
    
    def save_guild_config(self, guild_id: int, config: Dict[str, Any]) -> bool:
        """Sauvegarde la configuration d'annonces"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO announcement_config 
                    (guild_id, default_channel_id, announcement_role_id, moderator_role_id,
                     require_approval, approval_channel_id, max_daily_announcements,
                     enable_auto_reactions, auto_reactions, log_channel_id, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    guild_id,
                    config.get('default_channel_id'),
                    config.get('announcement_role_id'),
                    config.get('moderator_role_id'),
                    config.get('require_approval', False),
                    config.get('approval_channel_id'),
                    config.get('max_daily_announcements', 5),
                    config.get('enable_auto_reactions', False),
                    json.dumps(config.get('auto_reactions', [])),
                    config.get('log_channel_id')
                ))
                
                conn.commit()
                return True
                
            except Exception as e:
                logger.error(f"Erreur sauvegarde config annonces: {e}")
                return False
    
    def get_guild_stats(self, guild_id: int) -> Optional[Dict[str, Any]]:
        """Récupère les statistiques d'annonces d'un serveur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM announcement_stats WHERE guild_id = ?', (guild_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def _update_guild_stats(self, guild_id: int):
        """Met à jour les statistiques d'un serveur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                # Compter les annonces d'aujourd'hui
                cursor.execute('''
                    SELECT COUNT(*) FROM announcement_history 
                    WHERE guild_id = ? AND DATE(sent_at) = DATE('now')
                ''', (guild_id,))
                sent_today = cursor.fetchone()[0]
                
                # Compter les annonces de cette semaine
                cursor.execute('''
                    SELECT COUNT(*) FROM announcement_history 
                    WHERE guild_id = ? AND sent_at >= DATE('now', '-7 days')
                ''', (guild_id,))
                sent_this_week = cursor.fetchone()[0]
                
                # Compter les annonces de ce mois
                cursor.execute('''
                    SELECT COUNT(*) FROM announcement_history 
                    WHERE guild_id = ? AND sent_at >= DATE('now', 'start of month')
                ''', (guild_id,))
                sent_this_month = cursor.fetchone()[0]
                
                # Total des annonces
                cursor.execute('''
                    SELECT COUNT(*) FROM announcement_history WHERE guild_id = ?
                ''', (guild_id,))
                total_sent = cursor.fetchone()[0]
                
                # Mettre à jour les stats
                cursor.execute('''
                    INSERT OR REPLACE INTO announcement_stats 
                    (guild_id, total_sent, sent_today, sent_this_week, sent_this_month, 
                     last_announcement, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', (guild_id, total_sent, sent_today, sent_this_week, sent_this_month))
                
                conn.commit()
                
            except Exception as e:
                logger.error(f"Erreur mise à jour stats: {e}")


# =============================================================================
# GESTIONNAIRE D'ANNONCES
# =============================================================================

class AnnouncementManager:
    """Gestionnaire principal des annonces"""
    
    def __init__(self, bot, db: AnnouncementsDB):
        self.bot = bot
        self.db = db
    
    async def send_announcement(self, announcement: Dict[str, Any]) -> bool:
        """Envoie une annonce programmée"""
        try:
            guild = self.bot.get_guild(announcement['guild_id'])
            if not guild:
                logger.warning(f"Serveur {announcement['guild_id']} introuvable pour l'annonce {announcement['id']}")
                return False
            
            # Construire le message
            embed = await self._build_announcement_embed(announcement)
            content = await self._build_announcement_content(announcement, guild)
            
            message_ids = []
            channels_sent = []
            
            # Envoyer dans tous les canaux cibles
            for channel_id in announcement['target_channels']:
                channel = guild.get_channel(channel_id)
                if not channel:
                    logger.warning(f"Canal {channel_id} introuvable")
                    continue
                
                try:
                    if embed and content:
                        message = await channel.send(content=content, embed=embed)
                    elif embed:
                        message = await channel.send(embed=embed)
                    elif content:
                        message = await channel.send(content=content)
                    else:
                        continue
                    
                    message_ids.append(message.id)
                    channels_sent.append(channel_id)
                    
                    # Ajouter des réactions automatiques si configuré
                    await self._add_auto_reactions(message, announcement['guild_id'])
                    
                except discord.Forbidden:
                    logger.warning(f"Permission manquante pour envoyer dans {channel.name}")
                except Exception as e:
                    logger.error(f"Erreur envoi annonce dans {channel.name}: {e}")
            
            # Marquer comme envoyée
            if message_ids:
                self.db.mark_announcement_sent(announcement['id'], message_ids, channels_sent)
                
                # Gérer la répétition si configurée
                await self._handle_repeat_settings(announcement)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur envoi annonce {announcement['id']}: {e}")
            return False
    
    async def _build_announcement_embed(self, announcement: Dict[str, Any]) -> Optional[discord.Embed]:
        """Construit l'embed d'une annonce"""
        embed_data = announcement.get('embed_data', {})
        
        if not embed_data:
            return None
        
        embed = discord.Embed(
            title=embed_data.get('title', announcement['announcement_title']),
            description=embed_data.get('description', announcement['announcement_content']),
            color=embed_data.get('color', 3447003)
        )
        
        # Champs de l'embed
        if 'fields' in embed_data:
            for field in embed_data['fields']:
                embed.add_field(
                    name=field.get('name', 'Champ'),
                    value=field.get('value', 'Valeur'),
                    inline=field.get('inline', True)
                )
        
        # Image et thumbnail
        if 'image_url' in embed_data and embed_data['image_url']:
            embed.set_image(url=embed_data['image_url'])
        
        if 'thumbnail_url' in embed_data and embed_data['thumbnail_url']:
            embed.set_thumbnail(url=embed_data['thumbnail_url'])
        
        # Footer
        if 'footer_text' in embed_data and embed_data['footer_text']:
            embed.set_footer(text=embed_data['footer_text'])
        
        # Timestamp
        if embed_data.get('add_timestamp', False):
            embed.timestamp = datetime.now(timezone.utc)
        
        return embed
    
    async def _build_announcement_content(self, announcement: Dict[str, Any], guild: discord.Guild) -> Optional[str]:
        """Construit le contenu texte d'une annonce"""
        mentions = announcement.get('mentions', {})
        content_parts = []
        
        # Mentions
        if mentions.get('everyone'):
            content_parts.append("@everyone")
        elif mentions.get('here'):
            content_parts.append("@here")
        
        # Mentions de rôles
        if mentions.get('roles'):
            for role_id in mentions['roles']:
                role = guild.get_role(role_id)
                if role:
                    content_parts.append(role.mention)
        
        # Mentions d'utilisateurs
        if mentions.get('users'):
            for user_id in mentions['users']:
                user = guild.get_member(user_id)
                if user:
                    content_parts.append(user.mention)
        
        # Contenu personnalisé
        if announcement.get('content_prefix'):
            content_parts.append(announcement['content_prefix'])
        
        return " ".join(content_parts) if content_parts else None
    
    async def _add_auto_reactions(self, message: discord.Message, guild_id: int):
        """Ajoute des réactions automatiques à un message d'annonce"""
        config = self.db.get_guild_config(guild_id)
        
        if config and config.get('enable_auto_reactions') and config.get('auto_reactions'):
            for emoji in config['auto_reactions']:
                try:
                    await message.add_reaction(emoji)
                    await asyncio.sleep(0.5)  # Éviter le rate limiting
                except Exception as e:
                    logger.error(f"Erreur ajout réaction auto {emoji}: {e}")
    
    async def _handle_repeat_settings(self, announcement: Dict[str, Any]):
        """Gère les paramètres de répétition d'une annonce"""
        repeat_settings = announcement.get('repeat_settings', {})
        
        if not repeat_settings or not repeat_settings.get('enabled'):
            return
        
        # Calculer la prochaine occurrence
        next_time = None
        current_time = datetime.fromisoformat(announcement['scheduled_time'])
        
        repeat_type = repeat_settings.get('type')
        interval = repeat_settings.get('interval', 1)
        
        if repeat_type == 'daily':
            next_time = current_time + timedelta(days=interval)
        elif repeat_type == 'weekly':
            next_time = current_time + timedelta(weeks=interval)
        elif repeat_type == 'monthly':
            next_time = current_time + timedelta(days=30 * interval)  # Approximation
        
        if next_time:
            # Créer la prochaine occurrence
            next_announcement = announcement.copy()
            next_announcement['scheduled_time'] = next_time.isoformat()
            next_announcement['is_sent'] = False
            
            self.db.schedule_announcement(
                announcement['guild_id'],
                next_announcement,
                announcement['created_by']
            )


# =============================================================================
# VUES DISCORD UI POUR LA GESTION DES ANNONCES
# =============================================================================

class AnnouncementsSetupView(discord.ui.View):
    """Vue principale de gestion des annonces"""
    
    def __init__(self, guild_id: int, db: AnnouncementsDB):
        super().__init__(timeout=600)
        self.guild_id = guild_id
        self.db = db
    
    @discord.ui.button(label="📢 Nouvelle Annonce", style=discord.ButtonStyle.success, emoji="📢")
    async def new_announcement(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CreateAnnouncementModal(self.guild_id, self.db)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📝 Créer Template", style=discord.ButtonStyle.primary, emoji="📝")
    async def create_template(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CreateTemplateModal(self.guild_id, self.db)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 Mes Templates", style=discord.ButtonStyle.secondary, emoji="📋")
    async def list_templates(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._show_templates(interaction)
    
    @discord.ui.button(label="⚙️ Configuration", style=discord.ButtonStyle.secondary, emoji="⚙️")
    async def configure(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AnnouncementConfigModal(self.guild_id, self.db)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📊 Statistiques", style=discord.ButtonStyle.secondary, emoji="📊")
    async def show_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._show_stats(interaction)
    
    async def _show_templates(self, interaction: discord.Interaction):
        """Affiche tous les templates du serveur"""
        templates = self.db.get_templates(self.guild_id)
        
        embed = discord.Embed(
            title="📝 Templates d'Annonces",
            color=0x3366FF
        )
        
        if not templates:
            embed.description = "Aucun template créé. Utilisez le bouton **Créer Template** pour commencer."
        else:
            for template in templates[:10]:
                type_emoji = {
                    'embed': '📊',
                    'text': '📝',
                    'mixed': '🎭'
                }.get(template['template_type'], '📋')
                
                embed.add_field(
                    name=f"{type_emoji} {template['template_name']}",
                    value=f"**Type:** {template['template_type']}\n"
                          f"**Créé:** {template['created_at'][:10]}\n"
                          f"**ID:** {template['id']}",
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def _show_stats(self, interaction: discord.Interaction):
        """Affiche les statistiques des annonces"""
        stats = self.db.get_guild_stats(self.guild_id)
        config = self.db.get_guild_config(self.guild_id)
        
        embed = discord.Embed(
            title="📊 Statistiques des Annonces",
            color=0xFFD700
        )
        
        if stats:
            embed.add_field(
                name="📈 Annonces Envoyées",
                value=f"**Total:** {stats['total_sent']}\n"
                      f"**Aujourd'hui:** {stats['sent_today']}\n"
                      f"**Cette semaine:** {stats['sent_this_week']}\n"
                      f"**Ce mois:** {stats['sent_this_month']}",
                inline=True
            )
            
            embed.add_field(
                name="📋 Templates & Config",
                value=f"**Templates créés:** {stats['templates_created']}\n"
                      f"**Réactions moyennes:** {stats['avg_reactions']:.1f}\n"
                      f"**Dernière annonce:** {stats['last_announcement'][:16] if stats['last_announcement'] else 'Aucune'}",
                inline=True
            )
        else:
            embed.description = "Aucune statistique disponible. Envoyez votre première annonce !"
        
        if config:
            default_channel = interaction.guild.get_channel(config['default_channel_id']) if config['default_channel_id'] else None
            
            embed.add_field(
                name="⚙️ Configuration Actuelle",
                value=f"**Canal par défaut:** {default_channel.mention if default_channel else 'Non défini'}\n"
                      f"**Limite quotidienne:** {config['max_daily_announcements']}\n"
                      f"**Approbation requise:** {'Oui' if config['require_approval'] else 'Non'}\n"
                      f"**Réactions auto:** {'Activées' if config['enable_auto_reactions'] else 'Désactivées'}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


# =============================================================================
# MODALS POUR LA CRÉATION D'ANNONCES
# =============================================================================

class CreateAnnouncementModal(discord.ui.Modal):
    """Modal pour créer une nouvelle annonce"""
    
    def __init__(self, guild_id: int, db: AnnouncementsDB):
        super().__init__(title="📢 Nouvelle Annonce", timeout=300)
        self.guild_id = guild_id
        self.db = db
        
        self.title_input = discord.ui.TextInput(
            label="Titre de l'annonce",
            placeholder="ex: Mise à jour importante du serveur",
            max_length=100,
            required=True
        )
        
        self.content_input = discord.ui.TextInput(
            label="Contenu de l'annonce",
            placeholder="Votre message d'annonce...",
            style=discord.TextStyle.long,
            max_length=1500,
            required=True
        )
        
        self.channels_input = discord.ui.TextInput(
            label="IDs des canaux (séparés par des espaces)",
            placeholder="123456789 987654321",
            max_length=200,
            required=True
        )
        
        self.mentions_input = discord.ui.TextInput(
            label="Mentions (@everyone, @here, IDs rôles/users)",
            placeholder="@everyone ou 123456789 (optionnel)",
            max_length=200,
            required=False
        )
        
        self.schedule_input = discord.ui.TextInput(
            label="Programmer (YYYY-MM-DD HH:MM ou 'now')",
            placeholder="2024-12-31 15:30 ou now",
            max_length=20,
            default="now",
            required=False
        )
        
        self.add_item(self.title_input)
        self.add_item(self.content_input)
        self.add_item(self.channels_input)
        self.add_item(self.mentions_input)
        self.add_item(self.schedule_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Parser les canaux
            channel_ids = [int(cid) for cid in self.channels_input.value.split()]
            
            # Vérifier que les canaux existent
            valid_channels = []
            for channel_id in channel_ids:
                channel = interaction.guild.get_channel(channel_id)
                if channel:
                    valid_channels.append(channel_id)
            
            if not valid_channels:
                raise ValueError("Aucun canal valide trouvé")
            
            # Parser les mentions
            mentions = await self._parse_mentions(self.mentions_input.value, interaction.guild)
            
            # Parser la programmation
            if self.schedule_input.value.lower() == "now":
                scheduled_time = datetime.now(timezone.utc)
            else:
                # Format YYYY-MM-DD HH:MM
                scheduled_time = datetime.strptime(self.schedule_input.value, "%Y-%m-%d %H:%M")
                scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
            
            # Créer l'embed par défaut
            embed_data = {
                'title': self.title_input.value,
                'description': self.content_input.value,
                'color': 3447003,
                'add_timestamp': True
            }
            
            # Données de l'annonce
            announcement_data = {
                'announcement_title': self.title_input.value,
                'announcement_content': self.content_input.value,
                'target_channels': valid_channels,
                'mentions': mentions,
                'embed_data': embed_data,
                'scheduled_time': scheduled_time.isoformat()
            }
            
            # Programmer l'annonce
            scheduled_id = self.db.schedule_announcement(
                self.guild_id,
                announcement_data,
                interaction.user.id
            )
            
            if scheduled_id:
                embed = discord.Embed(
                    title="✅ Annonce Programmée",
                    description=f"Votre annonce **{self.title_input.value}** a été programmée avec succès !",
                    color=0x00FF88
                )
                
                channels_mentions = []
                for channel_id in valid_channels:
                    channel = interaction.guild.get_channel(channel_id)
                    if channel:
                        channels_mentions.append(channel.mention)
                
                embed.add_field(
                    name="📋 Détails",
                    value=f"**Canaux:** {', '.join(channels_mentions)}\n"
                          f"**Programmé pour:** {scheduled_time.strftime('%d/%m/%Y à %H:%M')}\n"
                          f"**ID:** {scheduled_id}",
                    inline=False
                )
                
                if scheduled_time <= datetime.now(timezone.utc) + timedelta(minutes=1):
                    embed.add_field(
                        name="⚡ Envoi Immédiat",
                        value="Votre annonce sera envoyée dans les prochaines secondes.",
                        inline=False
                    )
                
            else:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Une erreur s'est produite lors de la programmation.",
                    color=0xFF0000
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError as e:
            embed = discord.Embed(
                title="❌ Erreur de Format",
                description=f"Erreur: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur inattendue s'est produite: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def _parse_mentions(self, mentions_text: str, guild: discord.Guild) -> Dict[str, Any]:
        """Parse le texte des mentions"""
        mentions = {}
        
        if not mentions_text:
            return mentions
        
        if "@everyone" in mentions_text.lower():
            mentions['everyone'] = True
        elif "@here" in mentions_text.lower():
            mentions['here'] = True
        
        # Chercher des IDs de rôles/utilisateurs
        ids = re.findall(r'\d{17,19}', mentions_text)
        
        role_ids = []
        user_ids = []
        
        for id_str in ids:
            id_int = int(id_str)
            
            # Vérifier si c'est un rôle
            role = guild.get_role(id_int)
            if role:
                role_ids.append(id_int)
                continue
            
            # Vérifier si c'est un utilisateur
            member = guild.get_member(id_int)
            if member:
                user_ids.append(id_int)
        
        if role_ids:
            mentions['roles'] = role_ids
        if user_ids:
            mentions['users'] = user_ids
        
        return mentions


class CreateTemplateModal(discord.ui.Modal):
    """Modal pour créer un template d'annonce"""
    
    def __init__(self, guild_id: int, db: AnnouncementsDB):
        super().__init__(title="📝 Créer un Template", timeout=300)
        self.guild_id = guild_id
        self.db = db
        
        self.name_input = discord.ui.TextInput(
            label="Nom du template",
            placeholder="ex: Annonce événement",
            max_length=50,
            required=True
        )
        
        self.type_input = discord.ui.TextInput(
            label="Type (embed, text, mixed)",
            placeholder="embed",
            max_length=10,
            default="embed",
            required=True
        )
        
        self.title_input = discord.ui.TextInput(
            label="Titre par défaut",
            placeholder="Titre de l'embed",
            max_length=100,
            required=False
        )
        
        self.content_input = discord.ui.TextInput(
            label="Contenu template",
            placeholder="Contenu avec variables: {title}, {content}",
            style=discord.TextStyle.long,
            max_length=1000,
            required=False
        )
        
        self.color_input = discord.ui.TextInput(
            label="Couleur (hex sans #)",
            placeholder="3366FF",
            max_length=6,
            default="3366FF",
            required=False
        )
        
        self.add_item(self.name_input)
        self.add_item(self.type_input)
        self.add_item(self.title_input)
        self.add_item(self.content_input)
        self.add_item(self.color_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            template_type = self.type_input.value.lower()
            if template_type not in ['embed', 'text', 'mixed']:
                raise ValueError("Type de template invalide")
            
            # Convertir la couleur
            try:
                color = int(self.color_input.value, 16)
            except ValueError:
                color = 3447003  # Couleur par défaut
            
            # Données du template
            template_data = {
                'template_name': self.name_input.value,
                'template_type': template_type,
                'embed_data': {
                    'title': self.title_input.value,
                    'description': self.content_input.value,
                    'color': color,
                    'add_timestamp': True
                },
                'content_template': self.content_input.value,
                'color': color
            }
            
            # Créer le template
            template_id = self.db.create_template(self.guild_id, template_data)
            
            if template_id:
                embed = discord.Embed(
                    title="✅ Template Créé",
                    description=f"Le template **{self.name_input.value}** a été créé avec succès !",
                    color=0x00FF88
                )
                
                embed.add_field(
                    name="📋 Détails",
                    value=f"**Type:** {template_type}\n"
                          f"**Couleur:** #{self.color_input.value}\n"
                          f"**ID:** {template_id}",
                    inline=False
                )
            else:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Erreur lors de la création du template.",
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


class AnnouncementConfigModal(discord.ui.Modal):
    """Modal pour configurer les paramètres d'annonces"""
    
    def __init__(self, guild_id: int, db: AnnouncementsDB):
        super().__init__(title="⚙️ Configuration Annonces", timeout=300)
        self.guild_id = guild_id
        self.db = db
        
        # Récupérer la config actuelle
        config = db.get_guild_config(guild_id) or {}
        
        self.default_channel_input = discord.ui.TextInput(
            label="Canal par défaut (ID)",
            placeholder="123456789",
            default=str(config.get('default_channel_id', '')),
            max_length=20,
            required=False
        )
        
        self.max_daily_input = discord.ui.TextInput(
            label="Limite quotidienne d'annonces",
            placeholder="5",
            default=str(config.get('max_daily_announcements', 5)),
            max_length=3,
            required=False
        )
        
        self.moderator_role_input = discord.ui.TextInput(
            label="Rôle modérateur (ID)",
            placeholder="123456789",
            default=str(config.get('moderator_role_id', '')),
            max_length=20,
            required=False
        )
        
        self.auto_reactions_input = discord.ui.TextInput(
            label="Réactions automatiques",
            placeholder="👍 👎 ❤️ (séparées par espaces)",
            default=" ".join(config.get('auto_reactions', [])),
            max_length=50,
            required=False
        )
        
        self.add_item(self.default_channel_input)
        self.add_item(self.max_daily_input)
        self.add_item(self.moderator_role_input)
        self.add_item(self.auto_reactions_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            config = {}
            
            # Canal par défaut
            if self.default_channel_input.value:
                channel_id = int(self.default_channel_input.value)
                channel = interaction.guild.get_channel(channel_id)
                if channel:
                    config['default_channel_id'] = channel_id
            
            # Limite quotidienne
            if self.max_daily_input.value:
                config['max_daily_announcements'] = int(self.max_daily_input.value)
            
            # Rôle modérateur
            if self.moderator_role_input.value:
                role_id = int(self.moderator_role_input.value)
                role = interaction.guild.get_role(role_id)
                if role:
                    config['moderator_role_id'] = role_id
            
            # Réactions automatiques
            auto_reactions = []
            if self.auto_reactions_input.value:
                reactions = self.auto_reactions_input.value.split()
                auto_reactions = [r for r in reactions if r]
                config['enable_auto_reactions'] = len(auto_reactions) > 0
            
            config['auto_reactions'] = auto_reactions
            
            # Sauvegarder
            success = self.db.save_guild_config(self.guild_id, config)
            
            if success:
                embed = discord.Embed(
                    title="✅ Configuration Mise à Jour",
                    description="Les paramètres d'annonces ont été sauvegardés avec succès !",
                    color=0x00FF88
                )
                
                config_details = []
                if config.get('default_channel_id'):
                    channel = interaction.guild.get_channel(config['default_channel_id'])
                    config_details.append(f"**Canal par défaut:** {channel.mention}")
                
                if config.get('max_daily_announcements'):
                    config_details.append(f"**Limite quotidienne:** {config['max_daily_announcements']}")
                
                if config.get('moderator_role_id'):
                    role = interaction.guild.get_role(config['moderator_role_id'])
                    config_details.append(f"**Rôle modérateur:** {role.mention}")
                
                if config.get('auto_reactions'):
                    config_details.append(f"**Réactions auto:** {' '.join(config['auto_reactions'])}")
                
                if config_details:
                    embed.add_field(
                        name="⚙️ Configuration",
                        value="\n".join(config_details),
                        inline=False
                    )
                
            else:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Erreur lors de la sauvegarde.",
                    color=0xFF0000
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError as e:
            embed = discord.Embed(
                title="❌ Erreur de Format",
                description=f"Vérifiez les valeurs saisies: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


# =============================================================================
# COMMANDES PRINCIPALES DU SYSTÈME D'ANNONCES
# =============================================================================

class AnnouncementsSystem(commands.Cog):
    """📢 Système modulaire d'annonces Arsenal"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = AnnouncementsDB()
        self.manager = AnnouncementManager(bot, self.db)
        
        # Démarrer la tâche d'envoi des annonces programmées
        self.send_scheduled_announcements.start()
    
    def cog_unload(self):
        self.send_scheduled_announcements.cancel()
    
    @app_commands.command(name="announcements", description="📢 Système de gestion des annonces")
    @app_commands.describe(action="Action à effectuer")
    @app_commands.choices(action=[
        app_commands.Choice(name="setup - Configuration générale", value="setup"),
        app_commands.Choice(name="create - Nouvelle annonce", value="create"),
        app_commands.Choice(name="template - Créer un template", value="template"),
        app_commands.Choice(name="config - Configuration serveur", value="config"),
        app_commands.Choice(name="stats - Statistiques", value="stats")
    ])
    async def announcements(self, interaction: discord.Interaction, action: str = "setup"):
        """Commande principale de gestion des annonces"""
        
        # Vérifier les permissions
        if not (interaction.user.guild_permissions.manage_messages or 
                interaction.user.guild_permissions.administrator):
            
            # Vérifier le rôle modérateur configuré
            config = self.db.get_guild_config(interaction.guild_id)
            if config and config.get('moderator_role_id'):
                mod_role = interaction.guild.get_role(config['moderator_role_id'])
                if not (mod_role and mod_role in interaction.user.roles):
                    embed = discord.Embed(
                        title="❌ Permissions Insuffisantes",
                        description="Vous n'avez pas les permissions pour utiliser cette commande.",
                        color=0xFF0000
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            else:
                embed = discord.Embed(
                    title="❌ Permissions Insuffisantes",
                    description="Seuls les membres avec la permission **Gérer les messages** peuvent utiliser cette commande.",
                    color=0xFF0000
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        if action == "setup":
            await self.setup_announcements(interaction)
        elif action == "create":
            modal = CreateAnnouncementModal(interaction.guild_id, self.db)
            await interaction.response.send_modal(modal)
        elif action == "template":
            modal = CreateTemplateModal(interaction.guild_id, self.db)
            await interaction.response.send_modal(modal)
        elif action == "config":
            modal = AnnouncementConfigModal(interaction.guild_id, self.db)
            await interaction.response.send_modal(modal)
        elif action == "stats":
            view = AnnouncementsSetupView(interaction.guild_id, self.db)
            await view._show_stats(interaction)
    
    async def setup_announcements(self, interaction: discord.Interaction):
        """Configuration initiale des annonces"""
        embed = discord.Embed(
            title="📢 Système d'Annonces Arsenal",
            description="""
**Le système d'annonces le plus complet pour votre serveur !**

🎯 **Fonctionnalités principales :**
• **Annonces instantanées** - Envoi immédiat multi-canaux
• **Programmation avancée** - Planifiez vos annonces
• **Templates personnalisables** - Créez des modèles réutilisables
• **Mentions intelligentes** - @everyone, rôles, utilisateurs
• **Répétition automatique** - Annonces récurrentes
• **Statistiques détaillées** - Suivi complet des envois

📋 **Types d'annonces :**
• **Embed** - Annonces avec mise en forme riche
• **Texte** - Messages texte simples
• **Mixte** - Combinaison embed + texte

⚙️ **Options avancées :**
• **Approbation** - Validation par les modérateurs
• **Limites quotidiennes** - Contrôle des envois
• **Réactions automatiques** - Ajout d'emojis
• **Logs complets** - Historique détaillé

Créez votre première annonce maintenant !
            """,
            color=0xFF6600
        )
        
        view = AnnouncementsSetupView(interaction.guild_id, self.db)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @tasks.loop(minutes=1)
    async def send_scheduled_announcements(self):
        """Tâche d'envoi des annonces programmées"""
        try:
            pending_announcements = self.db.get_pending_announcements()
            
            for announcement in pending_announcements:
                success = await self.manager.send_announcement(announcement)
                
                if success:
                    logger.info(f"Annonce {announcement['id']} envoyée avec succès")
                else:
                    logger.warning(f"Échec envoi annonce {announcement['id']}")
                
                # Petit délai entre les envois
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Erreur tâche annonces programmées: {e}")
    
    @send_scheduled_announcements.before_loop
    async def before_send_scheduled_announcements(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    """Setup function pour charger le système d'annonces"""
    await bot.add_cog(AnnouncementsSystem(bot))
    logger.info("📢 Système d'Annonces Arsenal chargé avec succès!")
    print("✅ Announcements System - Système modulaire prêt!")
    print("📢 Types: Embed, Text, Mixed")
    print("📋 Commande: /announcements [setup|create|template|config|stats]")

