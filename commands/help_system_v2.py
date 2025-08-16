#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📚 ARSENAL HELP SYSTEM V2 - SYSTÈME D'AIDE RÉVOLUTIONNAIRE
Interface d'aide moderne avec navigation intuitive et design épuré
Par xerox3elite - Arsenal V4.5.2 ULTIMATE
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Dict, List, Optional
import asyncio

class HelpCategoryView(discord.ui.View):
    """Vue pour sélectionner une catégorie d'aide"""
    
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
    
    @discord.ui.select(
        placeholder="🔍 Sélectionnez une catégorie...",
        options=[
            discord.SelectOption(
                label="🚀 Commandes Principales",
                value="main",
                description="Profile, Config, Thèmes, Streaming",
                emoji="🚀"
            ),
            discord.SelectOption(
                label="⚖️ Modération & Sanctions",
                value="moderation",
                description="Timeout, Warn, Kick, Ban, Casier",
                emoji="⚖️"
            ),
            discord.SelectOption(
                label="🎤 Vocal & Musique",
                value="vocal",
                description="Hub vocal, Musique, Contrôles",
                emoji="🎤"
            ),
            discord.SelectOption(
                label="💰 Économie & Niveaux",
                value="economy",
                description="ArsenalCoins, Boutique, Levels",
                emoji="💰"
            ),
            discord.SelectOption(
                label="🎮 Gaming & Divertissement",
                value="gaming",
                description="Hunt Royal, Mini-jeux, APIs",
                emoji="🎮"
            ),
            discord.SelectOption(
                label="🛡️ AutoMod & Sécurité",
                value="automod",
                description="Protection automatique, Anti-raid",
                emoji="🛡️"
            ),
            discord.SelectOption(
                label="🎫 Tickets & Support",
                value="tickets",
                description="Absence, Support, Gestion",
                emoji="🎫"
            ),
            discord.SelectOption(
                label="⚙️ Configuration & Admin",
                value="admin",
                description="Setup, Permissions, Système",
                emoji="⚙️"
            ),
        ]
    )
    async def select_category(self, interaction: discord.Interaction, select: discord.ui.Select):
        category = select.values[0]
        
        embed, view = self.get_category_embed(category)
        await interaction.response.edit_message(embed=embed, view=view)
    
    def get_category_embed(self, category: str) -> tuple[discord.Embed, discord.ui.View]:
        """Génère l'embed et la vue pour une catégorie"""
        
        categories_data = {
            "main": {
                "title": "🚀 Commandes Principales",
                "color": 0x00ff00,
                "commands": {
                    "/profile_2000": "💎 Profil révolutionnaire avec streaming",
                    "/config": "🔧 Configuration complète et unifiée",
                    "/themes_2000": "🎨 Personnalisation thèmes avancée",
                    "/status_streaming": "📺 Gérer statuts streaming",
                    "/features": "✨ Toutes les fonctionnalités Arsenal",
                    "/diagnostic": "🔍 Vérification état du bot",
                    "/version": "📋 Informations version actuelle"
                }
            },
            "moderation": {
                "title": "⚖️ Modération & Sanctions",
                "color": 0xff0000,
                "commands": {
                    "/timeout": "⏰ Timeout un membre avec durée",
                    "/warn": "⚠️ Avertir un membre",
                    "/kick": "👢 Expulser un membre",
                    "/ban": "🔨 Bannir un membre",
                    "/mute": "🔇 Couper le micro d'un membre",
                    "/casier": "📋 Voir le casier judiciaire",
                    "/untimeout": "✅ Retirer un timeout",
                    "/unban": "✅ Débannir un utilisateur",
                    "/unmute": "✅ Retirer le mute",
                    "/unwarn": "✅ Retirer un avertissement"
                }
            },
            "vocal": {
                "title": "🎤 Vocal & Musique",
                "color": 0x9b59b6,
                "commands": {
                    "/hub_vocal_setup": "🎤 Configurer hub vocal temporaire",
                    "/play": "🎵 Jouer de la musique",
                    "/pause": "⏸️ Mettre en pause",
                    "/skip": "⏭️ Passer à la suivante",
                    "/queue": "📋 Voir la file d'attente",
                    "/volume": "🔊 Régler le volume",
                    "/loop": "🔁 Activer la répétition",
                    "/shuffle": "🔀 Mélanger la playlist"
                }
            },
            "economy": {
                "title": "💰 Économie & Niveaux",
                "color": 0xf1c40f,
                "commands": {
                    "/balance": "💰 Voir son solde ArsenalCoins",
                    "/daily": "🎁 Récompense quotidienne",
                    "/shop": "🛒 Boutique serveur",
                    "/buy": "💳 Acheter un article",
                    "/level": "🏆 Voir son niveau",
                    "/leaderboard": "📊 Classement serveur",
                    "/give": "💸 Donner des coins",
                    "/work": "💼 Travailler pour gagner des coins"
                }
            },
            "gaming": {
                "title": "🎮 Gaming & Divertissement",
                "color": 0x1abc9c,
                "commands": {
                    "/hunt": "🏹 Hunt Royal - Chasse aux trésors",
                    "/hunt_profile": "👤 Profil Hunt Royal",
                    "/hunt_leaderboard": "🏆 Classement Hunt Royal",
                    "/dice": "🎲 Lancer de dés",
                    "/coinflip": "🪙 Pile ou face",
                    "/8ball": "🎱 Boule magique",
                    "/trivia": "🧠 Questions culture générale"
                }
            },
            "automod": {
                "title": "🛡️ AutoMod & Sécurité",
                "color": 0xe74c3c,
                "commands": {
                    "/automod": "🛡️ Configuration auto-modération",
                    "/antiraid": "🔒 Protection anti-raid",
                    "/antispam": "📵 Protection anti-spam",
                    "/automod_logs": "📊 Logs auto-modération",
                    "/whitelist": "✅ Liste blanche",
                    "/blacklist": "❌ Liste noire"
                }
            },
            "tickets": {
                "title": "🎫 Tickets & Support",
                "color": 0xff9900,
                "commands": {
                    "/absence_setup": "🔧 Configurer tickets d'absence",
                    "/absence_panel": "🎫 Créer panel tickets",
                    "/ticket_close": "🔒 Fermer un ticket",
                    "/ticket_logs": "📊 Logs des tickets",
                    "/support_setup": "🆘 Configurer support",
                    "/contact": "📞 Contacter l'équipe"
                }
            },
            "admin": {
                "title": "⚙️ Configuration & Admin",
                "color": 0x95a5a6,
                "commands": {
                    "/setup": "⚙️ Configuration initiale serveur",
                    "/permissions": "🔐 Gérer les permissions",
                    "/logs": "📋 Configuration des logs",
                    "/backup": "💾 Sauvegarde serveur",
                    "/restore": "🔄 Restaurer serveur",
                    "/maintenance": "🔧 Mode maintenance",
                    "/stats": "📊 Statistiques détaillées"
                }
            }
        }
        
        if category not in categories_data:
            category = "main"
        
        data = categories_data[category]
        
        embed = discord.Embed(
            title=f"📚 Arsenal Help - {data['title']}",
            description="**Arsenal V4.5.2 ULTIMATE - Le bot Discord le plus avancé**",
            color=data['color'],
            timestamp=discord.utils.utcnow()
        )
        
        # Ajouter les commandes
        commands_text = ""
        for cmd, desc in data['commands'].items():
            commands_text += f"`{cmd}` - {desc}\n"
        
        embed.add_field(
            name=f"🔥 **Commandes {data['title']}**",
            value=commands_text,
            inline=False
        )
        
        # Informations supplémentaires selon la catégorie
        if category == "main":
            embed.add_field(
                name="✨ **Fonctionnalités Uniques**",
                value="• 🎯 **2000% Personnalisation** - Interface révolutionnaire\n• 🚀 **Streaming Integration** - Twitch/YouTube natif\n• 💎 **Profile Ultimate** - Le plus avancé Discord\n• 🔥 **Configuration Unifiée** - Un seul `/config`",
                inline=True
            )
            embed.add_field(
                name="🌟 **Arsenal Avantages**",
                value="• ⚡ **Performance Max** - Optimisé Render\n• 🛡️ **Sécurité Totale** - Anti-crash intégré\n• 🎨 **Design Moderne** - Interface épurée\n• 🔄 **Mises à jour Auto** - Toujours à jour",
                inline=True
            )
        elif category == "moderation":
            embed.add_field(
                name="📋 **Casier Judiciaire**",
                value="• 🏛️ **Permanent** - Survit aux départs/retours\n• 📊 **Statistiques** - Analytics complètes\n• 📱 **Notifications MP** - Info utilisateur\n• ⚖️ **Historique Complet** - Toutes les actions",
                inline=False
            )
        elif category == "vocal":
            embed.add_field(
                name="🎤 **Hub Vocal Avancé**",
                value="• 🏠 **Salons Temporaires** - Auto-création/suppression\n• 🎛️ **Contrôles Utilisateur** - Panel complet\n• 🔒 **Permissions** - Verrouillage/invite\n• 📊 **Statistiques** - Temps vocal trackés",
                inline=False
            )
        
        # Footer avec liens utiles
        embed.set_footer(
            text="🔗 arsenal-bot.com • 📺 Twitch: xerox3elite • 💬 Support: /contact",
            icon_url="https://cdn.discordapp.com/attachments/1234567890/arsenal_logo.png"
        )
        
        # Vue de retour
        view = HelpBackView(self.bot)
        return embed, view

class HelpBackView(discord.ui.View):
    """Vue pour retourner à la sélection principale avec support"""
    
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        
        # Ajouter les boutons link manuellement avec la bonne méthode
        website_btn = discord.ui.Button(label="🌐 Site Web", style=discord.ButtonStyle.link, url="https://arsenal-bot.com")
        twitch_btn = discord.ui.Button(label="📺 Twitch", style=discord.ButtonStyle.link, url="https://twitch.tv/xerox3elite")
        
        self.add_item(website_btn)
        self.add_item(twitch_btn)
    
    @discord.ui.button(label="⬅️ Retour au menu", style=discord.ButtonStyle.secondary)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Créer un nouvel embed principal et vue
        embed = discord.Embed(
            title="📚 Arsenal Help System V2",
            description="**🚀 Arsenal V4.5.2 ULTIMATE - Le bot Discord le plus avancé**\n\n✨ Interface moderne • 200+ commandes • 2000% personnalisation",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="🎯 **Fonctionnalités Principales**",
            value="• 🔧 **Configuration Unifiée** - Un seul `/config`\n• ⚖️ **Sanctions Permanentes** - Casier judiciaire\n• 🎤 **Hub Vocal Avancé** - Salons temporaires\n• 💰 **Économie Complète** - ArsenalCoins système",
            inline=True
        )
        
        embed.add_field(
            name="🚀 **Technologies Avancées**",
            value="• 🤖 **IA Integration** - ChatGPT-4 natif\n• 🎮 **Gaming APIs** - Steam/Riot/Xbox\n• 🌐 **Web Dashboard** - Interface web\n• 📱 **Mobile App** - Application native",
            inline=True
        )
        
        embed.add_field(
            name="💎 **Arsenal Exclusive**",
            value="• 🔥 **2000% Personnalisation** - Unique au monde\n• 📺 **Streaming Integration** - Twitch/YouTube\n• 🛡️ **Anti-Crash System** - Stabilité maximale\n• ⚡ **Performance Optimisée** - Render natif",
            inline=False
        )
        
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1234567890/arsenal_logo.png")
        embed.set_footer(
            text="Sélectionnez une catégorie ci-dessous pour explorer les commandes ⬇️",
            icon_url="https://cdn.discordapp.com/attachments/1234567890/arsenal_icon.png"
        )
        
        view = HelpCategoryView(self.bot)
        await interaction.response.edit_message(embed=embed, view=view)
    
    # Boutons avec callback (pas de decorateur pour éviter les conflits)
    @discord.ui.button(label="💬 Support", style=discord.ButtonStyle.success, emoji="💬")
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="💬 Support Arsenal",
            description="**Besoin d'aide ? Contactez notre équipe !**",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="📞 **Méthodes de contact**",
            value="• `/contact` - Ticket support rapide\n• 📺 **Twitch Live** - Support en direct\n• 🌐 **Site web** - Documentation complète\n• 📧 **Email** - support@arsenal-bot.com",
            inline=False
        )
        
        embed.add_field(
            name="⚡ **Support Prioritaire**",
            value="• 🚀 **Réponse < 1h** en journée\n• 🔧 **Aide configuration** personnalisée\n• 💡 **Suggestions** intégrées rapidement\n• 🛡️ **Support technique** avancé",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def get_main_embed(self) -> discord.Embed:
        """Embed principal du système d'aide"""
        embed = discord.Embed(
            title="📚 Arsenal Help System V2",
            description="**🚀 Arsenal V4.5.2 ULTIMATE - Le bot Discord le plus avancé**\n\n✨ Interface moderne • 200+ commandes • 2000% personnalisation",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="🎯 **Fonctionnalités Principales**",
            value="• 🔧 **Configuration Unifiée** - Un seul `/config`\n• ⚖️ **Sanctions Permanentes** - Casier judiciaire\n• 🎤 **Hub Vocal Avancé** - Salons temporaires\n• 💰 **Économie Complète** - ArsenalCoins système",
            inline=True
        )
        
        embed.add_field(
            name="🚀 **Technologies Avancées**",
            value="• 🤖 **IA Integration** - ChatGPT-4 natif\n• 🎮 **Gaming APIs** - Steam/Riot/Xbox\n• 🌐 **Web Dashboard** - Interface web\n• 📱 **Mobile App** - Application native",
            inline=True
        )
        
        embed.add_field(
            name="💎 **Arsenal Exclusive**",
            value="• 🔥 **2000% Personnalisation** - Unique au monde\n• 📺 **Streaming Integration** - Twitch/YouTube\n• 🛡️ **Anti-Crash System** - Stabilité maximale\n• ⚡ **Performance Optimisée** - Render natif",
            inline=False
        )
        
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1234567890/arsenal_logo.png")
        embed.set_footer(
            text="Sélectionnez une catégorie ci-dessous pour explorer les commandes ⬇️",
            icon_url="https://cdn.discordapp.com/attachments/1234567890/arsenal_icon.png"
        )
        
        return embed

class HelpSystemV2(commands.Cog):
    """Système d'aide révolutionnaire V2"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="📚 Système d'aide Arsenal - Interface moderne")
    async def help_command(self, interaction: discord.Interaction):
        """Commande d'aide principale avec interface moderne"""
        
        embed = discord.Embed(
            title="📚 Arsenal Help System V2",
            description="**🚀 Arsenal V4.5.2 ULTIMATE - Le bot Discord le plus avancé**\n\n✨ Interface moderne • 200+ commandes • 2000% personnalisation",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="🎯 **Fonctionnalités Principales**",
            value="• 🔧 **Configuration Unifiée** - Un seul `/config`\n• ⚖️ **Sanctions Permanentes** - Casier judiciaire\n• 🎤 **Hub Vocal Avancé** - Salons temporaires\n• 💰 **Économie Complète** - ArsenalCoins système",
            inline=True
        )
        
        embed.add_field(
            name="🚀 **Technologies Avancées**",
            value="• 🤖 **IA Integration** - ChatGPT-4 natif\n• 🎮 **Gaming APIs** - Steam/Riot/Xbox\n• 🌐 **Web Dashboard** - Interface web\n• 📱 **Mobile App** - Application native",
            inline=True
        )
        
        embed.add_field(
            name="💎 **Arsenal Exclusive**",
            value="• 🔥 **2000% Personnalisation** - Unique au monde\n• 📺 **Streaming Integration** - Twitch/YouTube\n• 🛡️ **Anti-Crash System** - Stabilité maximale\n• ⚡ **Performance Optimisée** - Render natif",
            inline=False
        )
        
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1234567890/arsenal_logo.png")
        embed.set_footer(
            text="Sélectionnez une catégorie ci-dessous pour explorer les commandes ⬇️",
            icon_url="https://cdn.discordapp.com/attachments/1234567890/arsenal_icon.png"
        )
        
        view = HelpCategoryView(self.bot)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="commands", description="📋 Liste rapide de toutes les commandes")
    async def commands_list(self, interaction: discord.Interaction):
        """Liste rapide de toutes les commandes"""
        
        embed = discord.Embed(
            title="📋 Arsenal Commands - Liste Rapide",
            description="**Toutes les commandes Arsenal en un coup d'œil**",
            color=0x3498db,
            timestamp=discord.utils.utcnow()
        )
        
        # Commandes par catégorie - Version condensée
        categories = [
            ("🚀 Principales", "/profile_2000, /config, /themes_2000, /diagnostic"),
            ("⚖️ Modération", "/timeout, /warn, /kick, /ban, /mute, /casier"),
            ("🎤 Vocal", "/hub_vocal_setup, /play, /pause, /skip, /volume"),
            ("💰 Économie", "/balance, /daily, /shop, /buy, /level"),
            ("🎮 Gaming", "/hunt, /dice, /coinflip, /8ball, /trivia"),
            ("🛡️ AutoMod", "/automod, /antiraid, /antispam, /whitelist"),
            ("🎫 Tickets", "/absence_setup, /absence_panel, /contact"),
            ("⚙️ Admin", "/setup, /permissions, /logs, /backup, /stats")
        ]
        
        for category, commands in categories:
            embed.add_field(
                name=category,
                value=f"`{commands.replace(', ', '`, `')}`",
                inline=False
            )
        
        embed.set_footer(text="Utilisez /help pour l'interface complète avec descriptions détaillées")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpSystemV2(bot))
    print("📚 [OK] Help System V2 - Interface révolutionnaire et moderne chargée !")
