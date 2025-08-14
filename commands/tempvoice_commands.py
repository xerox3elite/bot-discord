"""
🔊 Arsenal TempChannels Commands
Système complet de commandes pour les salons vocaux temporaires
Développé par XeRoX - Arsenal Bot V4.5
"""

import discord
from discord.ext import commands
from discord import app_commands
import datetime
import asyncio
import os
import json
from typing import Optional, Dict, Any, Union

class TempChannelCommands(commands.Cog):
    """Commandes pour la gestion des salons vocaux temporaires"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_channels = {}  # guild_id: {channel_id: owner_id}
        
    async def is_temp_channel_owner(self, member: discord.Member, channel: discord.VoiceChannel) -> bool:
        """Vérifier si le membre est propriétaire du salon temporaire"""
        guild_channels = self.active_channels.get(member.guild.id, {})
        return guild_channels.get(channel.id) == member.id
    
    async def is_temp_channel(self, channel: discord.VoiceChannel) -> bool:
        """Vérifier si c'est un salon temporaire"""
        guild_channels = self.active_channels.get(channel.guild.id, {})
        return channel.id in guild_channels

    @app_commands.command(name="tempvoice-lock", description="🔒 Verrouiller votre salon temporaire")
    async def lock_temp_channel(self, interaction: discord.Interaction):
        """Verrouiller le salon temporaire"""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Vous devez être dans un salon vocal!", ephemeral=True)
            return
            
        channel = interaction.user.voice.channel
        if not await self.is_temp_channel(channel):
            await interaction.response.send_message("❌ Vous n'êtes pas dans un salon temporaire!", ephemeral=True)
            return
            
        if not await self.is_temp_channel_owner(interaction.user, channel):
            await interaction.response.send_message("❌ Vous n'êtes pas le propriétaire de ce salon!", ephemeral=True)
            return
        
        # Verrouiller le salon
        overwrites = channel.overwrites
        overwrites[interaction.guild.default_role] = discord.PermissionOverwrite(connect=False)
        
        await channel.edit(overwrites=overwrites)
        
        embed = discord.Embed(
            title="🔒 Salon Verrouillé",
            description=f"Le salon {channel.mention} a été verrouillé par {interaction.user.mention}",
            color=0xff6b6b,
            timestamp=datetime.datetime.now()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tempvoice-unlock", description="🔓 Déverrouiller votre salon temporaire")
    async def unlock_temp_channel(self, interaction: discord.Interaction):
        """Déverrouiller le salon temporaire"""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Vous devez être dans un salon vocal!", ephemeral=True)
            return
            
        channel = interaction.user.voice.channel
        if not await self.is_temp_channel(channel):
            await interaction.response.send_message("❌ Vous n'êtes pas dans un salon temporaire!", ephemeral=True)
            return
            
        if not await self.is_temp_channel_owner(interaction.user, channel):
            await interaction.response.send_message("❌ Vous n'êtes pas le propriétaire de ce salon!", ephemeral=True)
            return
        
        # Déverrouiller le salon
        overwrites = channel.overwrites
        if interaction.guild.default_role in overwrites:
            del overwrites[interaction.guild.default_role]
        
        await channel.edit(overwrites=overwrites)
        
        embed = discord.Embed(
            title="🔓 Salon Déverrouillé",
            description=f"Le salon {channel.mention} a été déverrouillé par {interaction.user.mention}",
            color=0x4ecdc4,
            timestamp=datetime.datetime.now()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tempvoice-limit", description="👥 Modifier la limite d'utilisateurs")
    @app_commands.describe(limite="Nombre maximum d'utilisateurs (0-99)")
    async def set_user_limit(self, interaction: discord.Interaction, limite: int):
        """Modifier la limite d'utilisateurs du salon temporaire"""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Vous devez être dans un salon vocal!", ephemeral=True)
            return
            
        channel = interaction.user.voice.channel
        if not await self.is_temp_channel(channel):
            await interaction.response.send_message("❌ Vous n'êtes pas dans un salon temporaire!", ephemeral=True)
            return
            
        if not await self.is_temp_channel_owner(interaction.user, channel):
            await interaction.response.send_message("❌ Vous n'êtes pas le propriétaire de ce salon!", ephemeral=True)
            return
        
        if not 0 <= limite <= 99:
            await interaction.response.send_message("❌ La limite doit être entre 0 et 99!", ephemeral=True)
            return
        
        await channel.edit(user_limit=limite)
        
        limit_text = f"**{limite} utilisateurs**" if limite > 0 else "**Illimitée**"
        embed = discord.Embed(
            title="👥 Limite Modifiée",
            description=f"La limite du salon {channel.mention} est maintenant de {limit_text}",
            color=0x45b7d1,
            timestamp=datetime.datetime.now()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tempvoice-rename", description="📝 Renommer votre salon temporaire")
    @app_commands.describe(nom="Nouveau nom du salon (max 50 caractères)")
    async def rename_temp_channel(self, interaction: discord.Interaction, nom: str):
        """Renommer le salon temporaire"""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Vous devez être dans un salon vocal!", ephemeral=True)
            return
            
        channel = interaction.user.voice.channel
        if not await self.is_temp_channel(channel):
            await interaction.response.send_message("❌ Vous n'êtes pas dans un salon temporaire!", ephemeral=True)
            return
            
        if not await self.is_temp_channel_owner(interaction.user, channel):
            await interaction.response.send_message("❌ Vous n'êtes pas le propriétaire de ce salon!", ephemeral=True)
            return
        
        if len(nom) > 50:
            await interaction.response.send_message("❌ Le nom ne peut pas dépasser 50 caractères!", ephemeral=True)
            return
        
        old_name = channel.name
        await channel.edit(name=nom)
        
        embed = discord.Embed(
            title="📝 Salon Renommé",
            description=f"**Ancien nom :** {old_name}\n**Nouveau nom :** {nom}",
            color=0xf39c12,
            timestamp=datetime.datetime.now()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tempvoice-kick", description="⚡ Expulser un utilisateur de votre salon")
    @app_commands.describe(membre="Membre à expulser du salon")
    async def kick_from_temp_channel(self, interaction: discord.Interaction, membre: discord.Member):
        """Expulser un membre du salon temporaire"""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Vous devez être dans un salon vocal!", ephemeral=True)
            return
            
        channel = interaction.user.voice.channel
        if not await self.is_temp_channel(channel):
            await interaction.response.send_message("❌ Vous n'êtes pas dans un salon temporaire!", ephemeral=True)
            return
            
        if not await self.is_temp_channel_owner(interaction.user, channel):
            await interaction.response.send_message("❌ Vous n'êtes pas le propriétaire de ce salon!", ephemeral=True)
            return
        
        if membre == interaction.user:
            await interaction.response.send_message("❌ Vous ne pouvez pas vous expulser vous-même!", ephemeral=True)
            return
        
        if not membre.voice or membre.voice.channel != channel:
            await interaction.response.send_message("❌ Ce membre n'est pas dans votre salon!", ephemeral=True)
            return
        
        try:
            await membre.move_to(None)
            
            embed = discord.Embed(
                title="⚡ Membre Expulsé",
                description=f"{membre.mention} a été expulsé du salon par {interaction.user.mention}",
                color=0xe74c3c,
                timestamp=datetime.datetime.now()
            )
            await interaction.response.send_message(embed=embed)
            
        except discord.HTTPException:
            await interaction.response.send_message("❌ Impossible d'expulser ce membre!", ephemeral=True)

    @app_commands.command(name="tempvoice-ban", description="🚫 Bannir un utilisateur de votre salon")
    @app_commands.describe(membre="Membre à bannir du salon")
    async def ban_from_temp_channel(self, interaction: discord.Interaction, membre: discord.Member):
        """Bannir un membre du salon temporaire"""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Vous devez être dans un salon vocal!", ephemeral=True)
            return
            
        channel = interaction.user.voice.channel
        if not await self.is_temp_channel(channel):
            await interaction.response.send_message("❌ Vous n'êtes pas dans un salon temporaire!", ephemeral=True)
            return
            
        if not await self.is_temp_channel_owner(interaction.user, channel):
            await interaction.response.send_message("❌ Vous n'êtes pas le propriétaire de ce salon!", ephemeral=True)
            return
        
        if membre == interaction.user:
            await interaction.response.send_message("❌ Vous ne pouvez pas vous bannir vous-même!", ephemeral=True)
            return
        
        # Bannir le membre du salon
        overwrites = channel.overwrites
        overwrites[membre] = discord.PermissionOverwrite(connect=False)
        
        await channel.edit(overwrites=overwrites)
        
        # Expulser s'il est connecté
        if membre.voice and membre.voice.channel == channel:
            try:
                await membre.move_to(None)
            except discord.HTTPException:
                pass
        
        embed = discord.Embed(
            title="🚫 Membre Banni",
            description=f"{membre.mention} a été banni du salon par {interaction.user.mention}",
            color=0xc0392b,
            timestamp=datetime.datetime.now()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tempvoice-unban", description="✅ Débannir un utilisateur de votre salon")
    @app_commands.describe(membre="Membre à débannir du salon")
    async def unban_from_temp_channel(self, interaction: discord.Interaction, membre: discord.Member):
        """Débannir un membre du salon temporaire"""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Vous devez être dans un salon vocal!", ephemeral=True)
            return
            
        channel = interaction.user.voice.channel
        if not await self.is_temp_channel(channel):
            await interaction.response.send_message("❌ Vous n'êtes pas dans un salon temporaire!", ephemeral=True)
            return
            
        if not await self.is_temp_channel_owner(interaction.user, channel):
            await interaction.response.send_message("❌ Vous n'êtes pas le propriétaire de ce salon!", ephemeral=True)
            return
        
        # Débannir le membre
        overwrites = channel.overwrites
        if membre in overwrites:
            del overwrites[membre]
            await channel.edit(overwrites=overwrites)
        
        embed = discord.Embed(
            title="✅ Membre Débanni",
            description=f"{membre.mention} a été débanni du salon par {interaction.user.mention}",
            color=0x27ae60,
            timestamp=datetime.datetime.now()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tempvoice-transfer", description="👑 Transférer la propriété du salon")
    @app_commands.describe(nouveau_proprietaire="Nouveau propriétaire du salon")
    async def transfer_temp_channel(self, interaction: discord.Interaction, nouveau_proprietaire: discord.Member):
        """Transférer la propriété du salon temporaire"""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Vous devez être dans un salon vocal!", ephemeral=True)
            return
            
        channel = interaction.user.voice.channel
        if not await self.is_temp_channel(channel):
            await interaction.response.send_message("❌ Vous n'êtes pas dans un salon temporaire!", ephemeral=True)
            return
            
        if not await self.is_temp_channel_owner(interaction.user, channel):
            await interaction.response.send_message("❌ Vous n'êtes pas le propriétaire de ce salon!", ephemeral=True)
            return
        
        if nouveau_proprietaire == interaction.user:
            await interaction.response.send_message("❌ Vous êtes déjà le propriétaire!", ephemeral=True)
            return
        
        if not nouveau_proprietaire.voice or nouveau_proprietaire.voice.channel != channel:
            await interaction.response.send_message("❌ Le nouveau propriétaire doit être dans le salon!", ephemeral=True)
            return
        
        # Transférer la propriété
        guild_channels = self.active_channels.get(interaction.guild.id, {})
        guild_channels[channel.id] = nouveau_proprietaire.id
        
        # Modifier les permissions
        overwrites = channel.overwrites
        
        # Retirer les permissions de l'ancien propriétaire
        if interaction.user in overwrites:
            del overwrites[interaction.user]
        
        # Donner les permissions au nouveau propriétaire
        overwrites[nouveau_proprietaire] = discord.PermissionOverwrite(
            manage_channels=True,
            move_members=True,
            mute_members=True,
            deafen_members=True
        )
        
        await channel.edit(overwrites=overwrites)
        
        embed = discord.Embed(
            title="👑 Propriété Transférée",
            description=f"La propriété du salon {channel.mention} a été transférée à {nouveau_proprietaire.mention}",
            color=0x9b59b6,
            timestamp=datetime.datetime.now()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tempvoice-info", description="📊 Informations sur le salon temporaire")
    async def temp_channel_info(self, interaction: discord.Interaction):
        """Afficher les informations du salon temporaire"""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Vous devez être dans un salon vocal!", ephemeral=True)
            return
            
        channel = interaction.user.voice.channel
        if not await self.is_temp_channel(channel):
            await interaction.response.send_message("❌ Vous n'êtes pas dans un salon temporaire!", ephemeral=True)
            return
        
        guild_channels = self.active_channels.get(interaction.guild.id, {})
        owner_id = guild_channels.get(channel.id)
        owner = interaction.guild.get_member(owner_id) if owner_id else None
        
        embed = discord.Embed(
            title="📊 Informations du Salon Temporaire",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="📡 Salon", 
            value=f"**Nom :** {channel.name}\n**ID :** `{channel.id}`", 
            inline=True
        )
        
        embed.add_field(
            name="👑 Propriétaire",
            value=owner.mention if owner else "❌ Introuvable",
            inline=True
        )
        
        embed.add_field(
            name="👥 Membres",
            value=f"**Connectés :** {len(channel.members)}\n**Limite :** {channel.user_limit if channel.user_limit > 0 else 'Illimitée'}",
            inline=True
        )
        
        embed.add_field(
            name="🎵 Audio",
            value=f"**Bitrate :** {channel.bitrate // 1000}kbps\n**Région :** {channel.rtc_region or 'Automatique'}",
            inline=True
        )
        
        # Permissions spéciales
        special_perms = []
        if channel.overwrites:
            for target, perms in channel.overwrites.items():
                if isinstance(target, discord.Member):
                    if perms.connect is False:
                        special_perms.append(f"🚫 {target.mention}")
                    elif perms.manage_channels:
                        special_perms.append(f"👑 {target.mention}")
                        
        if special_perms:
            embed.add_field(
                name="🔐 Permissions Spéciales",
                value="\n".join(special_perms[:5]),  # Limite à 5 pour éviter les gros messages
                inline=False
            )
        
        embed.add_field(
            name="⏰ Créé",
            value=f"<t:{int(channel.created_at.timestamp())}:R>",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tempvoice-panel", description="🎛️ Panel de contrôle du salon temporaire")
    async def temp_channel_panel(self, interaction: discord.Interaction):
        """Afficher le panel de contrôle du salon temporaire"""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Vous devez être dans un salon vocal!", ephemeral=True)
            return
            
        channel = interaction.user.voice.channel
        if not await self.is_temp_channel(channel):
            await interaction.response.send_message("❌ Vous n'êtes pas dans un salon temporaire!", ephemeral=True)
            return
            
        if not await self.is_temp_channel_owner(interaction.user, channel):
            await interaction.response.send_message("❌ Vous n'êtes pas le propriétaire de ce salon!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎛️ Panel de Contrôle",
            description=f"Gestion du salon **{channel.name}**",
            color=0x7289da,
            timestamp=datetime.datetime.now()
        )
        
        view = TempChannelControlPanel(channel, interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class TempChannelControlPanel(discord.ui.View):
    """Panel de contrôle interactif pour les salons temporaires"""
    
    def __init__(self, channel: discord.VoiceChannel, owner: discord.Member):
        super().__init__(timeout=300)
        self.channel = channel
        self.owner = owner

    @discord.ui.button(label="🔒 Verrouiller", style=discord.ButtonStyle.danger, row=0)
    async def lock_channel(self, interaction: discord.Interaction, button):
        if interaction.user != self.owner:
            await interaction.response.send_message("❌ Seul le propriétaire peut utiliser ce panel!", ephemeral=True)
            return
        
        overwrites = self.channel.overwrites
        overwrites[interaction.guild.default_role] = discord.PermissionOverwrite(connect=False)
        await self.channel.edit(overwrites=overwrites)
        
        await interaction.response.send_message("🔒 Salon verrouillé!", ephemeral=True)

    @discord.ui.button(label="🔓 Déverrouiller", style=discord.ButtonStyle.success, row=0)
    async def unlock_channel(self, interaction: discord.Interaction, button):
        if interaction.user != self.owner:
            await interaction.response.send_message("❌ Seul le propriétaire peut utiliser ce panel!", ephemeral=True)
            return
        
        overwrites = self.channel.overwrites
        if interaction.guild.default_role in overwrites:
            del overwrites[interaction.guild.default_role]
        await self.channel.edit(overwrites=overwrites)
        
        await interaction.response.send_message("🔓 Salon déverrouillé!", ephemeral=True)

    @discord.ui.button(label="📝 Renommer", style=discord.ButtonStyle.secondary, row=0)
    async def rename_channel(self, interaction: discord.Interaction, button):
        if interaction.user != self.owner:
            await interaction.response.send_message("❌ Seul le propriétaire peut utiliser ce panel!", ephemeral=True)
            return
        
        await interaction.response.send_modal(RenameModal(self.channel))

    @discord.ui.button(label="👥 Limite", style=discord.ButtonStyle.secondary, row=1)
    async def set_limit(self, interaction: discord.Interaction, button):
        if interaction.user != self.owner:
            await interaction.response.send_message("❌ Seul le propriétaire peut utiliser ce panel!", ephemeral=True)
            return
        
        await interaction.response.send_modal(LimitModal(self.channel))

    @discord.ui.button(label="🎵 Qualité", style=discord.ButtonStyle.secondary, row=1)
    async def set_quality(self, interaction: discord.Interaction, button):
        if interaction.user != self.owner:
            await interaction.response.send_message("❌ Seul le propriétaire peut utiliser ce panel!", ephemeral=True)
            return
        
        view = QualitySelect(self.channel)
        await interaction.response.send_message("🎵 Choisissez la qualité audio:", view=view, ephemeral=True)

    @discord.ui.button(label="🗑️ Supprimer", style=discord.ButtonStyle.danger, row=2)
    async def delete_channel(self, interaction: discord.Interaction, button):
        if interaction.user != self.owner:
            await interaction.response.send_message("❌ Seul le propriétaire peut utiliser ce panel!", ephemeral=True)
            return
        
        view = DeleteConfirmView(self.channel)
        await interaction.response.send_message("⚠️ Êtes-vous sûr de vouloir supprimer ce salon?", view=view, ephemeral=True)

class RenameModal(discord.ui.Modal):
    def __init__(self, channel):
        super().__init__(title="📝 Renommer le salon")
        self.channel = channel

    new_name = discord.ui.TextInput(
        label="Nouveau nom",
        placeholder="Entrez le nouveau nom du salon...",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        await self.channel.edit(name=self.new_name.value)
        await interaction.response.send_message(f"✅ Salon renommé: **{self.new_name.value}**", ephemeral=True)

class LimitModal(discord.ui.Modal):
    def __init__(self, channel):
        super().__init__(title="👥 Modifier la limite")
        self.channel = channel

    new_limit = discord.ui.TextInput(
        label="Nouvelle limite (0-99)",
        placeholder="0 pour illimité",
        required=True,
        max_length=2
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit = int(self.new_limit.value)
            if 0 <= limit <= 99:
                await self.channel.edit(user_limit=limit)
                limit_text = f"{limit} utilisateurs" if limit > 0 else "Illimitée"
                await interaction.response.send_message(f"✅ Limite définie: **{limit_text}**", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Limite entre 0 et 99!", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Valeur numérique requise!", ephemeral=True)

class QualitySelect(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=60)
        self.channel = channel

    @discord.ui.select(
        placeholder="Choisissez la qualité audio...",
        options=[
            discord.SelectOption(label="🔉 Standard (64 kbps)", value="64000"),
            discord.SelectOption(label="🔊 Bonne (128 kbps)", value="128000"),
            discord.SelectOption(label="🎵 Haute (256 kbps)", value="256000"),
            discord.SelectOption(label="🎶 Maximale (384 kbps)", value="384000")
        ]
    )
    async def select_quality(self, interaction: discord.Interaction, select):
        bitrate = int(select.values[0])
        await self.channel.edit(bitrate=bitrate)
        
        quality_names = {
            64000: "Standard (64 kbps)",
            128000: "Bonne (128 kbps)", 
            256000: "Haute (256 kbps)",
            384000: "Maximale (384 kbps)"
        }
        
        await interaction.response.send_message(f"✅ Qualité audio: **{quality_names[bitrate]}**", ephemeral=True)

class DeleteConfirmView(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=30)
        self.channel = channel

    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.danger)
    async def confirm_delete(self, interaction: discord.Interaction, button):
        await interaction.response.send_message("🗑️ Salon supprimé!", ephemeral=True)
        await self.channel.delete()

    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
    async def cancel_delete(self, interaction: discord.Interaction, button):
        await interaction.response.send_message("❌ Suppression annulée", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TempChannelCommands(bot))
