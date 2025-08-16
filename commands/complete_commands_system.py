#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📋 ARSENAL COMPLETE COMMANDS SYSTEM - LISTE TOUTES LES COMMANDES
Système complet qui affiche TOUTES les commandes du bot avec descriptions
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

class AllCommandsView(discord.ui.View):
    """Vue avec pagination pour afficher TOUTES les commandes"""
    
    def __init__(self, bot, commands_per_page: int = 15):
        super().__init__(timeout=300)
        self.bot = bot
        self.commands_per_page = commands_per_page
        self.current_page = 0
        
        # Récupérer TOUTES les commandes du bot
        self.all_commands = self.get_all_bot_commands()
        self.total_pages = (len(self.all_commands) - 1) // self.commands_per_page + 1
        
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
                "type": "slash",
                "category": "Commandes Slash"
            })
        
        # Commandes classiques (prefix commands)
        for command in self.bot.commands:
            commands_list.append({
                "name": f"!{command.name}",
                "description": command.help or command.brief or "Aucune description",
                "type": "prefix",
                "category": "Commandes Classiques"
            })
        
        # Trier par nom
        commands_list.sort(key=lambda x: x["name"])
        
        return commands_list
    
    def update_buttons(self):
        """Met à jour l'état des boutons de pagination"""
        self.previous_page.disabled = (self.current_page == 0)
        self.next_page.disabled = (self.current_page >= self.total_pages - 1)
        
        # Mettre à jour le label du bouton info
        self.page_info.label = f"Page {self.current_page + 1}/{self.total_pages}"
    
    def create_embed(self) -> discord.Embed:
        """Crée l'embed pour la page actuelle"""
        start_idx = self.current_page * self.commands_per_page
        end_idx = start_idx + self.commands_per_page
        
        page_commands = self.all_commands[start_idx:end_idx]
        
        embed = discord.Embed(
            title="📋 Toutes les commandes Arsenal",
            description=f"**🚀 Arsenal V4.5.2 ULTIMATE - {len(self.all_commands)} commandes disponibles**\n\n"
                       f"📄 Page {self.current_page + 1}/{self.total_pages} ({len(page_commands)} commandes)",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Grouper par type
        slash_commands = []
        prefix_commands = []
        
        for cmd in page_commands:
            if cmd["type"] == "slash":
                slash_commands.append(cmd)
            else:
                prefix_commands.append(cmd)
        
        # Afficher les commandes slash
        if slash_commands:
            slash_text = ""
            for cmd in slash_commands:
                description = cmd["description"]
                if len(description) > 50:
                    description = description[:47] + "..."
                slash_text += f"• **{cmd['name']}** - {description}\\n"
            
            embed.add_field(
                name="⚡ **Commandes Slash**",
                value=slash_text[:1024] if slash_text else "Aucune",
                inline=False
            )
        
        # Afficher les commandes classiques
        if prefix_commands:
            prefix_text = ""
            for cmd in prefix_commands:
                description = cmd["description"]
                if len(description) > 50:
                    description = description[:47] + "..."
                prefix_text += f"• **{cmd['name']}** - {description}\\n"
            
            embed.add_field(
                name="🔤 **Commandes Classiques**",
                value=prefix_text[:1024] if prefix_text else "Aucune",
                inline=False
            )
        
        # Statistiques
        total_slash = len([c for c in self.all_commands if c["type"] == "slash"])
        total_prefix = len([c for c in self.all_commands if c["type"] == "prefix"])
        
        embed.add_field(
            name="📊 **Statistiques**",
            value=f"• **Total:** {len(self.all_commands)} commandes\n"
                  f"• **Slash:** {total_slash} commandes\n"
                  f"• **Classiques:** {total_prefix} commandes\n"
                  f"• **Statut:** 🟢 Toutes opérationnelles",
            inline=False
        )
        
        embed.set_footer(
            text="💡 Utilisez /help pour l'interface catégorisée | 🔍 /help_search pour rechercher",
            icon_url="https://cdn.discordapp.com/attachments/1234567890/arsenal_icon.png"
        )
        
        return embed
    
    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page précédente"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Page 1/1", style=discord.ButtonStyle.primary, disabled=True)
    async def page_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Affichage de la page actuelle (non cliquable)"""
        pass
    
    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page suivante"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_buttons()
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🔍 Rechercher", style=discord.ButtonStyle.success)
    async def search_command(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour ouvrir la recherche"""
        modal = SearchCommandModal(self.all_commands)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🏠 Menu principal", style=discord.ButtonStyle.danger)
    async def main_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu principal d'aide"""
        try:
            # Essayer d'importer le HelpSystemV2
            from commands.help_system_v2 import HelpCategoryView
            
            embed = discord.Embed(
                title="📚 Arsenal Help System V2",
                description="**🚀 Arsenal V4.5.2 ULTIMATE - Le bot Discord le plus avancé**\n\n✨ Interface moderne • 200+ commandes • 2000% personnalisation",
                color=0x00ff00,
                timestamp=discord.utils.utcnow()
            )
            
            view = HelpCategoryView(self.bot)
            await interaction.response.edit_message(embed=embed, view=view)
        except ImportError:
            # Fallback si le système d'aide n'est pas disponible
            await interaction.response.send_message(
                "❌ **Système d'aide principal non disponible**\n"
                "Utilisez cette page pour naviguer dans toutes les commandes.",
                ephemeral=True
            )

class SearchCommandModal(discord.ui.Modal):
    """Modal de recherche de commandes"""
    
    def __init__(self, all_commands: List[Dict]):
        super().__init__(title="🔍 Recherche de commandes")
        self.all_commands = all_commands
        
        self.search_input = discord.ui.TextInput(
            label="Terme de recherche",
            placeholder="Tapez le nom d'une commande ou un mot-clé...",
            style=discord.TextStyle.short,
            max_length=50,
            required=True
        )
        self.add_item(self.search_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Traitement de la recherche"""
        search_term = self.search_input.value.lower()
        
        # Rechercher dans les commandes
        results = []
        for cmd in self.all_commands:
            if (search_term in cmd["name"].lower() or 
                search_term in cmd["description"].lower()):
                results.append(cmd)
        
        if not results:
            await interaction.response.send_message(
                f"❌ **Aucune commande trouvée pour:** `{search_term}`\n"
                f"Essayez avec d'autres mots-clés.",
                ephemeral=True
            )
            return
        
        # Créer l'embed des résultats
        embed = discord.Embed(
            title=f"🔍 Résultats de recherche: {search_term}",
            description=f"**{len(results)} commande(s) trouvée(s)**",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        
        results_text = ""
        for i, cmd in enumerate(results[:20]):  # Limite à 20 résultats
            description = cmd["description"]
            if len(description) > 60:
                description = description[:57] + "..."
            results_text += f"**{i+1}.** {cmd['name']} - {description}\\n"
        
        if len(results) > 20:
            results_text += f"\\n... et {len(results) - 20} autres résultats"
        
        embed.add_field(
            name="📋 **Commandes trouvées**",
            value=results_text,
            inline=False
        )
        
        embed.set_footer(
            text=f"💡 Recherche: '{search_term}' | Total: {len(results)} résultats",
            icon_url="https://cdn.discordapp.com/attachments/1234567890/arsenal_icon.png"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class CompleteCommandsSystem(commands.Cog):
    """Système complet d'affichage de toutes les commandes"""
    
    def __init__(self, bot):
        self.bot = bot
        log.info("📋 [OK] Complete Commands System initialisé")
    
    @app_commands.command(name="commands", description="📋 Afficher TOUTES les commandes du bot avec descriptions")
    async def all_commands(self, interaction: discord.Interaction):
        """Commande pour afficher toutes les commandes du bot"""
        
        log.info(f"[COMMANDS] {interaction.user} utilise /commands")
        
        # Créer la vue avec pagination
        view = AllCommandsView(self.bot)
        embed = view.create_embed()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)
        log.info(f"[COMMANDS] Liste complète envoyée - {len(view.all_commands)} commandes")
    
    @app_commands.command(name="help_search", description="🔍 Rechercher une commande spécifique")
    @app_commands.describe(query="Terme à rechercher dans les noms et descriptions de commandes")
    async def search_commands(self, interaction: discord.Interaction, query: str):
        """Recherche dans toutes les commandes"""
        
        log.info(f"[SEARCH] {interaction.user} recherche: {query}")
        
        # Récupérer toutes les commandes
        view = AllCommandsView(self.bot)
        all_commands = view.all_commands
        
        # Rechercher
        search_term = query.lower()
        results = []
        for cmd in all_commands:
            if (search_term in cmd["name"].lower() or 
                search_term in cmd["description"].lower()):
                results.append(cmd)
        
        if not results:
            await interaction.response.send_message(
                f"❌ **Aucune commande trouvée pour:** `{query}`\n"
                f"💡 Essayez avec d'autres mots-clés ou utilisez `/commands` pour voir toutes les commandes.",
                ephemeral=True
            )
            return
        
        # Créer l'embed des résultats
        embed = discord.Embed(
            title=f"🔍 Résultats: {query}",
            description=f"**{len(results)} commande(s) trouvée(s)**",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Diviser en pages si trop de résultats
        if len(results) <= 15:
            results_text = ""
            for i, cmd in enumerate(results):
                description = cmd["description"]
                if len(description) > 70:
                    description = description[:67] + "..."
                results_text += f"**{i+1}.** `{cmd['name']}` - {description}\\n"
            
            embed.add_field(
                name="📋 **Commandes trouvées**",
                value=results_text,
                inline=False
            )
        else:
            # Trop de résultats, afficher les premiers et proposer d'affiner
            results_text = ""
            for i, cmd in enumerate(results[:10]):
                description = cmd["description"]
                if len(description) > 60:
                    description = description[:57] + "..."
                results_text += f"**{i+1}.** `{cmd['name']}` - {description}\\n"
            
            results_text += f"\\n**... et {len(results) - 10} autres résultats**"
            
            embed.add_field(
                name="📋 **Premiers résultats** (10 affichés)",
                value=results_text,
                inline=False
            )
            
            embed.add_field(
                name="💡 **Conseil**",
                value=f"Trop de résultats ! Affinez votre recherche ou utilisez `/commands` pour parcourir toutes les commandes.",
                inline=False
            )
        
        embed.set_footer(
            text=f"🔍 Recherche: '{query}' | {len(results)} résultats sur {len(all_commands)} commandes",
            icon_url="https://cdn.discordapp.com/attachments/1234567890/arsenal_icon.png"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=False)
        log.info(f"[SEARCH] {len(results)} résultats trouvés pour '{query}'")

async def setup(bot):
    """Setup du cog"""
    await bot.add_cog(CompleteCommandsSystem(bot))
    log.info("📋 [SETUP] Complete Commands System ajouté au bot")
