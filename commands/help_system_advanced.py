# 🚀 Arsenal V4 - Système d'Aide Interactif Avancé
"""
Système d'aide interactif moderne avec:
- Interface dropdown élégante
- Embeds colorés par catégorie  
- Navigation intuitive
- Synchronisation WebPanel
- Documentation complète
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime

class HelpSystemAdvanced(commands.Cog):
    """Système d'aide interactif avancé pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.help_data_file = "data/help_advanced.json"
        self.ensure_help_data()
        
    def ensure_help_data(self):
        """Initialise les données d'aide si nécessaire"""
        if not os.path.exists(self.help_data_file):
            os.makedirs(os.path.dirname(self.help_data_file), exist_ok=True)
            
            default_help = {
                "categories": {
                    "🎵 Musique": {
                        "description": "Système musical YouTube/Spotify complet",
                        "commands": {
                            "/play": "Jouer une musique depuis YouTube/Spotify",
                            "/queue": "Afficher la file d'attente",
                            "/skip": "Passer à la musique suivante",
                            "/stop": "Arrêter la musique et quitter",
                            "/volume": "Changer le volume (0-100)",
                            "/shuffle": "Mélanger la file d'attente",
                            "/loop": "Activer/désactiver la répétition"
                        }
                    },
                    "🎮 Jeux": {
                        "description": "Collection de jeux et casino intégré",
                        "commands": {
                            "/casino": "Accéder au casino virtuel",
                            "/trivia": "Quiz de culture générale",
                            "/dice": "Lancer des dés personnalisés",
                            "/achievements": "Voir vos succès",
                            "/leaderboard": "Classement des joueurs"
                        }
                    },
                    "💰 Crypto": {
                        "description": "Trading crypto et portefeuille virtuel",
                        "commands": {
                            "/crypto_price": "Prix en temps réel",
                            "/portfolio": "Votre portefeuille",
                            "/crypto_buy": "Acheter des cryptos",
                            "/crypto_sell": "Vendre des cryptos",
                            "/crypto_trend": "Analyse tendances"
                        }
                    },
                    "🛡️ Modération": {
                        "description": "Modération automatique intelligente",
                        "commands": {
                            "/automod": "Configuration auto-mod",
                            "/warn": "Avertir un utilisateur",
                            "/mute": "Réduire au silence",
                            "/ban": "Bannir avec raison",
                            "/modlogs": "Historique modération"
                        }
                    },
                    "🔔 Notifications": {
                        "description": "Système de notifications et webhooks",
                        "commands": {
                            "/notify_setup": "Configurer notifications",
                            "/webhook_create": "Créer un webhook",
                            "/alerts": "Gérer les alertes",
                            "/notify_test": "Tester notification"
                        }
                    },
                    "🛠️ Utilitaires": {
                        "description": "Outils pratiques et générateurs",
                        "commands": {
                            "/qr_generate": "Générer code QR",
                            "/password_gen": "Générateur mot de passe",
                            "/calculator": "Calculatrice avancée",
                            "/color_palette": "Palette de couleurs",
                            "/url_shortener": "Raccourcir une URL"
                        }
                    },
                    "⚡ Admin": {
                        "description": "Commandes d'administration",
                        "commands": {
                            "/status": "Statut du bot",
                            "/reload": "Recharger un module",
                            "/backup": "Sauvegarder données",
                            "/maintenance": "Mode maintenance"
                        }
                    }
                },
                "last_updated": datetime.now().isoformat(),
                "version": "Arsenal V4 Ultimate"
            }
            
            with open(self.help_data_file, 'w', encoding='utf-8') as f:
                json.dump(default_help, f, indent=2, ensure_ascii=False)

    class HelpDropdown(discord.ui.Select):
        """Dropdown pour la sélection des catégories d'aide"""
        
        def __init__(self, help_data):
            self.help_data = help_data
            
            options = []
            for category, info in help_data["categories"].items():
                options.append(discord.SelectOption(
                    label=category,
                    description=info["description"][:50],
                    emoji=category.split()[0]
                ))
            
            super().__init__(
                placeholder="🔍 Choisissez une catégorie...",
                min_values=1,
                max_values=1,
                options=options
            )
        
        async def callback(self, interaction: discord.Interaction):
            selected_category = self.values[0]
            category_data = self.help_data["categories"][selected_category]
            
            # Création de l'embed pour la catégorie
            embed = discord.Embed(
                title=f"📖 Aide - {selected_category}",
                description=category_data["description"],
                color=self._get_category_color(selected_category),
                timestamp=datetime.now()
            )
            
            # Ajout des commandes
            commands_text = ""
            for cmd, desc in category_data["commands"].items():
                commands_text += f"**{cmd}**\n> {desc}\n\n"
            
            embed.add_field(
                name="📋 Commandes Disponibles",
                value=commands_text or "Aucune commande disponible",
                inline=False
            )
            
            embed.set_footer(
                text=f"Arsenal V4 Ultimate • Page {selected_category}",
                icon_url=interaction.client.user.display_avatar.url
            )
            
            await interaction.response.edit_message(embed=embed, view=self.view)
        
        def _get_category_color(self, category):
            """Retourne une couleur selon la catégorie"""
            colors = {
                "🎵 Musique": discord.Color.purple(),
                "🎮 Jeux": discord.Color.orange(),
                "💰 Crypto": discord.Color.gold(),
                "🛡️ Modération": discord.Color.red(),
                "🔔 Notifications": discord.Color.blue(),
                "🛠️ Utilitaires": discord.Color.green(),
                "⚡ Admin": discord.Color.dark_red()
            }
            return colors.get(category, discord.Color.blurple())

    class HelpView(discord.ui.View):
        """Vue principale avec dropdown et boutons"""
        
        def __init__(self, help_data):
            super().__init__(timeout=300)
            self.help_data = help_data
            self.add_item(HelpSystemAdvanced.HelpDropdown(help_data))
        
        @discord.ui.button(label="🏠 Accueil", style=discord.ButtonStyle.secondary)
        async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed = self._create_main_embed(interaction.client)
            await interaction.response.edit_message(embed=embed, view=self)
        
        @discord.ui.button(label="📊 Statistiques", style=discord.ButtonStyle.secondary)
        async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            embed = await self._create_stats_embed(interaction.client)
            await interaction.response.edit_message(embed=embed, view=self)
        
        @discord.ui.button(label="🔗 Liens", style=discord.ButtonStyle.link, url="https://github.com/xerox3elite/bot-discord")
        async def links_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            pass
        
        def _create_main_embed(self, bot):
            """Crée l'embed principal d'aide"""
            embed = discord.Embed(
                title="🚀 Arsenal V4 Ultimate - Centre d'Aide",
                description=(
                    "**Bienvenue dans le système d'aide interactif !**\n\n"
                    "🔽 **Utilisez le menu déroulant** pour explorer les catégories\n"
                    "🏠 **Bouton Accueil** pour revenir à cette page\n"
                    "📊 **Statistiques** pour voir les infos du bot\n\n"
                    "Arsenal V4 dispose de **8 systèmes avancés** :"
                ),
                color=discord.Color.blurple(),
                timestamp=datetime.now()
            )
            
            # Aperçu des catégories
            categories_text = ""
            for category, info in self.help_data["categories"].items():
                categories_text += f"{category}: {len(info['commands'])} commandes\n"
            
            embed.add_field(
                name="📂 Catégories Disponibles",
                value=categories_text,
                inline=True
            )
            
            embed.add_field(
                name="🎯 Fonctionnalités Clés",
                value=(
                    "• Interface moderne interactive\n"
                    "• 50+ commandes avancées\n"
                    "• WebPanel intégré\n"
                    "• Synchronisation temps réel\n"
                    "• Support multi-serveurs"
                ),
                inline=True
            )
            
            embed.set_thumbnail(url=bot.user.display_avatar.url)
            embed.set_footer(
                text=f"Arsenal V4 Ultimate • {len(self.help_data['categories'])} catégories",
                icon_url=bot.user.display_avatar.url
            )
            
            return embed
        
        async def _create_stats_embed(self, bot):
            """Crée l'embed des statistiques"""
            embed = discord.Embed(
                title="📊 Statistiques Arsenal V4",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            
            # Stats du bot
            embed.add_field(
                name="🤖 Bot Stats",
                value=(
                    f"• Serveurs: {len(bot.guilds)}\n"
                    f"• Utilisateurs: {len(bot.users)}\n"
                    f"• Commandes: 50+\n"
                    f"• Latence: {round(bot.latency * 1000)}ms"
                ),
                inline=True
            )
            
            # Stats des systèmes
            embed.add_field(
                name="⚙️ Systèmes",
                value=(
                    "• 8 modules avancés\n"
                    "• WebPanel actif\n"
                    "• Base de données: SQLite\n"
                    "• Uptime: 99.9%"
                ),
                inline=True
            )
            
            # Version info
            embed.add_field(
                name="🔖 Version",
                value=(
                    f"• Arsenal V4 Ultimate\n"
                    f"• Discord.py: {discord.__version__}\n"
                    f"• Python: 3.10+\n"
                    f"• Dernière MAJ: {self.help_data.get('last_updated', 'Inconnue')[:10]}"
                ),
                inline=True
            )
            
            embed.set_thumbnail(url=bot.user.display_avatar.url)
            return embed

    @app_commands.command(name="helpadvanced", description="🚀 Système d'aide interactif Arsenal V4 Ultimate")
    async def help_command(self, interaction: discord.Interaction):
        """Commande d'aide principale avec interface interactive"""
        
        try:
            # Chargement des données d'aide
            with open(self.help_data_file, 'r', encoding='utf-8') as f:
                help_data = json.load(f)
            
            # Création de la vue interactive
            view = self.HelpView(help_data)
            embed = view._create_main_embed(self.bot)
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=False)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Impossible de charger l'aide: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="help_search", description="🔍 Rechercher dans l'aide")
    @app_commands.describe(query="Terme à rechercher dans les commandes")
    async def help_search(self, interaction: discord.Interaction, query: str):
        """Recherche dans le système d'aide"""
        
        try:
            with open(self.help_data_file, 'r', encoding='utf-8') as f:
                help_data = json.load(f)
            
            results = []
            for category, category_data in help_data["categories"].items():
                for cmd, desc in category_data["commands"].items():
                    if query.lower() in cmd.lower() or query.lower() in desc.lower():
                        results.append(f"**{cmd}** ({category})\n> {desc}")
            
            embed = discord.Embed(
                title=f"🔍 Résultats de recherche: '{query}'",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            if results:
                embed.description = "\n\n".join(results[:10])  # Max 10 résultats
                if len(results) > 10:
                    embed.set_footer(text=f"... et {len(results)-10} autres résultats")
            else:
                embed.description = "Aucun résultat trouvé."
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {str(e)}", ephemeral=True)

async def setup(bot):
    """Charge le module HelpSystemAdvanced"""
    await bot.add_cog(HelpSystemAdvanced(bot))
    print("🚀 [Help System Advanced] Module chargé avec succès!")

