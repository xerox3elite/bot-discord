#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ARSENAL HELP SYSTEM ULTIMATE - SYSTÈME D'AIDE RÉVOLUTIONNAIRE
Interface moderne avec pagination et toutes les commandes Arsenal
Par xerox3elite - Arsenal V4.5.2 ULTIMATE
"""

import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import math

class HelpPaginationView(discord.ui.View):
    """Vue avec pagination pour l'aide"""
    def __init__(self, bot, user_id, category_data, category_name):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.category_data = category_data
        self.category_name = category_name
        self.current_page = 0
        self.commands_per_page = 8
        
        # Diviser les commandes en pages
        commands_list = list(category_data["commands"].items())
        self.total_pages = math.ceil(len(commands_list) / self.commands_per_page)
        
        self.pages = []
        for i in range(0, len(commands_list), self.commands_per_page):
            page_commands = commands_list[i:i + self.commands_per_page]
            self.pages.append(page_commands)
    
    def create_embed(self, page_index: int):
        """Crée l'embed pour une page donnée"""
        embed = discord.Embed(
            title=f"{self.category_name}",
            description=f"**{self.category_data['description']}**\n\n📋 **Commandes disponibles :**",
            color=self.category_data["color"],
            timestamp=datetime.now(timezone.utc)
        )
        
        # Ajouter les commandes de la page
        if page_index < len(self.pages):
            commands_text = ""
            for cmd, desc in self.pages[page_index]:
                commands_text += f"{cmd}\n└─ {desc}\n\n"
            
            embed.add_field(
                name=f"📋 Page {page_index + 1}/{self.total_pages}",
                value=commands_text,
                inline=False
            )
        
        # Stats
        embed.add_field(
            name="📊 **Informations**",
            value=f"📋 **Total commandes:** {len(self.category_data['commands'])}\n📄 **Pages:** {self.total_pages}\n📍 **Page actuelle:** {page_index + 1}",
            inline=True
        )
        
        embed.set_footer(
            text=f"Arsenal V4.5.2 • Page {page_index + 1}/{self.total_pages}",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        return embed
    
    @discord.ui.button(label="◀️ Précédent", style=discord.ButtonStyle.primary, disabled=True)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut utiliser ces boutons!", ephemeral=True)
            return
        
        self.current_page -= 1
        
        # Mise à jour des boutons
        self.previous_page.disabled = (self.current_page == 0)
        self.next_page.disabled = (self.current_page == self.total_pages - 1)
        
        embed = self.create_embed(self.current_page)
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="▶️ Suivant", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut utiliser ces boutons!", ephemeral=True)
            return
        
        self.current_page += 1
        
        # Mise à jour des boutons
        self.previous_page.disabled = (self.current_page == 0)
        self.next_page.disabled = (self.current_page == self.total_pages - 1)
        
        embed = self.create_embed(self.current_page)
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="📋 Index", style=discord.ButtonStyle.secondary)
    async def back_to_index(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut utiliser ces boutons!", ephemeral=True)
            return
        
        # Retour au menu principal
        view = HelpMainView(self.bot, self.user_id)
        embed = view.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=view)

class HelpMainView(discord.ui.View):
    """Vue principale du système d'aide"""
    def __init__(self, bot, user_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        
        # Base de données complète des commandes Arsenal
        self.help_data = {
            "🎵 Audio & Musique": {
                "description": "Système audio professionnel HD avec IA et streaming",
                "color": 0x9146FF,
                "emoji": "🎵",
                "commands": {
                    "/play [musique]": "🎵 Jouer musique YouTube/Spotify/SoundCloud/Apple Music",
                    "/play_file [fichier]": "📁 Jouer fichier audio uploadé (MP3, WAV, FLAC)",
                    "/queue": "📋 Afficher file d'attente avec contrôles avancés",
                    "/skip [nombre]": "⏭️ Passer à la piste suivante ou numéro spécifique",
                    "/previous": "⏮️ Revenir à la piste précédente",
                    "/pause": "⏸️ Mettre en pause la lecture actuelle",
                    "/resume": "▶️ Reprendre la lecture en pause",
                    "/stop": "⏹️ Arrêter complètement et quitter le vocal",
                    "/volume [0-200]": "🔊 Ajuster volume avec égaliseur professionnel",
                    "/shuffle": "🔀 Mélanger aléatoirement la file d'attente",
                    "/loop [mode]": "🔄 Mode répétition (off/track/queue/autoplay)",
                    "/nowplaying": "🎧 Informations détaillées piste actuelle + contrôles",
                    "/lyrics [chanson]": "📝 Afficher paroles synchronisées avec timestamps",
                    "/radio [station]": "📻 Écouter 500+ stations radio mondiales HD",
                    "/soundboard": "🔊 Jouer sons personnalisés et effets audio",
                    "/equalizer": "🎛️ Égaliseur 10 bandes avec presets professionnels",
                    "/bassboost [niveau]": "🔊 Amplificateur de basses dynamique",
                    "/nightcore": "🎶 Mode Nightcore avec pitch shifting",
                    "/vaporwave": "🌊 Effet Vaporwave avec ralentissement",
                    "/karaoke": "🎤 Mode karaoké avec suppression vocale IA"
                }
            },
            "💰 Économie & Niveaux": {
                "description": "Système économique révolutionnaire ArsenalCoins + crypto",
                "color": 0xFFD700,
                "emoji": "💰",
                "commands": {
                    "/balance [utilisateur]": "💰 Voir solde ArsenalCoins + portefeuille crypto",
                    "/level [utilisateur]": "🏆 Afficher niveau, XP, rang et badges détaillés",
                    "/leaderboard [type]": "📊 Classements (coins, niveaux, temps vocal)",
                    "/daily": "🎁 Bonus quotidien +500-2000 coins (streak x7 max)",
                    "/weekly": "🎊 Récompense hebdomadaire exclusive +5000 coins",
                    "/work [métier]": "💼 Travailler (15 métiers) pour gagner coins",
                    "/crime": "🔫 Activités criminelles risquées pour gros gains",
                    "/rob [utilisateur]": "💸 Voler coins d'autres utilisateurs (risqué)",
                    "/gamble [montant]": "🎰 Casino avec 20+ jeux (slots, poker, blackjack)",
                    "/shop": "🏪 Boutique interactive (rôles, perks, items)",
                    "/inventory": "🎒 Inventaire personnel avec items collectés",
                    "/give [utilisateur] [montant]": "💝 Donner coins à un autre utilisateur",
                    "/pay [utilisateur] [montant]": "💳 Payer utilisateur (transaction sécurisée)",
                    "/crypto [devise]": "₿ Trading crypto 50+ devises (BTC, ETH, etc)",
                    "/portfolio": "📈 Portefeuille crypto avec graphiques temps réel",
                    "/invest [montant]": "📊 Investissement automatique avec intérêts",
                    "/loan [montant]": "🏦 Emprunter coins avec remboursement",
                    "/achievements": "🏅 Débloquer achievements pour récompenses",
                    "/prestige": "⭐ Système prestige pour bonus permanents"
                }
            },
            "🛡️ Modération & Sécurité": {
                "description": "Système de modération IA le plus avancé Discord",
                "color": 0xFF0000,
                "emoji": "🛡️",
                "commands": {
                    "/ban [utilisateur] [raison]": "🔨 Bannir définitivement avec logs détaillés",
                    "/tempban [utilisateur] [durée] [raison]": "⏰ Bannissement temporaire automatique",
                    "/kick [utilisateur] [raison]": "👢 Expulser utilisateur du serveur",
                    "/mute [utilisateur] [durée] [raison]": "🔇 Mute vocal/textuel temporaire ou permanent",
                    "/timeout [utilisateur] [durée]": "⏱️ Timeout Discord natif avec durée flexible",
                    "/warn [utilisateur] [raison]": "⚠️ Avertissement avec système de points",
                    "/warnings [utilisateur]": "📋 Historique avertissements et sanctions",
                    "/clear [nombre] [utilisateur]": "🧹 Supprimer messages (1-1000) avec filtres",
                    "/slowmode [durée]": "🐌 Mode lent canal avec configuration avancée",
                    "/lockdown [canal]": "🔒 Verrouillage d'urgence canal ou serveur",
                    "/unlock [canal]": "🔓 Déverrouiller canal après lockdown",
                    "/automod": "🤖 Configuration AutoMod Discord natif avancé",
                    "/filter [add/remove] [mot]": "🚫 Filtres de mots avec IA contextuelle",
                    "/antiraid [niveau]": "🛡️ Protection anti-raid (low/medium/high/extreme)",
                    "/quarantine [utilisateur]": "🏥 Quarantine automatique utilisateurs suspects",
                    "/massban [fichier]": "💥 Bannissement de masse via liste CSV",
                    "/unban [utilisateur/id]": "✅ Débannir utilisateur avec vérifications",
                    "/modlogs [utilisateur]": "📊 Logs modération complète utilisateur",
                    "/case [numéro]": "📁 Détails case de modération spécifique"
                }
            },
            "🎮 Gaming & Divertissement": {
                "description": "Hub gaming avec 30+ APIs et mini-jeux révolutionnaires",
                "color": 0x00FF00,
                "emoji": "🎮",
                "commands": {
                    "/hunt": "🏹 Hunt Royal - Chasse légendaire multijoueur",
                    "/hunt_profile": "👤 Profil chasseur avec stats détaillées",
                    "/hunt_leaderboard": "🏆 Classement chasseurs mondiaux",
                    "/hunt_inventory": "🎒 Inventaire d'armes et équipements",
                    "/steam [utilisateur]": "🎮 Profil Steam avec jeux et achievements",
                    "/minecraft [joueur]": "⛏️ Stats Minecraft serveur et skin 3D",
                    "/fortnite [joueur]": "🏗️ Stats Fortnite Battle Royale complètes",
                    "/valorant [joueur] [tag]": "🔫 Profil Valorant avec rang et matches",
                    "/lol [invocateur] [région]": "⚔️ Stats League of Legends détaillées",
                    "/csgo [steam_id]": "💥 Profil CS:GO avec ranks et matches",
                    "/overwatch [battletag]": "🦾 Stats Overwatch héros et compétitif",
                    "/apex [joueur] [plateforme]": "🏃 Stats Apex Legends avec KDA",
                    "/8ball [question]": "🎱 Boule magique avec réponses personnalisées",
                    "/dice [faces]": "🎲 Lancer de dés multiples avec animations",
                    "/coinflip": "🪙 Pile ou face avec paris ArsenalCoins",
                    "/rps [choix]": "✂️ Pierre papier ciseaux contre IA",
                    "/trivia [catégorie]": "🧠 Quiz interactif 10+ catégories",
                    "/hangman": "🎪 Jeu du pendu avec mots personnalisés",
                    "/wordle": "📝 Wordle français quotidien avec statistiques",
                    "/chess [utilisateur]": "♟️ Échecs multijoueur avec notation"
                }
            },
            "🎨 Créativité & IA": {
                "description": "Outils créatifs avec IA ChatGPT-4 et génération d'images",
                "color": 0xFF69B4,
                "emoji": "🎨",
                "commands": {
                    "/ai [prompt]": "🤖 ChatGPT-4 conversationnel avec contexte",
                    "/imagine [description]": "🎨 Génération d'images IA DALL-E 3 HD",
                    "/avatar [style] [description]": "👤 Créer avatar personnalisé avec IA",
                    "/meme [template] [texte]": "😂 Générateur memes avec 100+ templates",
                    "/quote [citation] [auteur]": "💭 Citations avec design professionnel",
                    "/ascii [texte]": "🔤 Convertir texte en art ASCII stylisé",
                    "/qr [contenu]": "📱 Générateur QR codes personnalisés",
                    "/color [couleur]": "🎨 Palette couleurs avec codes HEX/RGB",
                    "/logo [nom] [style]": "🏷️ Création logos avec IA design",
                    "/banner [texte] [thème]": "🖼️ Bannières Discord personnalisées HD",
                    "/gif [recherche]": "📸 Recherche GIFs Tenor avec prévisualisation",
                    "/emoji [description]": "😀 Créer emojis personnalisés avec IA",
                    "/sticker [image]": "🏷️ Convertir images en stickers Discord",
                    "/wallpaper [thème] [résolution]": "🖥️ Fonds d'écran générés par IA",
                    "/thumbnail [video/image]": "🖼️ Miniatures personnalisées pour vidéos"
                }
            },
            "⚙️ Utilitaires & Outils": {
                "description": "Outils professionnels pour gestion serveur et productivité",
                "color": 0x607D8B,
                "emoji": "⚙️", 
                "commands": {
                    "/serverinfo": "🏰 Informations serveur complètes avec analytics",
                    "/userinfo [utilisateur]": "👤 Profil utilisateur détaillé avec historique",
                    "/roleinfo [rôle]": "👑 Informations rôle avec membres et permissions",
                    "/channelinfo [canal]": "📺 Statistiques canal avec activité",
                    "/invites [utilisateur]": "📨 Tracker invitations avec leaderboard",
                    "/afk [raison]": "😴 Système AFK automatique avec mentions",
                    "/reminder [durée] [message]": "⏰ Rappels programmés avec récurrence",
                    "/poll [question] [options]": "📊 Sondages interactifs avec graphiques",
                    "/translate [langue] [texte]": "🌍 Traduction 100+ langues avec détection auto",
                    "/weather [ville]": "🌤️ Météo détaillée 7 jours avec cartes",
                    "/time [timezone]": "🕒 Heure mondiale avec fuseaux horaires",
                    "/calculator [expression]": "🧮 Calculatrice avancée avec graphiques",
                    "/password [longueur]": "🔐 Générateur mots de passe sécurisés",
                    "/shorturl [lien]": "🔗 Raccourcisseur URLs avec statistiques",
                    "/encode [type] [texte]": "🔒 Encodage/décodage (base64, hex, etc)",
                    "/hash [algorithme] [texte]": "🔑 Hachage cryptographique sécurisé",
                    "/whois [domaine]": "🌐 Informations domaine et DNS lookup",
                    "/screenshot [url]": "📸 Capture d'écran sites web HD",
                    "/youtube [recherche]": "📹 Recherche YouTube avec prévisualisation"
                }
            },
            "🌐 WebPanel & API": {
                "description": "Dashboard web révolutionnaire et intégrations API",
                "color": 0x00BCD4,
                "emoji": "🌐",
                "commands": {
                    "/dashboard": "💻 Accéder au dashboard web temps réel",
                    "/webpanel_setup": "🔧 Configuration panel web initial",
                    "/api_key": "🔑 Générer clé API pour intégrations externes",
                    "/webhook [url] [message]": "🔗 Créer webhooks personnalisés avancés",
                    "/oauth_setup": "🔐 Configuration OAuth2 pour applications",
                    "/mobile_app": "📱 Télécharger app mobile Arsenal companion",
                    "/web_stats": "📊 Statistiques utilisation web en temps réel",
                    "/custom_domain": "🌐 Configuration domaine personnalisé",
                    "/ssl_certificate": "🔒 Gestion certificats SSL/TLS",
                    "/api_status": "⚡ Statut APIs et services externes",
                    "/rate_limits": "🚦 Limites taux requêtes et quotas",
                    "/integration [service]": "🔌 Intégrations (Spotify, Google, etc)",
                    "/export_data": "💾 Export données serveur (JSON/CSV/XML)",
                    "/backup_cloud": "☁️ Sauvegardes cloud automatiques",
                    "/cdn_setup": "🌍 Configuration CDN pour performances"
                }
            },
            "🤖 Automation & IA": {
                "description": "Automatisation intelligente et workflows avancés",
                "color": 0x795548,
                "emoji": "🤖",
                "commands": {
                    "/autoresponse [trigger] [réponse]": "💬 Réponses automatiques intelligentes",
                    "/autorole [conditions]": "👑 Attribution rôles automatique avancée",
                    "/automod_ai [config]": "🛡️ Modération IA contextuelle",
                    "/workflow [nom] [actions]": "⚙️ Créer workflows automatisés",
                    "/scheduler [tâche] [horaire]": "📅 Planificateur tâches récurrentes",
                    "/trigger [événement] [action]": "⚡ Système déclencheurs personnalisés",
                    "/ai_chatbot [personnalité]": "🤖 Chatbot IA avec personnalités",
                    "/sentiment_analysis [texte]": "😊 Analyse sentiment messages IA",
                    "/spam_detector [config]": "🚫 Détection spam machine learning",
                    "/auto_translation [langues]": "🌍 Traduction automatique canaux",
                    "/smart_pins [config]": "📌 Épinglage automatique messages importants",
                    "/ai_moderation [niveau]": "🤖 Modération IA avec apprentissage",
                    "/content_filter [rules]": "🔍 Filtrage contenu IA avancé",
                    "/auto_backup [fréquence]": "💾 Sauvegardes automatiques programmées",
                    "/smart_welcome [template]": "👋 Messages bienvenue IA personnalisés"
                }
            },
            "🎫 Tickets & Absence": {
                "description": "Système de tickets d'absence avec gestion automatique",
                "color": 0xFF9900,
                "emoji": "🎫",
                "commands": {
                    "/absence_setup": "🔧 Configuration système d'absence (Admin)",
                    "/absence_panel": "🎫 Créer panel de demande de tickets", 
                    "/ticket_absence": "📝 Créer ticket d'absence manuel",
                    "/absence_list": "📋 Liste des absences actives",
                    "/absence_stats": "📊 Statistiques système d'absence",
                    "/absence_config": "⚙️ Configuration avancée absences",
                    "/approve_absence [ID]": "✅ Approuver demande d'absence",
                    "/reject_absence [ID]": "❌ Refuser demande d'absence", 
                    "/close_absence [ID]": "🗑️ Clôturer ticket d'absence",
                    "/extend_absence [ID] [durée]": "⏰ Prolonger période d'absence",
                    "/absence_role [rôle]": "👥 Définir rôle temporaire d'absence",
                    "/absence_logs [canal]": "📝 Canal de logs pour les absences",
                    "/absence_template": "📋 Modèles de demandes d'absence",
                    "/absence_calendar": "📅 Calendrier des absences du serveur",
                    "/absence_notify [utilisateur]": "🔔 Notifications retour d'absence",
                    "/absence_export": "📊 Export données absences (CSV/JSON)"
                }
            }
        }
    
    def create_main_embed(self):
        """Crée l'embed principal du système d'aide"""
        embed = discord.Embed(
            title="🚀 Arsenal Ultimate - Guide Complet",
            description="**Le bot Discord le plus avancé au monde**\n\n🎯 **200+ commandes** • 🔥 **15 catégories** • ⚡ **IA intégrée**\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n📋 **Sélectionnez une catégorie ci-dessous pour voir toutes les commandes :**",
            color=0x7289DA,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Statistiques générales
        total_commands = sum(len(category["commands"]) for category in self.help_data.values())
        
        embed.add_field(
            name="📊 **Statistiques Arsenal**",
            value=f"📋 **Total commandes:** {total_commands}\n🎯 **Catégories:** {len(self.help_data)}\n⚡ **IA ChatGPT-4:** Intégrée\n🌐 **Dashboard Web:** Actif",
            inline=True
        )
        
        embed.add_field(
            name="🔥 **Fonctionnalités Phares**",
            value="🤖 **IA Conversationnelle**\n💰 **Économie Crypto**\n🎵 **Audio HD Streaming**\n🛡️ **AutoMod Ultime**\n🎮 **30+ APIs Gaming**",
            inline=True
        )
        
        embed.add_field(
            name="🌟 **Liens & Support**",
            value="🌐 [Dashboard Web](https://arsenal-bot.com)\n📱 [App Mobile](https://app.arsenal-bot.com)\n💬 [Support Discord](https://discord.gg/arsenal)\n📚 [Documentation](https://docs.arsenal-bot.com)",
            inline=False
        )
        
        embed.set_footer(
            text="Arsenal V4.5.2 • Révolutionne Discord depuis 2025 • By xerox3elite",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        return embed
    
    @discord.ui.select(
        placeholder="📋 Sélectionnez une catégorie pour voir toutes les commandes...",
        options=[
            discord.SelectOption(label="🎵 Audio & Musique", value="🎵 Audio & Musique", description="Système audio HD + streaming", emoji="🎵"),
            discord.SelectOption(label="💰 Économie & Niveaux", value="💰 Économie & Niveaux", description="ArsenalCoins + crypto trading", emoji="💰"),
            discord.SelectOption(label="🛡️ Modération & Sécurité", value="🛡️ Modération & Sécurité", description="AutoMod IA le plus avancé", emoji="🛡️"),
            discord.SelectOption(label="🎮 Gaming & Divertissement", value="🎮 Gaming & Divertissement", description="30+ APIs gaming + mini-jeux", emoji="🎮"),
            discord.SelectOption(label="🎨 Créativité & IA", value="🎨 Créativité & IA", description="ChatGPT-4 + génération images", emoji="🎨"),
        ]
    )
    async def category_select_1(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut utiliser ce menu!", ephemeral=True)
            return
        
        category = select.values[0]
        await self.show_category(interaction, category)
    
    @discord.ui.select(
        placeholder="🔧 Plus de catégories...",
        options=[
            discord.SelectOption(label="⚙️ Utilitaires & Outils", value="⚙️ Utilitaires & Outils", description="Outils productivité pro", emoji="⚙️"),
            discord.SelectOption(label="🌐 WebPanel & API", value="🌐 WebPanel & API", description="Dashboard web révolutionnaire", emoji="🌐"),
            discord.SelectOption(label="🤖 Automation & IA", value="🤖 Automation & IA", description="Workflows intelligents", emoji="🤖"),
            discord.SelectOption(label="🎫 Tickets & Absence", value="🎫 Tickets & Absence", description="Gestion absences automatique", emoji="🎫"),
        ]
    )
    async def category_select_2(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut utiliser ce menu!", ephemeral=True)
            return
        
        category = select.values[0]
        await self.show_category(interaction, category)
    
    async def show_category(self, interaction: discord.Interaction, category: str):
        """Affiche une catégorie avec pagination"""
        if category not in self.help_data:
            await interaction.response.send_message("❌ Catégorie non trouvée!", ephemeral=True)
            return
        
        category_data = self.help_data[category]
        view = HelpPaginationView(self.bot, self.user_id, category_data, category)
        
        # Mettre à jour les boutons de pagination initial
        view.next_page.disabled = (view.total_pages <= 1)
        
        embed = view.create_embed(0)
        await interaction.response.edit_message(embed=embed, view=view)

class ArsenalHelpSystemUltimate(commands.Cog):
    """Système d'aide ultime Arsenal avec pagination"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="🚀 Guide complet Arsenal avec toutes les commandes")
    @app_commands.describe(
        catégorie="Catégorie spécifique à afficher (optionnel)"
    )
    async def help_command(self, interaction: discord.Interaction, catégorie: str = None):
        """Commande d'aide principale avec interface moderne"""
        
        view = HelpMainView(self.bot, interaction.user.id)
        embed = view.create_main_embed()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)
    
    @app_commands.command(name="commands", description="📋 Liste rapide de toutes les commandes")
    async def commands_list(self, interaction: discord.Interaction):
        """Liste rapide de toutes les commandes"""
        
        # Compter toutes les commandes
        view = HelpMainView(self.bot, interaction.user.id)
        total_commands = sum(len(category["commands"]) for category in view.help_data.values())
        
        embed = discord.Embed(
            title="📋 Arsenal - Liste Rapide des Commandes",
            description=f"**{total_commands} commandes disponibles dans {len(view.help_data)} catégories**\n\nUtilise `/help` pour voir les détails complets avec pagination.",
            color=0x00FF00,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Résumé par catégorie
        for category_name, category_data in view.help_data.items():
            embed.add_field(
                name=f"{category_name}",
                value=f"📋 **{len(category_data['commands'])} commandes**\n{category_data['description'][:50]}...",
                inline=True
            )
        
        embed.set_footer(text="Arsenal V4.5.2 • Utilisez /help pour plus de détails")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ArsenalHelpSystemUltimate(bot))
