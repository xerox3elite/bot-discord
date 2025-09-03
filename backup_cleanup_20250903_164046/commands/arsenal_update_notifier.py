import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from typing import Dict, Any, Optional, List
import datetime
import asyncio

class ArsenalUpdateNotifier(commands.Cog):
    """Système de notifications des mises à jour Arsenal"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "data/update_notifications"
        self.changelog_path = "data/changelogs"
        os.makedirs(self.config_path, exist_ok=True)
        os.makedirs(self.changelog_path, exist_ok=True)
        
        # Version actuelle d'Arsenal
        self.current_version = "4.5.0"
        
    def load_server_config(self, guild_id: int) -> Dict[str, Any]:
        """Charge la configuration notifications d'un serveur"""
        config_file = f"{self.config_path}/{guild_id}_notifications.json"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                "enabled": False,
                "channel_id": None,
                "ping_role": None,
                "notify_major": True,
                "notify_minor": True,
                "notify_patch": False,
                "custom_message": None
            }
    
    def save_server_config(self, guild_id: int, config: Dict[str, Any]) -> bool:
        """Sauvegarde la configuration notifications d'un serveur"""
        config_file = f"{self.config_path}/{guild_id}_notifications.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False

    def load_version_history(self) -> Dict[str, Any]:
        """Charge l'historique des versions"""
        version_file = f"{self.changelog_path}/version_history.json"
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"versions": [], "last_notified": None}

    def save_version_history(self, history: Dict[str, Any]) -> bool:
        """Sauvegarde l'historique des versions"""
        version_file = f"{self.changelog_path}/version_history.json"
        try:
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False

    @app_commands.command(name="changelog_setup", description="🔔 Configurer les notifications de mise à jour Arsenal")
    @app_commands.describe(
        channel="Salon où recevoir les notifications",
        ping_role="Rôle à mentionner lors des notifications",
        major_updates="Recevoir les mises à jour majeures (v5.0.0)",
        minor_updates="Recevoir les mises à jour mineures (v4.6.0)", 
        patch_updates="Recevoir les correctifs (v4.5.1)"
    )
    async def changelog_setup(
        self, 
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        ping_role: discord.Role = None,
        major_updates: bool = True,
        minor_updates: bool = True,
        patch_updates: bool = False
    ):
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes",
                description="Vous devez être **administrateur** pour configurer les notifications.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Vérifier les permissions du bot dans le salon
        bot_permissions = channel.permissions_for(interaction.guild.me)
        if not (bot_permissions.send_messages and bot_permissions.embed_links):
            embed = discord.Embed(
                title="❌ Permissions Bot Insuffisantes",
                description=f"Je n'ai pas les permissions nécessaires dans {channel.mention}.\n\nPermissions requises :\n• Envoyer des messages\n• Intégrer des liens",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Sauvegarder la configuration
        config = {
            "enabled": True,
            "channel_id": channel.id,
            "ping_role": ping_role.id if ping_role else None,
            "notify_major": major_updates,
            "notify_minor": minor_updates,
            "notify_patch": patch_updates,
            "setup_date": datetime.datetime.now().isoformat(),
            "setup_by": interaction.user.id
        }
        
        success = self.save_server_config(interaction.guild.id, config)
        
        if success:
            embed = discord.Embed(
                title="✅ Notifications Arsenal Configurées",
                description=f"""
**Configuration sauvegardée avec succès !**

**Salon de notification :** {channel.mention}
**Rôle à mentionner :** {ping_role.mention if ping_role else "`Aucun`"}

**Types de notifications :**
{'✅' if major_updates else '❌'} **Mises à jour majeures** (v5.0.0)
{'✅' if minor_updates else '❌'} **Mises à jour mineures** (v4.6.0)  
{'✅' if patch_updates else '❌'} **Correctifs** (v4.5.1)

> 🎉 Vous recevrez désormais toutes les actualités Arsenal automatiquement !
                """,
                color=0x00ff00,
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(
                name="📋 Version Actuelle",
                value=f"Arsenal V{self.current_version}",
                inline=True
            )
            
            embed.add_field(
                name="🔔 Prochaine Notification",
                value="Prochaine mise à jour",
                inline=True
            )
            
            embed.set_footer(
                text="Utilisez /changelog_disable pour désactiver les notifications"
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Message de test dans le salon configuré
            test_embed = discord.Embed(
                title="🔔 Test Notifications Arsenal",
                description=f"""
**Configuration testée avec succès !** ✅

Ce salon recevra désormais toutes les notifications de mise à jour Arsenal.

**Configuré par :** {interaction.user.mention}
**Date :** {datetime.datetime.now().strftime("%d/%m/%Y à %H:%M")}
                """,
                color=0x00ff00
            )
            test_embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
            
            try:
                await channel.send(
                    content=ping_role.mention if ping_role else None,
                    embed=test_embed
                )
            except:
                pass
                
        else:
            embed = discord.Embed(
                title="❌ Erreur de Sauvegarde",
                description="Impossible de sauvegarder la configuration. Réessayez plus tard.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="changelog_disable", description="🔕 Désactiver les notifications Arsenal")
    async def changelog_disable(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes", 
                description="Vous devez être **administrateur** pour désactiver les notifications.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        config = self.load_server_config(interaction.guild.id)
        config["enabled"] = False
        config["disabled_date"] = datetime.datetime.now().isoformat()
        config["disabled_by"] = interaction.user.id
        
        success = self.save_server_config(interaction.guild.id, config)
        
        if success:
            embed = discord.Embed(
                title="🔕 Notifications Désactivées",
                description="Les notifications de mise à jour Arsenal ont été désactivées pour ce serveur.\n\nUtilisez `/changelog_setup` pour les réactiver.",
                color=0xffa500
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Impossible de désactiver les notifications. Réessayez plus tard.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="changelog_status", description="📊 Voir le statut des notifications Arsenal")
    async def changelog_status(self, interaction: discord.Interaction):
        config = self.load_server_config(interaction.guild.id)
        
        if config["enabled"]:
            channel = self.bot.get_channel(config["channel_id"])
            role = interaction.guild.get_role(config["ping_role"]) if config["ping_role"] else None
            
            embed = discord.Embed(
                title="📊 Statut Notifications Arsenal",
                description="**Notifications activées** ✅",
                color=0x00ff00
            )
            
            embed.add_field(
                name="🏠 Configuration",
                value=f"""
**Salon :** {channel.mention if channel else "`Salon supprimé`"}
**Rôle :** {role.mention if role else "`Aucun`"}
**Configuré le :** {config.get('setup_date', 'Inconnu')[:10]}
                """,
                inline=True
            )
            
            embed.add_field(
                name="🔔 Types de Notifications",
                value=f"""
{'✅' if config.get('notify_major', True) else '❌'} Mises à jour majeures
{'✅' if config.get('notify_minor', True) else '❌'} Mises à jour mineures  
{'✅' if config.get('notify_patch', False) else '❌'} Correctifs
                """,
                inline=True
            )
            
        else:
            embed = discord.Embed(
                title="📊 Statut Notifications Arsenal",
                description="**Notifications désactivées** ❌",
                color=0xff0000
            )
            embed.add_field(
                name="💡 Activation",
                value="Utilisez `/changelog_setup` pour activer les notifications.",
                inline=False
            )
        
        embed.add_field(
            name="📋 Version Actuelle",
            value=f"Arsenal V{self.current_version}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="changelog_latest", description="📰 Voir le dernier changelog Arsenal")
    async def changelog_latest(self, interaction: discord.Interaction):
        """Affiche le dernier changelog disponible"""
        embed = discord.Embed(
            title="📰 Arsenal V4.5.0 - Configuration Complète Original",
            description="""
**Dernière mise à jour disponible** (14 Août 2025)

🎯 **FONCTIONNALITÉS MAJEURES**
• **Système de Configuration Arsenal Original** - 29 modules
• **ArsenalCoin Economy System** - Monnaie virtuelle complète  
• **Arsenal Shop System** - Boutique dynamique avec panel admin
• **Interface Arsenal 100% Original** - Aucune référence externe
            """,
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="✨ Nouveautés V4.5",
            value="""
• 29 modules de configuration
• Système ArsenalCoin complet
• Boutique avec objets globaux/serveur
• Interface utilisateur Arsenal
• Documentation technique complète
            """,
            inline=True
        )
        
        embed.add_field(
            name="🔧 Améliorations",
            value="""
• Architecture modulaire optimisée
• Sauvegarde JSON automatique
• Gestion d'erreurs avancée
• Interface administrateur
• Tests complets intégrés
            """,
            inline=True
        )
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"""
• **150+ commandes** disponibles
• **29 modules** configurables
• **~20,000 lignes** de code
• **Support multi-serveurs**
            """,
            inline=False
        )
        
        embed.set_footer(
            text="Arsenal V4.5 • Utilisez /changelog_setup pour recevoir les notifications automatiques"
        )
        
        await interaction.response.send_message(embed=embed)

    async def broadcast_update(self, version: str, changelog: Dict[str, Any]):
        """Diffuse une mise à jour à tous les serveurs configurés"""
        # Charger tous les serveurs avec notifications activées
        notification_servers = []
        
        for filename in os.listdir(self.config_path):
            if filename.endswith("_notifications.json"):
                guild_id = int(filename.split("_")[0])
                config = self.load_server_config(guild_id)
                
                if config["enabled"]:
                    guild = self.bot.get_guild(guild_id)
                    if guild:
                        notification_servers.append((guild, config))
        
        # Déterminer le type de mise à jour
        version_parts = version.split(".")
        if len(version_parts) >= 3:
            major, minor, patch = int(version_parts[0]), int(version_parts[1]), int(version_parts[2])
            
            for guild, config in notification_servers:
                should_notify = False
                
                # Vérifier si on doit notifier selon le type de mise à jour
                if patch > 0 and config.get("notify_patch", False):
                    should_notify = True
                elif minor > 0 and config.get("notify_minor", True):  
                    should_notify = True
                elif major > 0 and config.get("notify_major", True):
                    should_notify = True
                
                if should_notify:
                    await self.send_update_notification(guild, config, version, changelog)
        
        # Mettre à jour l'historique des versions
        history = self.load_version_history()
        history["versions"].append({
            "version": version,
            "date": datetime.datetime.now().isoformat(),
            "changelog": changelog,
            "servers_notified": len(notification_servers)
        })
        history["last_notified"] = datetime.datetime.now().isoformat()
        self.save_version_history(history)

    async def send_update_notification(self, guild: discord.Guild, config: Dict[str, Any], version: str, changelog: Dict[str, Any]):
        """Envoie la notification de mise à jour à un serveur"""
        try:
            channel = guild.get_channel(config["channel_id"])
            if not channel:
                return
                
            role = guild.get_role(config["ping_role"]) if config["ping_role"] else None
            
            embed = discord.Embed(
                title=f"🚀 Arsenal V{version} - Nouvelle Mise à Jour !",
                description=changelog.get("description", "Nouvelle version d'Arsenal disponible !"),
                color=0x00ff00,
                timestamp=datetime.datetime.now()
            )
            
            # Ajouter les nouvelles fonctionnalités
            if "features" in changelog:
                features_text = "\n".join([f"• {feature}" for feature in changelog["features"][:5]])
                embed.add_field(
                    name="✨ Nouveautés",
                    value=features_text,
                    inline=False
                )
            
            # Ajouter les améliorations
            if "improvements" in changelog:
                improvements_text = "\n".join([f"• {improvement}" for improvement in changelog["improvements"][:3]])
                embed.add_field(
                    name="🔧 Améliorations", 
                    value=improvements_text,
                    inline=True
                )
            
            # Ajouter les corrections de bugs
            if "fixes" in changelog:
                fixes_text = "\n".join([f"• {fix}" for fix in changelog["fixes"][:3]])
                embed.add_field(
                    name="🐛 Corrections",
                    value=fixes_text,
                    inline=True
                )
            
            embed.add_field(
                name="📋 Commandes",
                value="Utilisez `/changelog_latest` pour voir le changelog complet",
                inline=False
            )
            
            embed.set_footer(
                text=f"Arsenal V{version} • Serveur: {guild.name}"
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
            
            await channel.send(
                content=role.mention if role else None,
                embed=embed
            )
            
        except Exception as e:
            print(f"Erreur notification pour {guild.name}: {e}")

    # Commande développeur pour déclencher une notification de test
    @app_commands.command(name="dev_broadcast_update", description="🔧 [DEV] Diffuser une mise à jour test")
    async def dev_broadcast_update(self, interaction: discord.Interaction, version: str):
        """Commande développeur pour tester les notifications"""
        if interaction.user.id != 431359112039890945:  # ID du créateur
            await interaction.response.send_message("❌ Commande développeur uniquement.", ephemeral=True)
            return
        
        test_changelog = {
            "description": f"**Mise à jour test Arsenal V{version}**",
            "features": [
                "Nouvelle fonctionnalité test 1",
                "Nouvelle fonctionnalité test 2", 
                "Amélioration système test"
            ],
            "improvements": [
                "Optimisation performance",
                "Interface utilisateur améliorée"
            ],
            "fixes": [
                "Correction bug critique",
                "Fix problème de connectivité"
            ]
        }
        
        await interaction.response.defer()
        await self.broadcast_update(version, test_changelog)
        
        embed = discord.Embed(
            title="✅ Mise à Jour Diffusée",
            description=f"La notification Arsenal V{version} a été envoyée à tous les serveurs configurés.",
            color=0x00ff00
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ArsenalUpdateNotifier(bot))

