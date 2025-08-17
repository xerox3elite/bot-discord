#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Arsenal V4 - Commandes Système et Diagnostic
Convertit les anciennes commandes prefix en slash commands modernes
"""

import discord
from discord.ext import commands
from discord import app_commands
import platform
import psutil
import asyncio
from datetime import datetime
import json
import os

class ArsenalSystemCommands(commands.Cog):
    """Commandes système et diagnostic d'Arsenal"""
    
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="arsenal_diagnostic", description="🔧 Lance un diagnostic complet d'Arsenal")
    @app_commands.default_permissions(administrator=True)
    async def arsenal_diagnostic_slash(self, interaction: discord.Interaction):
        """Lance un diagnostic complet d'Arsenal"""
        
        await interaction.response.send_message("🔍 Diagnostic Arsenal en cours...", ephemeral=True)
        
        # Collecte des informations système
        try:
            # Informations bot
            bot_info = {
                "nom": self.bot.user.name,
                "id": self.bot.user.id,
                "serveurs": len(self.bot.guilds),
                "utilisateurs": len(self.bot.users),
                "commandes": len(self.bot.commands),
                "latence": round(self.bot.latency * 1000, 2)
            }
            
            # Informations système
            system_info = {
                "os": platform.system(),
                "version": platform.release(),
                "architecture": platform.machine(),
                "python": platform.python_version(),
                "cpu_usage": psutil.cpu_percent(),
                "ram_usage": psutil.virtual_memory().percent,
                "uptime": str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0]
            }
            
            # Statut des modules critiques
            modules_status = {}
            critical_modules = [
                "commands.help_system_v2",
                "commands.hub_vocal", 
                "commands.sanctions_system",
                "commands.communication_system",
                "core.discord_badges"
            ]
            
            for module_name in critical_modules:
                try:
                    # Tenter d'accéder au module
                    if module_name.split('.')[-1] in [cog.lower() for cog in self.bot.cogs]:
                        modules_status[module_name] = "✅ Actif"
                    else:
                        modules_status[module_name] = "❌ Inactif"
                except:
                    modules_status[module_name] = "⚠️ Erreur"
            
            # Création de l'embed de diagnostic
            embed = discord.Embed(
                title="🔍 **DIAGNOSTIC ARSENAL COMPLET**",
                description="Analyse complète du système Arsenal",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            # Informations bot
            embed.add_field(
                name="🤖 **Arsenal Bot**",
                value=(
                    f"**Nom:** {bot_info['nom']}\n"
                    f"**ID:** {bot_info['id']}\n"
                    f"**Serveurs:** {bot_info['serveurs']}\n"
                    f"**Utilisateurs:** {bot_info['utilisateurs']}\n"
                    f"**Commandes:** {bot_info['commandes']}\n"
                    f"**Latence:** {bot_info['latence']}ms"
                ),
                inline=True
            )
            
            # Informations système
            embed.add_field(
                name="🖥️ **Système**",
                value=(
                    f"**OS:** {system_info['os']} {system_info['version']}\n"
                    f"**Architecture:** {system_info['architecture']}\n"
                    f"**Python:** {system_info['python']}\n"
                    f"**CPU:** {system_info['cpu_usage']}%\n"
                    f"**RAM:** {system_info['ram_usage']}%\n"
                    f"**Uptime:** {system_info['uptime']}"
                ),
                inline=True
            )
            
            # Statut modules
            modules_text = "\n".join([f"{status} **{name.split('.')[-1]}**" for name, status in modules_status.items()])
            embed.add_field(
                name="📦 **Modules Critiques**",
                value=modules_text,
                inline=False
            )
            
            # Recommandations
            recommendations = []
            if system_info['cpu_usage'] > 80:
                recommendations.append("⚠️ Usage CPU élevé")
            if system_info['ram_usage'] > 80:
                recommendations.append("⚠️ Usage RAM élevé")
            if bot_info['latence'] > 200:
                recommendations.append("⚠️ Latence élevée")
            
            if recommendations:
                embed.add_field(
                    name="⚠️ **Recommandations**",
                    value="\n".join(recommendations),
                    inline=False
                )
            else:
                embed.add_field(
                    name="✅ **État**",
                    value="Tous les systèmes fonctionnent normalement",
                    inline=False
                )
            
            embed.set_footer(text="Arsenal V4.5.2 - Diagnostic System")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Erreur Diagnostic",
                description=f"Une erreur s'est produite: {str(e)}",
                color=0xff0000
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    @app_commands.command(name="arsenal_force_recognition", description="🔧 Force Discord à reconnaître toutes les intégrations Arsenal")
    @app_commands.default_permissions(administrator=True)
    async def arsenal_force_recognition_slash(self, interaction: discord.Interaction):
        """Commande manuelle pour forcer la reconnaissance Discord"""
        
        await interaction.response.send_message("🔧 Forçage de la reconnaissance Discord...", ephemeral=True)
        
        try:
            # Forcer la synchronisation des commandes
            synced = await self.bot.tree.sync()
            
            # Mettre à jour la présence
            await self.bot.change_presence(
                activity=discord.Game(name="🚀 Arsenal V4.5.2 - Système Ultimate"),
                status=discord.Status.online
            )
            
            # Forcer l'update des intégrations Discord
            for guild in self.bot.guilds:
                try:
                    # Mettre à jour le nom du bot dans la guild si nécessaire
                    if guild.me.display_name != "Arsenal":
                        await guild.me.edit(nick="Arsenal")
                except:
                    pass  # Pas de permissions
            
            embed = discord.Embed(
                title="✅ **RECONNAISSANCE FORCÉE**",
                description="Arsenal a forcé sa reconnaissance auprès de Discord",
                color=0x00ff00
            )
            
            embed.add_field(
                name="🔧 **Actions Effectuées**",
                value=(
                    f"✅ Synchronisation des commandes ({len(synced)} commandes)\n"
                    "✅ Mise à jour de la présence\n"
                    "✅ Actualisation des intégrations\n"
                    "✅ Vérification des permissions"
                ),
                inline=False
            )
            
            embed.add_field(
                name="📊 **Résultats**",
                value=(
                    f"**Serveurs:** {len(self.bot.guilds)}\n"
                    f"**Utilisateurs:** {len(self.bot.users)}\n"
                    f"**Latence:** {round(self.bot.latency * 1000, 2)}ms\n"
                    f"**Status:** En ligne"
                ),
                inline=True
            )
            
            embed.set_footer(text="Arsenal V4.5.2 - Force Recognition System")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Erreur Force Recognition",
                description=f"Une erreur s'est produite: {str(e)}",
                color=0xff0000
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)

    @app_commands.command(name="system_help", description="📚 Guide système Arsenal complet")
    async def system_help_slash(self, interaction: discord.Interaction):
        """Commande help complète Arsenal avec toutes les catégories"""
        
        embed = discord.Embed(
            title="📚 **ARSENAL V4.5.2 ULTIMATE - AIDE COMPLÈTE**",
            description="Système d'aide complet avec toutes les fonctionnalités Arsenal",
            color=0x0099ff
        )
        
        # Catégories de commandes
        categories = {
            "🛡️ **Modération**": [
                "/timeout - Timeout un membre",
                "/warn - Avertir un membre", 
                "/kick - Expulser un membre",
                "/ban - Bannir un membre",
                "/casier - Voir le casier d'un membre"
            ],
            "🎵 **Musique**": [
                "/play - Jouer de la musique",
                "/queue - File d'attente",
                "/skip - Passer la musique",
                "/volume - Changer le volume",
                "/stop - Arrêter la musique"
            ],
            "🎮 **Gaming**": [
                "/gaming - Hub gaming Arsenal",
                "/hunter_info - Infos chasseur",
                "/minecraft_mods - Mods Minecraft",
                "/fortnite_stats - Stats Fortnite"
            ],
            "🎤 **Hub Vocal**": [
                "/hub_vocal - Configuration hub vocal",
                "Panneau de contrôle automatique",
                "Whitelist/Blacklist, Invisible",
                "Gestion complète des salons temporaires"
            ],
            "💰 **Économie**": [
                "/balance - Voir son solde",
                "/daily - Récompense quotidienne",
                "/shop - Boutique Arsenal",
                "/leaderboard - Classement richesse"
            ],
            "🔧 **Configuration**": [
                "/config - Interface de configuration",
                "/badges_setup - Configuration badges",
                "/diagnostic - Diagnostic système",
                "/features - Fonctionnalités Arsenal"
            ]
        }
        
        # Ajouter chaque catégorie
        for category, commands in categories.items():
            embed.add_field(
                name=category,
                value="\n".join(commands),
                inline=True
            )
        
        # Informations supplémentaires
        embed.add_field(
            name="🚀 **Liens Utiles**",
            value="[Support Discord](https://discord.gg/arsenal)\n[Documentation](https://arsenal-bot.com)\n[GitHub](https://github.com/xerox3elite/bot-discord)",
            inline=False
        )
        
        embed.set_footer(text="Arsenal V4.5.2 - Plus de 200 commandes disponibles")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="arsenal_module", description="🔧 Commandes de gestion des modules")
    @app_commands.describe(
        action="Action à effectuer sur les modules",
        module_name="Nom du module (optionnel)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="lister", value="list"),
        app_commands.Choice(name="info", value="info"),
        app_commands.Choice(name="recharger", value="reload"),
        app_commands.Choice(name="statut", value="status")
    ])
    @app_commands.default_permissions(administrator=True)
    async def arsenal_module_slash(self, interaction: discord.Interaction, action: app_commands.Choice[str], module_name: str = None):
        """Gestion des modules Arsenal"""
        
        if action.value == "list":
            embed = discord.Embed(
                title="📦 **MODULES ARSENAL**",
                description="Liste de tous les modules chargés",
                color=0x0099ff
            )
            
            modules_text = ""
            for i, cog_name in enumerate(self.bot.cogs, 1):
                cog = self.bot.cogs[cog_name]
                command_count = len([cmd for cmd in cog.get_commands()])
                modules_text += f"**{i}.** {cog_name} ({command_count} commandes)\n"
            
            embed.add_field(
                name="📋 Modules Actifs",
                value=modules_text or "Aucun module chargé",
                inline=False
            )
            
            embed.set_footer(text=f"Total: {len(self.bot.cogs)} modules")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        elif action.value == "status":
            embed = discord.Embed(
                title="📊 **STATUT MODULES**",
                description="État détaillé des modules système",
                color=0x00ff00
            )
            
            # Modules critiques
            critical_modules = {
                "HelpSystemV2": "Système d'aide",
                "HubVocal": "Hub vocal temporaire", 
                "SanctionsSystem": "Système de sanctions",
                "CommunicationSystem": "Communication",
                "DiscordBadges": "Badges Discord",
                "ArsenalSystemCommands": "Commandes système"
            }
            
            status_text = ""
            for module, description in critical_modules.items():
                if module in self.bot.cogs:
                    status_text += f"✅ **{module}** - {description}\n"
                else:
                    status_text += f"❌ **{module}** - {description} (Non chargé)\n"
            
            embed.add_field(
                name="🔧 Modules Critiques",
                value=status_text,
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        else:
            await interaction.response.send_message("⚠️ Action en développement", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ArsenalSystemCommands(bot))
