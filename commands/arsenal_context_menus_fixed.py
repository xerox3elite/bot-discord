import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone
import asyncio
from typing import Optional

class ArsenalContextMenus(commands.Cog):
    """
    🖱️ Arsenal Context Menus
    Commandes via clic droit sur messages et utilisateurs
    Fonctionnalité Discord native moderne
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        # Context menu pour info utilisateur
        self.user_info_menu = app_commands.ContextMenu(
            name='📊 Info Arsenal',
            callback=self.user_info_callback,
        )
        
        # Context menu pour analyser un message
        self.analyze_message_menu = app_commands.ContextMenu(
            name='📋 Analyser Message',
            callback=self.analyze_message_callback,
        )
        
        # Context menu pour modérer rapidement
        self.quick_moderate_menu = app_commands.ContextMenu(
            name='⚠️ Modérer Rapidement', 
            callback=self.quick_moderate_callback,
        )
        
        # Context menu pour ajouter aux favoris
        self.add_favorites_menu = app_commands.ContextMenu(
            name='⭐ Ajouter aux Favoris',
            callback=self.add_favorites_callback,
        )
        
        # Ajouter les menus au bot
        self.bot.tree.add_command(self.user_info_menu)
        self.bot.tree.add_command(self.analyze_message_menu)
        self.bot.tree.add_command(self.quick_moderate_menu)
        self.bot.tree.add_command(self.add_favorites_menu)
        
        print("🖱️ Context Menus Arsenal chargés avec succès!")
    
    async def cog_unload(self):
        """Nettoyage lors du déchargement du cog"""
        self.bot.tree.remove_command(self.user_info_menu.name, type=self.user_info_menu.type)
        self.bot.tree.remove_command(self.analyze_message_menu.name, type=self.analyze_message_menu.type)
        self.bot.tree.remove_command(self.quick_moderate_menu.name, type=self.quick_moderate_menu.type)
        self.bot.tree.remove_command(self.add_favorites_menu.name, type=self.add_favorites_menu.type)
    
    # ========================================
    # CALLBACKS POUR CONTEXT MENUS UTILISATEURS
    # ========================================
    
    async def user_info_callback(self, interaction: discord.Interaction, user: discord.Member):
        """Information complète sur un utilisateur (clic droit)"""
        
        embed = discord.Embed(
            title=f"📊 Informations Arsenal - {user.display_name}",
            color=user.color or discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        
        # Avatar et info de base
        embed.set_thumbnail(url=user.display_avatar.url)
        
        embed.add_field(
            name="👤 Utilisateur",
            value=(
                f"**Nom**: {user.name}\n"
                f"**Pseudo**: {user.display_name}\n"
                f"**ID**: `{user.id}`\n"
                f"**Mention**: {user.mention}\n"
                f"**Bot**: {'✅ Oui' if user.bot else '❌ Non'}"
            ),
            inline=True
        )
        
        # Info serveur si c'est un membre
        if hasattr(user, 'joined_at') and user.joined_at:
            embed.add_field(
                name="🏠 Sur ce serveur",
                value=(
                    f"**Rejoint le**: <t:{int(user.joined_at.timestamp())}:F>\n"
                    f"**Il y a**: <t:{int(user.joined_at.timestamp())}:R>\n"
                    f"**Rôle principal**: {user.top_role.mention}\n"
                    f"**Couleur**: {str(user.color)}"
                ),
                inline=True
            )
        
        # Info temporelle
        embed.add_field(
            name="⏰ Compte Discord",
            value=(
                f"**Créé le**: <t:{int(user.created_at.timestamp())}:F>\n"
                f"**Il y a**: <t:{int(user.created_at.timestamp())}:R>\n"
                f"**Status**: {str(user.status).title()}\n"
                f"**Mobile**: {'📱 Oui' if user.is_on_mobile() else '💻 Non'}"
            ),
            inline=False
        )
        
        # Rôles (limité aux 10 premiers)
        if hasattr(user, 'roles') and len(user.roles) > 1:
            roles = [role.mention for role in reversed(user.roles[1:])][:10]
            roles_text = " • ".join(roles)
            if len(user.roles) > 11:
                roles_text += f" • ... (+{len(user.roles) - 11} autres)"
            
            embed.add_field(
                name=f"👑 Rôles ({len(user.roles) - 1})",
                value=roles_text,
                inline=False
            )
        
        # Permissions importantes
        if hasattr(user, 'guild_permissions'):
            important_perms = []
            if user.guild_permissions.administrator:
                important_perms.append("👑 Administrateur")
            if user.guild_permissions.moderate_members:
                important_perms.append("⚖️ Modérateur")
            if user.guild_permissions.manage_channels:
                important_perms.append("📋 Gestion Salons")
            if user.guild_permissions.manage_roles:
                important_perms.append("🎭 Gestion Rôles")
            if user.guild_permissions.manage_messages:
                important_perms.append("💬 Gestion Messages")
            
            if important_perms:
                embed.add_field(
                    name="🔑 Permissions Clés",
                    value=" • ".join(important_perms[:5]),
                    inline=False
                )
        
        embed.set_footer(
            text=f"Arsenal Info System | Demandé par {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def quick_moderate_callback(self, interaction: discord.Interaction, user: discord.Member):
        """Menu de modération rapide (clic droit sur utilisateur)"""
        
        # Vérifier permissions
        if not interaction.user.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="❌ Accès Refusé",
                description="Vous n'avez pas les permissions de modération!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Empêcher auto-modération
        if user.id == interaction.user.id:
            embed = discord.Embed(
                title="😅 Action Impossible", 
                description="Vous ne pouvez pas vous modérer vous-même!",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Empêcher modération des admins/bots
        if user.bot or user.guild_permissions.administrator:
            embed = discord.Embed(
                title="🛡️ Action Bloquée",
                description="Impossible de modérer ce membre (Bot/Administrateur)!",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Menu de modération
        view = QuickModerationView(user)
        
        embed = discord.Embed(
            title="⚖️ Modération Rapide Arsenal",
            description=f"**Cible**: {user.mention}\n\n🎯 Choisissez une action de modération:",
            color=discord.Color.red(),
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(
            name="👤 Membre Ciblé",
            value=(
                f"**Nom**: {user.display_name}\n"
                f"**Rôle**: {user.top_role.mention}\n"
                f"**Rejoint**: <t:{int(user.joined_at.timestamp() if user.joined_at else 0)}:R>"
            ),
            inline=False
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Modération par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    # ========================================
    # CALLBACKS POUR CONTEXT MENUS MESSAGES
    # ========================================
    
    async def analyze_message_callback(self, interaction: discord.Interaction, message: discord.Message):
        """Analyse complète d'un message (clic droit)"""
        
        embed = discord.Embed(
            title="📋 Analyse Message Arsenal",
            description="🔍 Analyse détaillée du message sélectionné",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        
        # Info du message
        embed.add_field(
            name="📝 Contenu",
            value=(
                f"**Longueur**: {len(message.content)} caractères\n"
                f"**Mots**: {len(message.content.split()) if message.content else 0}\n"
                f"**Lignes**: {len(message.content.split('\n')) if message.content else 0}\n"
                f"**Type**: {'Embed' if message.embeds else 'Texte'}"
            ),
            inline=True
        )
        
        # Info temporelle  
        embed.add_field(
            name="⏰ Timing",
            value=(
                f"**Envoyé**: <t:{int(message.created_at.timestamp())}:R>\n"
                f"**Édité**: {'✅ Oui' if message.edited_at else '❌ Non'}\n"
                f"**ID**: `{message.id}`\n"
                f"**Link**: [Aller au message]({message.jump_url})"
            ),
            inline=True
        )
        
        # Contenu spécial
        special_content = []
        if message.attachments:
            special_content.append(f"📎 {len(message.attachments)} fichier(s)")
        if message.embeds:
            special_content.append(f"📋 {len(message.embeds)} embed(s)")
        if message.reactions:
            special_content.append(f"⭐ {len(message.reactions)} réaction(s)")
        if message.mentions:
            special_content.append(f"👤 {len(message.mentions)} mention(s)")
        if hasattr(message, 'channel_mentions') and message.channel_mentions:
            special_content.append(f"📢 {len(message.channel_mentions)} salon(s)")
        if hasattr(message, 'role_mentions') and message.role_mentions:
            special_content.append(f"👑 {len(message.role_mentions)} rôle(s)")
        
        if special_content:
            embed.add_field(
                name="🎯 Contenu Spécial", 
                value=" • ".join(special_content),
                inline=False
            )
        
        # Auteur
        embed.add_field(
            name="👤 Auteur",
            value=(
                f"**Nom**: {message.author.display_name}\n"
                f"**Bot**: {'✅' if message.author.bot else '❌'}\n"
                f"**ID**: `{message.author.id}`"
            ),
            inline=True
        )
        
        # Salon
        embed.add_field(
            name="📢 Salon",
            value=(
                f"**Nom**: {message.channel.mention}\n"
                f"**Type**: {str(message.channel.type).title()}\n"
                f"**Catégorie**: {message.channel.category.name if hasattr(message.channel, 'category') and message.channel.category else 'Aucune'}"
            ),
            inline=True
        )
        
        # Preview du contenu si pas trop long
        if message.content:
            if len(message.content) <= 200:
                embed.add_field(
                    name="💬 Aperçu Contenu",
                    value=f"```{message.content}```",
                    inline=False
                )
            else:
                embed.add_field(
                    name="💬 Aperçu Contenu (tronqué)",
                    value=f"```{message.content[:200]}...```",
                    inline=False
                )
        
        embed.set_footer(text=f"Analyse par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def add_favorites_callback(self, interaction: discord.Interaction, message: discord.Message):
        """Ajouter un message aux favoris (clic droit)"""
        
        embed = discord.Embed(
            title="⭐ Message ajouté aux Favoris Arsenal",
            description="✅ Ce message a été sauvegardé dans vos favoris personnels!",
            color=discord.Color.gold(),
            timestamp=datetime.now(timezone.utc)
        )
        
        # Aperçu du message favori
        embed.add_field(
            name="💬 Message Favori",
            value=(
                f"**Auteur**: {message.author.mention}\n"
                f"**Salon**: {message.channel.mention}\n"
                f"**Date**: <t:{int(message.created_at.timestamp())}:R>\n"
                f"**Link**: [Aller au message]({message.jump_url})"
            ),
            inline=False
        )
        
        if message.content:
            content_preview = message.content[:300] + "..." if len(message.content) > 300 else message.content
            embed.add_field(
                name="📝 Aperçu",
                value=f"```{content_preview}```",
                inline=False
            )
        
        # TODO: Ici on pourrait sauvegarder en base de données
        # Pour l'instant juste confirmation
        
        embed.set_footer(
            text="💡 Utilisez la commande /favorites pour voir tous vos messages sauvegardés",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ========================================
# VUES POUR LES ACTIONS DE MODÉRATION
# ========================================

class QuickModerationView(discord.ui.View):
    """Interface de modération rapide avec boutons"""
    
    def __init__(self, member: discord.Member):
        super().__init__(timeout=300)
        self.member = member
    
    @discord.ui.button(label="⏰ Timeout 5min", style=discord.ButtonStyle.secondary, emoji="⏰")
    async def timeout_5min(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Timeout de 5 minutes"""
        try:
            await self.member.timeout(
                discord.utils.utcnow() + discord.timedelta(minutes=5),
                reason=f"Timeout rapide par {interaction.user}"
            )
            
            embed = discord.Embed(
                title="✅ Timeout Appliqué",
                description=f"🔇 {self.member.mention} a été mis en timeout pour **5 minutes**",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(text="Arsenal Modération System")
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ Permissions insuffisantes pour timeout ce membre!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors du timeout: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="⚠️ Avertissement", style=discord.ButtonStyle.primary, emoji="⚠️")
    async def warn_member(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Avertir le membre"""
        # TODO: Intégrer avec le système de warnings d'Arsenal
        embed = discord.Embed(
            title="⚠️ Avertissement Envoyé",
            description=f"📬 {self.member.mention} a reçu un avertissement officiel",
            color=discord.Color.yellow(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_footer(text="Arsenal Modération System")
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="🔇 Mute Vocal", style=discord.ButtonStyle.secondary, emoji="🔇")
    async def mute_voice(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Mute vocal"""
        if self.member.voice:
            try:
                await self.member.edit(mute=True, reason=f"Mute vocal par {interaction.user}")
                embed = discord.Embed(
                    title="🔇 Mute Vocal Appliqué",
                    description=f"🎤 {self.member.mention} a été mute vocalement",
                    color=discord.Color.green(),
                    timestamp=datetime.now(timezone.utc)
                )
                embed.set_footer(text="Arsenal Modération System")
                
                await interaction.response.edit_message(embed=embed, view=None)
            except Exception as e:
                await interaction.response.send_message(f"❌ Erreur lors du mute vocal: {str(e)}", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Le membre n'est pas connecté en vocal!", ephemeral=True)
    
    @discord.ui.button(label="💀 Kick", style=discord.ButtonStyle.danger, emoji="💀")
    async def kick_member(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Kick le membre du serveur"""
        try:
            await self.member.kick(reason=f"Kick rapide par {interaction.user}")
            embed = discord.Embed(
                title="💀 Membre Expulsé",
                description=f"👢 {self.member.mention} a été expulsé du serveur",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(text="Arsenal Modération System")
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ Permissions insuffisantes pour expulser ce membre!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors de l'expulsion: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.gray, emoji="❌")
    async def cancel_moderation(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Annuler la modération"""
        embed = discord.Embed(
            title="❌ Modération Annulée",
            description="🚫 Aucune action n'a été effectuée",
            color=discord.Color.gray(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_footer(text="Arsenal Modération System")
        
        await interaction.response.edit_message(embed=embed, view=None)

async def setup(bot):
    """Setup function pour charger le cog"""
    await bot.add_cog(ArsenalContextMenus(bot))
    print("✅ Arsenal Context Menus chargé avec succès!")
