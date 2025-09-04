"""
🔥 Arsenal Power Demo - Démonstration du système d'enregistrement
Montre la puissance du nouveau système avec niveaux et permissions
Auteur: Arsenal Studio
"""

import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
from datetime import datetime
import json
import random
from typing import Dict, List

# Import du système de protection Arsenal
from .arsenal_protection_middleware import require_registration, require_premium, require_beta, require_dev

class ArsenalPowerDemo(commands.Cog):
    """Démonstration de la puissance du système Arsenal"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="power-demo", description="🚀 Démonstration de la puissance Arsenal")
    @require_registration("basic")  # Nécessite juste l'enregistrement
    async def power_demo(self, interaction: discord.Interaction):
        """Démonstration complète du système"""
        
        # Récupérer le profil utilisateur
        async with aiosqlite.connect("arsenal_users_central.db") as db:
            cursor = await db.execute("""
                SELECT arsenal_id, arsenal_role, global_level, global_coins, 
                       total_commands_used, registration_date
                FROM arsenal_users WHERE discord_id = ?
            """, (interaction.user.id,))
            user_data = await cursor.fetchone()
        
        if not user_data:
            await interaction.response.send_message("❌ Erreur de récupération du profil", ephemeral=True)
            return
        
        arsenal_id, role, level, coins, commands, reg_date = user_data
        
        embed = discord.Embed(
            title="🚀 Arsenal Power Demo",
            description="**Démonstration de votre puissance Arsenal !**",
            color=0x7289da
        )
        
        embed.add_field(
            name="🆔 Votre Identité Arsenal",
            value=f"**ID:** `{arsenal_id}`\n**Rôle:** `{role.upper()}`",
            inline=True
        )
        
        embed.add_field(
            name="📊 Vos Stats",
            value=f"**Niveau:** `{level}`\n**Coins:** `{coins}`\n**Commandes:** `{commands}`",
            inline=True
        )
        
        # Calculer le score de puissance
        power_score = (level * 10) + (coins // 10) + commands
        embed.add_field(
            name="⚡ Score de Puissance",
            value=f"`{power_score}` points",
            inline=True
        )
        
        # Permissions disponibles selon le rôle
        permissions_map = {
            "membre": ["🔵 Commandes de base", "🔍 Consultation", "💬 Communication"],
            "beta": ["🔵 Commandes de base", "🧪 Fonctions beta", "🔍 Tests avancés"],
            "premium": ["🔵 Commandes de base", "🧪 Fonctions beta", "💎 Premium", "⚡ Accès prioritaire"],
            "dev": ["🔵 Commandes de base", "🧪 Fonctions beta", "💎 Premium", "🛠️ Outils dev", "🔧 Debug"],
            "creator": ["🔥 ACCÈS TOTAL", "🌟 CRÉATEUR", "👑 ADMIN SUPRÊME"]
        }
        
        user_permissions = permissions_map.get(role, ["❌ Aucune"])
        embed.add_field(
            name="🎯 Vos Permissions",
            value="\n".join(user_permissions),
            inline=False
        )
        
        # Prédictions et conseils
        if level < 10:
            next_unlock = "🎁 Récompenses niveau 10"
        elif level < 25:
            next_unlock = "🏆 Badge niveau 25"
        elif level < 50:
            next_unlock = "⭐ Statut VIP niveau 50"
        else:
            next_unlock = "👑 Légende Arsenal !"
        
        embed.add_field(
            name="🎯 Prochain Objectif",
            value=next_unlock,
            inline=True
        )
        
        # Recommandations personnalisées
        if role == "membre":
            recommendation = "💡 **Conseil:** Soyez actif pour débloquer le statut Beta !"
        elif role == "beta":
            recommendation = "🚀 **Conseil:** Excellent ! Visez le Premium pour plus de fonctionnalités !"
        elif role == "premium":
            recommendation = "⭐ **Conseil:** Statut Premium ! Vous avez accès à tout !"
        else:
            recommendation = "🔥 **Status:** Vous êtes une légende Arsenal !"
        
        embed.add_field(
            name="💡 Recommandation",
            value=recommendation,
            inline=False
        )
        
        embed.set_footer(
            text=f"Membre Arsenal depuis {reg_date[:10]} • Arsenal Studio"
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="level-up", description="📈 Système de montée de niveau")
    @require_registration("basic")
    async def level_up_demo(self, interaction: discord.Interaction):
        """Simulation du système de level"""
        
        # Simuler un gain d'XP
        xp_gained = random.randint(10, 50)
        coins_gained = random.randint(5, 25)
        
        async with aiosqlite.connect("arsenal_users_central.db") as db:
            # Mettre à jour les stats
            await db.execute("""
                UPDATE arsenal_users 
                SET global_level = global_level + ?, 
                    global_coins = global_coins + ?
                WHERE discord_id = ?
            """, (1, coins_gained, interaction.user.id))
            
            # Récupérer les nouvelles stats
            cursor = await db.execute("""
                SELECT global_level, global_coins FROM arsenal_users 
                WHERE discord_id = ?
            """, (interaction.user.id,))
            new_level, new_coins = await cursor.fetchone()
            
            await db.commit()
        
        embed = discord.Embed(
            title="📈 Level Up !",
            description="**Félicitations ! Vous avez progressé !**",
            color=0x00ff00
        )
        
        embed.add_field(
            name="⬆️ Gains",
            value=f"**XP:** +{xp_gained}\n**Level:** +1\n**Coins:** +{coins_gained}",
            inline=True
        )
        
        embed.add_field(
            name="📊 Nouvelles Stats",
            value=f"**Niveau:** `{new_level}`\n**Coins:** `{new_coins}`",
            inline=True
        )
        
        # Récompenses spéciales selon le niveau
        rewards = []
        if new_level % 5 == 0:
            rewards.append("🎁 Bonus multi-niveaux !")
        if new_level % 10 == 0:
            rewards.append("🏆 Badge de niveau !")
        if new_level >= 25:
            rewards.append("⭐ Statut VIP débloqué !")
        
        if rewards:
            embed.add_field(
                name="🎉 Récompenses Spéciales",
                value="\n".join(rewards),
                inline=False
            )
        
        embed.set_footer(text="Arsenal Studio • Système de progression")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="premium-features", description="💎 Fonctionnalités Premium")
    @require_premium()  # SEULEMENT pour les Premium+
    async def premium_features(self, interaction: discord.Interaction):
        """Démonstration des fonctionnalités premium"""
        
        embed = discord.Embed(
            title="💎 Arsenal Premium",
            description="**Vous avez accès aux fonctionnalités Premium !**",
            color=0xffd700
        )
        
        features = [
            "⚡ **Commandes prioritaires** - Exécution instantanée",
            "🎨 **Personnalisation avancée** - Profils custom",
            "📊 **Statistiques détaillées** - Analytics complets",
            "💰 **Bonus économie** - +50% coins sur toutes les actions",
            "🚀 **Accès beta** - Nouvelles fonctionnalités en avant-première",
            "👥 **Support premium** - Assistance prioritaire",
            "🏆 **Badges exclusifs** - Statuts uniques",
            "🔧 **Outils avancés** - Commandes de power-user"
        ]
        
        embed.add_field(
            name="🌟 Vos Avantages Premium",
            value="\n".join(features),
            inline=False
        )
        
        embed.add_field(
            name="🎯 Accès Exclusif",
            value="Cette commande n'est accessible qu'aux membres Premium+ !",
            inline=False
        )
        
        embed.set_footer(text="Arsenal Studio • Merci de votre soutien Premium !")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="dev-tools", description="🛠️ Outils développeur")
    @require_dev()  # SEULEMENT pour les Développeurs
    async def dev_tools(self, interaction: discord.Interaction):
        """Outils de développement et debug"""
        
        embed = discord.Embed(
            title="🛠️ Arsenal Developer Tools",
            description="**Outils de développement avancés**",
            color=0xff6b6b
        )
        
        # Stats du bot
        embed.add_field(
            name="🤖 Stats Bot",
            value=f"**Serveurs:** `{len(self.bot.guilds)}`\n"
                  f"**Utilisateurs:** `{sum(guild.member_count for guild in self.bot.guilds)}`\n"
                  f"**Commandes:** `{len(self.bot.tree.get_commands())}`",
            inline=True
        )
        
        # Stats de la base de données
        async with aiosqlite.connect("arsenal_users_central.db") as db:
            cursor = await db.execute("SELECT COUNT(*) FROM arsenal_users")
            total_users = (await cursor.fetchone())[0]
            
            cursor = await db.execute("SELECT COUNT(*) FROM user_activity")
            total_activities = (await cursor.fetchone())[0]
        
        embed.add_field(
            name="📊 Stats DB",
            value=f"**Utilisateurs:** `{total_users}`\n"
                  f"**Activités:** `{total_activities}`",
            inline=True
        )
        
        embed.add_field(
            name="🔧 Outils Disponibles",
            value="• `/debug-user` - Debug utilisateur\n"
                  "• `/system-status` - Statut système\n"
                  "• `/force-sync` - Sync commandes\n"
                  "• `/db-backup` - Sauvegarde DB\n"
                  "• `/performance` - Analyse perfs",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Accès Développeur",
            value="Ces outils sont réservés aux développeurs Arsenal !",
            inline=False
        )
        
        embed.set_footer(text="Arsenal Studio • Developer Access")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="multi-server-stats", description="🏰 Stats multi-serveurs")
    @require_registration("basic")
    async def multi_server_stats(self, interaction: discord.Interaction):
        """Afficher les stats multi-serveurs de l'utilisateur"""
        
        async with aiosqlite.connect("arsenal_users_central.db") as db:
            # Stats globales
            cursor = await db.execute("""
                SELECT global_level, global_coins FROM arsenal_users 
                WHERE discord_id = ?
            """, (interaction.user.id,))
            global_stats = await cursor.fetchone()
            
            # Stats par serveur
            cursor = await db.execute("""
                SELECT guild_id, server_level, server_coins, highest_role 
                FROM user_server_data WHERE discord_id = ?
            """, (interaction.user.id,))
            server_stats = await cursor.fetchall()
        
        embed = discord.Embed(
            title="🏰 Statistiques Multi-Serveurs",
            description="**Vos statistiques sur tous les serveurs Arsenal**",
            color=0x7289da
        )
        
        if global_stats:
            global_level, global_coins = global_stats
            embed.add_field(
                name="🌍 Global",
                value=f"**Niveau:** `{global_level}`\n**Coins:** `{global_coins}`",
                inline=True
            )
        
        if server_stats:
            total_server_level = sum(stat[1] for stat in server_stats)
            total_server_coins = sum(stat[2] for stat in server_stats)
            
            embed.add_field(
                name="🏰 Serveurs",
                value=f"**Serveurs actifs:** `{len(server_stats)}`\n"
                      f"**Niveau total:** `{total_server_level}`\n"
                      f"**Coins totaux:** `{total_server_coins}`",
                inline=True
            )
            
            # Détail des 3 premiers serveurs
            server_details = []
            for guild_id, level, coins, role in server_stats[:3]:
                try:
                    guild = self.bot.get_guild(guild_id)
                    guild_name = guild.name if guild else f"Serveur {guild_id}"
                    server_details.append(f"**{guild_name}**\n├ Niveau: `{level}`\n├ Coins: `{coins}`\n└ Rôle: `{role}`")
                except:
                    server_details.append(f"**Serveur {guild_id}**\n├ Niveau: `{level}`\n├ Coins: `{coins}`\n└ Rôle: `{role}`")
            
            if server_details:
                embed.add_field(
                    name="📊 Détail Serveurs",
                    value="\n\n".join(server_details),
                    inline=False
                )
        
        embed.set_footer(text="Arsenal Studio • Système Multi-Serveurs")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    """Setup du cog de démonstration"""
    await bot.add_cog(ArsenalPowerDemo(bot))
