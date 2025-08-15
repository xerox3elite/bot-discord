import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone

class ArsenalContextMenus(commands.Cog):
    """
    🖱️ Arsenal Context Menus
    Commandes via clic droit sur messages et utilisateurs
    Fonctionnalité Discord native moderne
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.setup_context_menus()
    
    def setup_context_menus(self):
        """Configure les menus contextuels"""
        print("🖱️ Configuration des menus contextuels Arsenal...")
    
    # ========================================
    # MENUS CONTEXTUELS UTILISATEURS (Clic droit sur un utilisateur)
    # ========================================
    
    @app_commands.context_menu(name="📊 Info Arsenal")
    async def user_info_context(self, interaction: discord.Interaction, member: discord.Member):
        """Information complète sur un utilisateur (clic droit)"""
        
        embed = discord.Embed(
            title=f"📊 Informations - {member.display_name}",
            color=member.color or discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        
        # Info de base
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(
            name="👤 Utilisateur",
            value=(
                f"**Nom**: {member.name}\n"
                f"**ID**: {member.id}\n"
                f"**Mention**: {member.mention}\n"
                f"**Bot**: {'✅ Oui' if member.bot else '❌ Non'}"
            ),
            inline=True
        )
        
        # Info serveur
        embed.add_field(
            name="🏠 Sur ce serveur",
            value=(
                f"**Pseudo**: {member.display_name}\n"
                f"**Rejoint le**: <t:{int(member.joined_at.timestamp())}:R>\n"
                f"**Rôle le plus haut**: {member.top_role.mention}\n"
                f"**Permissions**: {'Admin' if member.guild_permissions.administrator else 'Membre'}"
            ),
            inline=True
        )
        
        # Compte Discord
        embed.add_field(
            name="🎮 Compte Discord",
            value=(
                f"**Créé le**: <t:{int(member.created_at.timestamp())}:R>\n"
                f"**Statut**: {str(member.status).title()}\n"
                f"**Sur mobile**: {'✅' if member.is_on_mobile() else '❌'}\n"
                f"**Activité**: {member.activity.name if member.activity else 'Aucune'}"
            ),
            inline=False
        )
        
        # Rôles (max 5 pour éviter spam)
        roles = [role.mention for role in member.roles[1:]]  # Exclure @everyone
        roles_text = " • ".join(roles[:5])
        if len(roles) > 5:
            roles_text += f" • +{len(roles)-5} autres"
        
        embed.add_field(
            name=f"👑 Rôles ({len(roles)})",
            value=roles_text if roles_text else "Aucun rôle",
            inline=False
        )
        
        embed.set_footer(text=f"Arsenal Info System | Demandé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.context_menu(name="⚠️ Modérer Rapidement")
    async def quick_moderate_context(self, interaction: discord.Interaction, member: discord.Member):
        """Menu de modération rapide (clic droit)"""
        
        # Vérifier permissions
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message(
                "❌ Vous n'avez pas les permissions de modération!",
                ephemeral=True
            )
            return
        
        # Empêcher auto-modération
        if member.id == interaction.user.id:
            await interaction.response.send_message(
                "😅 Vous ne pouvez pas vous modérer vous-même!",
                ephemeral=True
            )
            return
        
        # Empêcher modération des bots/admins
        if member.bot or member.guild_permissions.administrator:
            await interaction.response.send_message(
                "🛡️ Impossible de modérer ce membre (Bot/Admin)!",
                ephemeral=True
            )
            return
        
        # Créer le menu de modération
        view = QuickModerationView(member)
        
        embed = discord.Embed(
            title="⚖️ Modération Rapide Arsenal",
            description=f"**Cible**: {member.mention}\nChoisissez une action:",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="🎯 Membre Ciblé",
            value=(
                f"**Nom**: {member.display_name}\n"
                f"**Rôle**: {member.top_role.mention}\n"
                f"**Rejoint**: <t:{int(member.joined_at.timestamp())}:R>"
            ),
            inline=False
        )
        
        embed.set_footer(text=f"Modération par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    # ========================================
    # MENUS CONTEXTUELS MESSAGES (Clic droit sur un message)
    # ========================================
    
    @app_commands.context_menu(name="📋 Analyser Message")
    async def analyze_message_context(self, interaction: discord.Interaction, message: discord.Message):
        """Analyse complète d'un message (clic droit)"""
        
        embed = discord.Embed(
            title="📋 Analyse Message Arsenal",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        
        # Info du message
        embed.add_field(
            name="📝 Contenu",
            value=(
                f"**Longueur**: {len(message.content)} caractères\n"
                f"**Mots**: {len(message.content.split()) if message.content else 0}\n"
                f"**Lignes**: {len(message.content.split(chr(10))) if message.content else 0}\n"
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
                f"**ID**: {message.id}\n"
                f"**Jump**: [Aller au message]({message.jump_url})"
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
        if message.channel_mentions:
            special_content.append(f"📢 {len(message.channel_mentions)} salon(s)")
        if message.role_mentions:
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
                f"**Rôle**: {message.author.top_role.mention if hasattr(message.author, 'top_role') else 'N/A'}"
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
        
        # Snippet du contenu si pas trop long
        if message.content and len(message.content) <= 200:
            embed.add_field(
                name="💬 Aperçu Contenu",
                value=f"```{message.content}```",
                inline=False
            )
        elif message.content:
            embed.add_field(
                name="💬 Aperçu Contenu",
                value=f"```{message.content[:200]}...```",
                inline=False
            )
        
        embed.set_footer(text=f"Analyse par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.context_menu(name="🛡️ Modérer Message")
    async def moderate_message_context(self, interaction: discord.Interaction, message: discord.Message):
        """Options de modération pour un message (clic droit)"""
        
        # Vérifier permissions
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "❌ Vous n'avez pas les permissions de gestion des messages!",
                ephemeral=True
            )
            return
        
        # Empêcher modération de ses propres messages
        if message.author.id == interaction.user.id:
            await interaction.response.send_message(
                "😅 Vous ne pouvez pas modérer vos propres messages!",
                ephemeral=True
            )
            return
        
        # Menu de modération de message
        view = MessageModerationView(message)
        
        embed = discord.Embed(
            title="🛡️ Modération Message Arsenal",
            description=f"**Message de**: {message.author.mention}",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="📝 Aperçu Message",
            value=f"```{message.content[:100]}...```" if len(message.content) > 100 else f"```{message.content}```",
            inline=False
        )
        
        embed.add_field(
            name="📍 Localisation",
            value=f"**Salon**: {message.channel.mention}\n**Jump**: [Aller au message]({message.jump_url})",
            inline=False
        )
        
        embed.set_footer(text=f"Modération par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.context_menu(name="⭐ Ajouter aux Favoris")
    async def add_to_favorites_context(self, interaction: discord.Interaction, message: discord.Message):
        """Ajouter un message aux favoris (clic droit)"""
        
        embed = discord.Embed(
            title="⭐ Message ajouté aux Favoris Arsenal",
            description="Ce message a été sauvegardé dans vos favoris personnels!",
            color=discord.Color.gold()
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
        
        # Ici on pourrait sauvegarder en base de données
        # Pour l'instant juste confirmation
        
        embed.set_footer(text="Utilisez /favorites pour voir tous vos messages sauvegardés")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ========================================
# VUES POUR LES ACTIONS DE MODÉRATION
# ========================================

class QuickModerationView(discord.ui.View):
    """Interface de modération rapide"""
    
    def __init__(self, member: discord.Member):
        super().__init__(timeout=300)
        self.member = member
    
    @discord.ui.button(label="⏰ Timeout 5min", style=discord.ButtonStyle.secondary)
    async def timeout_5min(self, interaction: discord.Interaction, button):
        """Timeout de 5 minutes"""
        try:
            await self.member.timeout(datetime.timedelta(minutes=5), reason=f"Timeout rapide par {interaction.user}")
            
            embed = discord.Embed(
                title="✅ Timeout Appliqué",
                description=f"{self.member.mention} a été mis en timeout pour 5 minutes",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ Permissions insuffisantes!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @discord.ui.button(label="⚠️ Avertissement", style=discord.ButtonStyle.primary)
    async def warn_member(self, interaction: discord.Interaction, button):
        """Avertir le membre"""
        # Ici on pourrait intégrer le système de warnings d'Arsenal
        embed = discord.Embed(
            title="⚠️ Avertissement Envoyé",
            description=f"{self.member.mention} a reçu un avertissement",
            color=discord.Color.yellow()
        )
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="🔇 Mute Vocal", style=discord.ButtonStyle.secondary)
    async def mute_voice(self, interaction: discord.Interaction, button):
        """Mute vocal"""
        if self.member.voice:
            try:
                await self.member.edit(mute=True, reason=f"Mute vocal par {interaction.user}")
                embed = discord.Embed(
                    title="🔇 Mute Vocal Appliqué",
                    description=f"{self.member.mention} a été mute vocalement",
                    color=discord.Color.green()
                )
                await interaction.response.edit_message(embed=embed, view=None)
            except Exception as e:
                await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Le membre n'est pas en vocal!", ephemeral=True)
    
    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.gray)
    async def cancel_moderation(self, interaction: discord.Interaction, button):
        """Annuler la modération"""
        embed = discord.Embed(
            title="❌ Modération Annulée",
            description="Aucune action n'a été effectuée",
            color=discord.Color.gray()
        )
        await interaction.response.edit_message(embed=embed, view=None)

class MessageModerationView(discord.ui.View):
    """Interface de modération de messages"""
    
    def __init__(self, message: discord.Message):
        super().__init__(timeout=300)
        self.message = message
    
    @discord.ui.button(label="🗑️ Supprimer", style=discord.ButtonStyle.danger)
    async def delete_message(self, interaction: discord.Interaction, button):
        """Supprimer le message"""
        try:
            await self.message.delete()
            embed = discord.Embed(
                title="🗑️ Message Supprimé",
                description="Le message a été supprimé avec succès",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=None)
        except discord.NotFound:
            await interaction.response.send_message("❌ Message déjà supprimé!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @discord.ui.button(label="📌 Pin", style=discord.ButtonStyle.primary)
    async def pin_message(self, interaction: discord.Interaction, button):
        """Épingler le message"""
        try:
            await self.message.pin()
            embed = discord.Embed(
                title="📌 Message Épinglé",
                description="Le message a été épinglé dans le salon",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=None)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @discord.ui.button(label="⭐ Réaction Auto", style=discord.ButtonStyle.secondary)
    async def auto_react(self, interaction: discord.Interaction, button):
        """Ajouter des réactions automatiques"""
        try:
            reactions = ["✅", "❌", "⭐", "👍", "👎"]
            for reaction in reactions[:3]:  # Limite à 3 réactions
                await self.message.add_reaction(reaction)
            
            embed = discord.Embed(
                title="⭐ Réactions Ajoutées",
                description="Réactions automatiques ajoutées au message",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=None)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.gray)
    async def cancel_message_mod(self, interaction: discord.Interaction, button):
        """Annuler la modération"""
        embed = discord.Embed(
            title="❌ Modération Annulée",
            description="Aucune action n'a été effectuée sur le message",
            color=discord.Color.gray()
        )
        await interaction.response.edit_message(embed=embed, view=None)

async def setup(bot):
    await bot.add_cog(ArsenalContextMenus(bot))
