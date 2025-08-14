# 🚀 Arsenal V4 - Server Management System
"""
Système de gestion des serveurs pour Arsenal V4:
- Liste de tous les serveurs où se trouve le bot
- Informations détaillées sur chaque serveur
- Possibilité de quitter des serveurs
- Statistiques des serveurs
- Gestion des permissions
- Interface interactive pour la gestion
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
from datetime import datetime
import os
from typing import Optional, List

class ServerManagementSystem(commands.Cog):
    """Système de gestion des serveurs pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.server_logs_file = "data/server_logs.json"
        self.authorized_users = []  # IDs des utilisateurs autorisés
        self.init_server_management()

    def init_server_management(self):
        """Initialise le système de gestion des serveurs"""
        os.makedirs("data", exist_ok=True)
        
        # Charger les utilisateurs autorisés depuis les variables d'environnement
        creator_id = os.getenv("CREATOR_ID")
        if creator_id:
            try:
                self.authorized_users.append(int(creator_id))
            except ValueError:
                pass
        
        # Ajouter d'autres IDs autorisés si nécessaire
        admin_ids = os.getenv("ADMIN_IDS", "").split(",")
        for admin_id in admin_ids:
            if admin_id.strip():
                try:
                    self.authorized_users.append(int(admin_id.strip()))
                except ValueError:
                    pass

    def is_authorized(self, user_id: int) -> bool:
        """Vérifie si l'utilisateur est autorisé"""
        return user_id in self.authorized_users

    def save_server_action(self, action: str, guild_data: dict, user_id: int):
        """Sauvegarde les actions sur les serveurs"""
        if not os.path.exists(self.server_logs_file):
            logs = {"actions": []}
        else:
            try:
                with open(self.server_logs_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = {"actions": []}
        
        log_entry = {
            "action": action,
            "guild": guild_data,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        logs["actions"].append(log_entry)
        
        # Garder seulement les 50 dernières actions
        logs["actions"] = logs["actions"][-50:]
        
        with open(self.server_logs_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    @app_commands.command(name="servers", description="🌐 Gestion des serveurs Arsenal")
    async def servers_management(self, interaction: discord.Interaction):
        """Menu principal de gestion des serveurs"""
        
        if not self.is_authorized(interaction.user.id):
            await interaction.response.send_message("❌ Vous n'êtes pas autorisé à utiliser cette commande.", ephemeral=True)
            return
        
        guilds = self.bot.guilds
        total_members = sum(guild.member_count for guild in guilds if guild.member_count)
        
        embed = discord.Embed(
            title="🌐 Gestion des Serveurs Arsenal",
            description=f"Arsenal est présent sur **{len(guilds)} serveurs** avec un total de **{total_members:,} membres**",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📊 Statistiques Rapides",
            value=f"**Serveurs:** {len(guilds)}\n**Membres totaux:** {total_members:,}\n**Moyenne/serveur:** {total_members//len(guilds) if guilds else 0} membres",
            inline=True
        )
        
        embed.add_field(
            name="🔧 Actions Disponibles",
            value="`/servers_list` - Liste détaillée\n`/server_info` - Info serveur\n`/leave_server` - Quitter serveur",
            inline=True
        )
        
        embed.add_field(
            name="📈 Top 3 Serveurs",
            value="\n".join([f"**{guild.name}** ({guild.member_count or 0} membres)" 
                           for guild in sorted(guilds, key=lambda g: g.member_count or 0, reverse=True)[:3]]),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="servers_list", description="📋 Liste détaillée des serveurs")
    @app_commands.describe(page="Page à afficher (10 serveurs par page)")
    async def servers_list(self, interaction: discord.Interaction, page: int = 1):
        """Liste paginée des serveurs"""
        
        if not self.is_authorized(interaction.user.id):
            await interaction.response.send_message("❌ Vous n'êtes pas autorisé à utiliser cette commande.", ephemeral=True)
            return
        
        guilds = sorted(self.bot.guilds, key=lambda g: g.member_count or 0, reverse=True)
        
        # Pagination
        per_page = 10
        total_pages = (len(guilds) + per_page - 1) // per_page
        
        if page < 1 or page > total_pages:
            await interaction.response.send_message(f"❌ Page invalide. Pages disponibles: 1-{total_pages}", ephemeral=True)
            return
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_guilds = guilds[start_idx:end_idx]
        
        embed = discord.Embed(
            title=f"📋 Liste des Serveurs (Page {page}/{total_pages})",
            color=discord.Color.green()
        )
        
        for i, guild in enumerate(page_guilds, start=start_idx + 1):
            # Calculer l'âge du serveur
            created_days = (datetime.now(guild.created_at.tzinfo) - guild.created_at).days
            
            # Status du bot sur ce serveur
            bot_member = guild.get_member(self.bot.user.id)
            joined_date = bot_member.joined_at if bot_member and bot_member.joined_at else None
            
            guild_info = (
                f"**ID:** {guild.id}\n"
                f"**Membres:** {guild.member_count or 0}\n"
                f"**Créé:** il y a {created_days} jours\n"
                f"**Propriétaire:** {guild.owner.mention if guild.owner else 'Inconnu'}"
            )
            
            if joined_date:
                joined_days = (datetime.now(joined_date.tzinfo) - joined_date).days
                guild_info += f"\n**Bot rejoint:** il y a {joined_days} jours"
            
            embed.add_field(
                name=f"{i}. {guild.name}",
                value=guild_info,
                inline=False
            )
        
        embed.set_footer(text=f"Page {page}/{total_pages} • {len(guilds)} serveurs total • Arsenal V4")
        
        # Boutons de navigation
        view = ServerPaginationView(page, total_pages, self.is_authorized(interaction.user.id))
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="server_info", description="📊 Informations détaillées sur un serveur")
    @app_commands.describe(server_id="ID du serveur à consulter")
    async def server_info(self, interaction: discord.Interaction, server_id: str):
        """Informations détaillées sur un serveur spécifique"""
        
        if not self.is_authorized(interaction.user.id):
            await interaction.response.send_message("❌ Vous n'êtes pas autorisé à utiliser cette commande.", ephemeral=True)
            return
        
        try:
            guild_id = int(server_id)
        except ValueError:
            await interaction.response.send_message("❌ ID de serveur invalide.", ephemeral=True)
            return
        
        guild = self.bot.get_guild(guild_id)
        if not guild:
            await interaction.response.send_message("❌ Serveur introuvable ou bot non présent.", ephemeral=True)
            return
        
        # Informations détaillées
        bot_member = guild.get_member(self.bot.user.id)
        created_date = guild.created_at
        joined_date = bot_member.joined_at if bot_member and bot_member.joined_at else None
        
        embed = discord.Embed(
            title=f"📊 {guild.name}",
            description=f"Informations détaillées du serveur",
            color=discord.Color.blue()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Informations générales
        embed.add_field(
            name="🏷️ Informations Générales",
            value=(
                f"**ID:** {guild.id}\n"
                f"**Propriétaire:** {guild.owner.mention if guild.owner else 'Inconnu'}\n"
                f"**Région:** {guild.preferred_locale}\n"
                f"**Niveau de vérification:** {guild.verification_level.name}"
            ),
            inline=False
        )
        
        # Statistiques
        total_channels = len(guild.channels)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(
            name="📊 Statistiques",
            value=(
                f"**Membres:** {guild.member_count or 0}\n"
                f"**Canaux:** {total_channels} (📝{text_channels} 🔊{voice_channels})\n"
                f"**Catégories:** {categories}\n"
                f"**Rôles:** {len(guild.roles)}\n"
                f"**Emojis:** {len(guild.emojis)}"
            ),
            inline=True
        )
        
        # Dates importantes
        created_days = (datetime.now(created_date.tzinfo) - created_date).days
        joined_info = f"il y a {(datetime.now(joined_date.tzinfo) - joined_date).days} jours" if joined_date else "Inconnu"
        
        embed.add_field(
            name="📅 Dates",
            value=(
                f"**Serveur créé:** <t:{int(created_date.timestamp())}:R>\n"
                f"**Bot rejoint:** {joined_info}"
            ),
            inline=True
        )
        
        # Permissions du bot
        if bot_member:
            perms = bot_member.guild_permissions
            important_perms = []
            if perms.administrator:
                important_perms.append("👑 Administrateur")
            if perms.manage_guild:
                important_perms.append("⚙️ Gérer le serveur")
            if perms.kick_members:
                important_perms.append("👢 Expulser des membres")
            if perms.ban_members:
                important_perms.append("🔨 Bannir des membres")
            if perms.manage_channels:
                important_perms.append("📝 Gérer les canaux")
            
            embed.add_field(
                name="🛡️ Permissions du Bot",
                value="\n".join(important_perms[:5]) if important_perms else "Permissions de base",
                inline=False
            )
        
        # Bouton pour quitter le serveur
        view = ServerActionView(guild.id, self.is_authorized(interaction.user.id))
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="leave_server", description="🚪 Faire quitter Arsenal d'un serveur")
    @app_commands.describe(server_id="ID du serveur à quitter")
    async def leave_server(self, interaction: discord.Interaction, server_id: str):
        """Fait quitter le bot d'un serveur"""
        
        if not self.is_authorized(interaction.user.id):
            await interaction.response.send_message("❌ Vous n'êtes pas autorisé à utiliser cette commande.", ephemeral=True)
            return
        
        try:
            guild_id = int(server_id)
        except ValueError:
            await interaction.response.send_message("❌ ID de serveur invalide.", ephemeral=True)
            return
        
        guild = self.bot.get_guild(guild_id)
        if not guild:
            await interaction.response.send_message("❌ Serveur introuvable ou bot non présent.", ephemeral=True)
            return
        
        # Confirmation avant de quitter
        embed = discord.Embed(
            title="⚠️ Confirmation de Départ",
            description=f"Êtes-vous sûr de vouloir faire quitter Arsenal du serveur **{guild.name}** ?",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="📊 Informations du serveur",
            value=f"**Nom:** {guild.name}\n**ID:** {guild.id}\n**Membres:** {guild.member_count or 0}",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Attention",
            value="Cette action est **irréversible**. Le bot devra être réinvité pour revenir.",
            inline=False
        )
        
        view = LeaveConfirmationView(guild, interaction.user.id, self)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def execute_leave_server(self, guild: discord.Guild, user_id: int):
        """Exécute le départ du serveur"""
        
        guild_data = {
            "id": guild.id,
            "name": guild.name,
            "member_count": guild.member_count or 0
        }
        
        try:
            await guild.leave()
            
            # Logger l'action
            self.save_server_action("leave", guild_data, user_id)
            
            return True, f"✅ Arsenal a quitté le serveur **{guild.name}** avec succès."
        
        except Exception as e:
            return False, f"❌ Erreur lors du départ: {str(e)}"

class ServerPaginationView(discord.ui.View):
    """Vue pour la navigation dans la liste des serveurs"""
    
    def __init__(self, current_page: int, total_pages: int, is_authorized: bool):
        super().__init__(timeout=60)
        self.current_page = current_page
        self.total_pages = total_pages
        self.is_authorized = is_authorized
        
        # Désactiver les boutons si nécessaire
        if current_page <= 1:
            self.previous_page.disabled = True
        if current_page >= total_pages:
            self.next_page.disabled = True

    @discord.ui.button(label="◀️ Précédent", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_authorized:
            await interaction.response.send_message("❌ Non autorisé", ephemeral=True)
            return
        
        # Re-lancer la commande avec la page précédente
        cog = interaction.client.get_cog("ServerManagementSystem")
        if cog:
            await cog.servers_list(interaction, self.current_page - 1)

    @discord.ui.button(label="▶️ Suivant", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_authorized:
            await interaction.response.send_message("❌ Non autorisé", ephemeral=True)
            return
        
        # Re-lancer la commande avec la page suivante
        cog = interaction.client.get_cog("ServerManagementSystem")
        if cog:
            await cog.servers_list(interaction, self.current_page + 1)

class ServerActionView(discord.ui.View):
    """Vue pour les actions sur un serveur spécifique"""
    
    def __init__(self, guild_id: int, is_authorized: bool):
        super().__init__(timeout=60)
        self.guild_id = guild_id
        self.is_authorized = is_authorized

    @discord.ui.button(label="🚪 Quitter ce serveur", style=discord.ButtonStyle.danger)
    async def leave_server_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_authorized:
            await interaction.response.send_message("❌ Non autorisé", ephemeral=True)
            return
        
        cog = interaction.client.get_cog("ServerManagementSystem")
        if cog:
            await cog.leave_server(interaction, str(self.guild_id))

    @discord.ui.button(label="🔄 Actualiser", style=discord.ButtonStyle.primary)
    async def refresh_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_authorized:
            await interaction.response.send_message("❌ Non autorisé", ephemeral=True)
            return
        
        cog = interaction.client.get_cog("ServerManagementSystem")
        if cog:
            await cog.server_info(interaction, str(self.guild_id))

class LeaveConfirmationView(discord.ui.View):
    """Vue de confirmation pour quitter un serveur"""
    
    def __init__(self, guild: discord.Guild, user_id: int, cog):
        super().__init__(timeout=30)
        self.guild = guild
        self.user_id = user_id
        self.cog = cog

    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.danger)
    async def confirm_leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut confirmer.", ephemeral=True)
            return
        
        success, message = await self.cog.execute_leave_server(self.guild, self.user_id)
        
        if success:
            embed = discord.Embed(
                title="✅ Départ Confirmé",
                description=message,
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Erreur",
                description=message,
                color=discord.Color.red()
            )
        
        # Désactiver tous les boutons
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
    async def cancel_leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut annuler.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="❌ Action Annulée",
            description="Le bot restera sur le serveur.",
            color=discord.Color.blue()
        )
        
        # Désactiver tous les boutons
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)

async def setup(bot):
    await bot.add_cog(ServerManagementSystem(bot))
    print("🌐 [Server Management System] Module chargé avec succès!")
