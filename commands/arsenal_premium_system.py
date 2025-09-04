"""
💎 Arsenal Premium System - Système de gestion Premium
Système pour devenir Premium Arsenal basé sur l'activité
Auteur: Arsenal Studio
"""

import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
from datetime import datetime, timedelta
import json
from typing import Optional, Dict

# Import du système de protection Arsenal
from .arsenal_protection_middleware import require_registration, require_creator

class ArsenalPremiumSystem(commands.Cog):
    """Système de gestion Premium Arsenal"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="request-premium", description="💎 Demander le statut Premium")
    @require_registration("basic")
    async def request_premium(self, interaction: discord.Interaction):
        """Demander à devenir Premium Arsenal"""
        
        async with aiosqlite.connect("arsenal_users_central.db") as db:
            # Récupérer les stats de l'utilisateur
            cursor = await db.execute("""
                SELECT arsenal_role, global_level, total_commands_used, 
                       registration_date, global_coins
                FROM arsenal_users WHERE discord_id = ?
            """, (interaction.user.id,))
            user_data = await cursor.fetchone()
            
            if not user_data:
                await interaction.response.send_message("❌ Erreur de récupération du profil", ephemeral=True)
                return
            
            current_role, level, commands, reg_date, coins = user_data
            
            if current_role in ["premium", "moderator", "admin", "fondateur", "dev", "creator"]:
                await interaction.response.send_message(
                    f"✅ Vous avez déjà un statut supérieur : `{current_role.upper()}`", ephemeral=True
                )
                return
        
        # Calculer les critères Premium
        embed = discord.Embed(
            title="💎 Demande de Statut Premium",
            description="**Analysons votre éligibilité Premium...**",
            color=0xffd700
        )
        
        # Critères d'éligibilité
        criteria = {
            "Niveau minimum (15+)": level >= 15,
            "Commandes utilisées (50+)": commands >= 50,
            "Coins accumulés (500+)": coins >= 500,
            "Ancienneté (7 jours+)": (datetime.now() - datetime.fromisoformat(reg_date)).days >= 7
        }
        
        eligible_count = sum(criteria.values())
        total_criteria = len(criteria)
        
        # Afficher les critères
        criteria_text = []
        for criterion, met in criteria.items():
            status = "✅" if met else "❌"
            criteria_text.append(f"{status} {criterion}")
        
        embed.add_field(
            name="📋 Critères Premium",
            value="\n".join(criteria_text),
            inline=False
        )
        
        # Vos stats actuelles
        embed.add_field(
            name="📊 Vos Stats",
            value=f"**Niveau:** `{level}`\n"
                  f"**Commandes:** `{commands}`\n"
                  f"**Coins:** `{coins}`\n"
                  f"**Ancienneté:** `{(datetime.now() - datetime.fromisoformat(reg_date)).days} jours`",
            inline=True
        )
        
        # Résultat
        if eligible_count >= total_criteria:
            embed.add_field(
                name="🎉 Résultat",
                value="**✅ ÉLIGIBLE !**\nVous répondez à tous les critères Premium !",
                inline=True
            )
            embed.color = 0x00ff00
            
            # Auto-promotion si tous les critères sont remplis
            async with aiosqlite.connect("arsenal_users_central.db") as db:
                await db.execute("""
                    UPDATE arsenal_users SET arsenal_role = 'premium' WHERE discord_id = ?
                """, (interaction.user.id,))
                
                # Enregistrer l'historique
                cursor = await db.execute(
                    "SELECT arsenal_id FROM arsenal_users WHERE discord_id = ?", (interaction.user.id,)
                )
                arsenal_id = (await cursor.fetchone())[0]
                
                await db.execute("""
                    INSERT INTO user_activity 
                    (arsenal_id, discord_id, guild_id, activity_type, activity_data, timestamp)
                    VALUES (?, ?, ?, 'auto_promotion', ?, datetime('now'))
                """, (
                    arsenal_id, interaction.user.id, interaction.guild.id if interaction.guild else 0,
                    json.dumps({"new_role": "premium", "method": "auto_criteria"})
                ))
                
                await db.commit()
            
            embed.add_field(
                name="🚀 Félicitations !",
                value="Vous êtes maintenant **PREMIUM ARSENAL** !",
                inline=False
            )
            
        else:
            missing = total_criteria - eligible_count
            embed.add_field(
                name="⏳ Résultat",
                value=f"**❌ NON ÉLIGIBLE**\nIl vous manque `{missing}` critère(s)",
                inline=True
            )
            embed.color = 0xff6b6b
            
            # Conseils pour progresser
            tips = []
            if level < 15:
                tips.append(f"• Gagnez `{15-level}` niveaux (utilisez plus le bot)")
            if commands < 50:
                tips.append(f"• Utilisez `{50-commands}` commandes de plus")
            if coins < 500:
                tips.append(f"• Gagnez `{500-coins}` coins supplémentaires")
            
            if tips:
                embed.add_field(
                    name="💡 Comment progresser",
                    value="\n".join(tips),
                    inline=False
                )
        
        embed.set_footer(text="Arsenal Studio • Système Premium")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="premium-benefits", description="💎 Voir les avantages Premium")
    @require_registration("basic")
    async def premium_benefits(self, interaction: discord.Interaction):
        """Afficher les avantages Premium Arsenal"""
        
        # Récupérer le rôle actuel
        async with aiosqlite.connect("arsenal_users_central.db") as db:
            cursor = await db.execute(
                "SELECT arsenal_role FROM arsenal_users WHERE discord_id = ?", (interaction.user.id,)
            )
            result = await cursor.fetchone()
            current_role = result[0] if result else "membre"
        
        embed = discord.Embed(
            title="💎 Arsenal Premium Benefits",
            description="**Découvrez les avantages Premium !**",
            color=0xffd700
        )
        
        benefits = [
            "⚡ **Commandes prioritaires** - Exécution plus rapide",
            "🎨 **Profil personnalisé** - Couleurs et badges custom",
            "💰 **Bonus économie** - +25% de coins sur toutes les actions",
            "📊 **Statistiques avancées** - Analytics détaillées",
            "🎁 **Récompenses exclusives** - Items et badges Premium",
            "🔧 **Outils avancés** - Commandes spécialisées",
            "👥 **Support prioritaire** - Aide rapide",
            "🏆 **Badge Premium** - Statut visible partout",
            "🚀 **Accès anticipé** - Nouvelles fonctions en premier",
            "💎 **Salon Premium** - Accès aux channels VIP"
        ]
        
        embed.add_field(
            name="🌟 Avantages Premium",
            value="\n".join(benefits),
            inline=False
        )
        
        # Status actuel
        if current_role == "premium" or current_role in ["moderator", "admin", "fondateur", "dev", "creator"]:
            embed.add_field(
                name="✅ Votre Statut",
                value=f"**{current_role.upper()}** - Vous avez accès aux avantages Premium !",
                inline=False
            )
            embed.color = 0x00ff00
        else:
            embed.add_field(
                name="⏳ Votre Statut",
                value=f"**{current_role.upper()}** - Utilisez `/request-premium` pour devenir Premium !",
                inline=False
            )
        
        # Comment devenir Premium
        embed.add_field(
            name="🎯 Comment devenir Premium ?",
            value="**Méthode 1:** Critères automatiques (`/request-premium`)\n"
                  "• Niveau 15+\n"
                  "• 50+ commandes utilisées\n"
                  "• 500+ coins\n"
                  "• 7 jours d'ancienneté\n\n"
                  "**Méthode 2:** Promotion manuelle par le Créateur",
            inline=False
        )
        
        embed.set_footer(text="Arsenal Studio • Premium System")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="premium-stats", description="📊 Statistiques système Premium")
    @require_creator()  # Créateur uniquement
    async def premium_stats(self, interaction: discord.Interaction):
        """Statistiques du système Premium"""
        
        async with aiosqlite.connect("arsenal_users_central.db") as db:
            # Stats générales
            cursor = await db.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN arsenal_role = 'premium' THEN 1 ELSE 0 END) as premium_count,
                    SUM(CASE WHEN arsenal_role IN ('moderator', 'admin', 'fondateur', 'dev', 'creator') THEN 1 ELSE 0 END) as staff_count
                FROM arsenal_users
            """)
            stats = await cursor.fetchone()
            
            # Promotions récentes
            cursor = await db.execute("""
                SELECT COUNT(*) FROM user_activity 
                WHERE activity_type = 'auto_promotion' 
                AND datetime(timestamp) > datetime('now', '-7 days')
            """)
            recent_promotions = (await cursor.fetchone())[0]
        
        total, premium_count, staff_count = stats
        premium_percentage = (premium_count / total * 100) if total > 0 else 0
        
        embed = discord.Embed(
            title="📊 Arsenal Premium Statistics",
            description="**Statistiques du système Premium**",
            color=0xffd700
        )
        
        embed.add_field(
            name="👥 Répartition Utilisateurs",
            value=f"**Total:** `{total}`\n"
                  f"**Premium:** `{premium_count}` ({premium_percentage:.1f}%)\n"
                  f"**Staff+:** `{staff_count}`",
            inline=True
        )
        
        embed.add_field(
            name="📈 Activité",
            value=f"**Auto-promotions (7j):** `{recent_promotions}`",
            inline=True
        )
        
        embed.set_footer(text="Arsenal Studio • Premium Analytics")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    """Setup du système Premium"""
    await bot.add_cog(ArsenalPremiumSystem(bot))
