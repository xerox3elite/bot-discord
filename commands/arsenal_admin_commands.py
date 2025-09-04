"""
👑 Arsenal Admin Commands - Commandes d'administration
Commandes réservées aux administrateurs et fondateurs
Auteur: Arsenal Studio
"""

import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
from datetime import datetime
import json
from typing import Optional, List

# Import du système de protection Arsenal
from .arsenal_protection_middleware import (
    require_registration, require_moderator, require_admin, 
    require_fondateur, require_dev, require_creator
)

class ArsenalAdminCommands(commands.Cog):
    """Commandes d'administration Arsenal"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="promote-user", description="⬆️ Promouvoir un utilisateur Arsenal")
    @app_commands.describe(
        user="Utilisateur à promouvoir",
        new_role="Nouveau rôle Arsenal"
    )
    @app_commands.choices(new_role=[
        app_commands.Choice(name="Beta Testeur", value="beta"),
        app_commands.Choice(name="Premium", value="premium"),
        app_commands.Choice(name="Modérateur", value="moderator"),
        app_commands.Choice(name="Administrateur", value="admin"),
        app_commands.Choice(name="Fondateur", value="fondateur"),
        app_commands.Choice(name="Développeur", value="dev")
    ])
    @require_fondateur()  # Fondateurs uniquement
    async def promote_user(self, interaction: discord.Interaction, user: discord.Member, new_role: str):
        """Promouvoir un utilisateur à un rôle Arsenal supérieur"""
        
        async with aiosqlite.connect("arsenal_users_central.db") as db:
            # Vérifier si l'utilisateur est enregistré
            cursor = await db.execute(
                "SELECT arsenal_role FROM arsenal_users WHERE discord_id = ?", (user.id,)
            )
            current_data = await cursor.fetchone()
            
            if not current_data:
                await interaction.response.send_message(
                    f"❌ {user.mention} n'est pas enregistré dans Arsenal !", ephemeral=True
                )
                return
            
            current_role = current_data[0]
            
            # Mettre à jour le rôle
            await db.execute("""
                UPDATE arsenal_users 
                SET arsenal_role = ? 
                WHERE discord_id = ?
            """, (new_role, user.id))
            
            # Enregistrer l'historique
            cursor = await db.execute(
                "SELECT arsenal_id FROM arsenal_users WHERE discord_id = ?", (user.id,)
            )
            arsenal_id = (await cursor.fetchone())[0]
            
            await db.execute("""
                INSERT INTO user_activity 
                (arsenal_id, discord_id, guild_id, activity_type, activity_data, timestamp)
                VALUES (?, ?, ?, 'promotion', ?, datetime('now'))
            """, (
                arsenal_id, user.id, interaction.guild.id,
                json.dumps({
                    "old_role": current_role,
                    "new_role": new_role,
                    "promoted_by": str(interaction.user)
                })
            ))
            
            await db.commit()
        
        embed = discord.Embed(
            title="⬆️ Promotion Arsenal",
            description=f"**{user.display_name}** a été promu !",
            color=0x00ff00
        )
        embed.add_field(
            name="👤 Utilisateur",
            value=user.mention,
            inline=True
        )
        embed.add_field(
            name="📈 Ancien Rôle",
            value=f"`{current_role.upper()}`",
            inline=True
        )
        embed.add_field(
            name="🌟 Nouveau Rôle",
            value=f"`{new_role.upper()}`",
            inline=True
        )
        embed.add_field(
            name="👑 Promu par",
            value=interaction.user.mention,
            inline=False
        )
        embed.set_footer(text="Arsenal Studio • Système de promotions")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="user-arsenal-info", description="👤 Info complète d'un utilisateur Arsenal")
    @app_commands.describe(user="Utilisateur à analyser")
    @require_admin()  # Administrateurs uniquement
    async def user_arsenal_info(self, interaction: discord.Interaction, user: discord.Member):
        """Informations complètes d'un utilisateur Arsenal"""
        
        async with aiosqlite.connect("arsenal_users_central.db") as db:
            # Données principales
            cursor = await db.execute("""
                SELECT arsenal_id, arsenal_role, global_level, global_coins,
                       premium_status, beta_access, total_commands_used, 
                       registration_date, last_activity
                FROM arsenal_users WHERE discord_id = ?
            """, (user.id,))
            user_data = await cursor.fetchone()
            
            if not user_data:
                await interaction.response.send_message(
                    f"❌ {user.mention} n'est pas enregistré dans Arsenal !", ephemeral=True
                )
                return
            
            # Activité récente
            cursor = await db.execute("""
                SELECT activity_type, timestamp FROM user_activity 
                WHERE discord_id = ? 
                ORDER BY timestamp DESC LIMIT 5
            """, (user.id,))
            recent_activity = await cursor.fetchall()
            
            # Stats serveurs
            cursor = await db.execute("""
                SELECT COUNT(*), SUM(server_level), SUM(server_coins)
                FROM user_server_data WHERE discord_id = ?
            """, (user.id,))
            server_stats = await cursor.fetchone()
        
        arsenal_id, role, level, coins, premium, beta, commands, reg_date, last_active = user_data
        server_count, total_server_level, total_server_coins = server_stats or (0, 0, 0)
        
        embed = discord.Embed(
            title="👤 Arsenal User Analysis",
            description=f"**Analyse complète de {user.display_name}**",
            color=0x7289da
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        
        # Identité Arsenal
        embed.add_field(
            name="🆔 Identité Arsenal",
            value=f"**ID:** `{arsenal_id}`\n"
                  f"**Rôle:** `{role.upper()}`\n"
                  f"**Discord:** {user.mention}",
            inline=False
        )
        
        # Statistiques
        embed.add_field(
            name="📊 Statistiques Globales",
            value=f"**Niveau:** `{level}`\n"
                  f"**Coins:** `{coins}`\n"
                  f"**Commandes:** `{commands}`",
            inline=True
        )
        
        # Statuts spéciaux
        embed.add_field(
            name="⭐ Statuts",
            value=f"**Premium:** {'✅' if premium else '❌'}\n"
                  f"**Beta:** {'✅' if beta else '❌'}\n"
                  f"**Serveurs:** `{server_count or 0}`",
            inline=True
        )
        
        # Multi-serveurs
        if server_count:
            embed.add_field(
                name="🏰 Multi-Serveurs",
                value=f"**Total Niveau:** `{total_server_level or 0}`\n"
                      f"**Total Coins:** `{total_server_coins or 0}`",
                inline=True
            )
        
        # Activité récente
        if recent_activity:
            activities = []
            for activity_type, timestamp in recent_activity[:3]:
                activities.append(f"• `{activity_type}` - {timestamp[:10]}")
            
            embed.add_field(
                name="📅 Activité Récente",
                value="\n".join(activities),
                inline=False
            )
        
        # Informations temporelles
        embed.add_field(
            name="⏰ Informations",
            value=f"**Enregistré:** `{reg_date[:10]}`\n"
                  f"**Dernière activité:** `{last_active[:10] if last_active else 'Jamais'}`",
            inline=False
        )
        
        embed.set_footer(text="Arsenal Studio • Admin Panel")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="arsenal-stats", description="📊 Statistiques globales Arsenal")
    @require_admin()  # Administrateurs uniquement
    async def arsenal_global_stats(self, interaction: discord.Interaction):
        """Statistiques globales du système Arsenal"""
        
        async with aiosqlite.connect("arsenal_users_central.db") as db:
            # Stats générales
            cursor = await db.execute("SELECT COUNT(*) FROM arsenal_users")
            total_users = (await cursor.fetchone())[0]
            
            cursor = await db.execute("SELECT COUNT(*) FROM user_activity")
            total_activities = (await cursor.fetchone())[0]
            
            cursor = await db.execute("SELECT SUM(total_commands_used) FROM arsenal_users")
            total_commands = (await cursor.fetchone())[0] or 0
            
            # Stats par rôle
            cursor = await db.execute("""
                SELECT arsenal_role, COUNT(*) FROM arsenal_users 
                GROUP BY arsenal_role ORDER BY COUNT(*) DESC
            """)
            role_stats = await cursor.fetchall()
            
            # Utilisateurs actifs (dernière semaine)
            cursor = await db.execute("""
                SELECT COUNT(DISTINCT discord_id) FROM user_activity 
                WHERE datetime(timestamp) > datetime('now', '-7 days')
            """)
            active_users = (await cursor.fetchone())[0]
        
        embed = discord.Embed(
            title="📊 Arsenal Global Statistics",
            description="**Statistiques du système Arsenal**",
            color=0x7289da
        )
        
        # Stats principales
        embed.add_field(
            name="👥 Utilisateurs",
            value=f"**Total:** `{total_users}`\n"
                  f"**Actifs (7j):** `{active_users}`\n"
                  f"**Ratio:** `{(active_users/total_users*100):.1f}%`" if total_users > 0 else "0%",
            inline=True
        )
        
        embed.add_field(
            name="📈 Activité",
            value=f"**Événements:** `{total_activities}`\n"
                  f"**Commandes:** `{total_commands}`\n"
                  f"**Moyenne/user:** `{(total_commands/total_users):.1f}`" if total_users > 0 else "0",
            inline=True
        )
        
        # Stats du bot
        embed.add_field(
            name="🤖 Bot Stats",
            value=f"**Serveurs:** `{len(self.bot.guilds)}`\n"
                  f"**Utilisateurs:** `{sum(g.member_count for g in self.bot.guilds)}`\n"
                  f"**Commandes:** `{len(self.bot.tree.get_commands())}`",
            inline=True
        )
        
        # Répartition par rôles
        if role_stats:
            role_info = []
            for role, count in role_stats:
                percentage = (count / total_users * 100) if total_users > 0 else 0
                role_info.append(f"**{role.upper()}:** `{count}` ({percentage:.1f}%)")
            
            embed.add_field(
                name="👑 Répartition des Rôles",
                value="\n".join(role_info),
                inline=False
            )
        
        embed.set_footer(text=f"Arsenal Studio • Mis à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="emergency-reset", description="🚨 Reset d'urgence utilisateur")
    @app_commands.describe(user="Utilisateur à reset", confirm="Tapez 'CONFIRMER' pour valider")
    @require_creator()  # Creator uniquement - dangereux
    async def emergency_reset(self, interaction: discord.Interaction, user: discord.Member, confirm: str):
        """Reset complet d'un utilisateur (DANGEREUX)"""
        
        if confirm != "CONFIRMER":
            await interaction.response.send_message(
                "❌ Vous devez taper 'CONFIRMER' exactement pour valider !", ephemeral=True
            )
            return
        
        async with aiosqlite.connect("arsenal_users_central.db") as db:
            # Vérifier si l'utilisateur existe
            cursor = await db.execute(
                "SELECT arsenal_id FROM arsenal_users WHERE discord_id = ?", (user.id,)
            )
            result = await cursor.fetchone()
            
            if not result:
                await interaction.response.send_message(
                    f"❌ {user.mention} n'est pas enregistré !", ephemeral=True
                )
                return
            
            arsenal_id = result[0]
            
            # RESET COMPLET
            await db.execute("DELETE FROM arsenal_users WHERE discord_id = ?", (user.id,))
            await db.execute("DELETE FROM user_server_data WHERE discord_id = ?", (user.id,))
            await db.execute("DELETE FROM user_permissions WHERE arsenal_id = ?", (arsenal_id,))
            await db.execute("DELETE FROM user_activity WHERE discord_id = ?", (user.id,))
            
            await db.commit()
        
        embed = discord.Embed(
            title="🚨 Reset d'Urgence Effectué",
            description=f"**{user.display_name}** a été complètement supprimé d'Arsenal !",
            color=0xff0000
        )
        embed.add_field(
            name="⚠️ Actions effectuées",
            value="• Profil Arsenal supprimé\n"
                  "• Données serveurs effacées\n"
                  "• Permissions révoquées\n"
                  "• Historique purgé",
            inline=False
        )
        embed.add_field(
            name="👑 Effectué par",
            value=interaction.user.mention,
            inline=True
        )
        embed.set_footer(text="Arsenal Studio • Emergency Reset System")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    """Setup des commandes admin"""
    await bot.add_cog(ArsenalAdminCommands(bot))
