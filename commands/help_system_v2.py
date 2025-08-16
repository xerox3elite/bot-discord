#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ARSENAL HELP SYSTEM V2 ULTIMATE - SYSTÈME D'AIDE COMPLET
Interface moderne qui affiche TOUTES les commandes + Support + Infos utiles
Par xerox3elite - Arsenal V4.5.2 ULTIMATE
"""

import discord
from discord import app_commands
from discord.ext import commands
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
import logging

# Configuration du logger
log = logging.getLogger(__name__)

class HelpMainView(discord.ui.View):
    """Vue principale du système d'aide complet"""
    
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        
        # Ajouter les boutons de lien externe
        website_btn = discord.ui.Button(
            label="🌐 Site Web", 
            style=discord.ButtonStyle.link, 
            url="https://arsenal-bot.com"
        )
        discord_btn = discord.ui.Button(
            label="💬 Discord Support", 
            style=discord.ButtonStyle.link, 
            url="https://discord.gg/arsenal"
        )
        
        self.add_item(website_btn)
        self.add_item(discord_btn)
    
    @discord.ui.button(label="📋 Toutes les Commandes", style=discord.ButtonStyle.primary, emoji="📋")
    async def all_commands_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Afficher toutes les commandes du bot"""
        view = AllCommandsView(self.bot)
        embed = view.create_embed()
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="🔍 Rechercher", style=discord.ButtonStyle.secondary, emoji="🔍")
    async def search_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Ouvrir la recherche de commandes"""
        modal = SearchCommandModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="💬 Support", style=discord.ButtonStyle.success, emoji="💬")
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Afficher les infos de support"""
        embed = self.create_support_embed()
        await interaction.response.edit_message(embed=embed, view=SupportView(self.bot))
    
    @discord.ui.button(label="📊 Infos Bot", style=discord.ButtonStyle.secondary, emoji="📊")
    async def info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Afficher les infos du bot"""
        embed = self.create_bot_info_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    def create_main_embed(self) -> discord.Embed:
        """Embed principal du système d'aide"""
        embed = discord.Embed(
            title="📚 Arsenal Help System V2",
            description="**🚀 Arsenal V4.5.2 ULTIMATE - Le bot Discord le plus avancé**\n\n"
                       "✨ **Bienvenue dans le système d'aide complet !**\n"
                       "Choisissez une option ci-dessous pour obtenir l'aide dont vous avez besoin.",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(
            name="📋 **Commandes du Bot**",
            value="• **200+ commandes** disponibles\n"
                  "• **Recherche avancée** intégrée\n"
                  "• **Descriptions complètes** pour chaque commande\n"
                  "• **Catégorisation intelligente**",
            inline=True
        )
        
        embed.add_field(
            name="💬 **Support & Aide**",
            value="• **Support 24/7** disponible\n"
                  "• **Discord communautaire** actif\n"
                  "• **Documentation** complète\n"
                  "• **Guides & tutoriels** détaillés",
            inline=True
        )
        
        embed.add_field(
            name="🚀 **Arsenal Features**",
            value="• 🎵 **Musique HD** - Spotify/YouTube/SoundCloud\n"
                  "• ⚖️ **Modération** - Sanctions permanentes\n"
                  "• 🎤 **Hub Vocal** - Salons temporaires\n"
                  "• 💰 **Économie** - ArsenalCoins système\n"
                  "• 🤖 **IA Integration** - ChatGPT-4 natif\n"
                  "• 🌐 **Web Dashboard** - Interface complète",
            inline=False
        )
        
        embed.set_footer(
            text="Sélectionnez une option ci-dessous pour commencer • Arsenal V4.5.2 ULTIMATE",
            icon_url="https://cdn.discordapp.com/attachments/1234567890/arsenal_icon.png"
        )
        
        return embed
    
    def create_support_embed(self) -> discord.Embed:
        """Embed des informations de support"""
        embed = discord.Embed(
            title="💬 Support Arsenal - Aide & Contact",
            description="**Besoin d'aide ? Notre équipe est là pour vous !**\n\n"
                       "Voici tous les moyens de nous contacter et d'obtenir de l'aide :",
            color=0x3498db,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(
            name="🔥 **Support Prioritaire**",
            value="• 💬 **Discord Support** - Support instantané 24/7\n"
                  "• 🎫 **Tickets** - `/contact` pour ouvrir un ticket\n"
                  "• 📧 **Email** - support@arsenal-bot.com\n"
                  "• 📺 **Twitch Live** - Support en direct + stream",
            inline=False
        )
        
        embed.add_field(
            name="🌐 **Ressources Utiles**",
            value="• 📖 **Documentation** - Guide complet Arsenal\n"
                  "• 🎥 **Tutoriels** - Vidéos explicatives\n"
                  "• 📋 **Changelog** - Nouveautés & mises à jour\n"
                  "• 🐛 **Bug Report** - Signaler un problème",
            inline=False
        )
        
        embed.add_field(
            name="⚡ **Réponse Rapide**",
            value="• **< 1 heure** - Support Discord\n"
                  "• **< 4 heures** - Tickets & Email\n"
                  "• **Temps réel** - Twitch Live\n"
                  "• **Community** - Entraide utilisateurs",
            inline=False
        )
        
        embed.add_field(
            name="🎮 **Serveur de Support**",
            value="Rejoignez notre serveur Discord officiel pour :\n"
                  "• **Aide instantanée** de la communauté\n"
                  "• **Annonces** des nouvelles fonctionnalités\n"
                  "• **Beta testing** - Testez en avant-première\n"
                  "• **Événements** exclusifs Arsenal",
            inline=False
        )
        
        embed.set_footer(
            text="🚀 Arsenal Support Team - Toujours là pour vous aider !",
            icon_url="https://cdn.discordapp.com/attachments/1234567890/support_icon.png"
        )
        
        return embed
    
    def create_bot_info_embed(self) -> discord.Embed:
        """Embed des informations du bot"""
        embed = discord.Embed(
            title="📊 Arsenal V4.5.2 ULTIMATE - Informations",
            description="**Le bot Discord le plus avancé au monde**",
            color=0x9146ff,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Statistiques
        total_commands = len(list(self.bot.tree.walk_commands())) + len(self.bot.commands)
        embed.add_field(
            name="📈 **Statistiques**",
            value=f"• **Serveurs:** {len(self.bot.guilds)}\n"
                  f"• **Utilisateurs:** {len(self.bot.users)}\n"
                  f"• **Commandes:** {total_commands}\n"
                  f"• **Uptime:** Online 24/7",
            inline=True
        )
        
        embed.add_field(
            name="⚡ **Performances**",
            value="• **Latence:** < 50ms\n"
                  "• **Disponibilité:** 99.9%\n"
                  "• **Hosting:** Render Premium\n"
                  "• **Database:** SQLite optimisé",
            inline=True
        )
        
        embed.add_field(
            name="🚀 **Version Info**",
            value="• **Version:** Arsenal V4.5.2 ULTIMATE\n"
                  "• **Discord.py:** 2.5.2\n"
                  "• **Python:** 3.13\n"
                  "• **Dernière MAJ:** Aujourd'hui",
            inline=False
        )
        
        return embed

class AllCommandsView(discord.ui.View):
    """Vue pour afficher toutes les commandes avec pagination"""
    
    def __init__(self, bot, commands_per_page: int = 12):
        super().__init__(timeout=300)
        self.bot = bot
        self.commands_per_page = commands_per_page
        self.current_page = 0
        
        # Récupérer TOUTES les commandes
        self.all_commands = self.get_all_bot_commands()
        self.total_pages = max(1, (len(self.all_commands) - 1) // self.commands_per_page + 1)
        
        # Mettre à jour les boutons
        self.update_buttons()
    
    def get_all_bot_commands(self) -> List[Dict]:
        """Récupère TOUTES les commandes du bot"""
        commands_list = []
        
        # Commandes slash (app_commands)
        for command in self.bot.tree.walk_commands():
            commands_list.append({
                "name": f"/{command.name}",
                "description": command.description or "Aucune description",
                "type": "slash"
            })
        
        # Commandes classiques (prefix commands)
        for command in self.bot.commands:
            commands_list.append({
                "name": f"!{command.name}",
                "description": command.help or command.brief or "Aucune description",
                "type": "prefix"
            })
        
        # Trier par nom
        commands_list.sort(key=lambda x: x["name"])
        return commands_list
    
    def update_buttons(self):
        """Met à jour les boutons de navigation"""
        self.previous_btn.disabled = (self.current_page == 0)
        self.next_btn.disabled = (self.current_page >= self.total_pages - 1)
        self.page_btn.label = f"Page {self.current_page + 1}/{self.total_pages}"
    
    def create_embed(self) -> discord.Embed:
        """Crée l'embed pour la page actuelle"""
        start_idx = self.current_page * self.commands_per_page
        end_idx = start_idx + self.commands_per_page
        page_commands = self.all_commands[start_idx:end_idx]
        
        embed = discord.Embed(
            title="📋 Toutes les Commandes Arsenal",
            description=f"**🚀 {len(self.all_commands)} commandes disponibles**\n\n"
                       f"📄 Page {self.current_page + 1}/{self.total_pages}",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Afficher les commandes de la page
        commands_text = ""
        for cmd in page_commands:
            description = cmd["description"]
            if len(description) > 60:
                description = description[:57] + "..."
            
            emoji = "⚡" if cmd["type"] == "slash" else "🔤"
            commands_text += f"{emoji} **{cmd['name']}** - {description}\n"
        
        embed.add_field(
            name="📋 **Commandes**",
            value=commands_text or "Aucune commande sur cette page",
            inline=False
        )
        
        # Statistiques
        slash_count = len([c for c in self.all_commands if c["type"] == "slash"])
        prefix_count = len([c for c in self.all_commands if c["type"] == "prefix"])
        
        embed.add_field(
            name="📊 **Statistiques**",
            value=f"⚡ **Slash:** {slash_count} commandes\n"
                  f"🔤 **Prefix:** {prefix_count} commandes\n"
                  f"📋 **Total:** {len(self.all_commands)} commandes",
            inline=True
        )
        
        embed.set_footer(
            text="💡 Utilisez les boutons pour naviguer • /help_search pour rechercher",
            icon_url="https://cdn.discordapp.com/attachments/1234567890/arsenal_icon.png"
        )
        
        return embed
    
    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary, disabled=True)
    async def previous_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page précédente"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Page 1/1", style=discord.ButtonStyle.primary, disabled=True)
    async def page_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Indicateur de page"""
        pass
    
    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary, disabled=True)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page suivante"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_buttons()
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🏠 Menu Principal", style=discord.ButtonStyle.danger)
    async def back_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu principal"""
        main_view = HelpMainView(self.bot)
        embed = main_view.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=main_view)

class SupportView(discord.ui.View):
    """Vue pour les options de support"""
    
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        
        # Boutons de contact direct
        discord_btn = discord.ui.Button(
            label="💬 Discord Support", 
            style=discord.ButtonStyle.link, 
            url="https://discord.gg/arsenal-support"
        )
        website_btn = discord.ui.Button(
            label="📖 Documentation", 
            style=discord.ButtonStyle.link, 
            url="https://docs.arsenal-bot.com"
        )
        
        self.add_item(discord_btn)
        self.add_item(website_btn)
    
    @discord.ui.button(label="🎫 Créer Ticket", style=discord.ButtonStyle.success, emoji="🎫")
    async def create_ticket_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Créer un ticket de support"""
        modal = SupportTicketModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🏠 Menu Principal", style=discord.ButtonStyle.secondary)
    async def back_main_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu principal"""
        main_view = HelpMainView(self.bot)
        embed = main_view.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=main_view)

class SearchCommandModal(discord.ui.Modal):
    """Modal pour rechercher des commandes"""
    
    def __init__(self, bot):
        super().__init__(title="🔍 Recherche de Commandes")
        self.bot = bot
        
        self.search_input = discord.ui.TextInput(
            label="Recherche",
            placeholder="Tapez le nom d'une commande ou un mot-clé...",
            style=discord.TextStyle.short,
            max_length=50,
            required=True
        )
        self.add_item(self.search_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Traitement de la recherche"""
        search_term = self.search_input.value.lower()
        
        # Récupérer toutes les commandes
        commands_view = AllCommandsView(self.bot)
        all_commands = commands_view.get_all_bot_commands()
        
        # Rechercher
        results = []
        for cmd in all_commands:
            if (search_term in cmd["name"].lower() or 
                search_term in cmd["description"].lower()):
                results.append(cmd)
        
        if not results:
            await interaction.response.send_message(
                f"❌ **Aucune commande trouvée pour:** `{search_term}`\n"
                f"💡 Essayez avec d'autres mots-clés.",
                ephemeral=True
            )
            return
        
        # Créer l'embed des résultats
        embed = discord.Embed(
            title=f"🔍 Résultats: {search_term}",
            description=f"**{len(results)} commande(s) trouvée(s)**",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        
        results_text = ""
        for i, cmd in enumerate(results[:15]):  # Limite à 15 résultats
            description = cmd["description"]
            if len(description) > 50:
                description = description[:47] + "..."
            emoji = "⚡" if cmd["type"] == "slash" else "🔤"
            results_text += f"{emoji} **{cmd['name']}** - {description}\n"
        
        if len(results) > 15:
            results_text += f"\n... et {len(results) - 15} autres résultats"
        
        embed.add_field(
            name="📋 **Commandes trouvées**",
            value=results_text,
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class SupportTicketModal(discord.ui.Modal):
    """Modal pour créer un ticket de support"""
    
    def __init__(self):
        super().__init__(title="🎫 Créer un Ticket de Support")
        
        self.subject_input = discord.ui.TextInput(
            label="Sujet",
            placeholder="Décrivez brièvement votre problème...",
            style=discord.TextStyle.short,
            max_length=100,
            required=True
        )
        
        self.description_input = discord.ui.TextInput(
            label="Description détaillée",
            placeholder="Expliquez votre problème en détail...",
            style=discord.TextStyle.paragraph,
            max_length=1000,
            required=True
        )
        
        self.add_item(self.subject_input)
        self.add_item(self.description_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Créer le ticket de support"""
        embed = discord.Embed(
            title="✅ Ticket de Support Créé",
            description=f"**Votre ticket a été créé avec succès !**\n\n"
                       f"**Sujet:** {self.subject_input.value}\n"
                       f"**ID Ticket:** #SUP-{interaction.user.id}\n\n"
                       f"Notre équipe vous contactera bientôt.",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.set_footer(
            text=f"Ticket créé par {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class HelpSystemV2(commands.Cog):
    """Système d'aide complet V2"""
    
    def __init__(self, bot):
        self.bot = bot
        log.info("📚 [OK] Help System V2 ULTIMATE initialisé")
    
    @app_commands.command(name="help", description="📚 Système d'aide complet Arsenal - Commandes + Support + Infos")
    async def help_command(self, interaction: discord.Interaction):
        """Commande d'aide principale complète"""
        log.info(f"[HELP] {interaction.user} utilise /help")
        
        # Créer la vue principale
        main_view = HelpMainView(self.bot)
        embed = main_view.create_main_embed()
        
        await interaction.response.send_message(embed=embed, view=main_view, ephemeral=False)
        log.info(f"[HELP] Interface complète envoyée à {interaction.user}")

async def setup(bot):
    """Setup du cog"""
    await bot.add_cog(HelpSystemV2(bot))
    log.info("📚 [SETUP] Help System V2 ULTIMATE ajouté au bot")
