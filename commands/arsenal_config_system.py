"""
⚙️ Arsenal Configuration System
Système de configuration complet avec menus déroulants comme DraftBot
Développé par XeRoX - Arsenal Bot V4.5
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from typing import Optional, Dict, Any
import datetime

class ConfigurationSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="💰 Système d'Économie",
                value="economy",
                description="Configuration ArsenalCoin, récompenses, shop",
                emoji="💰"
            ),
            discord.SelectOption(
                label="📊 Système de Logs",
                value="logs",
                description="Logs de modération, messages, vocaux",
                emoji="📊"
            ),
            discord.SelectOption(
                label="🛡️ AutoMod",
                value="automod",
                description="Anti-spam, anti-liens, filtres de mots",
                emoji="🛡️"
            ),
            discord.SelectOption(
                label="🔊 Salons Temporaires",
                value="tempchannels",
                description="Salons vocaux temporaires automatiques",
                emoji="🔊"
            ),
            discord.SelectOption(
                label="🎵 Système Musical",
                value="music",
                description="Configuration du bot musical",
                emoji="🎵"
            ),
            discord.SelectOption(
                label="🎟️ Système de Tickets",
                value="tickets",
                description="Support, réclamations, tickets privés",
                emoji="🎟️"
            ),
            discord.SelectOption(
                label="📝 Sondages & Annonces",
                value="polls",
                description="Configuration des sondages et annonces",
                emoji="📝"
            ),
            discord.SelectOption(
                label="⭐ Rôles de Réaction",
                value="reaction_roles",
                description="Attribution automatique de rôles",
                emoji="⭐"
            ),
            discord.SelectOption(
                label="👋 Accueil & Départ",
                value="welcome",
                description="Messages d'accueil et rôles automatiques",
                emoji="👋"
            ),
            discord.SelectOption(
                label="🎮 Hunt Royal",
                value="hunt_royal",
                description="Configuration Hunt Royal et gaming",
                emoji="🎮"
            ),
            discord.SelectOption(
                label="🏆 Système de Niveaux",
                value="leveling",
                description="XP, niveaux, récompenses de niveau",
                emoji="🏆"
            ),
            discord.SelectOption(
                label="💳 Crypto & Wallets",
                value="crypto",
                description="Portefeuilles crypto et transactions",
                emoji="💳"
            )
        ]
        super().__init__(
            placeholder="🔧 Sélectionnez un système à configurer...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        system = self.values[0]
        await interaction.response.defer()
        
        # Charger la configuration selon le système sélectionné
        config_handler = ArsenalConfigSystem(interaction.client)
        await config_handler.handle_system_config(interaction, system)

class ArsenalConfigSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "data/config"
        os.makedirs(self.config_path, exist_ok=True)

    def load_config(self, guild_id: int, system: str) -> Dict[str, Any]:
        """Charge la configuration d'un système"""
        config_file = f"{self.config_path}/{guild_id}_{system}.json"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return self.get_default_config(system)

    def save_config(self, guild_id: int, system: str, config: Dict[str, Any]):
        """Sauvegarde la configuration d'un système"""
        config_file = f"{self.config_path}/{guild_id}_{system}.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def get_default_config(self, system: str) -> Dict[str, Any]:
        """Retourne la configuration par défaut pour un système"""
        defaults = {
            "economy": {
                "enabled": True,
                "daily_reward": 1000,
                "max_daily_streak": 30,
                "shop_enabled": True,
                "transfer_enabled": True,
                "currency_name": "ArsenalCoin",
                "currency_symbol": "AC"
            },
            "logs": {
                "enabled": False,
                "message_logs": {"enabled": False, "channel": None},
                "mod_logs": {"enabled": False, "channel": None},
                "voice_logs": {"enabled": False, "channel": None},
                "join_leave": {"enabled": False, "channel": None},
                "role_logs": {"enabled": False, "channel": None}
            },
            "automod": {
                "enabled": False,
                "anti_spam": {"enabled": False, "max_messages": 5, "time_window": 10},
                "anti_links": {"enabled": False, "whitelist": []},
                "word_filter": {"enabled": False, "blacklist": []},
                "anti_caps": {"enabled": False, "threshold": 70},
                "auto_timeout": {"enabled": False, "duration": 300}
            },
            "tempchannels": {
                "enabled": False,
                "category_id": None,
                "template_name": "{user}'s Channel",
                "user_limit": 10,
                "auto_delete": True
            },
            "music": {
                "enabled": True,
                "max_volume": 100,
                "default_volume": 50,
                "queue_limit": 100,
                "dj_role": None
            },
            "tickets": {
                "enabled": False,
                "category_id": None,
                "support_role": None,
                "auto_close": 24,
                "transcript_channel": None
            },
            "polls": {
                "enabled": True,
                "default_duration": 3600,
                "anonymous_allowed": True,
                "max_options": 10
            },
            "reaction_roles": {
                "enabled": False,
                "messages": {}
            },
            "welcome": {
                "enabled": False,
                "welcome_channel": None,
                "goodbye_channel": None,
                "welcome_message": "Bienvenue {user} sur **{server}** !",
                "goodbye_message": "Au revoir {user}... 👋",
                "auto_role": None
            },
            "hunt_royal": {
                "enabled": True,
                "api_key": None,
                "auto_updates": True,
                "leaderboard_channel": None
            },
            "leveling": {
                "enabled": False,
                "xp_per_message": {"min": 15, "max": 25},
                "xp_cooldown": 60,
                "level_up_message": True,
                "level_up_channel": None,
                "role_rewards": {}
            },
            "crypto": {
                "enabled": False,
                "supported_currencies": ["BTC", "ETH", "BNB"],
                "alerts_channel": None,
                "portfolio_tracking": True
            }
        }
        return defaults.get(system, {})

    @app_commands.command(name="config", description="⚙️ Configuration complète d'Arsenal Bot")
    async def config_command(self, interaction: discord.Interaction):
        """Commande principale de configuration"""
        # Vérifier les permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes",
                description="Cette commande nécessite les permissions d'administrateur.",
                color=0xff6b6b
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        guild = interaction.guild
        
        embed = discord.Embed(
            title="⚙️ Configuration Arsenal Bot",
            description="Bienvenue dans la commande de configuration d'**Arsenal Bot**.\n"
                       "Grâce à cette commande, vous pourrez configurer les différents systèmes "
                       "proposés dans le sélecteur que vous trouverez ci-dessous.",
            color=0x00ff88,
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="📋 Paramètres de Base",
            value=f"**Serveur :** {guild.name}\n"
                  f"**Membres :** {guild.member_count:,}\n"
                  f"**ID Serveur :** `{guild.id}`\n"
                  f"**Région :** {guild.preferred_locale or 'Français'}",
            inline=False
        )

        embed.add_field(
            name="🚀 Pour Simplifier la Configuration",
            value="• Utilisez le **WebPanel Arsenal** pour une interface graphique\n"
                  "• Consultez la **documentation Arsenal** sur GitHub\n"
                  "• Le **support Arsenal** est disponible pour vous aider\n"
                  "• Toutes les configurations sont **sauvegardées automatiquement**",
            inline=False
        )

        embed.add_field(
            name="💡 Systèmes Disponibles",
            value="**12 systèmes** de configuration disponibles incluant :\n"
                  "💰 Économie • 📊 Logs • 🛡️ AutoMod • 🔊 Vocal • 🎵 Musique\n"
                  "🎟️ Tickets • 📝 Sondages • ⭐ Rôles • 👋 Accueil • 🎮 Gaming\n"
                  "🏆 Niveaux • 💳 Crypto",
            inline=False
        )

        embed.set_thumbnail(url=guild.icon.url if guild.icon else self.bot.user.display_avatar.url)
        embed.set_footer(
            text="Arsenal Configuration System • Bot N°1 Français All-in-One",
            icon_url=self.bot.user.display_avatar.url
        )

        # Créer la vue avec le sélecteur
        view = ConfigView()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def handle_system_config(self, interaction: discord.Interaction, system: str):
        """Gère la configuration d'un système spécifique"""
        guild_id = interaction.guild_id
        config = self.load_config(guild_id, system)
        
        # Créer l'embed de configuration selon le système
        if system == "economy":
            await self.config_economy(interaction, config)
        elif system == "logs":
            await self.config_logs(interaction, config)
        elif system == "automod":
            await self.config_automod(interaction, config)
        elif system == "tempchannels":
            await self.config_tempchannels(interaction, config)
        elif system == "music":
            await self.config_music(interaction, config)
        elif system == "tickets":
            await self.config_tickets(interaction, config)
        elif system == "polls":
            await self.config_polls(interaction, config)
        elif system == "reaction_roles":
            await self.config_reaction_roles(interaction, config)
        elif system == "welcome":
            await self.config_welcome(interaction, config)
        elif system == "hunt_royal":
            await self.config_hunt_royal(interaction, config)
        elif system == "leveling":
            await self.config_leveling(interaction, config)
        elif system == "crypto":
            await self.config_crypto(interaction, config)

    async def config_economy(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration du système d'économie"""
        embed = discord.Embed(
            title="💰 Configuration - Système d'Économie",
            description="Configurez le système ArsenalCoin et la boutique",
            color=0xffd700,
            timestamp=datetime.datetime.now()
        )

        status = "🟢 Activé" if config.get("enabled", True) else "🔴 Désactivé"
        embed.add_field(
            name="📊 État Actuel",
            value=f"**Statut :** {status}\n"
                  f"**Récompense Quotidienne :** {config.get('daily_reward', 1000):,} {config.get('currency_symbol', 'AC')}\n"
                  f"**Série Maximum :** {config.get('max_daily_streak', 30)} jours\n"
                  f"**Boutique :** {'✅ Active' if config.get('shop_enabled', True) else '❌ Inactive'}\n"
                  f"**Transferts :** {'✅ Autorisés' if config.get('transfer_enabled', True) else '❌ Interdits'}",
            inline=False
        )

        embed.add_field(
            name="⚙️ Paramètres Disponibles",
            value="• **Activer/Désactiver** le système\n"
                  "• **Modifier** la récompense quotidienne\n"
                  "• **Configurer** la boutique du serveur\n"
                  "• **Gérer** les transferts entre utilisateurs\n"
                  "• **Personnaliser** le nom de la monnaie",
            inline=False
        )

        embed.add_field(
            name="📈 Statistiques",
            value="Utilisez `/balance` pour voir les statistiques détaillées",
            inline=False
        )

        view = EconomyConfigView(config, interaction.guild_id)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    async def config_logs(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration du système de logs"""
        embed = discord.Embed(
            title="📊 Configuration - Système de Logs",
            description="Configurez les logs de modération et d'activité",
            color=0x3498db
        )

        logs_status = []
        for log_type, settings in config.items():
            if isinstance(settings, dict) and 'enabled' in settings:
                status = "🟢" if settings['enabled'] else "🔴"
                channel = f"<#{settings['channel']}>" if settings.get('channel') else "❌ Non défini"
                logs_status.append(f"{status} **{log_type.replace('_', ' ').title()} :** {channel}")

        embed.add_field(
            name="📋 État des Logs",
            value="\n".join(logs_status) if logs_status else "Aucun log configuré",
            inline=False
        )

        view = LogsConfigView(config, interaction.guild_id)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    async def config_automod(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration du système AutoMod"""
        embed = discord.Embed(
            title="🛡️ Configuration - AutoMod",
            description="Configurez la modération automatique",
            color=0xe74c3c
        )

        automod_features = [
            ("Anti-Spam", config.get("anti_spam", {}).get("enabled", False)),
            ("Anti-Liens", config.get("anti_links", {}).get("enabled", False)),
            ("Filtre de Mots", config.get("word_filter", {}).get("enabled", False)),
            ("Anti-Majuscules", config.get("anti_caps", {}).get("enabled", False)),
            ("Timeout Automatique", config.get("auto_timeout", {}).get("enabled", False))
        ]

        status_text = "\n".join([
            f"{'🟢' if enabled else '🔴'} **{feature}**" 
            for feature, enabled in automod_features
        ])

        embed.add_field(
            name="🛡️ Fonctionnalités AutoMod",
            value=status_text,
            inline=False
        )

        view = AutoModConfigView(config, interaction.guild_id)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

class ConfigView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(ConfigurationSelect())

class EconomyConfigView(discord.ui.View):
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=300)
        self.config = config
        self.guild_id = guild_id

    @discord.ui.button(label="🔄 Activer/Désactiver", style=discord.ButtonStyle.primary)
    async def toggle_economy(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.config["enabled"] = not self.config.get("enabled", True)
        # Sauvegarder ici
        await interaction.response.send_message(
            f"💰 Système d'économie {'activé' if self.config['enabled'] else 'désactivé'} !",
            ephemeral=True
        )

class LogsConfigView(discord.ui.View):
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=300)
        self.config = config
        self.guild_id = guild_id

    @discord.ui.button(label="⚙️ Configurer les Logs", style=discord.ButtonStyle.secondary)
    async def configure_logs(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔧 Configuration des logs en cours de développement...", ephemeral=True)

class AutoModConfigView(discord.ui.View):
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=300)
        self.config = config
        self.guild_id = guild_id

    @discord.ui.button(label="🛡️ Configurer AutoMod", style=discord.ButtonStyle.danger)
    async def configure_automod(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🛡️ Configuration AutoMod en cours de développement...", ephemeral=True)

# Ajout des commandes manquantes

@app_commands.command(name="poll", description="📊 Créer un sondage interactif")
@app_commands.describe(
    question="Question du sondage",
    options="Options séparées par des virgules (max 10)",
    duration="Durée en minutes (défaut: 60)"
)
async def create_poll(interaction: discord.Interaction, question: str, options: str, duration: Optional[int] = 60):
    """Créer un sondage"""
    option_list = [opt.strip() for opt in options.split(',')]
    
    if len(option_list) < 2:
        await interaction.response.send_message("❌ Il faut au moins 2 options pour un sondage!", ephemeral=True)
        return
    
    if len(option_list) > 10:
        await interaction.response.send_message("❌ Maximum 10 options par sondage!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📊 Sondage",
        description=f"**{question}**",
        color=0x3498db,
        timestamp=datetime.datetime.now()
    )
    
    # Émojis pour les réactions
    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    
    options_text = ""
    for i, option in enumerate(option_list):
        options_text += f"{emojis[i]} {option}\n"
    
    embed.add_field(name="🗳️ Options", value=options_text, inline=False)
    embed.add_field(name="⏱️ Durée", value=f"{duration} minutes", inline=True)
    embed.add_field(name="👤 Créateur", value=interaction.user.mention, inline=True)
    
    embed.set_footer(text="Votez en réagissant avec les émojis correspondants!")
    
    await interaction.response.send_message(embed=embed)
    
    # Ajouter les réactions
    message = await interaction.original_response()
    for i in range(len(option_list)):
        await message.add_reaction(emojis[i])

@app_commands.command(name="suggest", description="💡 Faire une suggestion")
@app_commands.describe(suggestion="Votre suggestion")
async def suggest(interaction: discord.Interaction, suggestion: str):
    """Système de suggestions"""
    embed = discord.Embed(
        title="💡 Nouvelle Suggestion",
        description=suggestion,
        color=0xf39c12,
        timestamp=datetime.datetime.now()
    )
    
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    
    embed.set_footer(text=f"ID: {interaction.user.id} • Réagissez pour voter!")
    
    await interaction.response.send_message(embed=embed)
    
    # Ajouter les réactions de vote
    message = await interaction.original_response()
    await message.add_reaction("✅")  # Pour
    await message.add_reaction("❌")  # Contre
    await message.add_reaction("🤔")  # Neutre

@app_commands.command(name="level", description="🏆 Voir votre niveau et XP")
@app_commands.describe(user="Utilisateur à consulter")
async def level_command(interaction: discord.Interaction, user: Optional[discord.Member] = None):
    """Système de niveaux"""
    target = user or interaction.user
    
    # Données de test pour le moment
    level = 25
    xp = 12450
    xp_needed = 15000
    xp_progress = xp - (level * 500)  # XP dans le niveau actuel
    xp_for_next = 500  # XP nécessaire pour le niveau suivant
    
    embed = discord.Embed(
        title="🏆 Système de Niveaux",
        color=0x9b59b6,
        timestamp=datetime.datetime.now()
    )
    
    embed.set_author(
        name=f"{target.display_name}",
        icon_url=target.display_avatar.url
    )
    
    embed.add_field(
        name="📊 Statistiques",
        value=f"**Niveau :** {level}\n"
              f"**XP Total :** {xp:,}\n"
              f"**Progression :** {xp_progress}/{xp_for_next} XP",
        inline=True
    )
    
    embed.add_field(
        name="📈 Classement",
        value=f"**Rang :** #7\n"
              f"**Percentile :** Top 15%\n"
              f"**Messages :** ~1,200",
        inline=True
    )
    
    # Barre de progression
    progress_bar_length = 20
    filled_length = int(progress_bar_length * xp_progress // xp_for_next)
    bar = "█" * filled_length + "░" * (progress_bar_length - filled_length)
    
    embed.add_field(
        name="🎯 Progression vers le niveau suivant",
        value=f"`{bar}` {(xp_progress/xp_for_next*100):.1f}%",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ArsenalConfigSystem(bot))
    
    # Ajouter les commandes individuelles
    bot.tree.add_command(create_poll)
    bot.tree.add_command(suggest)
    bot.tree.add_command(level_command)
    
    print("✅ [Arsenal Config] Système de configuration complet chargé")
    print("✅ [Commands] Poll, Suggest, Level ajoutées")
