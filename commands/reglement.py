#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Arsenal V4 - Système de Règlement Ultra Complet
Gestion complète des règlements avec acceptation, sanctions et modération automatique
"""

import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import json
import asyncio
from datetime import datetime, timedelta
import os
from typing import Optional, Dict, List

class ReglementSystem(commands.Cog):
    """Système de règlement ultra complet pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/reglement.db"
        self.config_path = "data/reglement_config.json"
        
        # Configuration par défaut
        self.default_config = {
            "reglement_channel": None,
            "accept_emoji": "✅",
            "refuse_emoji": "❌",
            "auto_kick_refuse": True,
            "auto_timeout_unread": True,
            "timeout_duration": 3600,  # 1 heure
            "required_role": None,
            "mod_log_channel": None,
            "welcome_message": True,
            "dm_on_refuse": True
        }
        
        # Règles personnalisables (vides par défaut)
        self.default_rules = {}

    async def setup_database(self):
        """Initialise la base de données"""
        os.makedirs("data", exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            # Table des acceptations de règlement
            await db.execute("""
                CREATE TABLE IF NOT EXISTS reglement_acceptations (
                    user_id INTEGER PRIMARY KEY,
                    guild_id INTEGER,
                    accepted_at TIMESTAMP,
                    version TEXT,
                    ip_hash TEXT
                )
            """)
            
            # Table des sanctions liées aux règles
            await db.execute("""
                CREATE TABLE IF NOT EXISTS reglement_sanctions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    guild_id INTEGER,
                    rule_broken TEXT,
                    sanction_type TEXT,
                    reason TEXT,
                    moderator_id INTEGER,
                    created_at TIMESTAMP,
                    active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Table des statistiques de règlement
            await db.execute("""
                CREATE TABLE IF NOT EXISTS reglement_stats (
                    guild_id INTEGER,
                    accepted_count INTEGER DEFAULT 0,
                    refused_count INTEGER DEFAULT 0,
                    violations_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP
                )
            """)
            
            await db.commit()

    def load_rules(self, guild_id: int) -> Dict:
        """Charge les règles personnalisées pour un serveur"""
        try:
            rules_path = f"data/rules_{guild_id}.json"
            if os.path.exists(rules_path):
                with open(rules_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_rules(self, guild_id: int, rules: Dict):
        """Sauvegarde les règles personnalisées"""
        try:
            os.makedirs("data", exist_ok=True)
            rules_path = f"data/rules_{guild_id}.json"
            with open(rules_path, 'w', encoding='utf-8') as f:
                json.dump(rules, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde règles: {e}")
        """Charge la configuration pour un serveur"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    all_configs = json.load(f)
                    return all_configs.get(str(guild_id), self.default_config)
        except:
            pass
        return self.default_config.copy()

    def save_config(self, guild_id: int, config: Dict):
        """Sauvegarde la configuration"""
        try:
            all_configs = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    all_configs = json.load(f)
            
            all_configs[str(guild_id)] = config
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(all_configs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde config règlement: {e}")

    @app_commands.command(name="reglement", description="📜 Afficher le règlement complet du serveur")
    async def reglement_display(self, interaction: discord.Interaction):
        """Affiche le règlement complet avec boutons d'interaction"""
        
        config = self.load_config(interaction.guild.id)
        rules = self.load_rules(interaction.guild.id)
        
        # Vérifier si des règles existent
        if not rules:
            embed = discord.Embed(
                title="📜 **RÈGLEMENT DU SERVEUR**",
                description=f"**{interaction.guild.name}**\n\n"
                           "❌ **Aucune règle configurée pour ce serveur.**\n\n"
                           "Les administrateurs doivent créer les règles avec `/reglement_add`\n"
                           "📝 **Système 100% personnalisable !**",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="🛠️ **Configuration**",
                value="• `/reglement_add` - Ajouter une règle\n"
                      "• `/reglement_edit` - Modifier une règle\n"
                      "• `/reglement_remove` - Supprimer une règle\n"
                      "• `/reglement_config` - Configurer le système",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Embed principal du règlement
        embed = discord.Embed(
            title="📜 **RÈGLEMENT OFFICIEL DU SERVEUR**",
            description=f"**{interaction.guild.name}**\n\n"
                       "**⚠️ L'acceptation de ce règlement est OBLIGATOIRE pour rester sur le serveur.**\n"
                       "**📚 Lisez attentivement chaque règle avant d'accepter.**\n\n"
                       f"**🔄 Dernière mise à jour:** {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        
        # Ajouter toutes les règles personnalisées
        for rule_id, rule_data in rules.items():
            severity_emoji = {
                "low": "🟢",
                "medium": "🟡", 
                "high": "🔴",
                "critical": "⚫"
            }.get(rule_data.get("severity", "medium"), "⚪")
            
            embed.add_field(
                name=f"{severity_emoji} **Règle #{rule_id}** - {rule_data.get('title', 'Sans titre')}",
                value=f"**📋 Description:** {rule_data.get('description', 'Aucune description')}\n"
                      f"**⚖️ Sanctions:** {', '.join(rule_data.get('sanctions', ['Non spécifiées'])[:3])}{'...' if len(rule_data.get('sanctions', [])) > 3 else ''}",
                inline=False
            )
        
        # Footer avec informations importantes
        embed.set_footer(
            text=f"Arsenal Bot V4 | Règlement #{interaction.guild.id} | {len(rules)} règle(s) configurée(s)",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        # Boutons d'interaction
        view = ReglementView(config)
        
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="reglement_add", description="➕ Ajouter une nouvelle règle")
    @app_commands.describe(
        rule_id="Numéro de la règle (ex: 1, 2, 3...)",
        title="Titre de la règle",
        description="Description détaillée",
        severity="Niveau de gravité",
        sanctions="Sanctions séparées par des virgules"
    )
    async def reglement_add(
        self, 
        interaction: discord.Interaction,
        rule_id: str,
        title: str,
        description: str,
        severity: str = "medium",
        sanctions: str = "Avertissement"
    ):
        """Ajoute une nouvelle règle personnalisée"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Permission requise: `Gérer le serveur`", ephemeral=True)
            return
        
        # Valider le niveau de gravité
        if severity not in ["low", "medium", "high", "critical"]:
            severity = "medium"
            
        # Charger les règles existantes
        rules = self.load_rules(interaction.guild.id)
        
        # Ajouter la nouvelle règle
        rules[rule_id] = {
            "title": title,
            "description": description,
            "severity": severity,
            "sanctions": [s.strip() for s in sanctions.split(",")]
        }
        
        # Sauvegarder
        self.save_rules(interaction.guild.id, rules)
        
        severity_emoji = {
            "low": "🟢",
            "medium": "🟡", 
            "high": "🔴",
            "critical": "⚫"
        }.get(severity, "⚪")
        
        embed = discord.Embed(
            title="✅ **Règle Ajoutée !**",
            description=f"**Règle #{rule_id} créée avec succès**",
            color=discord.Color.green()
        )
        
        embed.add_field(name="📌 Titre", value=title, inline=False)
        embed.add_field(name="📝 Description", value=description, inline=False)
        embed.add_field(name=f"{severity_emoji} Gravité", value=severity.upper(), inline=True)
        embed.add_field(name="⚖️ Sanctions", value=", ".join([s.strip() for s in sanctions.split(",")]), inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="reglement_remove", description="🗑️ Supprimer une règle")
    @app_commands.describe(rule_id="Numéro de la règle à supprimer")
    async def reglement_remove(self, interaction: discord.Interaction, rule_id: str):
        """Supprime une règle existante"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Permission requise: `Gérer le serveur`", ephemeral=True)
            return
        
        rules = self.load_rules(interaction.guild.id)
        
        if rule_id not in rules:
            await interaction.response.send_message(f"❌ Règle #{rule_id} introuvable", ephemeral=True)
            return
        
        rule_title = rules[rule_id].get("title", "Sans titre")
        del rules[rule_id]
        
        self.save_rules(interaction.guild.id, rules)
        
        embed = discord.Embed(
            title="🗑️ **Règle Supprimée**",
            description=f"**Règle #{rule_id}** - {rule_title}\n\nSupprimée avec succès !",
            color=discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="reglement_list", description="📋 Lister toutes les règles")
    async def reglement_list(self, interaction: discord.Interaction):
        """Liste toutes les règles configurées"""
        
        rules = self.load_rules(interaction.guild.id)
        
        embed = discord.Embed(
            title="📋 **Liste des Règles Configurées**",
            description=f"**Serveur:** {interaction.guild.name}",
            color=discord.Color.blue()
        )
        
        if not rules:
            embed.add_field(
                name="❌ Aucune règle",
                value="Utilisez `/reglement_add` pour créer des règles",
                inline=False
            )
        else:
            for rule_id, rule_data in rules.items():
                severity_emoji = {
                    "low": "🟢",
                    "medium": "🟡", 
                    "high": "🔴",
                    "critical": "⚫"
                }.get(rule_data.get("severity", "medium"), "⚪")
                
                embed.add_field(
                    name=f"{severity_emoji} **Règle #{rule_id}**",
                    value=f"**{rule_data.get('title', 'Sans titre')}**\n{rule_data.get('description', 'Aucune description')[:100]}{'...' if len(rule_data.get('description', '')) > 100 else ''}",
                    inline=True
                )
        
        embed.set_footer(text=f"{len(rules)} règle(s) configurée(s)")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="reglement_config", description="⚙️ Configurer le système de règlement")
    @app_commands.describe(
        channel="Salon pour le règlement",
        accept_emoji="Emoji d'acceptation",
        refuse_emoji="Emoji de refus",
        auto_kick="Kick automatique si refus",
        timeout_duration="Durée de timeout (secondes)"
    )
    async def reglement_config(
        self, 
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None,
        accept_emoji: Optional[str] = None,
        refuse_emoji: Optional[str] = None,
        auto_kick: Optional[bool] = None,
        timeout_duration: Optional[int] = None
    ):
        """Configure le système de règlement"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Vous n'avez pas la permission de configurer le règlement.", ephemeral=True)
            return
        
        config = self.load_config(interaction.guild.id)
        
        # Appliquer les modifications
        if channel:
            config["reglement_channel"] = channel.id
        if accept_emoji:
            config["accept_emoji"] = accept_emoji
        if refuse_emoji:
            config["refuse_emoji"] = refuse_emoji
        if auto_kick is not None:
            config["auto_kick_refuse"] = auto_kick
        if timeout_duration:
            config["timeout_duration"] = timeout_duration
        
        self.save_config(interaction.guild.id, config)
        
        embed = discord.Embed(
            title="⚙️ Configuration Règlement Mise à Jour",
            description="✅ **Configuration sauvegardée avec succès !**",
            color=discord.Color.green()
        )
        
        embed.add_field(name="📍 Salon règlement", value=f"<#{config['reglement_channel']}>" if config.get('reglement_channel') else "Non défini", inline=True)
        embed.add_field(name="✅ Emoji acceptation", value=config.get('accept_emoji', '✅'), inline=True)
        embed.add_field(name="❌ Emoji refus", value=config.get('refuse_emoji', '❌'), inline=True)
        embed.add_field(name="🦵 Kick auto refus", value="Activé" if config.get('auto_kick_refuse') else "Désactivé", inline=True)
        embed.add_field(name="⏱️ Timeout durée", value=f"{config.get('timeout_duration', 3600)}s", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="reglement_stats", description="📊 Statistiques du règlement")
    async def reglement_stats(self, interaction: discord.Interaction):
        """Affiche les statistiques du règlement"""
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Acceptations
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM reglement_acceptations WHERE guild_id = ?",
                    (interaction.guild.id,)
                )
                accepted_count = (await cursor.fetchone())[0]
                
                # Sanctions
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM reglement_sanctions WHERE guild_id = ? AND active = TRUE",
                    (interaction.guild.id,)
                )
                sanctions_count = (await cursor.fetchone())[0]
                
                # Acceptations récentes (7 derniers jours)
                week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM reglement_acceptations WHERE guild_id = ? AND accepted_at > ?",
                    (interaction.guild.id, week_ago)
                )
                recent_accepted = (await cursor.fetchone())[0]
        
        except Exception as e:
            accepted_count = sanctions_count = recent_accepted = 0
        
        embed = discord.Embed(
            title="📊 Statistiques du Règlement",
            description=f"**Serveur:** {interaction.guild.name}",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="✅ Total acceptations", value=f"**{accepted_count}** membres", inline=True)
        embed.add_field(name="⚖️ Sanctions actives", value=f"**{sanctions_count}** sanctions", inline=True)
        embed.add_field(name="📈 Cette semaine", value=f"**{recent_accepted}** nouvelles acceptations", inline=True)
        
        # Taux de conformité
        total_members = interaction.guild.member_count
        compliance_rate = (accepted_count / total_members * 100) if total_members > 0 else 0
        
        embed.add_field(name="📋 Taux de conformité", value=f"**{compliance_rate:.1f}%** ({accepted_count}/{total_members})", inline=False)
        
        # Graphique de conformité (simple barre)
        compliance_bar = "█" * int(compliance_rate / 5) + "░" * (20 - int(compliance_rate / 5))
        embed.add_field(name="📊 Graphique conformité", value=f"`{compliance_bar}` {compliance_rate:.1f}%", inline=False)
        
        await interaction.response.send_message(embed=embed)

    async def record_acceptance(self, user_id: int, guild_id: int, version: str = "1.0"):
        """Enregistre une acceptation de règlement"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO reglement_acceptations 
                    (user_id, guild_id, accepted_at, version)
                    VALUES (?, ?, ?, ?)
                """, (user_id, guild_id, datetime.now().isoformat(), version))
                await db.commit()
        except Exception as e:
            print(f"Erreur enregistrement acceptation: {e}")

    async def record_sanction(self, user_id: int, guild_id: int, rule: str, sanction: str, reason: str, moderator_id: int):
        """Enregistre une sanction"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO reglement_sanctions 
                    (user_id, guild_id, rule_broken, sanction_type, reason, moderator_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, guild_id, rule, sanction, reason, moderator_id, datetime.now().isoformat()))
                await db.commit()
        except Exception as e:
            print(f"Erreur enregistrement sanction: {e}")

class ReglementView(discord.ui.View):
    """Interface utilisateur pour le règlement"""
    
    def __init__(self, config: Dict):
        super().__init__(timeout=None)
        self.config = config
        
    @discord.ui.button(label="✅ J'accepte le règlement", style=discord.ButtonStyle.success, custom_id="accept_reglement")
    async def accept_reglement(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton d'acceptation du règlement"""
        
        # Vérifier si déjà accepté
        cog = interaction.client.get_cog("ReglementSystem")
        if cog:
            await cog.record_acceptance(interaction.user.id, interaction.guild.id)
        
        embed = discord.Embed(
            title="✅ **Règlement Accepté !**",
            description=f"**{interaction.user.mention}**, merci d'avoir accepté le règlement !\n\n"
                       "🎉 **Bienvenue officielle sur le serveur !**\n"
                       "🔓 **Accès complet aux salons déverrouillé**\n\n"
                       "📚 **Rappel:** Ce règlement peut être modifié. Restez informé des mises à jour.",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        embed.set_footer(text=f"Accepté le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Ajouter rôle si configuré
        if self.config.get("required_role"):
            try:
                role = interaction.guild.get_role(self.config["required_role"])
                if role:
                    await interaction.user.add_roles(role, reason="Acceptation du règlement")
            except:
                pass

    @discord.ui.button(label="❌ Je refuse le règlement", style=discord.ButtonStyle.danger, custom_id="refuse_reglement")
    async def refuse_reglement(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton de refus du règlement"""
        
        embed = discord.Embed(
            title="❌ **Règlement Refusé**",
            description=f"**{interaction.user.mention}**, vous avez refusé le règlement.\n\n"
                       "⚠️ **Conséquences:**\n"
                       "• Accès limité aux salons\n"
                       "• Timeout automatique appliqué\n"
                       "• Exclusion possible du serveur\n\n"
                       "💭 **Reconsidérez votre décision** pour profiter pleinement du serveur.",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Actions automatiques selon config
        if self.config.get("auto_kick_refuse"):
            try:
                await interaction.user.kick(reason="Refus du règlement")
            except:
                pass
        elif self.config.get("auto_timeout_unread"):
            timeout_duration = self.config.get("timeout_duration", 3600)
            until = datetime.now() + timedelta(seconds=timeout_duration)
            try:
                await interaction.user.timeout(until, reason="Refus du règlement")
            except:
                pass

    @discord.ui.button(label="📖 Lire en détail", style=discord.ButtonStyle.secondary, custom_id="read_detail")
    async def read_detail(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour lecture détaillée"""
        
        embed = discord.Embed(
            title="📖 **Guide de Lecture du Règlement**",
            description="**Comment bien comprendre notre règlement:**",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🔍 **Niveaux de Gravité**",
            value="🟢 **Faible** - Rappels et avertissements\n"
                  "🟡 **Moyen** - Mutes et restrictions temporaires\n"
                  "🔴 **Élevé** - Kicks et bans temporaires\n"
                  "⚫ **Critique** - Ban permanent immédiat",
            inline=False
        )
        
        embed.add_field(
            name="⚖️ **Système de Sanctions**",
            value="• Les sanctions sont **progressives**\n"
                  "• Chaque infraction est **évaluée individuellement**\n"
                  "• Les **récidives** aggravent les sanctions\n"
                  "• Possibilité d'**appel** pour les sanctions majeures",
            inline=False
        )
        
        embed.add_field(
            name="🤝 **Nos Valeurs**",
            value="**Respect • Bienveillance • Entraide • Fair-play**\n\n"
                  "Ce règlement garantit une **expérience positive** pour tous !",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    """Charge le module Reglement"""
    cog = ReglementSystem(bot)
    await cog.setup_database()
    await bot.add_cog(cog)
    print("📜 [Reglement System] Module chargé avec succès!")
