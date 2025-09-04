#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐛 Arsenal Bug Reporter V1.0 - Système de Signalement Automatique
Permet aux utilisateurs de signaler des bugs facilement
Développé par XeRoX - Arsenal Bot V4.6
"""

import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import datetime
import asyncio
import json
from typing import Optional
import traceback

# 🔒 Arsenal Protection Middleware
from commands.arsenal_protection_middleware import require_registration

class ArsenalBugReporter(commands.Cog):
    """Système de signalement de bugs Arsenal"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/bug_reports.db"
        self.dev_user_id = 123456789  # Remplace par ton ID Discord
        
    async def cog_load(self):
        """Initialize database when cog loads"""
        await self.init_database()
        print("[Bug Reporter] Système de signalement initialisé")

    async def init_database(self):
        """Initialize bug reports database"""
        import os
        os.makedirs('data', exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS bug_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    username TEXT,
                    bug_title TEXT,
                    bug_description TEXT,
                    command_used TEXT,
                    error_message TEXT,
                    status TEXT DEFAULT 'open',
                    priority TEXT DEFAULT 'medium',
                    timestamp TEXT,
                    resolved_at TEXT,
                    developer_notes TEXT
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS bug_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_reports INTEGER DEFAULT 0,
                    resolved_reports INTEGER DEFAULT 0,
                    open_reports INTEGER DEFAULT 0,
                    last_updated TEXT
                )
            ''')
            
            await db.commit()

    @app_commands.command(name="bug", description="🐛 Signaler un bug dans Arsenal Bot")
    @require_registration("basic")  # Accessible à tous les membres enregistrés
    @app_commands.describe(
        title="Titre du bug (court et précis)",
        description="Description détaillée du problème",
        command="Commande qui a causé le bug (optionnel)",
        priority="Priorité du bug"
    )
    @app_commands.choices(priority=[
        app_commands.Choice(name="🔥 Critique (Bot crash)", value="critical"),
        app_commands.Choice(name="🔴 Élevé (Fonction cassée)", value="high"), 
        app_commands.Choice(name="🟡 Moyen (Bug gênant)", value="medium"),
        app_commands.Choice(name="🟢 Faible (Amélioration)", value="low")
    ])
    async def bug_report(self, interaction: discord.Interaction, title: str, 
                        description: str, command: str = None, 
                        priority: str = "medium"):
        """Signaler un bug"""
        
        # Créer le rapport de bug
        bug_id = await self.create_bug_report(
            guild_id=interaction.guild.id if interaction.guild else 0,
            user_id=interaction.user.id,
            username=str(interaction.user),
            title=title,
            description=description,
            command_used=command,
            priority=priority
        )
        
        # Embed pour l'utilisateur
        embed = discord.Embed(
            title="🐛 **BUG SIGNALÉ**",
            description=f"**Bug #{bug_id}** enregistré avec succès !",
            color=self.get_priority_color(priority)
        )
        
        embed.add_field(
            name="📝 **DÉTAILS**",
            value=f"**Titre:** {title}\n"
                  f"**Priorité:** {self.get_priority_emoji(priority)} {priority.upper()}\n"
                  f"**Commande:** `{command}` {command if command else 'Non spécifiée'}",
            inline=False
        )
        
        embed.add_field(
            name="⏱️ **SUIVI**",
            value="• Vous recevrez une notification quand le bug sera corrigé\n"
                  "• Utilisez `/bugstatus` pour voir vos rapports\n"
                  "• Merci de contribuer à l'amélioration d'Arsenal !",
            inline=False
        )
        
        embed.set_footer(
            text=f"Bug ID: {bug_id} • {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Notifier le développeur si critique
        if priority == "critical":
            await self.notify_developer(bug_id, title, description, interaction.user)

    @app_commands.command(name="bugstatus", description="📊 Voir le statut de tes rapports de bugs")
    @require_registration("basic")  # Accessible à tous les membres enregistrés
    async def bug_status(self, interaction: discord.Interaction):
        """Voir ses rapports de bugs"""
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT id, bug_title, status, priority, timestamp 
                FROM bug_reports 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''', (interaction.user.id,))
            
            reports = await cursor.fetchall()
        
        if not reports:
            embed = discord.Embed(
                title="📊 **MES RAPPORTS DE BUGS**",
                description="Aucun rapport de bug trouvé.\n\n"
                           "Utilisez `/bug` pour signaler un problème !",
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(
                title="📊 **MES RAPPORTS DE BUGS**",
                description=f"**{len(reports)} rapport(s)** trouvé(s)",
                color=discord.Color.blue()
            )
            
            for bug_id, title, status, priority, timestamp in reports:
                status_emoji = "✅" if status == "resolved" else "🔍" if status == "investigating" else "🔴"
                priority_emoji = self.get_priority_emoji(priority)
                
                embed.add_field(
                    name=f"{status_emoji} **Bug #{bug_id}**",
                    value=f"**{title}**\n"
                          f"{priority_emoji} {priority.upper()} • {status.upper()}\n"
                          f"📅 {timestamp[:10]}",
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="bugstats", description="📈 Statistiques globales des bugs")
    @require_registration("beta")  # Réservé aux beta testeurs et plus
    async def bug_stats(self, interaction: discord.Interaction):
        """Statistiques des bugs"""
        
        async with aiosqlite.connect(self.db_path) as db:
            # Stats globales
            cursor = await db.execute('''
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved,
                    COUNT(CASE WHEN status = 'open' THEN 1 END) as open,
                    COUNT(CASE WHEN priority = 'critical' THEN 1 END) as critical
                FROM bug_reports
            ''')
            
            stats = await cursor.fetchone()
            total, resolved, open_bugs, critical = stats
            
        embed = discord.Embed(
            title="📈 **STATISTIQUES BUGS ARSENAL**",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📊 **GLOBAL**",
            value=f"📝 **Total:** {total} rapports\n"
                  f"✅ **Résolus:** {resolved}\n"
                  f"🔴 **Ouverts:** {open_bugs}\n"
                  f"🔥 **Critiques:** {critical}",
            inline=True
        )
        
        # Pourcentage de résolution
        resolution_rate = (resolved / total * 100) if total > 0 else 0
        embed.add_field(
            name="⚡ **PERFORMANCES**",
            value=f"📈 **Taux résolution:** {resolution_rate:.1f}%\n"
                  f"🎯 **Objectif:** 95%\n"
                  f"⭐ **Qualité:** {'Excellent' if resolution_rate >= 95 else 'Bon' if resolution_rate >= 80 else 'À améliorer'}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

    # Commandes admin pour les développeurs
    @app_commands.command(name="bugadmin", description="🔧 Gestion des bugs (Admin)")
    @require_registration("dev")  # Réservé aux développeurs
    @app_commands.describe(
        action="Action à effectuer",
        bug_id="ID du bug",
        status="Nouveau statut",
        notes="Notes du développeur"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="📋 Lister tous", value="list"),
            app_commands.Choice(name="🔍 Voir détails", value="view"),
            app_commands.Choice(name="✅ Marquer résolu", value="resolve"),
            app_commands.Choice(name="🔄 Changer statut", value="status")
        ],
        status=[
            app_commands.Choice(name="🔴 Ouvert", value="open"),
            app_commands.Choice(name="🔍 Investigation", value="investigating"),
            app_commands.Choice(name="✅ Résolu", value="resolved"),
            app_commands.Choice(name="❌ Fermé", value="closed")
        ]
    )
    async def bug_admin(self, interaction: discord.Interaction, action: str,
                       bug_id: int = None, status: str = None, notes: str = None):
        """Gestion des bugs par les admins"""
        
        # Vérifier permissions (tu peux ajuster cette logique)
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Permissions insuffisantes !", ephemeral=True)
            return
            
        if action == "list":
            await self.list_bugs_admin(interaction)
        elif action == "view" and bug_id:
            await self.view_bug_admin(interaction, bug_id)
        elif action == "resolve" and bug_id:
            await self.resolve_bug_admin(interaction, bug_id, notes)
        elif action == "status" and bug_id and status:
            await self.update_bug_status_admin(interaction, bug_id, status, notes)

    async def create_bug_report(self, guild_id: int, user_id: int, username: str,
                              title: str, description: str, command_used: str = None,
                              priority: str = "medium") -> int:
        """Créer un nouveau rapport de bug"""
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO bug_reports 
                (guild_id, user_id, username, bug_title, bug_description, command_used, priority, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (guild_id, user_id, username, title, description, command_used, priority,
                  datetime.datetime.now().isoformat()))
            
            await db.commit()
            return cursor.lastrowid

    async def notify_developer(self, bug_id: int, title: str, description: str, user):
        """Notifier le développeur d'un bug critique"""
        try:
            dev_user = self.bot.get_user(self.dev_user_id)
            if dev_user:
                embed = discord.Embed(
                    title="🚨 **BUG CRITIQUE SIGNALÉ**",
                    description=f"**Bug #{bug_id}**\n\n**{title}**",
                    color=discord.Color.red()
                )
                embed.add_field(name="Description", value=description[:1024], inline=False)
                embed.add_field(name="Signalé par", value=f"{user} ({user.id})", inline=True)
                
                await dev_user.send(embed=embed)
        except:
            pass  # Pas grave si la notification échoue

    def get_priority_color(self, priority: str) -> discord.Color:
        """Couleur selon la priorité"""
        colors = {
            "critical": discord.Color.red(),
            "high": discord.Color.orange(), 
            "medium": discord.Color.yellow(),
            "low": discord.Color.green()
        }
        return colors.get(priority, discord.Color.blue())

    def get_priority_emoji(self, priority: str) -> str:
        """Emoji selon la priorité"""
        emojis = {
            "critical": "🔥",
            "high": "🔴",
            "medium": "🟡", 
            "low": "🟢"
        }
        return emojis.get(priority, "❓")

    async def list_bugs_admin(self, interaction):
        """Lister tous les bugs pour admin"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT id, bug_title, priority, status, username
                FROM bug_reports 
                ORDER BY 
                    CASE priority 
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2  
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                    END,
                    timestamp DESC
                LIMIT 15
            ''')
            
            reports = await cursor.fetchall()
        
        if not reports:
            await interaction.response.send_message("Aucun bug trouvé.", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="🔧 **GESTION DES BUGS**",
            description=f"**{len(reports)} bug(s)** récent(s)",
            color=discord.Color.blue()
        )
        
        for bug_id, title, priority, status, username in reports:
            priority_emoji = self.get_priority_emoji(priority)
            status_emoji = "✅" if status == "resolved" else "🔍" if status == "investigating" else "🔴"
            
            embed.add_field(
                name=f"{status_emoji} **Bug #{bug_id}**",
                value=f"**{title[:30]}...**\n"
                      f"{priority_emoji} {priority.upper()}\n"
                      f"👤 {username[:15]}",
                inline=True
            )
            
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ArsenalBugReporter(bot))

