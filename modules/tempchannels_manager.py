import discord
from discord.ext import commands
import asyncio
import datetime
from typing import Dict, Any, Optional, List
import json
import os

class TempChannelsConfigView(discord.ui.View):
    """Interface de configuration complète des salons temporaires"""
    
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=300)
        self.config = config
        self.guild_id = guild_id

    @discord.ui.button(label="🎯 Canal Générateur", style=discord.ButtonStyle.primary)
    async def set_parent_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Définir le canal générateur principal"""
        await interaction.response.send_modal(ParentChannelModal(self.config))

    @discord.ui.button(label="👥 Permissions", style=discord.ButtonStyle.secondary)
    async def configure_permissions(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configurer les permissions des salons temporaires"""
        view = PermissionsConfigView(self.config)
        await interaction.response.send_message("🔐 Configuration des permissions", view=view, ephemeral=True)

    @discord.ui.button(label="⚙️ Création", style=discord.ButtonStyle.secondary) 
    async def configure_creation(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Paramètres de création des salons"""
        await interaction.response.send_modal(CreationConfigModal(self.config))

    @discord.ui.button(label="🤖 Auto-Gestion", style=discord.ButtonStyle.secondary)
    async def configure_auto_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configuration de la gestion automatique"""
        view = AutoManagementView(self.config)
        await interaction.response.send_message("🤖 Gestion automatique", view=view, ephemeral=True)

    @discord.ui.button(label="📝 Logs", style=discord.ButtonStyle.secondary, row=1)
    async def configure_logs(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configuration des logs"""
        await interaction.response.send_modal(LogsConfigModal(self.config))

    @discord.ui.button(label="📁 Catégories", style=discord.ButtonStyle.secondary, row=1)
    async def configure_categories(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gestion des catégories"""
        await interaction.response.send_modal(CategoriesModal(self.config))

    @discord.ui.button(label="📊 Statistiques", style=discord.ButtonStyle.secondary, row=1)
    async def view_statistics(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Voir les statistiques détaillées"""
        embed = await self.create_stats_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="💾 Sauvegarder", style=discord.ButtonStyle.success, row=1)
    async def save_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Sauvegarder la configuration"""
        await self.save_configuration()
        await interaction.response.send_message("✅ Configuration sauvegardée avec succès!", ephemeral=True)

    @discord.ui.button(label="🔄 Reset", style=discord.ButtonStyle.danger, row=1)
    async def reset_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Reset de la configuration"""
        view = ResetConfirmView(self.config)
        await interaction.response.send_message("⚠️ Confirmer le reset de la configuration?", view=view, ephemeral=True)

    async def create_stats_embed(self) -> discord.Embed:
        """Créer l'embed des statistiques"""
        stats = self.config.get("stats", {})
        
        embed = discord.Embed(
            title="📊 Statistiques Salons Temporaires",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="📈 Utilisation Générale",
            value=f"**Total créés :** `{stats.get('total_created', 0)}`\n"
                  f"**Actuellement actifs :** `{stats.get('currently_active', 0)}`\n"
                  f"**Pic simultané :** `{stats.get('peak_concurrent', 0)}`\n"
                  f"**Moyenne par jour :** `{stats.get('daily_average', 0)}`",
            inline=True
        )
        
        embed.add_field(
            name="⏱️ Durées",
            value=f"**Durée moyenne :** `{stats.get('avg_duration', '45min')}`\n"
                  f"**Plus longue session :** `{stats.get('longest_session', '3h 24min')}`\n"
                  f"**Sessions courtes (<5min) :** `{stats.get('short_sessions', 0)}`\n"
                  f"**Sessions longues (>2h) :** `{stats.get('long_sessions', 0)}`",
            inline=True
        )
        
        embed.add_field(
            name="👥 Utilisateurs",
            value=f"**Utilisateurs uniques :** `{stats.get('unique_users', 0)}`\n"
                  f"**Créateurs actifs :** `{stats.get('active_creators', 0)}`\n"
                  f"**Top créateur :** `{stats.get('top_creator', 'N/A')}`\n"
                  f"**Moyenne membres/salon :** `{stats.get('avg_members', 0)}`",
            inline=True
        )
        
        return embed

    async def save_configuration(self):
        """Sauvegarder la configuration dans un fichier"""
        config_dir = "data/tempchannels"
        os.makedirs(config_dir, exist_ok=True)
        
        config_file = f"{config_dir}/guild_{self.guild_id}.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

class ParentChannelModal(discord.ui.Modal):
    """Modal pour définir le canal générateur"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="🎯 Configurer Canal Générateur")
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
            await interaction.response.send_message(f"✅ Canal générateur défini: {channel.mention}", ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ ID de canal invalide!", ephemeral=True)

class CreationConfigModal(discord.ui.Modal):
    """Modal pour les paramètres de création"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="⚙️ Paramètres de Création")
        self.config = config

    default_limit = discord.ui.TextInput(
        label="Limite d'utilisateurs par défaut",
        placeholder="10",
        required=False,
        max_length=2
    )

    default_name = discord.ui.TextInput(
        label="Nom par défaut (variables: {username}, {count})",
        placeholder="Salon de {username}",
        required=False,
        max_length=50
    )

    bitrate = discord.ui.TextInput(
        label="Bitrate (kbps)",
        placeholder="64",
        required=False,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        creation_config = self.config.setdefault("creation", {})
        
        if self.default_limit.value:
            try:
                limit = int(self.default_limit.value)
                if 1 <= limit <= 99:
                    creation_config["default_limit"] = limit
            except ValueError:
                pass
                
        if self.default_name.value:
            creation_config["default_name"] = self.default_name.value
            
        if self.bitrate.value:
            try:
                bitrate = int(self.bitrate.value)
                if 8 <= bitrate <= 384:
                    creation_config["bitrate"] = bitrate
            except ValueError:
                pass
        
        await interaction.response.send_message("✅ Paramètres de création mis à jour!", ephemeral=True)

class PermissionsConfigView(discord.ui.View):
    """Vue pour la configuration des permissions"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(timeout=180)
        self.config = config

    @discord.ui.button(label="👑 Créateur = Admin", style=discord.ButtonStyle.primary)
    async def toggle_creator_admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        perms = self.config.setdefault("permissions", {})
        perms["creator_admin"] = not perms.get("creator_admin", True)
        
        status = "✅ Activé" if perms["creator_admin"] else "❌ Désactivé"
        await interaction.response.send_message(f"👑 Créateur = Admin: {status}", ephemeral=True)

    @discord.ui.button(label="🔒 Invite Uniquement", style=discord.ButtonStyle.secondary)
    async def toggle_invite_only(self, interaction: discord.Interaction, button: discord.ui.Button):
        perms = self.config.setdefault("permissions", {})
        perms["invite_only"] = not perms.get("invite_only", False)
        
        status = "✅ Activé" if perms["invite_only"] else "❌ Désactivé"
        await interaction.response.send_message(f"🔒 Invite uniquement: {status}", ephemeral=True)

    @discord.ui.button(label="🔄 Transfert Propriété", style=discord.ButtonStyle.secondary)
    async def toggle_transfer(self, interaction: discord.Interaction, button: discord.ui.Button):
        perms = self.config.setdefault("permissions", {})
        perms["transfer_ownership"] = not perms.get("transfer_ownership", True)
        
        status = "✅ Activé" if perms["transfer_ownership"] else "❌ Désactivé"
        await interaction.response.send_message(f"🔄 Transfert de propriété: {status}", ephemeral=True)

class AutoManagementView(discord.ui.View):
    """Vue pour la gestion automatique"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(timeout=180)
        self.config = config

    @discord.ui.button(label="🗑️ Suppression Auto", style=discord.ButtonStyle.danger)
    async def toggle_auto_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        auto_mgmt = self.config.setdefault("auto_management", {})
        auto_mgmt["auto_delete"] = not auto_mgmt.get("auto_delete", True)
        
        status = "✅ Activé" if auto_mgmt["auto_delete"] else "❌ Désactivé"
        await interaction.response.send_message(f"🗑️ Suppression automatique: {status}", ephemeral=True)

    @discord.ui.button(label="🧹 Nettoyage Inactifs", style=discord.ButtonStyle.secondary)
    async def set_cleanup_timer(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CleanupTimerModal(self.config))

    @discord.ui.button(label="💾 Sauvegarde Config", style=discord.ButtonStyle.primary)
    async def toggle_save_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        auto_mgmt = self.config.setdefault("auto_management", {})
        auto_mgmt["save_config"] = not auto_mgmt.get("save_config", True)
        
        status = "✅ Activé" if auto_mgmt["save_config"] else "❌ Désactivé"
        await interaction.response.send_message(f"💾 Sauvegarde config: {status}", ephemeral=True)

class CleanupTimerModal(discord.ui.Modal):
    """Modal pour configurer le timer de nettoyage"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="⏰ Timer Nettoyage")
        self.config = config

    timer_minutes = discord.ui.TextInput(
        label="Minutes avant nettoyage (salon vide)",
        placeholder="5",
        required=True,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            minutes = int(self.timer_minutes.value)
            if 1 <= minutes <= 180:
                auto_mgmt = self.config.setdefault("auto_management", {})
                auto_mgmt["cleanup_inactive"] = f"{minutes}min"
                await interaction.response.send_message(f"✅ Nettoyage configuré: {minutes} minutes", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Valeur entre 1 et 180 minutes", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Valeur numérique requise", ephemeral=True)

class LogsConfigModal(discord.ui.Modal):
    """Modal pour configurer les logs"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="📝 Configuration Logs")
        self.config = config

    log_channel_id = discord.ui.TextInput(
        label="ID Canal de Logs",
        placeholder="123456789012345678",
        required=False,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.log_channel_id.value:
            try:
                channel_id = int(self.log_channel_id.value)
                channel = interaction.guild.get_channel(channel_id)
                
                if channel and isinstance(channel, discord.TextChannel):
                    logs_config = self.config.setdefault("logging", {})
                    logs_config["log_channel"] = channel_id
                    await interaction.response.send_message(f"✅ Canal de logs: {channel.mention}", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Canal textuel introuvable!", ephemeral=True)
            except ValueError:
                await interaction.response.send_message("❌ ID invalide!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ ID canal requis!", ephemeral=True)

class CategoriesModal(discord.ui.Modal):
    """Modal pour configurer les catégories"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="📁 Gestion Catégories")
        self.config = config

    main_category = discord.ui.TextInput(
        label="Nom Catégorie Principale",
        placeholder="🔊 Salons Temporaires",
        required=False,
        max_length=50
    )

    max_per_category = discord.ui.TextInput(
        label="Maximum par catégorie",
        placeholder="50",
        required=False,
        max_length=2
    )

    async def on_submit(self, interaction: discord.Interaction):
        categories = self.config.setdefault("categories", {})
        
        if self.main_category.value:
            categories["main_category"] = self.main_category.value
            
        if self.max_per_category.value:
            try:
                max_val = int(self.max_per_category.value)
                if 10 <= max_val <= 50:
                    categories["max_per_category"] = max_val
            except ValueError:
                pass
                
        await interaction.response.send_message("✅ Configuration catégories mise à jour!", ephemeral=True)

class ResetConfirmView(discord.ui.View):
    """Vue de confirmation pour le reset"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(timeout=60)
        self.config = config

    @discord.ui.button(label="✅ Confirmer Reset", style=discord.ButtonStyle.danger)
    async def confirm_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Reset configuration à défaut
        self.config.clear()
        self.config.update({
            "enabled": False,
            "permissions": {
                "creator_admin": True,
                "invite_only": False,
                "transfer_ownership": True
            },
            "creation": {
                "default_limit": 10,
                "default_name": "Salon de {username}",
                "bitrate": 64
            },
            "auto_management": {
                "auto_delete": True,
                "cleanup_inactive": "5min",
                "save_config": True
            }
        })
        
        await interaction.response.send_message("🔄 Configuration remise à zéro!", ephemeral=True)

    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
    async def cancel_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Reset annulé", ephemeral=True)

class TempChannelsManager(commands.Cog):
    """Gestionnaire complet des salons vocaux temporaires"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_channels = {}  # guild_id: {channel_id: owner_id}
        self.channel_configs = {}  # channel_id: config
        
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Gestion automatique des salons temporaires"""
        await self.handle_tempchannel_join(member, before, after)
        await self.handle_tempchannel_leave(member, before, after)
    
    async def handle_tempchannel_join(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Gestion de la connexion aux salons temporaires"""
        if not after.channel:
            return
            
        # Vérifier si c'est un canal générateur
        guild_config = await self.get_guild_config(member.guild.id)
        if not guild_config.get("enabled"):
            return
            
        parent_channel_id = guild_config.get("parent_channel_id")
        if after.channel.id == parent_channel_id:
            # Créer un nouveau salon temporaire
            await self.create_temp_channel(member, guild_config)
    
    async def handle_tempchannel_leave(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Gestion de la déconnexion des salons temporaires"""
        if not before.channel:
            return
            
        # Vérifier si le salon doit être supprimé
        guild_channels = self.active_channels.get(member.guild.id, {})
        if before.channel.id in guild_channels:
            if len(before.channel.members) == 0:
                # Salon vide, programmer la suppression
                await asyncio.sleep(5)  # Délai de grâce
                if len(before.channel.members) == 0:
                    await self.delete_temp_channel(before.channel)
    
    async def create_temp_channel(self, member: discord.Member, config: Dict[str, Any]):
        """Créer un salon temporaire personnalisé"""
        creation_config = config.get("creation", {})
        
        # Nom personnalisé avec variables
        name_template = creation_config.get("default_name", "Salon de {username}")
        channel_name = name_template.format(
            username=member.display_name,
            nickname=member.nick or member.name,
            count=len(member.guild.members),
            time=datetime.datetime.now().strftime("%H:%M")
        )
        
        # Paramètres du salon
        user_limit = creation_config.get("default_limit", 10)
        bitrate = creation_config.get("bitrate", 64) * 1000  # Conversion en bps
        
        # Créer le salon
        category = member.voice.channel.category
        temp_channel = await member.guild.create_voice_channel(
            name=channel_name,
            category=category,
            user_limit=user_limit,
            bitrate=bitrate
        )
        
        # Permissions du créateur
        perms_config = config.get("permissions", {})
        if perms_config.get("creator_admin", True):
            overwrites = {
                member: discord.PermissionOverwrite(
                    manage_channels=True,
                    move_members=True,
                    mute_members=True,
                    deafen_members=True
                )
            }
            await temp_channel.edit(overwrites=overwrites)
        
        # Déplacer le créateur
        await member.move_to(temp_channel)
        
        # Enregistrer le salon
        if member.guild.id not in self.active_channels:
            self.active_channels[member.guild.id] = {}
        self.active_channels[member.guild.id][temp_channel.id] = member.id
        
        # Log de création
        await self.log_channel_creation(member.guild, member, temp_channel, config)
    
    async def delete_temp_channel(self, channel: discord.VoiceChannel):
        """Supprimer un salon temporaire"""
        try:
            guild_channels = self.active_channels.get(channel.guild.id, {})
            if channel.id in guild_channels:
                del guild_channels[channel.id]
            await channel.delete()
        except discord.NotFound:
            pass
    
    async def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """Récupérer la configuration d'un serveur"""
        config_file = f"data/tempchannels/guild_{guild_id}.json"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    async def log_channel_creation(self, guild: discord.Guild, creator: discord.Member, channel: discord.VoiceChannel, config: Dict[str, Any]):
        """Logger la création d'un salon temporaire"""
        logs_config = config.get("logging", {})
        if not logs_config.get("log_creation", True):
            return
            
        log_channel_id = logs_config.get("log_channel")
        if not log_channel_id:
            return
            
        log_channel = guild.get_channel(log_channel_id)
        if not log_channel:
            return
            
        embed = discord.Embed(
            title="🔊 Salon Temporaire Créé",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="👤 Créateur", value=creator.mention, inline=True)
        embed.add_field(name="📡 Salon", value=channel.mention, inline=True)
        embed.add_field(name="👥 Limite", value=str(channel.user_limit), inline=True)
        
        await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TempChannelsManager(bot))

