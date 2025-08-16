"""
🏆 ARSENAL LEVEL SYSTEM - SYSTÈME DE NIVEAUX RÉVOLUTIONNAIRE
Interface moderne avec XP, rangs, badges, récompenses et analytics détaillées
Par xerox3elite - Arsenal V4.5.2 ULTIMATE
"""

import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
import json
import os
import math
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

class LevelStatsView(discord.ui.View):
    """Vue avec statistiques de niveau détaillées"""
    def __init__(self, bot, user_id, target_member):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.target_member = target_member
    
    @discord.ui.button(label="📊 Analytics Détaillées", style=discord.ButtonStyle.primary, emoji="📊")
    async def detailed_analytics(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut utiliser ce bouton!", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        embed = await self.create_detailed_analytics_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label="🏆 Leaderboard", style=discord.ButtonStyle.secondary, emoji="🏆")
    async def leaderboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut utiliser ce bouton!", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        embed = await self.create_leaderboard_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label="🎁 Récompenses", style=discord.ButtonStyle.success, emoji="🎁")
    async def rewards(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut utiliser ce bouton!", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        embed = await self.create_rewards_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label="🏅 Badges", style=discord.ButtonStyle.secondary, emoji="🏅")
    async def badges(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seul l'utilisateur qui a lancé la commande peut utiliser ce bouton!", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        embed = await self.create_badges_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    async def create_detailed_analytics_embed(self) -> discord.Embed:
        """Crée l'embed d'analytics détaillées"""
        
        # Récupérer données depuis la base
        level_data = await self.get_user_level_data(self.target_member.id)
        
        embed = discord.Embed(
            title=f"📊 Analytics Détaillées - {self.target_member.display_name}",
            description="**Analyse complète des performances et activité**",
            color=0x00FFFF,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.set_thumbnail(url=self.target_member.display_avatar.url)
        
        # Stats XP détaillées
        embed.add_field(
            name="📈 Progression XP",
            value=(
                f"**XP Total**: {level_data['total_xp']:,}\\n"
                f"**XP ce niveau**: {level_data['current_xp']:,}/{level_data['needed_xp']:,}\\n"
                f"**Progression**: {level_data['progress_percent']:.1f}%\\n"
                f"**XP manquant**: {level_data['needed_xp'] - level_data['current_xp']:,}"
            ),
            inline=True
        )
        
        # Activité récente
        embed.add_field(
            name="⚡ Activité Récente",
            value=(
                f"**Messages 24h**: {level_data['messages_24h']}\\n"
                f"**XP gagné 24h**: +{level_data['xp_24h']}\\n"
                f"**Streak actuel**: {level_data['streak']} jours\\n"
                f"**Dernière activité**: <t:{level_data['last_activity']}:R>"
            ),
            inline=True
        )
        
        # Statistiques globales
        embed.add_field(
            name="🎯 Statistiques Globales",
            value=(
                f"**Messages total**: {level_data['total_messages']:,}\\n"
                f"**Temps vocal**: {level_data['voice_time_formatted']}\\n"
                f"**Commandes utilisées**: {level_data['commands_used']:,}\\n"
                f"**Membre depuis**: <t:{level_data['joined_timestamp']}:R>"
            ),
            inline=True
        )
        
        # Graphique progression (ASCII)
        progress_bar = self.create_progress_bar(level_data['progress_percent'])
        embed.add_field(
            name="📊 Barre de Progression",
            value=f"```{progress_bar}```",
            inline=False
        )
        
        # Comparaison serveur
        embed.add_field(
            name="🏆 Position Serveur",
            value=(
                f"**Rang XP**: #{level_data['server_rank']} / {level_data['total_members']}\\n"
                f"**Top**: {level_data['top_percent']:.1f}%\\n"
                f"**Messages rang**: #{level_data['messages_rank']}\\n"
                f"**Vocal rang**: #{level_data['voice_rank']}"
            ),
            inline=True
        )
        
        return embed
    
    async def create_leaderboard_embed(self) -> discord.Embed:
        """Crée l'embed du leaderboard"""
        
        top_users = await self.get_top_users()
        
        embed = discord.Embed(
            title="🏆 Leaderboard Arsenal Levels",
            description="**Top 15 membres par XP et niveau**",
            color=0xFFD700,
            timestamp=datetime.now(timezone.utc)
        )
        
        leaderboard_text = ""
        medals = ["🥇", "🥈", "🥉"]
        
        for i, user_data in enumerate(top_users[:15]):
            try:
                member = self.bot.get_user(user_data['user_id'])
                name = member.display_name if member else f"Utilisateur {user_data['user_id']}"
                
                medal = medals[i] if i < 3 else f"**{i+1}.**"
                
                leaderboard_text += (
                    f"{medal} **{name}** - Niveau {user_data['level']} "
                    f"({user_data['total_xp']:,} XP)\\n"
                )
            except:
                continue
        
        embed.add_field(
            name="🏅 Classement XP",
            value=leaderboard_text or "Aucune donnée disponible",
            inline=False
        )
        
        # Position de l'utilisateur cible
        user_position = await self.get_user_rank(self.target_member.id)
        if user_position:
            embed.add_field(
                name=f"📍 Position de {self.target_member.display_name}",
                value=f"**#{user_position}** sur {len(top_users)} membres classés",
                inline=False
            )
        
        return embed
    
    async def create_rewards_embed(self) -> discord.Embed:
        """Crée l'embed des récompenses"""
        
        embed = discord.Embed(
            title="🎁 Système de Récompenses Arsenal",
            description="**Récompenses automatiques par niveau atteint**",
            color=0x00FF00,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Récompenses par paliers
        rewards_data = {
            5: {"coins": 100, "role": "Débutant", "badge": "🌱"},
            10: {"coins": 250, "role": "Actif", "badge": "⚡"},
            15: {"coins": 500, "role": "Régulier", "badge": "🔥"},
            25: {"coins": 1000, "role": "Vétéran", "badge": "🏆"},
            35: {"coins": 2000, "role": "Expert", "badge": "💎"},
            50: {"coins": 5000, "role": "Maître", "badge": "👑"},
            75: {"coins": 10000, "role": "Légende", "badge": "🌟"},
            100: {"coins": 25000, "role": "Arsenal God", "badge": "🚀"}
        }
        
        current_level = await self.get_user_level(self.target_member.id)
        
        rewards_text = ""
        for level, reward in rewards_data.items():
            status = "✅" if current_level >= level else "❌"
            rewards_text += (
                f"{status} **Niveau {level}**: {reward['coins']} ArsenalCoins + "
                f"Rôle {reward['role']} + Badge {reward['badge']}\\n"
            )
        
        embed.add_field(
            name="🏅 Récompenses par Niveau",
            value=rewards_text,
            inline=False
        )
        
        # Prochaine récompense
        next_reward_level = None
        for level in sorted(rewards_data.keys()):
            if current_level < level:
                next_reward_level = level
                break
        
        if next_reward_level:
            next_reward = rewards_data[next_reward_level]
            embed.add_field(
                name="🎯 Prochaine Récompense",
                value=(
                    f"**Niveau {next_reward_level}** ({next_reward_level - current_level} niveaux restants)\\n"
                    f"🪙 {next_reward['coins']} ArsenalCoins\\n"
                    f"🎭 Rôle {next_reward['role']}\\n"
                    f"🏅 Badge {next_reward['badge']}"
                ),
                inline=False
            )
        
        return embed
    
    async def create_badges_embed(self) -> discord.Embed:
        """Crée l'embed des badges"""
        
        user_badges = await self.get_user_badges(self.target_member.id)
        
        embed = discord.Embed(
            title=f"🏅 Badges de {self.target_member.display_name}",
            description="**Collection de badges et achievements**",
            color=0xFF69B4,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.set_thumbnail(url=self.target_member.display_avatar.url)
        
        # Badges obtenus
        earned_badges = [badge for badge in user_badges if badge['earned']]
        if earned_badges:
            badges_text = ""
            for badge in earned_badges:
                badges_text += f"{badge['emoji']} **{badge['name']}** - {badge['description']}\\n"
            
            embed.add_field(
                name=f"✅ Badges Obtenus ({len(earned_badges)})",
                value=badges_text,
                inline=False
            )
        
        # Badges à débloquer
        locked_badges = [badge for badge in user_badges if not badge['earned']][:10]
        if locked_badges:
            locked_text = ""
            for badge in locked_badges:
                locked_text += f"🔒 **{badge['name']}** - {badge['requirement']}\\n"
            
            embed.add_field(
                name="🔒 Badges à Débloquer",
                value=locked_text,
                inline=False
            )
        
        return embed
    
    def create_progress_bar(self, percent: float) -> str:
        """Crée une barre de progression ASCII"""
        filled = int(percent / 5)  # 20 caractères max
        empty = 20 - filled
        
        bar = "█" * filled + "░" * empty
        return f"[{bar}] {percent:.1f}%"
    
    async def get_user_level_data(self, user_id: int) -> Dict[str, Any]:
        """Récupère les données de niveau d'un utilisateur"""
        # Simulation des données (à remplacer par vraie base de données)
        return {
            "total_xp": 15750,
            "current_xp": 750, 
            "needed_xp": 1000,
            "progress_percent": 75.0,
            "messages_24h": 45,
            "xp_24h": 180,
            "streak": 7,
            "last_activity": int(datetime.now().timestamp()) - 3600,
            "total_messages": 2847,
            "voice_time_formatted": "12h 34m",
            "commands_used": 156,
            "joined_timestamp": int(datetime.now().timestamp()) - (30 * 24 * 3600),
            "server_rank": 8,
            "total_members": 150,
            "top_percent": 5.3,
            "messages_rank": 12,
            "voice_rank": 6
        }
    
    async def get_top_users(self) -> List[Dict[str, Any]]:
        """Récupère le top des utilisateurs"""
        # Simulation (à remplacer par vraie base)
        return [
            {"user_id": 123456789, "level": 42, "total_xp": 89750},
            {"user_id": 987654321, "level": 38, "total_xp": 76280},
            {"user_id": 456789123, "level": 35, "total_xp": 65890}
        ]
    
    async def get_user_rank(self, user_id: int) -> int:
        """Récupère le rang d'un utilisateur"""
        return 8  # Simulation
    
    async def get_user_level(self, user_id: int) -> int:
        """Récupère le niveau d'un utilisateur"""
        return 18  # Simulation
    
    async def get_user_badges(self, user_id: int) -> List[Dict[str, Any]]:
        """Récupère les badges d'un utilisateur"""
        return [
            {"name": "First Steps", "emoji": "🌱", "description": "Premiers pas sur le serveur", "earned": True, "requirement": ""},
            {"name": "Chatty", "emoji": "💬", "description": "100 messages envoyés", "earned": True, "requirement": ""},
            {"name": "Voice Master", "emoji": "🎤", "description": "5h en vocal", "earned": False, "requirement": "Rester 5h en vocal"},
            {"name": "Command Expert", "emoji": "⚡", "description": "50 commandes utilisées", "earned": True, "requirement": ""},
            {"name": "Level Crusher", "emoji": "🔥", "description": "Niveau 25 atteint", "earned": False, "requirement": "Atteindre niveau 25"}
        ]

class ArsenalLevelSystem(commands.Cog):
    """🏆 Arsenal Level System - Système de niveaux révolutionnaire"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/levels.db"
        self.ensure_database()
    
    def ensure_database(self):
        """Initialise la base de données des niveaux"""
        os.makedirs("data", exist_ok=True)
        # Ici on créerait la vraie base de données SQLite
    
    def calculate_level(self, xp: int) -> int:
        """Calcule le niveau basé sur l'XP"""
        # Formule: niveau = sqrt(XP / 100)
        return int(math.sqrt(xp / 100))
    
    def calculate_xp_for_level(self, level: int) -> int:
        """Calcule l'XP nécessaire pour un niveau"""
        return level * level * 100
    
    @app_commands.command(name="level", description="🏆 Afficher niveau et XP avec analytics détaillées")
    @app_commands.describe(member="Membre à analyser (optionnel)")
    async def level_command(self, interaction: discord.Interaction, member: discord.Member = None):
        """Commande principale du système de niveaux"""
        
        target = member or interaction.user
        
        # Simuler données (remplacer par vraie base)
        total_xp = 15750
        level = self.calculate_level(total_xp)
        current_level_xp = self.calculate_xp_for_level(level)
        next_level_xp = self.calculate_xp_for_level(level + 1)
        current_xp = total_xp - current_level_xp
        needed_xp = next_level_xp - current_level_xp
        progress = (current_xp / needed_xp) * 100
        
        embed = discord.Embed(
            title=f"🏆 Profil Niveau - {target.display_name}",
            description=f"**Analyse complète du système de niveaux Arsenal**",
            color=0xFFD700,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # Informations principales
        embed.add_field(
            name="📊 Statistiques Principales",
            value=(
                f"**🏆 Niveau**: {level}\\n"
                f"**⚡ XP Total**: {total_xp:,}\\n"
                f"**📈 Progression**: {current_xp:,}/{needed_xp:,} XP\\n"
                f"**📊 Pourcentage**: {progress:.1f}%"
            ),
            inline=True
        )
        
        # Performance
        embed.add_field(
            name="⚡ Performance 24h",
            value=(
                f"**💬 Messages**: 45\\n"
                f"**🎤 Temps vocal**: 2h 15m\\n"
                f"**⚡ Commandes**: 12\\n"
                f"**🪙 XP gagné**: +180"
            ),
            inline=True
        )
        
        # Récompenses
        next_reward_level = ((level // 5) + 1) * 5  # Prochaine récompense à un multiple de 5
        embed.add_field(
            name="🎁 Prochaine Récompense",
            value=(
                f"**🏅 Niveau {next_reward_level}**\\n"
                f"🪙 {next_reward_level * 100} ArsenalCoins\\n"
                f"🎭 Nouveau rôle\\n"
                f"🏅 Badge exclusif"
            ),
            inline=True
        )
        
        # Barre de progression visuelle
        progress_bar = self.create_visual_progress_bar(progress)
        embed.add_field(
            name="📈 Progression Visuelle",
            value=f"```{progress_bar}```\\n**{current_xp:,}** / **{needed_xp:,}** XP",
            inline=False
        )
        
        # Classement
        embed.add_field(
            name="🏆 Classement Serveur",
            value=(
                f"**📍 Rang XP**: #8 / 150\\n"
                f"**🏅 Top**: 5.3%\\n"
                f"**📊 Score**: A+"
            ),
            inline=True
        )
        
        # Badges
        embed.add_field(
            name="🏅 Badges Récents",
            value=(
                f"🌱 **First Steps** - Obtenu\\n"
                f"💬 **Chatty** - Obtenu\\n"
                f"⚡ **Command Expert** - Obtenu\\n"
                f"🔒 **Voice Master** - En cours"
            ),
            inline=True
        )
        
        embed.set_footer(
            text=f"Arsenal Level System • Membre depuis {(datetime.now() - target.joined_at).days} jours",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        # Vue avec boutons d'analytics
        view = LevelStatsView(self.bot, interaction.user.id, target)
        await interaction.response.send_message(embed=embed, view=view)
    
    def create_visual_progress_bar(self, percent: float) -> str:
        """Crée une barre de progression visuelle"""
        filled = int(percent / 5)  # 20 segments
        empty = 20 - filled
        
        bar = "█" * filled + "░" * empty
        return f"[{bar}] {percent:.1f}%"
    
    @app_commands.command(name="level_leaderboard", description="🏆 Classement des niveaux du serveur")
    async def level_leaderboard(self, interaction: discord.Interaction):
        """Affiche le leaderboard des niveaux"""
        
        embed = discord.Embed(
            title="🏆 Leaderboard Arsenal Levels",
            description=f"**Top membres de {interaction.guild.name}**",
            color=0xFFD700,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Données simulées du top
        leaderboard_data = [
            {"name": "User1", "level": 42, "xp": 89750},
            {"name": "User2", "level": 38, "xp": 76280}, 
            {"name": "User3", "level": 35, "xp": 65890},
            {"name": "User4", "level": 32, "xp": 58430},
            {"name": "User5", "level": 29, "xp": 51200}
        ]
        
        leaderboard_text = ""
        medals = ["🥇", "🥈", "🥉"]
        
        for i, user in enumerate(leaderboard_data):
            medal = medals[i] if i < 3 else f"**{i+1}.**"
            leaderboard_text += f"{medal} **{user['name']}** - Niveau {user['level']} ({user['xp']:,} XP)\\n"
        
        embed.add_field(
            name="🏅 Top 5 Serveur",
            value=leaderboard_text,
            inline=False
        )
        
        embed.add_field(
            name="📊 Statistiques Globales",
            value=(
                f"**👥 Membres actifs**: {len(interaction.guild.members)}\\n"
                f"**📈 XP total serveur**: 2,847,392\\n"
                f"**🏆 Niveau moyen**: 12.4\\n"
                f"**🔥 Most active today**: User1"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="level_rewards", description="🎁 Voir toutes les récompenses de niveau")
    async def level_rewards(self, interaction: discord.Interaction):
        """Affiche toutes les récompenses disponibles"""
        
        embed = discord.Embed(
            title="🎁 Système de Récompenses Arsenal",
            description="**Récompenses automatiques par niveau**",
            color=0x00FF00,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Récompenses détaillées
        rewards_text = (
            "🌱 **Niveau 5**: 100 ArsenalCoins + Rôle Débutant\\n"
            "⚡ **Niveau 10**: 250 ArsenalCoins + Rôle Actif\\n"
            "🔥 **Niveau 15**: 500 ArsenalCoins + Rôle Régulier\\n"
            "🏆 **Niveau 25**: 1,000 ArsenalCoins + Rôle Vétéran\\n"
            "💎 **Niveau 35**: 2,000 ArsenalCoins + Rôle Expert\\n"
            "👑 **Niveau 50**: 5,000 ArsenalCoins + Rôle Maître\\n"
            "🌟 **Niveau 75**: 10,000 ArsenalCoins + Rôle Légende\\n"
            "🚀 **Niveau 100**: 25,000 ArsenalCoins + Rôle Arsenal God"
        )
        
        embed.add_field(
            name="🏅 Récompenses par Paliers",
            value=rewards_text,
            inline=False
        )
        
        embed.add_field(
            name="💡 Comment gagner de l'XP",
            value=(
                "💬 **Messages**: +5-15 XP par message\\n"
                "🎤 **Vocal**: +10 XP par minute\\n"
                "⚡ **Commandes**: +20-50 XP par commande\\n"
                "🎯 **Bonus daily**: +100 XP quotidien\\n"
                "🔥 **Streak**: Multiplicateur jusqu'à x2"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Charge le module ArsenalLevelSystem"""
    await bot.add_cog(ArsenalLevelSystem(bot))
    print("🏆 [Arsenal Level System] Module chargé - Système de niveaux révolutionnaire!")
