"""
ARSENAL CONFIG COMMAND SYSTEM - SYSTÈME DE CONFIGURATION UNIFIÉ
Commandes /config avec sous-commandes pour tous les systèmes Arsenal
Par xerox3elite - Arsenal V4.5.1 ULTIMATE
"""

import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import asyncio

class ArsenalConfigSystem(commands.Cog):
    """
    🚀 ARSENAL CONFIG SYSTEM - CONFIGURATION UNIFIÉE
    Système de configuration avec sous-commandes /config
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "data/arsenal_config"
        os.makedirs(self.config_path, exist_ok=True)

    def check_admin_permissions(self, interaction: discord.Interaction) -> bool:
        """Vérifie les permissions administrateur"""
        if hasattr(interaction.user, 'guild_permissions'):
            return interaction.user.guild_permissions.administrator
        return False

    # Groupe de commandes /config
    config_group = app_commands.Group(name="config", description="🚀 Configuration Arsenal")

    @config_group.command(name="show", description="📋 Afficher toutes les configurations disponibles")
    async def config_show(self, interaction: discord.Interaction):
        """Afficher toutes les configurations disponibles"""
        if not self.check_admin_permissions(interaction):
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes",
                description="Seuls les **administrateurs** peuvent accéder à la configuration.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🚀 Arsenal Configuration System",
            description="**Système de configuration ultra-avancé**",
            color=discord.Color.gold(),
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(
            name="🎫 **Tickets**",
            value="`/config tickets` - Système de tickets avancé\n`/ticket setup` - Configuration tickets",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ **Modération**",
            value="`/config moderation` - Système de modération\n`/config automod` - AutoMod avancé",
            inline=False
        )
        
        embed.add_field(
            name="💰 **Économie**",
            value="`/config economy` - Système économique\n`/config shop` - Boutique Arsenal",
            inline=False
        )
        
        embed.add_field(
            name="🎮 **Hunt Royal**",
            value="`/config huntroyal` - Intégration Hunt Royal\n`/huntroyal setup` - Configuration jeu",
            inline=False
        )
        
        embed.add_field(
            name="🔐 **Permissions**",
            value="`/config permissions` - Système permissions\n`/config roles` - Gestion rôles",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ **Autres**",
            value="`/config logs` - Configuration logs\n`/config welcome` - Messages bienvenue\n`/config custom` - Commandes custom",
            inline=False
        )
        
        embed.set_footer(text="Arsenal V4.5.1 Ultimate | Configuration System")
        if hasattr(self.bot.user, 'display_avatar'):
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @config_group.command(name="tickets", description="🎫 Configuration système de tickets")
    async def config_tickets(self, interaction: discord.Interaction):
        """Configuration du système de tickets"""
        if not self.check_admin_permissions(interaction):
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes",
                description="Seuls les **administrateurs** peuvent configurer les tickets.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Récupérer le système de tickets
        ticket_system = self.bot.get_cog("AdvancedTicketSystem")
        
        embed = discord.Embed(
            title="🎫 Configuration Tickets",
            description="**Système de tickets ultra-avancé avec catégories**",
            color=discord.Color.blue()
        )
        
        if ticket_system:
            try:
                config = await ticket_system.get_guild_config(interaction.guild.id)
                categories = config.get('ticket_categories', {})
                
                embed.add_field(
                    name="📋 **Catégories disponibles**",
                    value="\n".join([f"{cat.get('emoji', '🎫')} **{cat.get('name', 'N/A')}**" 
                                   for cat in categories.values()]) or "Aucune catégorie configurée",
                    inline=False
                )
                
                embed.add_field(
                    name="✅ **Statut**",
                    value="🟢 Système de tickets **actif** et opérationnel",
                    inline=True
                )
                
            except Exception as e:
                embed.add_field(
                    name="⚠️ **Erreur**",
                    value=f"Erreur lors du chargement: {str(e)}",
                    inline=False
                )
        else:
            embed.add_field(
                name="❌ **Statut**",
                value="🔴 Système de tickets **non chargé**",
                inline=True
            )
        
        embed.add_field(
            name="⚙️ **Commandes disponibles**",
            value=(
                "`/ticket` - Créer un nouveau ticket\n"
                "`/ticket setup` - Configuration avancée\n"
                "`/ticket panel` - Créer panneau public\n"
                "`/ticket close` - Fermer ticket actuel"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @config_group.command(name="moderation", description="🛡️ Configuration système de modération")
    async def config_moderation(self, interaction: discord.Interaction):
        """Configuration de la modération"""
        if not self.check_admin_permissions(interaction):
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes",
                description="Seuls les **administrateurs** peuvent configurer la modération.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🛡️ Configuration Modération",
            description="**Système de modération ultra-avancé Arsenal**",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="🤖 **AutoMod Discord Natif**",
            value="• Filtres de contenu automatiques\n• Protection anti-spam intégrée\n• Détection de liens malveillants",
            inline=False
        )
        
        embed.add_field(
            name="🔒 **Protection Anti-Raid**",
            value="• Détection automatique des raids\n• Quarantine système\n• Protection membres récents",
            inline=False
        )
        
        embed.add_field(
            name="📊 **Analytics Modération**",
            value="• Statistiques temps réel\n• Rapport d'activité\n• Historique des sanctions",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ **Configuration**",
            value="Configuration bientôt disponible via interface dédiée",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @config_group.command(name="economy", description="💰 Configuration système économique")
    async def config_economy(self, interaction: discord.Interaction):
        """Configuration de l'économie"""
        if not self.check_admin_permissions(interaction):
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes",
                description="Seuls les **administrateurs** peuvent configurer l'économie.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="💰 Configuration Économie",
            description="**Système économique révolutionnaire Arsenal**",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="💎 **Arsenal Coins**",
            value="• Monnaie virtuelle du serveur\n• Gains par activité\n• Système de récompenses",
            inline=False
        )
        
        embed.add_field(
            name="🏪 **Shop Arsenal**",
            value="• Boutique intégrée\n• Objets personnalisés\n• Rôles premium",
            inline=False
        )
        
        embed.add_field(
            name="🎯 **Système de Gains**",
            value="• Messages récompensés\n• Activité vocale\n• Événements spéciaux",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ **Commandes**",
            value="`/coins` - Voir solde\n`/shop` - Boutique\n`/daily` - Bonus quotidien",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @config_group.command(name="huntroyal", description="🎮 Configuration Hunt Royal")
    async def config_huntroyal(self, interaction: discord.Interaction):
        """Configuration Hunt Royal"""
        if not self.check_admin_permissions(interaction):
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes",
                description="Seuls les **administrateurs** peuvent configurer Hunt Royal.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎮 Configuration Hunt Royal",
            description="**Intégration complète avec Hunt Royal**",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="🏆 **Statistiques Joueurs**",
            value="• Stats en temps réel\n• Classements serveur\n• Progression tracking",
            inline=False
        )
        
        embed.add_field(
            name="🎫 **Support Dédié**",
            value="• Tickets Hunt Royal spéciaux\n• Support technique jeu\n• Assistance multijoueur",
            inline=False
        )
        
        embed.add_field(
            name="🔗 **API Integration**",
            value="• Connexion API Hunt Royal\n• Synchronisation profils\n• Données temps réel",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ **Commandes**",
            value="`/huntroyal` - Menu principal\n`/huntroyal stats` - Statistiques\n`/huntroyal setup` - Configuration",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @config_group.command(name="permissions", description="🔐 Configuration des permissions")
    async def config_permissions(self, interaction: discord.Interaction):
        """Configuration des permissions"""
        if not self.check_admin_permissions(interaction):
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes",
                description="Seuls les **administrateurs** peuvent configurer les permissions.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔐 Configuration Permissions",
            description="**Système de permissions avancé Arsenal**",
            color=discord.Color.dark_blue()
        )
        
        embed.add_field(
            name="👥 **Rôles Staff**",
            value="• Hiérarchie automatique\n• Permissions par niveau\n• Gestion centralisée",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ **Permissions Commandes**",
            value="• Contrôle par commande\n• Whitelist/Blacklist\n• Permissions temporaires",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ **Sécurité Avancée**",
            value="• Protection commandes sensibles\n• Audit des permissions\n• Contrôle accès",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ **Configuration**",
            value="Interface de permissions bientôt disponible",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @config_group.command(name="logs", description="📊 Configuration des logs")
    async def config_logs(self, interaction: discord.Interaction):
        """Configuration des logs"""
        if not self.check_admin_permissions(interaction):
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes",
                description="Seuls les **administrateurs** peuvent configurer les logs.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📊 Configuration Logs",
            description="**Système de logs ultra-complet Arsenal**",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📝 **Logs Serveur**",
            value="• Messages supprimés/modifiés\n• Entrées/Sorties membres\n• Changements rôles",
            inline=False
        )
        
        embed.add_field(
            name="🔧 **Logs Bot**",
            value="• Commandes utilisées\n• Erreurs système\n• Performance monitoring",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ **Logs Modération**",
            value="• Actions modération\n• AutoMod détections\n• Sanctions appliquées",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ **Configuration**",
            value="Interface de configuration logs bientôt disponible",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @config_group.command(name="custom", description="🛠️ Configuration commandes personnalisées")
    async def config_custom(self, interaction: discord.Interaction):
        """Configuration des commandes personnalisées"""
        if not self.check_admin_permissions(interaction):
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes",
                description="Seuls les **administrateurs** peuvent configurer les commandes personnalisées.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🛠️ Configuration Commandes Personnalisées",
            description="**Système de commandes personnalisées Arsenal**\n*15 commandes gratuites par serveur*",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="⚡ **Fonctionnalités**",
            value="• Réponses automatiques personnalisées\n• Embeds dynamiques\n• Variables serveur\n• Conditions logiques",
            inline=False
        )
        
        embed.add_field(
            name="🎯 **Limites Gratuites**",
            value="• **15 commandes** maximum par serveur\n• Texte et embeds basiques\n• Variables standard",
            inline=False
        )
        
        embed.add_field(
            name="💎 **Arsenal Premium**",
            value="• **Commandes illimitées**\n• API externes\n• Logique avancée\n• Support prioritaire",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ **Bientôt Disponible**",
            value="Interface de création de commandes personnalisées en développement",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ArsenalConfigSystem(bot))
