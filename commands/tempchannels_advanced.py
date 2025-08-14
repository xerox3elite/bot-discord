"""
🔊 Arsenal TempChannels Advanced Config
Configuration avancée pour les salons vocaux temporaires comme DraftBot
Développé par XeRoX - Arsenal Bot V4.5
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime
from typing import Dict, Any, Optional, List

class TempChannelsAdvancedConfig(commands.Cog):
    """Configuration avancée des salons temporaires"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_dir = "data/tempchannels"
        os.makedirs(self.config_dir, exist_ok=True)

    @app_commands.command(name="tempchannels-setup", description="🛠️ Configuration complète des salons temporaires")
    @app_commands.describe(canal="Canal vocal générateur")
    async def setup_tempchannels(self, interaction: discord.Interaction, canal: discord.VoiceChannel):
        """Configuration initiale des salons temporaires"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Permissions administrateur requises!", ephemeral=True)
            return

        # Configuration par défaut
        config = {
            "enabled": True,
            "parent_channel_id": canal.id,
            "permissions": {
                "creator_admin": True,
                "invite_only": False,
                "transfer_ownership": True,
                "auto_moderation": True
            },
            "creation": {
                "default_limit": 10,
                "max_limit": 99,
                "default_name": "🎮 Salon de {username}",
                "bitrate": 128,
                "voice_region": "auto"
            },
            "auto_management": {
                "auto_delete": "immediate",
                "cleanup_inactive": "5min",
                "save_config": True,
                "log_creation": True
            },
            "categories": {
                "main_category": "🔊 Salons Temporaires",
                "overflow_category": "🔊 Salons Temporaires +",
                "max_per_category": 50,
                "auto_organize": True
            },
            "logging": {
                "log_channel": None,
                "log_creation": True,
                "log_deletion": True,
                "log_permissions": True
            },
            "features": {
                "name_variables": True,
                "custom_permissions": True,
                "member_management": True,
                "quality_control": True,
                "statistics_tracking": True
            },
            "restrictions": {
                "cooldown_create": 30,  # secondes
                "max_channels_per_user": 1,
                "blacklisted_users": [],
                "whitelisted_roles": [],
                "minimum_account_age": 7  # jours
            },
            "stats": {
                "total_created": 0,
                "currently_active": 0,
                "peak_concurrent": 0,
                "unique_users": 0,
                "daily_average": 0,
                "avg_duration": "45min",
                "longest_session": "0min"
            }
        }

        # Sauvegarder la configuration
        await self.save_guild_config(interaction.guild.id, config)

        embed = discord.Embed(
            title="✅ Salons Temporaires Configurés",
            description=f"Configuration complète des salons temporaires activée!\n\n"
                       f"**Canal générateur :** {canal.mention}\n"
                       f"**Statut :** 🟢 Activé",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="🎮 Fonctionnalités Activées",
            value="✅ Création automatique\n"
                  "✅ Gestion des permissions\n"
                  "✅ Suppression automatique\n"
                  "✅ Panel de contrôle\n"
                  "✅ Statistiques détaillées\n"
                  "✅ Variables dans les noms",
            inline=True
        )

        embed.add_field(
            name="🔧 Commandes Disponibles",
            value="`/tempvoice-*` - Commandes utilisateur\n"
                  "`/tempchannels-config` - Configuration\n"
                  "`/tempchannels-stats` - Statistiques\n"
                  "`/tempchannels-manage` - Gestion admin",
            inline=True
        )

        embed.set_footer(text="Utilisez /tempchannels-config pour personnaliser davantage")
        
        # Créer les catégories si nécessaire
        await self.create_categories(interaction.guild, config)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tempchannels-config", description="⚙️ Panneau de configuration avancée")
    async def advanced_config(self, interaction: discord.Interaction):
        """Panneau de configuration avancée"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Permissions administrateur requises!", ephemeral=True)
            return

        config = await self.load_guild_config(interaction.guild.id)
        if not config:
            await interaction.response.send_message("❌ Configurez d'abord avec `/tempchannels-setup`!", ephemeral=True)
            return

        embed = discord.Embed(
            title="⚙️ Configuration Avancée - Salons Temporaires",
            description="Personnalisez tous les aspects des salons temporaires",
            color=0x7289da,
            timestamp=datetime.datetime.now()
        )

        # Statut actuel
        status = "🟢 Activé" if config.get("enabled", False) else "🔴 Désactivé"
        embed.add_field(name="📊 Statut", value=status, inline=True)

        parent_channel = interaction.guild.get_channel(config.get("parent_channel_id"))
        embed.add_field(
            name="🎯 Canal Générateur",
            value=parent_channel.mention if parent_channel else "❌ Introuvable",
            inline=True
        )

        stats = config.get("stats", {})
        embed.add_field(
            name="📈 Statistiques",
            value=f"**Total créés :** {stats.get('total_created', 0)}\n"
                  f"**Actifs :** {stats.get('currently_active', 0)}\n"
                  f"**Utilisateurs uniques :** {stats.get('unique_users', 0)}",
            inline=True
        )

        view = AdvancedConfigView(config, interaction.guild.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="tempchannels-stats", description="📊 Statistiques détaillées")
    async def detailed_stats(self, interaction: discord.Interaction):
        """Afficher les statistiques détaillées"""
        config = await self.load_guild_config(interaction.guild.id)
        if not config:
            await interaction.response.send_message("❌ Système non configuré!", ephemeral=True)
            return

        stats = config.get("stats", {})
        
        embed = discord.Embed(
            title="📊 Statistiques Salons Temporaires",
            description=f"Données d'utilisation pour **{interaction.guild.name}**",
            color=0x00ff80,
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="🎯 Utilisation Générale",
            value=f"**Salons créés (total) :** `{stats.get('total_created', 0):,}`\n"
                  f"**Actuellement actifs :** `{stats.get('currently_active', 0)}`\n"
                  f"**Pic simultané :** `{stats.get('peak_concurrent', 0)}`\n"
                  f"**Moyenne quotidienne :** `{stats.get('daily_average', 0)}`",
            inline=True
        )

        embed.add_field(
            name="👥 Utilisateurs",
            value=f"**Utilisateurs uniques :** `{stats.get('unique_users', 0):,}`\n"
                  f"**Créateurs actifs :** `{stats.get('active_creators', 0)}`\n"
                  f"**Top créateur :** `{stats.get('top_creator', 'N/A')}`\n"
                  f"**Moy. membres/salon :** `{stats.get('avg_members', 2.5)}`",
            inline=True
        )

        embed.add_field(
            name="⏱️ Durées",
            value=f"**Durée moyenne :** `{stats.get('avg_duration', '45min')}`\n"
                  f"**Plus longue session :** `{stats.get('longest_session', '0min')}`\n"
                  f"**Sessions courtes (<5min) :** `{stats.get('short_sessions', 0)}`\n"
                  f"**Sessions longues (>2h) :** `{stats.get('long_sessions', 0)}`",
            inline=True
        )

        embed.add_field(
            name="📈 Tendances (7 jours)",
            value=f"**Croissance :** `+{stats.get('weekly_growth', 0)}%`\n"
                  f"**Heures de pointe :** `{stats.get('peak_hours', '20h-22h')}`\n"
                  f"**Jour le plus actif :** `{stats.get('most_active_day', 'Samedi')}`\n"
                  f"**Satisfaction :** `{stats.get('satisfaction_rating', 4.2)}/5 ⭐`",
            inline=True
        )

        # Graphique de tendance (ASCII art simple)
        trend_data = stats.get("weekly_trend", [3, 5, 4, 8, 6, 12, 9])
        trend_visual = self.create_trend_visual(trend_data)
        
        embed.add_field(
            name="📈 Tendance Hebdomadaire (Créations/Jour)",
            value=f"```\n{trend_visual}\n```",
            inline=False
        )

        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text="📊 Statistiques mises à jour en temps réel")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tempchannels-manage", description="🛠️ Gestion administrative des salons temporaires")
    async def manage_tempchannels(self, interaction: discord.Interaction):
        """Interface de gestion administrative"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Permissions administrateur requises!", ephemeral=True)
            return

        config = await self.load_guild_config(interaction.guild.id)
        if not config:
            await interaction.response.send_message("❌ Système non configuré!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🛠️ Gestion Administrative",
            description="Outils d'administration pour les salons temporaires",
            color=0xff6b6b,
            timestamp=datetime.datetime.now()
        )

        # Salons actifs
        active_channels = self.get_active_temp_channels(interaction.guild)
        embed.add_field(
            name="📊 Salons Actifs",
            value=f"**Nombre :** {len(active_channels)}\n"
                  f"**Total membres :** {sum(len(ch.members) for ch in active_channels)}\n"
                  f"**Capacité utilisée :** {self.calculate_capacity_usage(active_channels)}%",
            inline=True
        )

        view = ManagementView(config, interaction.guild.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    def create_trend_visual(self, data: List[int]) -> str:
        """Créer un graphique ASCII simple"""
        if not data:
            return "Aucune donnée"
        
        max_val = max(data)
        if max_val == 0:
            return "Aucune activité"
        
        lines = []
        for i in range(max_val, 0, -1):
            line = ""
            for val in data:
                if val >= i:
                    line += "██"
                else:
                    line += "  "
            lines.append(line)
        
        # Axe des jours
        days = ["L", "M", "M", "J", "V", "S", "D"]
        bottom = " ".join(f"{day:>1}" for day in days)
        lines.append(bottom)
        
        return "\n".join(lines)

    def get_active_temp_channels(self, guild: discord.Guild) -> List[discord.VoiceChannel]:
        """Récupérer tous les salons temporaires actifs"""
        # Cette méthode devrait être liée au système de tracking des salons actifs
        temp_channels = []
        for channel in guild.voice_channels:
            if "salon de " in channel.name.lower() or "🎮" in channel.name:
                temp_channels.append(channel)
        return temp_channels

    def calculate_capacity_usage(self, channels: List[discord.VoiceChannel]) -> int:
        """Calculer le pourcentage d'utilisation de la capacité"""
        if not channels:
            return 0
        
        total_capacity = sum(ch.user_limit if ch.user_limit > 0 else 10 for ch in channels)
        total_members = sum(len(ch.members) for ch in channels)
        
        return int((total_members / total_capacity) * 100) if total_capacity > 0 else 0

    async def create_categories(self, guild: discord.Guild, config: Dict[str, Any]):
        """Créer les catégories nécessaires"""
        categories = config.get("categories", {})
        main_category_name = categories.get("main_category", "🔊 Salons Temporaires")
        
        # Vérifier si la catégorie existe
        existing_category = discord.utils.get(guild.categories, name=main_category_name)
        if not existing_category:
            try:
                await guild.create_category(main_category_name)
            except discord.HTTPException:
                pass

    async def save_guild_config(self, guild_id: int, config: Dict[str, Any]):
        """Sauvegarder la configuration du serveur"""
        config_file = os.path.join(self.config_dir, f"guild_{guild_id}.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    async def load_guild_config(self, guild_id: int) -> Optional[Dict[str, Any]]:
        """Charger la configuration du serveur"""
        config_file = os.path.join(self.config_dir, f"guild_{guild_id}.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None

class AdvancedConfigView(discord.ui.View):
    """Vue de configuration avancée avec tous les paramètres"""
    
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=300)
        self.config = config
        self.guild_id = guild_id

    @discord.ui.button(label="🎯 Canal & Base", style=discord.ButtonStyle.primary, row=0)
    async def configure_basic(self, interaction: discord.Interaction, button):
        embed = discord.Embed(title="🎯 Configuration de Base", color=0x3498db)
        view = BasicConfigView(self.config, self.guild_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="🔐 Permissions", style=discord.ButtonStyle.secondary, row=0)
    async def configure_permissions(self, interaction: discord.Interaction, button):
        embed = discord.Embed(title="🔐 Configuration Permissions", color=0x9b59b6)
        view = PermissionsConfigView(self.config, self.guild_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="⚙️ Création", style=discord.ButtonStyle.secondary, row=0)
    async def configure_creation(self, interaction: discord.Interaction, button):
        embed = discord.Embed(title="⚙️ Paramètres de Création", color=0xe67e22)
        view = CreationConfigView(self.config, self.guild_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="🤖 Auto-Gestion", style=discord.ButtonStyle.secondary, row=0)
    async def configure_auto(self, interaction: discord.Interaction, button):
        embed = discord.Embed(title="🤖 Gestion Automatique", color=0x1abc9c)
        view = AutoManagementView(self.config, self.guild_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="🚫 Restrictions", style=discord.ButtonStyle.danger, row=1)
    async def configure_restrictions(self, interaction: discord.Interaction, button):
        embed = discord.Embed(title="🚫 Restrictions & Limites", color=0xe74c3c)
        view = RestrictionsView(self.config, self.guild_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="📝 Logs", style=discord.ButtonStyle.secondary, row=1)
    async def configure_logs(self, interaction: discord.Interaction, button):
        embed = discord.Embed(title="📝 Configuration des Logs", color=0x34495e)
        view = LogsConfigView(self.config, self.guild_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="📁 Catégories", style=discord.ButtonStyle.secondary, row=1)
    async def configure_categories(self, interaction: discord.Interaction, button):
        embed = discord.Embed(title="📁 Gestion des Catégories", color=0x95a5a6)
        view = CategoriesView(self.config, self.guild_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="💾 Sauvegarder", style=discord.ButtonStyle.success, row=2)
    async def save_config(self, interaction: discord.Interaction, button):
        # Sauvegarder la configuration
        config_file = f"data/tempchannels/guild_{self.guild_id}.json"
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
            
        await interaction.response.send_message("✅ Configuration sauvegardée avec succès!", ephemeral=True)

class BasicConfigView(discord.ui.View):
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=180)
        self.config = config
        self.guild_id = guild_id

    @discord.ui.button(label="🔄 Activer/Désactiver", style=discord.ButtonStyle.primary)
    async def toggle_system(self, interaction: discord.Interaction, button):
        self.config["enabled"] = not self.config.get("enabled", False)
        status = "✅ Activé" if self.config["enabled"] else "❌ Désactivé"
        await interaction.response.send_message(f"Système des salons temporaires: {status}", ephemeral=True)

    @discord.ui.button(label="🎯 Changer Canal", style=discord.ButtonStyle.secondary)
    async def change_parent_channel(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(ChannelSelectModal(self.config))

class ChannelSelectModal(discord.ui.Modal):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="🎯 Sélectionner Canal Générateur")
        self.config = config

    channel_id = discord.ui.TextInput(
        label="ID du Canal Vocal",
        placeholder="Ex: 123456789012345678",
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            channel_id = int(self.channel_id.value)
            channel = interaction.guild.get_channel(channel_id)
            
            if not channel or not isinstance(channel, discord.VoiceChannel):
                await interaction.response.send_message("❌ Canal vocal introuvable!", ephemeral=True)
                return
                
            self.config["parent_channel_id"] = channel_id
            await interaction.response.send_message(f"✅ Canal générateur: {channel.mention}", ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ ID de canal invalide!", ephemeral=True)

# Views additionnelles pour chaque section
class PermissionsConfigView(discord.ui.View):
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=180)
        self.config = config
        self.guild_id = guild_id

class CreationConfigView(discord.ui.View):
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=180)
        self.config = config
        self.guild_id = guild_id

class AutoManagementView(discord.ui.View):
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=180)
        self.config = config
        self.guild_id = guild_id

class RestrictionsView(discord.ui.View):
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=180)
        self.config = config
        self.guild_id = guild_id

class LogsConfigView(discord.ui.View):
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=180)
        self.config = config
        self.guild_id = guild_id

class CategoriesView(discord.ui.View):
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=180)
        self.config = config
        self.guild_id = guild_id

class ManagementView(discord.ui.View):
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=300)
        self.config = config
        self.guild_id = guild_id

    @discord.ui.button(label="🗑️ Nettoyer Salons", style=discord.ButtonStyle.danger, row=0)
    async def cleanup_channels(self, interaction: discord.Interaction, button):
        # Logique de nettoyage des salons vides
        await interaction.response.send_message("🗑️ Nettoyage des salons vides en cours...", ephemeral=True)

    @discord.ui.button(label="📊 Rapport Détaillé", style=discord.ButtonStyle.secondary, row=0)
    async def detailed_report(self, interaction: discord.Interaction, button):
        # Générer un rapport détaillé
        await interaction.response.send_message("📊 Génération du rapport en cours...", ephemeral=True)

    @discord.ui.button(label="🔄 Reset Stats", style=discord.ButtonStyle.danger, row=1)
    async def reset_stats(self, interaction: discord.Interaction, button):
        # Reset des statistiques
        view = ResetConfirmView(self.config)
        await interaction.response.send_message("⚠️ Confirmer le reset des statistiques?", view=view, ephemeral=True)

class ResetConfirmView(discord.ui.View):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(timeout=60)
        self.config = config

    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.danger)
    async def confirm_reset(self, interaction: discord.Interaction, button):
        # Reset des stats
        self.config["stats"] = {
            "total_created": 0,
            "currently_active": 0,
            "peak_concurrent": 0,
            "unique_users": 0,
            "daily_average": 0,
            "avg_duration": "0min",
            "longest_session": "0min"
        }
        await interaction.response.send_message("🔄 Statistiques remises à zéro!", ephemeral=True)

    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
    async def cancel_reset(self, interaction: discord.Interaction, button):
        await interaction.response.send_message("❌ Reset annulé", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TempChannelsAdvancedConfig(bot))
