"""
🛡️ ARSENAL REGLEMENT SYSTEM V2.0
Système modulaire de règlement et gestion des règles

Fonctionnalités:
- Création/modification règlement interactif
- Système de validation par réaction
- Templates de règlement prédéfinis  
- Gestion multi-langues
- Integration avec modération

Author: Arsenal Bot Team
Version: 2.0.0
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import sqlite3
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# BASE DE DONNÉES RÈGLEMENT
# =============================================================================

class ReglementDB:
    """Gestionnaire de base de données pour le système de règlement"""
    
    def __init__(self, db_path: str = "arsenal_reglement.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des règlements par serveur
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS server_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER,
                    message_id INTEGER,
                    title TEXT NOT NULL DEFAULT "📋 Règlement du Serveur",
                    language TEXT DEFAULT "fr",
                    template_used TEXT DEFAULT "general",
                    rules_content TEXT NOT NULL,
                    acceptance_required BOOLEAN DEFAULT TRUE,
                    acceptance_emoji TEXT DEFAULT "✅",
                    acceptance_role_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    UNIQUE(guild_id)
                )
            ''')
            
            # Table des acceptations utilisateur
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rules_acceptances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    accepted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    rules_version INTEGER DEFAULT 1,
                    ip_address TEXT,
                    user_agent TEXT,
                    UNIQUE(guild_id, user_id)
                )
            ''')
            
            # Table des templates de règlement
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rules_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_name TEXT UNIQUE NOT NULL,
                    language TEXT DEFAULT "fr",
                    title TEXT NOT NULL,
                    rules_content TEXT NOT NULL,
                    description TEXT,
                    category TEXT DEFAULT "general",
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def get_server_rules(self, guild_id: int) -> Optional[Dict[str, Any]]:
        """Récupère le règlement d'un serveur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM server_rules WHERE guild_id = ? AND is_active = TRUE
            ''', (guild_id,))
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def save_server_rules(self, guild_id: int, rules_data: Dict[str, Any]) -> bool:
        """Sauvegarde le règlement d'un serveur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO server_rules 
                    (guild_id, channel_id, message_id, title, language, template_used, 
                     rules_content, acceptance_required, acceptance_emoji, acceptance_role_id, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    guild_id,
                    rules_data.get('channel_id'),
                    rules_data.get('message_id'),
                    rules_data.get('title', '📋 Règlement du Serveur'),
                    rules_data.get('language', 'fr'),
                    rules_data.get('template_used', 'custom'),
                    rules_data.get('rules_content', ''),
                    rules_data.get('acceptance_required', True),
                    rules_data.get('acceptance_emoji', '✅'),
                    rules_data.get('acceptance_role_id')
                ))
                
                conn.commit()
                return True
                
            except Exception as e:
                logger.error(f"Erreur sauvegarde règlement {guild_id}: {e}")
                return False
    
    def accept_rules(self, guild_id: int, user_id: int) -> bool:
        """Enregistre l'acceptation des règles par un utilisateur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO rules_acceptances (guild_id, user_id, accepted_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (guild_id, user_id))
                
                conn.commit()
                return True
                
            except Exception as e:
                logger.error(f"Erreur acceptation règles {guild_id}/{user_id}: {e}")
                return False
    
    def has_accepted_rules(self, guild_id: int, user_id: int) -> bool:
        """Vérifie si un utilisateur a accepté les règles"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id FROM rules_acceptances WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id))
            
            return cursor.fetchone() is not None
    
    def get_acceptance_stats(self, guild_id: int) -> Dict[str, int]:
        """Statistiques d'acceptation des règles"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM rules_acceptances WHERE guild_id = ?
            ''', (guild_id,))
            total_acceptances = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM rules_acceptances 
                WHERE guild_id = ? AND DATE(accepted_at) = DATE('now')
            ''', (guild_id,))
            today_acceptances = cursor.fetchone()[0]
            
            return {
                'total_acceptances': total_acceptances,
                'today_acceptances': today_acceptances
            }


# =============================================================================
# TEMPLATES DE RÈGLEMENT PRÉDÉFINIS
# =============================================================================

REGLEMENT_TEMPLATES = {
    "general": {
        "title": "📋 Règlement Général du Serveur",
        "description": "Règlement standard pour serveurs communautaires",
        "content": """
**📋 RÈGLEMENT DU SERVEUR**

**🔸 Article 1 - Respect et Courtoisie**
• Respectez tous les membres du serveur
• Pas d'insultes, de harcèlement ou de discrimination  
• Soyez bienveillant dans vos interactions

**🔸 Article 2 - Contenu Approprié**
• Pas de contenu NSFW, violent ou choquant
• Pas de spam ou de flood
• Utilisez les salons appropriés pour vos messages

**🔸 Article 3 - Pseudonymes et Avatars**
• Pseudonyme lisible et approprié
• Avatar décent (pas de contenu inapproprié)
• Pas d'usurpation d'identité

**🔸 Article 4 - Publicité et Liens**
• Pas de publicité non autorisée
• Demandez l'autorisation avant de partager des liens
• Pas d'invitation vers d'autres serveurs

**🔸 Article 5 - Sanctions**
• Les infractions peuvent entraîner des sanctions
• Avertissement → Mute temporaire → Ban temporaire → Ban permanent
• Les sanctions sont à la discrétion de l'équipe de modération

**✅ En réagissant avec ✅, vous acceptez ce règlement**

*Dernière mise à jour: {date}*
        """
    },
    
    "gaming": {
        "title": "🎮 Règlement Serveur Gaming",
        "description": "Règlement spécialisé pour serveurs de jeu",
        "content": """
**🎮 RÈGLEMENT SERVEUR GAMING**

**🔸 Article 1 - Fair-Play**
• Jouez de manière équitable et sportive
• Pas de triche, hack ou exploitation de bugs
• Respectez vos adversaires et coéquipiers

**🔸 Article 2 - Communication Vocale**
• Utilisez un micro de qualité correcte
• Pas de musique ou bruits parasites
• Respectez les autres joueurs en vocal

**🔸 Article 3 - Organisation d'Équipes**
• Respectez les créneaux et horaires fixés
• Prévenez en cas d'absence
• Pas de rage quit ou abandon d'équipe

**🔸 Article 4 - Contenu Gaming**
• Partagez vos exploits dans les salons dédiés
• Pas de spoil sans avertissement
• Aidez les nouveaux joueurs

**🔸 Article 5 - Comportement en Jeu**
• Pas de comportement toxique
• Acceptez les défaites avec fair-play
• Encouragez l'esprit d'équipe

**✅ En réagissant avec ✅, vous acceptez ce règlement**

*Bon gaming à tous ! 🎮*
        """
    },
    
    "business": {
        "title": "💼 Règlement Serveur Professionnel",
        "description": "Règlement pour serveurs d'entreprise/travail",
        "content": """
**💼 RÈGLEMENT SERVEUR PROFESSIONNEL**

**🔸 Article 1 - Professionnalisme**
• Maintenez un langage professionnel
• Respectez les horaires de travail
• Soyez constructif dans vos échanges

**🔸 Article 2 - Confidentialité**
• Respectez la confidentialité des informations
• Pas de partage de données sensibles
• Utilisez les canaux appropriés selon le niveau de confidentialité

**🔸 Article 3 - Organisation du Travail**
• Utilisez les bons salons pour chaque sujet
• Respectez les deadlines et engagements
• Communiquez clairement sur l'avancement des projets

**🔸 Article 4 - Réunions et Vocal**
• Coupez votre micro quand vous ne parlez pas
• Soyez ponctuel aux réunions
• Préparez vos interventions à l'avance

**🔸 Article 5 - Support et Entraide**
• Aidez vos collègues quand possible
• Documentez vos processus
• Partagez les bonnes pratiques

**✅ En réagissant avec ✅, vous acceptez ce règlement**

*Travaillons ensemble efficacement ! 💼*
        """
    },
    
    "community": {
        "title": "🌟 Règlement Communauté",
        "description": "Règlement pour serveurs communautaires diversifiés",
        "content": """
**🌟 RÈGLEMENT DE LA COMMUNAUTÉ**

**🔸 Article 1 - Bienveillance**
• Accueillez chaleureusement les nouveaux membres
• Aidez et soutenez la communauté
• Créez un environnement positif et inclusif

**🔸 Article 2 - Diversité et Inclusion**
• Respectez toutes les identités et orientations
• Pas de discrimination sous aucune forme
• Valorisez la richesse de notre diversité

**🔸 Article 3 - Participation Active**
• Participez aux événements communautaires
• Proposez des idées et initiatives
• Contribuez à l'animation du serveur

**🔸 Article 4 - Partage et Création**
• Partagez vos créations et talents
• Respectez les droits d'auteur
• Encouragez la créativité de chacun

**🔸 Article 5 - Résolution de Conflits**
• Privilégiez le dialogue en cas de désaccord
• Contactez la modération si nécessaire
• Gardez un esprit constructif

**✅ En réagissant avec ✅, vous acceptez ce règlement**

*Ensemble, construisons une communauté extraordinaire ! 🌟*
        """
    }
}


# =============================================================================
# VUES DISCORD UI POUR LE RÈGLEMENT
# =============================================================================

class ReglementSetupView(discord.ui.View):
    """Vue principale pour configurer le règlement"""
    
    def __init__(self, guild_id: int, db: ReglementDB):
        super().__init__(timeout=600)
        self.guild_id = guild_id
        self.db = db
    
    @discord.ui.button(label="📝 Créer Règlement", style=discord.ButtonStyle.primary, emoji="📝")
    async def create_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CreateReglementModal(self.guild_id, self.db)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 Templates", style=discord.ButtonStyle.secondary, emoji="📋")
    async def show_templates(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = TemplateSelectionView(self.guild_id, self.db)
        embed = discord.Embed(
            title="📋 Templates de Règlement",
            description="Choisissez un template prédéfini pour votre serveur",
            color=0x3366FF
        )
        
        for template_name, template_data in REGLEMENT_TEMPLATES.items():
            embed.add_field(
                name=f"📄 {template_data['title']}",
                value=template_data['description'],
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="🎨 Personnaliser", style=discord.ButtonStyle.success, emoji="🎨")
    async def customize_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CustomReglementModal(self.guild_id, self.db)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="⚙️ Configuration", style=discord.ButtonStyle.secondary, emoji="⚙️")
    async def configure_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        rules = self.db.get_server_rules(self.guild_id)
        if not rules:
            embed = discord.Embed(
                title="❌ Aucun Règlement",
                description="Créez d'abord un règlement avant de le configurer.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        modal = ConfigureReglementModal(self.guild_id, self.db, rules)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📊 Statistiques", style=discord.ButtonStyle.success, emoji="📊")
    async def show_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        stats = self.db.get_acceptance_stats(self.guild_id)
        rules = self.db.get_server_rules(self.guild_id)
        
        embed = discord.Embed(
            title="📊 Statistiques du Règlement",
            color=0x00FF88
        )
        
        if rules:
            embed.add_field(
                name="📋 Règlement Actuel",
                value=f"**Titre:** {rules['title']}\n"
                      f"**Template:** {rules['template_used']}\n"
                      f"**Dernière MAJ:** {rules['updated_at'][:10]}",
                inline=True
            )
        
        embed.add_field(
            name="✅ Acceptations",
            value=f"**Total:** {stats['total_acceptances']}\n"
                  f"**Aujourd'hui:** {stats['today_acceptances']}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class TemplateSelectionView(discord.ui.View):
    """Vue pour sélectionner un template de règlement"""
    
    def __init__(self, guild_id: int, db: ReglementDB):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.db = db
    
    @discord.ui.select(
        placeholder="Choisissez un template de règlement...",
        options=[
            discord.SelectOption(
                label="Règlement Général",
                description="Template standard pour serveurs communautaires",
                value="general",
                emoji="📋"
            ),
            discord.SelectOption(
                label="Serveur Gaming",
                description="Spécialisé pour les serveurs de jeu",
                value="gaming",
                emoji="🎮"
            ),
            discord.SelectOption(
                label="Serveur Business",
                description="Pour environnements professionnels",
                value="business",
                emoji="💼"
            ),
            discord.SelectOption(
                label="Communauté",
                description="Pour communautés diversifiées et inclusives",
                value="community",
                emoji="🌟"
            )
        ]
    )
    async def template_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        template_name = select.values[0]
        template = REGLEMENT_TEMPLATES[template_name]
        
        # Préparation du contenu avec la date
        content = template["content"].format(date=datetime.now().strftime("%d/%m/%Y"))
        
        embed = discord.Embed(
            title="📋 Aperçu du Template",
            description=f"**Template sélectionné:** {template['title']}",
            color=0x3366FF
        )
        
        # Afficher un extrait du règlement
        content_preview = content[:1000] + "..." if len(content) > 1000 else content
        embed.add_field(
            name="📄 Contenu (aperçu)",
            value=f"```{content_preview}```",
            inline=False
        )
        
        view = ConfirmTemplateView(self.guild_id, self.db, template_name, template, content)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class ConfirmTemplateView(discord.ui.View):
    """Vue de confirmation pour appliquer un template"""
    
    def __init__(self, guild_id: int, db: ReglementDB, template_name: str, template_data: dict, content: str):
        super().__init__(timeout=180)
        self.guild_id = guild_id
        self.db = db
        self.template_name = template_name
        self.template_data = template_data
        self.content = content
    
    @discord.ui.button(label="✅ Appliquer ce Template", style=discord.ButtonStyle.success, emoji="✅")
    async def apply_template(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Sauvegarder le règlement avec le template
        rules_data = {
            'title': self.template_data['title'],
            'template_used': self.template_name,
            'rules_content': self.content,
            'language': 'fr',
            'acceptance_required': True,
            'acceptance_emoji': '✅'
        }
        
        success = self.db.save_server_rules(self.guild_id, rules_data)
        
        if success:
            embed = discord.Embed(
                title="✅ Template Appliqué",
                description=f"Le template **{self.template_data['title']}** a été appliqué avec succès !",
                color=0x00FF88
            )
            embed.add_field(
                name="📋 Prochaines étapes",
                value="• Utilisez `/reglement publish` pour publier le règlement\n"
                      "• Configurez le salon et les rôles d'acceptation\n"
                      "• Personnalisez le contenu si nécessaire",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Une erreur s'est produite lors de l'application du template.",
                color=0xFF0000
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔄 Choisir un autre", style=discord.ButtonStyle.secondary, emoji="🔄")
    async def back_to_selection(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = TemplateSelectionView(self.guild_id, self.db)
        embed = discord.Embed(
            title="📋 Templates de Règlement",
            description="Choisissez un template prédéfini pour votre serveur",
            color=0x3366FF
        )
        
        for template_name, template_data in REGLEMENT_TEMPLATES.items():
            embed.add_field(
                name=f"📄 {template_data['title']}",
                value=template_data['description'],
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# =============================================================================
# MODALS POUR LA CRÉATION/CONFIGURATION
# =============================================================================

class CreateReglementModal(discord.ui.Modal):
    """Modal pour créer un règlement personnalisé"""
    
    def __init__(self, guild_id: int, db: ReglementDB):
        super().__init__(title="📝 Créer un Règlement Personnalisé", timeout=600)
        self.guild_id = guild_id
        self.db = db
        
        self.title_input = discord.ui.TextInput(
            label="Titre du règlement",
            placeholder="📋 Règlement du Serveur",
            max_length=100,
            required=True
        )
        
        self.content_input = discord.ui.TextInput(
            label="Contenu du règlement",
            placeholder="Rédigez ici le contenu de votre règlement...\nUtilisez le markdown Discord pour le formatage.",
            style=discord.TextStyle.long,
            max_length=2000,
            required=True
        )
        
        self.add_item(self.title_input)
        self.add_item(self.content_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        rules_data = {
            'title': self.title_input.value,
            'template_used': 'custom',
            'rules_content': self.content_input.value,
            'language': 'fr',
            'acceptance_required': True,
            'acceptance_emoji': '✅'
        }
        
        success = self.db.save_server_rules(self.guild_id, rules_data)
        
        if success:
            embed = discord.Embed(
                title="✅ Règlement Créé",
                description=f"Le règlement **{self.title_input.value}** a été créé avec succès !",
                color=0x00FF88
            )
            embed.add_field(
                name="📋 Prochaines étapes",
                value="• Utilisez `/reglement publish` pour publier le règlement\n"
                      "• Configurez le salon et les rôles d'acceptation\n"
                      "• Testez le système d'acceptation",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Une erreur s'est produite lors de la création du règlement.",
                color=0xFF0000
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class CustomReglementModal(discord.ui.Modal):
    """Modal pour créer un règlement personnalisé"""
    
    def __init__(self, guild_id: int, db: ReglementDB):
        super().__init__(title="🎨 Règlement Personnalisé", timeout=300)
        self.guild_id = guild_id
        self.db = db
        
        self.title_input = discord.ui.TextInput(
            label="Titre du règlement",
            placeholder="Règlement du serveur Discord",
            max_length=100,
            required=True
        )
        
        self.content_input = discord.ui.TextInput(
            label="Contenu du règlement",
            placeholder="1. Respectez les autres membres...\n2. Pas de spam...\n3. Utilisez les bons salons...",
            style=discord.TextStyle.long,
            max_length=2000,
            required=True
        )
        
        self.color_input = discord.ui.TextInput(
            label="Couleur (hex sans #)",
            placeholder="3366FF",
            default="3366FF",
            max_length=6,
            required=False
        )
        
        self.emoji_input = discord.ui.TextInput(
            label="Emoji d'acceptation",
            placeholder="✅",
            default="✅",
            max_length=10,
            required=False
        )
        
        self.role_input = discord.ui.TextInput(
            label="ID du rôle à attribuer (optionnel)",
            placeholder="Laissez vide pour aucun rôle",
            max_length=20,
            required=False
        )
        
        self.add_item(self.title_input)
        self.add_item(self.content_input)
        self.add_item(self.color_input)
        self.add_item(self.emoji_input)
        self.add_item(self.role_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Convertir la couleur
            try:
                color = int(self.color_input.value, 16) if self.color_input.value else 0x3366FF
            except ValueError:
                color = 0x3366FF
            
            # Vérifier le rôle
            role_id = None
            if self.role_input.value:
                try:
                    role_id = int(self.role_input.value)
                    role = interaction.guild.get_role(role_id)
                    if not role:
                        raise ValueError("Rôle introuvable")
                except ValueError:
                    embed = discord.Embed(
                        title="❌ Erreur de Rôle",
                        description="L'ID du rôle n'est pas valide ou le rôle n'existe pas.",
                        color=0xFF0000
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            
            # Créer les données du règlement
            rules_data = {
                'title': self.title_input.value,
                'content': self.content_input.value,
                'color': color,
                'acceptance_emoji': self.emoji_input.value or '✅',
                'acceptance_role_id': role_id,
                'custom_rules': True,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Sauvegarder le règlement
            success = self.db.save_server_rules(self.guild_id, rules_data)
            
            if success:
                embed = discord.Embed(
                    title="✅ Règlement Personnalisé Créé",
                    description=f"Votre règlement **{self.title_input.value}** a été créé avec vos préférences !",
                    color=color
                )
                
                embed.add_field(
                    name="🎨 Personnalisations",
                    value=f"**Couleur:** #{self.color_input.value or '3366FF'}\n"
                          f"**Emoji:** {self.emoji_input.value or '✅'}\n"
                          f"**Rôle:** {'Configuré' if role_id else 'Aucun'}",
                    inline=True
                )
                
                embed.add_field(
                    name="📋 Prochaines étapes",
                    value="• Utilisez `/reglement publish` pour publier\n"
                          "• Le règlement est prêt à l'emploi\n"
                          "• Modifiable à tout moment",
                    inline=False
                )
                
                # Aperçu du règlement
                preview_embed = discord.Embed(
                    title=self.title_input.value,
                    description=self.content_input.value[:500] + "..." if len(self.content_input.value) > 500 else self.content_input.value,
                    color=color
                )
                preview_embed.set_footer(text=f"Réagissez avec {self.emoji_input.value or '✅'} pour accepter le règlement")
                
                await interaction.response.send_message(embeds=[embed, preview_embed], ephemeral=True)
            else:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Une erreur s'est produite lors de la création du règlement personnalisé.",
                    color=0xFF0000
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            logger.error(f"Erreur création règlement personnalisé: {e}")
            embed = discord.Embed(
                title="❌ Erreur Inattendue",
                description="Une erreur inattendue s'est produite. Veuillez réessayer.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


class ConfigureReglementModal(discord.ui.Modal):
    """Modal pour configurer les paramètres du règlement"""
    
    def __init__(self, guild_id: int, db: ReglementDB, current_rules: dict):
        super().__init__(title="⚙️ Configuration du Règlement", timeout=300)
        self.guild_id = guild_id
        self.db = db
        self.current_rules = current_rules
        
        self.emoji_input = discord.ui.TextInput(
            label="Emoji d'acceptation",
            placeholder="✅",
            default=current_rules.get('acceptance_emoji', '✅'),
            max_length=10,
            required=True
        )
        
        self.role_input = discord.ui.TextInput(
            label="ID du rôle à attribuer (optionnel)",
            placeholder="Laissez vide pour aucun rôle",
            default=str(current_rules.get('acceptance_role_id', '') or ''),
            max_length=20,
            required=False
        )
        
        self.add_item(self.emoji_input)
        self.add_item(self.role_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            role_id = int(self.role_input.value) if self.role_input.value else None
        except ValueError:
            role_id = None
        
        # Mettre à jour la configuration
        updated_rules = self.current_rules.copy()
        updated_rules['acceptance_emoji'] = self.emoji_input.value
        updated_rules['acceptance_role_id'] = role_id
        
        success = self.db.save_server_rules(self.guild_id, updated_rules)
        
        if success:
            embed = discord.Embed(
                title="✅ Configuration Mise à Jour",
                description="Les paramètres du règlement ont été mis à jour avec succès !",
                color=0x00FF88
            )
            embed.add_field(
                name="⚙️ Nouveaux paramètres",
                value=f"**Emoji:** {self.emoji_input.value}\n"
                      f"**Rôle:** {f'<@&{role_id}>' if role_id else 'Aucun'}",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Une erreur s'est produite lors de la mise à jour.",
                color=0xFF0000
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


# =============================================================================
# COMMANDES PRINCIPALES DU SYSTÈME DE RÈGLEMENT
# =============================================================================

class ReglementSystem(commands.Cog):
    """🛡️ Système modulaire de règlement Arsenal"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = ReglementDB()
    
    @app_commands.command(name="reglement", description="🛡️ Gestion du règlement du serveur")
    @app_commands.describe(action="Action à effectuer")
    @app_commands.choices(action=[
        app_commands.Choice(name="setup - Configuration du règlement", value="setup"),
        app_commands.Choice(name="publish - Publier le règlement", value="publish"), 
        app_commands.Choice(name="edit - Modifier le règlement", value="edit"),
        app_commands.Choice(name="stats - Voir les statistiques", value="stats"),
        app_commands.Choice(name="preview - Prévisualiser", value="preview")
    ])
    async def reglement(self, interaction: discord.Interaction, action: str = "setup"):
        """Commande principale de gestion du règlement"""
        
        if not interaction.user.guild_permissions.manage_guild:
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes",
                description="Seuls les membres avec la permission **Gérer le serveur** peuvent utiliser cette commande.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if action == "setup":
            await self.setup_rules(interaction)
        elif action == "publish":
            await self.publish_rules(interaction)
        elif action == "edit":
            await self.edit_rules(interaction)
        elif action == "stats":
            await self.show_stats(interaction)
        elif action == "preview":
            await self.preview_rules(interaction)
    
    async def setup_rules(self, interaction: discord.Interaction):
        """Configuration initiale du règlement"""
        embed = discord.Embed(
            title="🛡️ Configuration du Règlement",
            description="""
**Bienvenue dans le système de règlement Arsenal !**

🔧 **Fonctionnalités disponibles :**
• **Création** de règlement personnalisé ou via templates
• **Système d'acceptation** par réaction automatique
• **Attribution de rôles** après acceptation
• **Statistiques** et suivi des acceptations
• **Multi-templates** pour différents types de serveurs

📋 **Templates disponibles :**
• **Général** - Pour serveurs communautaires
• **Gaming** - Spécialisé jeux vidéo
• **Business** - Environnement professionnel 
• **Community** - Communautés inclusives

Choisissez une option ci-dessous pour commencer.
            """,
            color=0x3366FF
        )
        
        view = ReglementSetupView(interaction.guild_id, self.db)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    async def publish_rules(self, interaction: discord.Interaction):
        """Publier le règlement dans un salon"""
        rules = self.db.get_server_rules(interaction.guild_id)
        
        if not rules:
            embed = discord.Embed(
                title="❌ Aucun Règlement",
                description="Créez d'abord un règlement avec `/reglement setup`.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Créer l'embed du règlement
        rules_embed = discord.Embed(
            title=rules['title'],
            description=rules['rules_content'],
            color=0x3366FF,
            timestamp=datetime.now(timezone.utc)
        )
        
        rules_embed.set_footer(text=f"Règlement du serveur {interaction.guild.name}")
        
        if interaction.guild.icon:
            rules_embed.set_thumbnail(url=interaction.guild.icon.url)
        
        await interaction.response.send_message(embed=rules_embed)
        
        # Ajouter la réaction d'acceptation
        if rules['acceptance_required']:
            message = await interaction.original_response()
            await message.add_reaction(rules['acceptance_emoji'])
            
            # Mettre à jour l'ID du message dans la DB
            updated_rules = rules.copy()
            updated_rules['message_id'] = message.id
            updated_rules['channel_id'] = interaction.channel_id
            self.db.save_server_rules(interaction.guild_id, updated_rules)
    
    async def edit_rules(self, interaction: discord.Interaction):
        """Modifier le règlement existant"""
        rules = self.db.get_server_rules(interaction.guild_id)
        
        if not rules:
            embed = discord.Embed(
                title="❌ Aucun Règlement",
                description="Créez d'abord un règlement avec `/reglement setup`.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        modal = CreateReglementModal(interaction.guild_id, self.db)
        # Pré-remplir avec le contenu existant
        modal.title_input.default = rules['title']
        modal.content_input.default = rules['rules_content']
        
        await interaction.response.send_modal(modal)
    
    async def show_stats(self, interaction: discord.Interaction):
        """Afficher les statistiques du règlement"""
        stats = self.db.get_acceptance_stats(interaction.guild_id)
        rules = self.db.get_server_rules(interaction.guild_id)
        
        embed = discord.Embed(
            title="📊 Statistiques du Règlement",
            color=0x00FF88
        )
        
        if rules:
            embed.add_field(
                name="📋 Règlement Actuel",
                value=f"**Titre:** {rules['title']}\n"
                      f"**Template:** {rules['template_used']}\n"
                      f"**Créé:** {rules['created_at'][:10]}\n"
                      f"**MAJ:** {rules['updated_at'][:10]}",
                inline=True
            )
            
            embed.add_field(
                name="⚙️ Configuration",
                value=f"**Emoji:** {rules['acceptance_emoji']}\n"
                      f"**Rôle:** {'<@&' + str(rules['acceptance_role_id']) + '>' if rules['acceptance_role_id'] else 'Aucun'}\n"
                      f"**Acceptation:** {'Requise' if rules['acceptance_required'] else 'Optionnelle'}",
                inline=True
            )
        
        embed.add_field(
            name="✅ Acceptations",
            value=f"**Total:** {stats['total_acceptances']}\n"
                  f"**Aujourd'hui:** {stats['today_acceptances']}",
            inline=True
        )
        
        if interaction.guild.member_count:
            acceptance_rate = (stats['total_acceptances'] / interaction.guild.member_count) * 100
            embed.add_field(
                name="📈 Taux d'Acceptation",
                value=f"**{acceptance_rate:.1f}%** des membres\n"
                      f"({stats['total_acceptances']}/{interaction.guild.member_count})",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def preview_rules(self, interaction: discord.Interaction):
        """Prévisualiser le règlement sans le publier"""
        rules = self.db.get_server_rules(interaction.guild_id)
        
        if not rules:
            embed = discord.Embed(
                title="❌ Aucun Règlement",
                description="Créez d'abord un règlement avec `/reglement setup`.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Créer l'embed de prévisualisation
        preview_embed = discord.Embed(
            title=f"👁️ Aperçu: {rules['title']}",
            description=rules['rules_content'],
            color=0xFFD700
        )
        
        preview_embed.add_field(
            name="ℹ️ Informations",
            value=f"**Template:** {rules['template_used']}\n"
                  f"**Emoji acceptation:** {rules['acceptance_emoji']}\n"
                  f"**Rôle attribué:** {'<@&' + str(rules['acceptance_role_id']) + '>' if rules['acceptance_role_id'] else 'Aucun'}",
            inline=False
        )
        
        preview_embed.set_footer(text="⚠️ Ceci est un aperçu - utilisez /reglement publish pour publier")
        
        await interaction.response.send_message(embed=preview_embed, ephemeral=True)
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Gestion des réactions d'acceptation du règlement"""
        if user.bot:
            return
        
        # Vérifier si c'est une réaction sur un message de règlement
        rules = self.db.get_server_rules(reaction.message.guild.id)
        
        if not rules or not rules['message_id'] or rules['message_id'] != reaction.message.id:
            return
        
        if str(reaction.emoji) != rules['acceptance_emoji']:
            return
        
        # Enregistrer l'acceptation
        if self.db.accept_rules(reaction.message.guild.id, user.id):
            # Attribuer le rôle si configuré
            if rules['acceptance_role_id']:
                try:
                    guild = reaction.message.guild
                    member = guild.get_member(user.id)
                    role = guild.get_role(rules['acceptance_role_id'])
                    
                    if member and role:
                        await member.add_roles(role, reason="Acceptation du règlement")
                        
                        # Envoi d'un message de confirmation en DM
                        try:
                            embed = discord.Embed(
                                title="✅ Règlement Accepté",
                                description=f"Merci d'avoir accepté le règlement de **{guild.name}** !\n\n"
                                           f"Le rôle **{role.name}** vous a été attribué.",
                                color=0x00FF88
                            )
                            await user.send(embed=embed)
                        except discord.Forbidden:
                            pass  # L'utilisateur n'accepte pas les DM
                            
                except Exception as e:
                    logger.error(f"Erreur attribution rôle règlement: {e}")


async def setup(bot):
    """Setup function pour charger le système de règlement"""
    await bot.add_cog(ReglementSystem(bot))
    logger.info("🛡️ Système de Règlement Arsenal chargé avec succès!")
    print("✅ Reglement System - Système modulaire prêt!")
    print("📋 Templates: Général, Gaming, Business, Community")
    print("🎯 Commande: /reglement [setup|publish|edit|stats|preview]")

