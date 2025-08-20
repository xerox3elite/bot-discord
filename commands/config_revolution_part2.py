#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ARSENAL CONFIG REVOLUTION V2.0 - PARTIE 2
Méthodes complémentaires pour le système de configuration révolutionnaire
"""

import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Set
import logging

logger = logging.getLogger('ArsenalConfigRevolution')

# =============================================================================
# VUES SUPPLÉMENTAIRES ET MÉTHODES MANQUANTES 
# =============================================================================

class ReconfigurationView(discord.ui.View):
    """Vue pour serveur déjà configuré"""
    
    def __init__(self, cog, guild_id: int):
        super().__init__(timeout=1800)
        self.cog = cog
        self.guild_id = guild_id
    
    @discord.ui.button(label="🔄 Reconfigurer", style=discord.ButtonStyle.primary)
    async def reconfigure_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Reconfigure le serveur"""
        await interaction.response.defer()
        
        # Reset la configuration
        config = self.cog.get_default_config()
        await self.cog.save_guild_config(self.guild_id, config)
        
        # Redémarrer la configuration
        view = ConfigMainView(self.cog, self.guild_id)
        embed = self.cog.create_welcome_embed(interaction.guild)
        
        await interaction.edit_original_response(embed=embed, view=view)
    
    @discord.ui.button(label="⚙️ Modifier Modules", style=discord.ButtonStyle.secondary)
    async def modify_modules_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Modifier des modules spécifiques"""
        await interaction.response.defer()
        
        view = AdvancedConfigView(self.cog, self.guild_id)
        embed = self.cog.create_advanced_config_embed(await self.cog.load_guild_config(self.guild_id))
        
        await interaction.edit_original_response(embed=embed, view=view)

class StatusActionsView(discord.ui.View):
    """Actions du statut de configuration"""
    
    def __init__(self, cog, guild_id: int):
        super().__init__(timeout=1800)
        self.cog = cog
        self.guild_id = guild_id
    
    @discord.ui.button(label="📊 Dashboard", style=discord.ButtonStyle.primary)
    async def dashboard_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Ouvre le dashboard"""
        await interaction.response.defer()
        
        view = AnalyticsDashboardView(self.cog, self.guild_id)
        embed = await self.cog.create_analytics_embed(interaction.guild)
        
        await interaction.edit_original_response(embed=embed, view=view)

class BackupManagementView(discord.ui.View):
    """Gestion des sauvegardes"""
    
    def __init__(self, cog, guild_id: int):
        super().__init__(timeout=1800)
        self.cog = cog
        self.guild_id = guild_id
    
    @discord.ui.button(label="💾 Créer Backup", style=discord.ButtonStyle.success)
    async def create_backup_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Crée un backup manuel"""
        await interaction.response.defer()
        
        try:
            config = await self.cog.load_guild_config(self.guild_id)
            await self.cog.create_config_backup(self.guild_id, config)
            
            embed = discord.Embed(
                title="💾 Backup Créé",
                description="Un backup de votre configuration a été créé avec succès.",
                color=0x00FF88
            )
            
            await interaction.edit_original_response(embed=embed, view=self)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur Backup",
                description=f"Erreur lors de la création du backup: {str(e)}",
                color=0xFF0000
            )
            await interaction.edit_original_response(embed=embed, view=self)

class ResetConfirmationView(discord.ui.View):
    """Confirmation de reset"""
    
    def __init__(self, cog, guild_id: int):
        super().__init__(timeout=300)
        self.cog = cog
        self.guild_id = guild_id
    
    @discord.ui.button(label="⚠️ CONFIRMER RESET", style=discord.ButtonStyle.danger)
    async def confirm_reset_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Confirme le reset"""
        await interaction.response.defer()
        
        try:
            # Créer backup avant reset
            current_config = await self.cog.load_guild_config(self.guild_id)
            await self.cog.create_config_backup(self.guild_id, current_config)
            
            # Reset la configuration
            default_config = self.cog.get_default_config()
            await self.cog.save_guild_config(self.guild_id, default_config)
            
            embed = discord.Embed(
                title="🔄 Configuration Réinitialisée",
                description="La configuration a été réinitialisée aux valeurs par défaut.\n"
                           "Un backup de l'ancienne configuration a été créé.",
                color=0xFF9900
            )
            
            await interaction.edit_original_response(embed=embed, view=None)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur Reset",
                description=f"Erreur lors du reset: {str(e)}",
                color=0xFF0000
            )
            await interaction.edit_original_response(embed=embed, view=None)
    
    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
    async def cancel_reset_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Annule le reset"""
        embed = discord.Embed(
            title="❌ Reset Annulé",
            description="Le reset de la configuration a été annulé.",
            color=0x999999
        )
        await interaction.response.edit_message(embed=embed, view=None)

class GuideView(discord.ui.View):
    """Vue du guide complet"""
    
    def __init__(self, cog):
        super().__init__(timeout=1800)
        self.cog = cog
        self.current_page = 0
        self.max_pages = 5
    
    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page précédente"""
        if self.current_page > 0:
            self.current_page -= 1
            embed = self.cog.create_guide_page_embed(self.current_page)
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page suivante"""
        if self.current_page < self.max_pages - 1:
            self.current_page += 1
            embed = self.cog.create_guide_page_embed(self.current_page)
            await interaction.response.edit_message(embed=embed, view=self)

class ManualCreationGuideView(discord.ui.View):
    """Guide de création manuelle"""
    
    def __init__(self, cog, guild_id: int, server_type: str, server_size: str):
        super().__init__(timeout=1800)
        self.cog = cog
        self.guild_id = guild_id
        self.server_type = server_type
        self.server_size = server_size
    
    @discord.ui.button(label="✅ Terminé Manuellement", style=discord.ButtonStyle.success)
    async def manual_complete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Marque la création manuelle comme terminée"""
        await interaction.response.defer()
        
        # Passer à l'étape finale
        view = QuickSetupStep5(self.cog, self.guild_id)
        embed = await self.cog.create_step5_embed(interaction.guild)
        
        await interaction.edit_original_response(embed=embed, view=view)

class ShopConfigView(discord.ui.View):
    """Configuration de la boutique"""
    
    def __init__(self, cog, guild_id: int):
        super().__init__(timeout=1800)
        self.cog = cog
        self.guild_id = guild_id
    
    @discord.ui.button(label="🛍️ Ajouter Article", style=discord.ButtonStyle.primary)
    async def add_item_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Ajouter un article à la boutique"""
        await interaction.response.send_modal(ShopItemModal(self.cog, self.guild_id))

class ShopItemModal(discord.ui.Modal):
    """Modal pour ajouter un article à la boutique"""
    
    def __init__(self, cog, guild_id: int):
        super().__init__(title="🛍️ Nouvel Article Boutique")
        self.cog = cog
        self.guild_id = guild_id
        
        self.item_name = discord.ui.TextInput(
            label="Nom de l'Article",
            placeholder="Rôle VIP",
            max_length=50
        )
        self.add_item(self.item_name)
        
        self.item_price = discord.ui.TextInput(
            label="Prix (ArsenalCoin)",
            placeholder="1000",
            max_length=10
        )
        self.add_item(self.item_price)
        
        self.item_description = discord.ui.TextInput(
            label="Description",
            placeholder="Accès VIP avec avantages exclusifs",
            style=discord.TextStyle.paragraph,
            max_length=200
        )
        self.add_item(self.item_description)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Ajoute l'article à la boutique"""
        await interaction.response.defer()
        
        try:
            config = await self.cog.load_guild_config(self.guild_id)
            
            if "economy" not in config:
                config["economy"] = {}
            if "shop" not in config["economy"]:
                config["economy"]["shop"] = {"custom_items": []}
            
            new_item = {
                "name": self.item_name.value,
                "price": int(self.item_price.value),
                "description": self.item_description.value,
                "type": "custom",
                "available": True
            }
            
            config["economy"]["shop"]["custom_items"].append(new_item)
            await self.cog.save_guild_config(self.guild_id, config)
            
            embed = discord.Embed(
                title="🛍️ Article Ajouté !",
                description=f"L'article **{self.item_name.value}** a été ajouté à la boutique.",
                color=0x00FF88
            )
            embed.add_field(
                name="📊 Détails",
                value=f"• **Prix:** {self.item_price.value} AC\n"
                      f"• **Description:** {self.item_description.value}",
                inline=False
            )
            
            await interaction.edit_original_response(embed=embed)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Le prix doit être un nombre valide.",
                color=0xFF0000
            )
            await interaction.edit_original_response(embed=embed)

# =============================================================================
# MÉTHODES D'ASSISTANCE POUR CRÉATION D'EMBEDS
# =============================================================================

def create_step1_embed(self) -> discord.Embed:
    """Crée l'embed de l'étape 1"""
    embed = discord.Embed(
        title="🎯 Étape 1/5 : Type de Serveur",
        description="**Sélectionnez le type de votre serveur**\n\n"
                   "Cette sélection détermine les modules recommandés et la configuration optimale.\n"
                   "Vous pourrez toujours personnaliser après.",
        color=0x3366FF
    )
    
    embed.add_field(
        name="🎮 Gaming",
        value="• Jeux & tournois\n• Hunt Royal\n• Économie avancée",
        inline=True
    )
    
    embed.add_field(
        name="👥 Communauté",
        value="• Discussion générale\n• Événements\n• Modération équilibrée",
        inline=True
    )
    
    embed.add_field(
        name="💼 Professionnel",
        value="• Collaboration\n• Sécurité renforcée\n• Tickets support",
        inline=True
    )
    
    embed.set_footer(text="Étape 1/5 • Arsenal Config Revolution V2.0")
    return embed

def create_step2_embed(self, server_type: str) -> discord.Embed:
    """Crée l'embed de l'étape 2"""
    embed = discord.Embed(
        title="📊 Étape 2/5 : Taille du Serveur",
        description=f"**Serveur {server_type.title()} sélectionné ✅**\n\n"
                   "Maintenant, indiquez la taille de votre serveur pour optimiser les performances.",
        color=0x3366FF
    )
    
    embed.add_field(
        name="🏠 Petit (1-100)",
        value="• Configuration légère\n• Fonctions essentielles\n• Performance optimale",
        inline=True
    )
    
    embed.add_field(
        name="🏢 Moyen (100-500)",
        value="• Équilibre fonctionnalités\n• Modération adaptée\n• Évolutivité",
        inline=True
    )
    
    embed.add_field(
        name="🏭 Grand (500-2000)",
        value="• Outils avancés\n• Sécurité renforcée\n• Analytics détaillées",
        inline=True
    )
    
    embed.set_footer(text="Étape 2/5 • Arsenal Config Revolution V2.0")
    return embed

def create_step3_embed(self, server_type: str, server_size: str) -> discord.Embed:
    """Crée l'embed de l'étape 3"""
    embed = discord.Embed(
        title="⚙️ Étape 3/5 : Sélection des Modules",
        description=f"**Serveur {server_type.title()} {server_size.title()} ✅**\n\n"
                   "Choisissez comment configurer vos modules :",
        color=0x3366FF
    )
    
    embed.add_field(
        name="✅ Preset Recommandé",
        value="• Configuration automatique\n• Optimisé pour votre serveur\n• **Recommandé pour débutants**",
        inline=True
    )
    
    embed.add_field(
        name="🔧 Sélection Personnalisée",
        value="• Contrôle total\n• Choisir chaque module\n• **Pour utilisateurs avancés**",
        inline=True
    )
    
    embed.set_footer(text="Étape 3/5 • Arsenal Config Revolution V2.0")
    return embed

async def create_step4_embed(self, server_type: str, server_size: str, use_preset: bool, selected_modules: set = None) -> discord.Embed:
    """Crée l'embed de l'étape 4"""
    embed = discord.Embed(
        title="🚀 Étape 4/5 : Création de la Structure",
        description="**Configuration prête !**\n\n"
                   "Arsenal va maintenant créer la structure de votre serveur :",
        color=0x3366FF
    )
    
    if use_preset:
        preset = await self.get_server_preset(ServerType(server_type), ServerSize(server_size))
        modules_count = sum(1 for module in preset.keys() if preset.get(module, {}).get("enabled", False))
        
        embed.add_field(
            name="📦 Preset Appliqué",
            value=f"• **Type:** {server_type.title()}\n"
                  f"• **Taille:** {server_size.title()}\n"
                  f"• **Modules:** {modules_count} activés",
            inline=True
        )
    else:
        embed.add_field(
            name="🔧 Configuration Personnalisée",
            value=f"• **Modules sélectionnés:** {len(selected_modules or set())}\n"
                  f"• **Type:** {server_type.title()}\n"
                  f"• **Taille:** {server_size.title()}",
            inline=True
        )
    
    embed.add_field(
        name="🔧 Éléments à Créer",
        value="• Catégories et salons\n• Rôles et permissions\n• Configuration modules\n• Paramètres sécurité",
        inline=True
    )
    
    embed.set_footer(text="Étape 4/5 • Arsenal Config Revolution V2.0")
    return embed

async def create_step5_embed(self, guild: discord.Guild) -> discord.Embed:
    """Crée l'embed de l'étape 5"""
    embed = discord.Embed(
        title="🎉 Étape 5/5 : Finalisation",
        description=f"**Bravo ! {guild.name} est presque prêt !**\n\n"
                   "Structure créée avec succès. Il ne reste plus qu'à finaliser.",
        color=0x00FF88
    )
    
    embed.add_field(
        name="✅ Créé avec Succès",
        value="• Salons et catégories\n• Rôles et permissions\n• Configuration modules\n• Paramètres de base",
        inline=True
    )
    
    embed.add_field(
        name="🚀 Prochaines Étapes",
        value="• Tester les fonctionnalités\n• Ajuster si nécessaire\n• Inviter vos membres\n• Profiter d'Arsenal !",
        inline=True
    )
    
    embed.set_footer(text="Configuration Terminée • Arsenal Config Revolution V2.0")
    return embed

def create_module_selection_embed(self) -> discord.Embed:
    """Embed pour sélection de modules"""
    embed = discord.Embed(
        title="🔧 Sélection Personnalisée des Modules",
        description="**Choisissez précisément les modules à activer**\n\n"
                   "Sélectionnez dans chaque catégorie les fonctionnalités que vous souhaitez.",
        color=0x3366FF
    )
    
    embed.add_field(
        name="🛡️ Modération & Sécurité",
        value="Protection et gestion du serveur",
        inline=True
    )
    
    embed.add_field(
        name="💰 Économie & Divertissement", 
        value="ArsenalCoin, jeux et niveaux",
        inline=True
    )
    
    embed.add_field(
        name="🗣️ Vocal & Communication",
        value="Hub vocal et système musical",
        inline=True
    )
    
    return embed

def create_manual_guide_embed(self, server_type: str, server_size: str) -> discord.Embed:
    """Guide de création manuelle"""
    embed = discord.Embed(
        title="📝 Guide de Création Manuelle",
        description=f"**Guide pour serveur {server_type.title()} {server_size.title()}**\n\n"
                   "Suivez ces étapes pour créer votre structure manuellement :",
        color=0x3366FF
    )
    
    # Guide spécifique selon le type
    if server_type == "gaming":
        embed.add_field(
            name="🎮 Salons Gaming Recommandés",
            value="• 📢 #annonces-gaming\n• 🎮 #gaming-général\n• 🎯 #tournois\n• 🏹 #hunt-royal\n• 🎵 Salon vocal gaming",
            inline=False
        )
    elif server_type == "community":
        embed.add_field(
            name="👥 Salons Communauté",
            value="• 📢 #annonces\n• 💬 #général\n• 🎪 #détente\n• 📸 #partages\n• 🗣️ Salons vocaux",
            inline=False
        )
    
    embed.add_field(
        name="⚙️ Rôles de Base",
        value="• 👑 Administrateur\n• 🛡️ Modérateur\n• 🎓 Membre\n• 🤖 Arsenal Bot",
        inline=True
    )
    
    embed.add_field(
        name="🔒 Permissions Importantes", 
        value="• Gérer les salons\n• Gérer les rôles\n• Modérer\n• Utiliser les commandes",
        inline=True
    )
    
    return embed

# Ajout des méthodes à la classe ArsenalConfigRevolution
ArsenalConfigRevolution.create_step1_embed = create_step1_embed
ArsenalConfigRevolution.create_step2_embed = create_step2_embed  
ArsenalConfigRevolution.create_step3_embed = create_step3_embed
ArsenalConfigRevolution.create_step4_embed = create_step4_embed
ArsenalConfigRevolution.create_step5_embed = create_step5_embed
ArsenalConfigRevolution.create_module_selection_embed = create_module_selection_embed
ArsenalConfigRevolution.create_manual_guide_embed = create_manual_guide_embed
