#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Arsenal V4 - Groupes de Commandes Organisés
Organisation des commandes par permissions et catégories
Développé par XeRoX - Arsenal Bot V4.5.2
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import json
import aiosqlite
import os
import logging

class ArsenalCommandGroups(commands.Cog):
    """Groupes de commandes organisés par permissions"""
    
    def __init__(self, bot):
        self.bot = bot

    # ═══════════════════════════════════════════════════════════════════
    # 👑 GROUPE CRÉATEUR - Commandes exclusives au créateur du bot
    # ═══════════════════════════════════════════════════════════════════
    
    creator_group = app_commands.Group(
        name="creator", 
        description="🔒 Commandes réservées au créateur du bot"
    )

    @creator_group.command(name="diagnostic", description="🔧 Diagnostic complet du bot")
    async def creator_diagnostic(self, interaction: discord.Interaction):
        """Diagnostic système complet - Réservé créateur"""
        
        # Vérification permission créateur
        if interaction.user.id != 431359112039890945:
            await interaction.response.send_message("❌ Cette commande est réservée au créateur du bot.", ephemeral=True)
            return
            
        await interaction.response.send_message("🔍 Diagnostic système en cours...", ephemeral=True)
        
        # Diagnostic complet
        embed = discord.Embed(
            title="🔧 **DIAGNOSTIC SYSTÈME ARSENAL**",
            color=0xff0000
        )
        
        # Infos bot
        embed.add_field(
            name="🤖 Bot",
            value=f"**Nom:** {self.bot.user.name}\n**ID:** {self.bot.user.id}\n**Latence:** {round(self.bot.latency * 1000, 2)}ms",
            inline=True
        )
        
        # Serveurs
        embed.add_field(
            name="🌐 Serveurs", 
            value=f"**Total:** {len(self.bot.guilds)}\n**Utilisateurs:** {len(self.bot.users)}\n**Commandes:** {len(self.bot.tree.get_commands())}",
            inline=True
        )
        
        # Modules chargés
        cogs_loaded = len(self.bot.cogs)
        embed.add_field(
            name="📦 Modules",
            value=f"**Chargés:** {cogs_loaded}\n**Status:** {'✅ Tous OK' if cogs_loaded > 20 else '⚠️ Manquants'}",
            inline=True
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @creator_group.command(name="force_sync", description="🔄 Force la synchronisation des commandes")
    async def creator_force_sync(self, interaction: discord.Interaction):
        """Force sync commandes - Réservé créateur"""
        
        if interaction.user.id != 431359112039890945:
            await interaction.response.send_message("❌ Cette commande est réservée au créateur du bot.", ephemeral=True)
            return
            
        await interaction.response.send_message("🔄 Synchronisation forcée des commandes...", ephemeral=True)
        
        try:
            synced = await self.bot.tree.sync()
            await interaction.followup.send(f"✅ {len(synced)} commandes synchronisées avec Discord.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur sync: {e}", ephemeral=True)

    @creator_group.command(name="bot_status", description="📊 Status complet du bot")
    async def creator_bot_status(self, interaction: discord.Interaction):
        """Status bot complet - Réservé créateur"""
        
        if interaction.user.id != 431359112039890945:
            await interaction.response.send_message("❌ Cette commande est réservée au créateur du bot.", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="📊 **STATUS BOT ARSENAL**",
            color=0x00ff00
        )
        
        # Status serveurs
        guild_info = []
        for guild in self.bot.guilds[:5]:  # Limiter à 5 pour éviter overflow
            guild_info.append(f"**{guild.name}** - {guild.member_count} membres")
        
        embed.add_field(
            name="🏰 Serveurs Actifs",
            value="\n".join(guild_info) + (f"\n... et {len(self.bot.guilds) - 5} autres" if len(self.bot.guilds) > 5 else ""),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ═══════════════════════════════════════════════════════════════════
    # 👑 GROUPE PROPRIÉTAIRE - Commandes pour propriétaires de serveur
    # ═══════════════════════════════════════════════════════════════════
    
    owner_group = app_commands.Group(
        name="owner", 
        description="👑 Commandes pour propriétaires de serveur"
    )

    @owner_group.command(name="config", description="⚙️ Configuration complète du serveur")
    async def owner_config(self, interaction: discord.Interaction):
        """Configuration serveur - Propriétaire uniquement"""
        
        # Vérification permission propriétaire
        if interaction.user.id != interaction.guild.owner_id and interaction.user.id != 431359112039890945:
            await interaction.response.send_message("❌ Cette commande est réservée au propriétaire du serveur.", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="⚙️ **CONFIGURATION SERVEUR**",
            description="Interface de configuration complète",
            color=0xffd700
        )
        
        embed.add_field(
            name="🎵 Hub Vocal",
            value="Configuration des salons temporaires",
            inline=True
        )
        
        embed.add_field(
            name="🛡️ Modération",
            value="Système de sanctions et règles",
            inline=True
        )
        
        embed.add_field(
            name="🎮 Gaming",
            value="Configuration gaming et statistiques",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @owner_group.command(name="reset_server", description="🔄 Reset complet des configurations")
    async def owner_reset(self, interaction: discord.Interaction):
        """Reset serveur - Propriétaire uniquement"""
        
        if interaction.user.id != interaction.guild.owner_id and interaction.user.id != 431359112039890945:
            await interaction.response.send_message("❌ Cette commande est réservée au propriétaire du serveur.", ephemeral=True)
            return
            
        await interaction.response.send_message("⚠️ Cette action reset toutes les configurations. Êtes-vous sûr?", ephemeral=True)

    # ═══════════════════════════════════════════════════════════════════
    # 🛡️ GROUPE ADMINISTRATION - Commandes administrateurs
    # ═══════════════════════════════════════════════════════════════════
    
    admin_group = app_commands.Group(
        name="admin", 
        description="🛡️ Commandes d'administration"
    )

    @admin_group.command(name="setup", description="🔧 Configuration des modules")
    async def admin_setup(self, interaction: discord.Interaction, module: str):
        """Setup modules - Administrateurs"""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Vous devez être administrateur.", ephemeral=True)
            return
            
        await interaction.response.send_message(f"🔧 Configuration du module **{module}**", ephemeral=True)

    @admin_group.command(name="permissions", description="🔐 Gestion des permissions")
    async def admin_permissions(self, interaction: discord.Interaction):
        """Gestion permissions - Administrateurs"""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Vous devez être administrateur.", ephemeral=True)
            return
            
        await interaction.response.send_message("🔐 Interface de gestion des permissions", ephemeral=True)

    # ═══════════════════════════════════════════════════════════════════
    # 🚨 GROUPE MODÉRATION - Commandes de modération
    # ═══════════════════════════════════════════════════════════════════
    
    mod_group = app_commands.Group(
        name="mod", 
        description="🚨 Commandes de modération"
    )

    @mod_group.command(name="warn", description="⚠️ Avertir un membre")
    @app_commands.describe(member="Membre à avertir", reason="Raison de l'avertissement")
    async def mod_warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison"):
        """Avertir un membre"""
        
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ Vous n'avez pas les permissions de modération.", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="⚠️ **AVERTISSEMENT**",
            description=f"{member.mention} a été averti",
            color=0xffaa00
        )
        embed.add_field(name="Raison", value=reason, inline=False)
        embed.add_field(name="Modérateur", value=interaction.user.mention, inline=True)
        
        await interaction.response.send_message(embed=embed)

    @mod_group.command(name="timeout", description="⏰ Timeout un membre")
    @app_commands.describe(member="Membre à timeout", duration="Durée en minutes", reason="Raison")
    async def mod_timeout(self, interaction: discord.Interaction, member: discord.Member, duration: int = 10, reason: str = "Timeout"):
        """Timeout un membre"""
        
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ Vous n'avez pas les permissions de modération.", ephemeral=True)
            return
            
        import datetime
        timeout_until = discord.utils.utcnow() + datetime.timedelta(minutes=duration)
        
        try:
            await member.timeout(timeout_until, reason=reason)
            await interaction.response.send_message(f"⏰ {member.mention} a été timeout pendant {duration} minutes. Raison: {reason}")
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)

    # ═══════════════════════════════════════════════════════════════════
    # 🎵 GROUPE MUSIQUE - Commandes musicales
    # ═══════════════════════════════════════════════════════════════════
    
    music_group = app_commands.Group(
        name="music", 
        description="🎵 Commandes musicales"
    )

    @music_group.command(name="play", description="▶️ Jouer de la musique")
    @app_commands.describe(query="Chanson ou URL à jouer")
    async def music_play(self, interaction: discord.Interaction, query: str):
        """Jouer de la musique"""
        
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Vous devez être dans un salon vocal.", ephemeral=True)
            return
            
        await interaction.response.send_message(f"🎵 Recherche: **{query}**", ephemeral=True)

    @music_group.command(name="queue", description="📋 File d'attente musicale")
    async def music_queue(self, interaction: discord.Interaction):
        """Afficher la file d'attente"""
        
        embed = discord.Embed(
            title="📋 **FILE D'ATTENTE**",
            description="Aucune musique en cours",
            color=0x9932cc
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @music_group.command(name="stop", description="⏹️ Arrêter la musique")
    async def music_stop(self, interaction: discord.Interaction):
        """Arrêter la musique"""
        
        await interaction.response.send_message("⏹️ Musique arrêtée", ephemeral=True)

    # ═══════════════════════════════════════════════════════════════════
    # 🎮 GROUPE GAMING - Commandes gaming
    # ═══════════════════════════════════════════════════════════════════
    
    gaming_group = app_commands.Group(
        name="gaming", 
        description="🎮 Commandes gaming"
    )

    @gaming_group.command(name="stats", description="📊 Statistiques de jeu")
    @app_commands.describe(game="Jeu à rechercher", player="Joueur à rechercher")
    async def gaming_stats(self, interaction: discord.Interaction, game: str, player: str):
        """Stats de jeu"""
        
        await interaction.response.send_message(f"📊 Recherche des stats **{game}** pour **{player}**", ephemeral=True)

    @gaming_group.command(name="leaderboard", description="🏆 Classement du serveur")
    async def gaming_leaderboard(self, interaction: discord.Interaction):
        """Classement gaming"""
        
        embed = discord.Embed(
            title="🏆 **CLASSEMENT GAMING**",
            color=0xff6b35
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ArsenalCommandGroups(bot))
