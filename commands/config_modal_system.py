#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Arsenal V4 - Système de Configuration MODAL MODERNE
Remplace complètement l'ancien système de menus déroulants superficiels
Configuration ultra-moderne avec formulaires interactifs complets
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from typing import Optional, Dict, Any
import asyncio

class ArsenalConfigSystemModal(commands.Cog):
    """Système de configuration Arsenal V4 avec modals - REMPLACE L'ANCIEN"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "data/server_configs"
        os.makedirs(self.config_path, exist_ok=True)

    def load_config(self, guild_id: int):
        """Charge la configuration d'un serveur"""
        try:
            config_file = f"{self.config_path}/{guild_id}.json"
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return self.get_default_config()

    def save_config(self, guild_id: int, config):
        """Sauvegarde la configuration d'un serveur"""
        try:
            config_file = f"{self.config_path}/{guild_id}.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde config: {e}")

    def get_default_config(self):
        """Configuration par défaut"""
        return {
            "automod": {
                "enabled": False,
                "anti_spam": {"enabled": False, "max_messages": 5, "time_window": 10},
                "anti_links": {"enabled": False, "whitelist": []},
                "anti_invites": {"enabled": False, "action": "delete"},
                "anti_nsfw": {"enabled": False, "action": "delete"},
                "filter_words": {"enabled": False, "words": []},
                "logs_channel": None
            },
            "economy": {
                "enabled": True,
                "daily_reward": 100,
                "message_reward": 5,
                "voice_reward": 10,
                "shop_enabled": True,
                "transfer_enabled": True
            },
            "levels": {
                "enabled": True,
                "message_xp": 15,
                "voice_xp": 25,
                "level_up_channel": None,
                "level_rewards": {}
            },
            "temp_channels": {
                "enabled": False,
                "category": None,
                "channel_name": "🎵 {user}'s Channel",
                "user_limit": 0,
                "auto_delete": True
            },
            "music": {
                "enabled": True,
                "max_queue": 50,
                "max_duration": 7200,
                "default_volume": 50,
                "dj_role": None
            },
            "logs": {
                "enabled": False,
                "message_logs": None,
                "mod_logs": None,
                "voice_logs": None,
                "join_leave": None
            }
        }

    @app_commands.command(name="config_modal", description="⚙️ Configuration moderne Arsenal avec MODALS")
    async def config_main(self, interaction: discord.Interaction):
        """Menu principal de configuration avec boutons modals"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Permission requise: `Gérer le serveur`", ephemeral=True)
            return

        embed = discord.Embed(
            title="⚙️ **ARSENAL CONFIGURATION MODERNE**",
            description=f"**🏠 Serveur:** {interaction.guild.name}\n\n"
                       "🆕 **NOUVEAU ! Configuration avec formulaires modals**\n"
                       "✨ **Fini les menus superficiels - place aux VRAIS paramètres !**\n\n"
                       "🎯 **Chaque bouton ouvre un formulaire interactif complet**\n"
                       "📝 **Configuration profonde et fonctionnelle**",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="🛡️ **AutoMod Arsenal**",
            value="• 🚫 Anti-spam intelligent\n• 🔗 Blocage de liens\n• 📝 Filtrage de mots\n• ⚡ Actions automatiques",
            inline=True
        )
        
        embed.add_field(
            name="💰 **Économie ArsenalCoin**", 
            value="• 🪙 Récompenses quotidiennes\n• 💬 Gains par message\n• 🎤 Gains vocaux\n• 🛒 Boutique intégrée",
            inline=True
        )
        
        embed.add_field(
            name="🗣️ **Salons Temporaires**",
            value="• 🎵 Création automatique\n• 🏷️ Noms personnalisés\n• 👥 Limites d'utilisateurs\n• 🗑️ Suppression auto",
            inline=True
        )
        
        embed.add_field(
            name="🎵 **Système Musical HD**",
            value="• 🎶 Configuration audio\n• 📝 File d'attente\n• 🎧 Permissions DJ\n• 🔊 Volume personnalisé",
            inline=True
        )
        
        embed.add_field(
            name="📊 **Système de Logs**",
            value="• 📝 Messages & éditions\n• 🛡️ Actions de modération\n• 🚪 Entrées & sorties\n• 🎤 Activités vocales",
            inline=True
        )
        
        embed.add_field(
            name="🎮 **Fonctionnalités Bonus**",
            value="• 📈 Système de niveaux\n• 🎯 Configurations avancées\n• 🔄 Reset facile\n• 💾 Sauvegarde auto",
            inline=True
        )
        
        embed.set_footer(text="Arsenal V4.5.1 - Configuration Modal Révolutionnaire | Cliquez pour configurer")
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)

        view = ArsenalConfigModalView(self)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# ===== MODALS DE CONFIGURATION ARSENAL =====

class AutoModArsenalModal(discord.ui.Modal):
    """Modal AutoMod Arsenal avec configuration complète"""
    
    def __init__(self, config_system, current_config):
        super().__init__(title="🛡️ AutoMod Arsenal - Configuration Complète", timeout=300)
        self.config_system = config_system
        self.current_config = current_config
        
        automod_config = current_config.get("automod", {})
        
        self.add_item(discord.ui.TextInput(
            label="🛡️ Activer AutoMod Arsenal (true/false)",
            placeholder="true = Activer toute la protection Arsenal | false = Désactiver",
            default=str(automod_config.get("enabled", False)).lower(),
            min_length=4,
            max_length=5
        ))
        
        self.add_item(discord.ui.TextInput(
            label="⚡ Anti-spam: Messages max",
            placeholder="Nombre max de messages en 10 secondes (recommandé: 5)",
            default=str(automod_config.get("anti_spam", {}).get("max_messages", 5)),
            min_length=1,
            max_length=2
        ))
        
        self.add_item(discord.ui.TextInput(
            label="⏰ Anti-spam: Fenêtre temps",
            placeholder="Durée en secondes pour compter les messages (recommandé: 10)",
            default=str(automod_config.get("anti_spam", {}).get("time_window", 10)),
            min_length=1,
            max_length=3
        ))
        
        self.add_item(discord.ui.TextInput(
            label="🚫 Mots interdits (séparés par virgules)",
            placeholder="Exemple: merde, putain, connard, salope, fdp...",
            default=", ".join(automod_config.get("filter_words", {}).get("words", [])),
            required=False,
            max_length=1000
        ))
        
        self.add_item(discord.ui.TextInput(
            label="🔗 Bloquer liens externes (true/false)",
            placeholder="true = Bloquer tous les liens externes | false = Autoriser",
            default=str(automod_config.get("anti_links", {}).get("enabled", False)).lower(),
            min_length=4,
            max_length=5
        ))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Récupérer et valider toutes les valeurs
            enabled = self.children[0].value.lower() == "true"
            max_messages = max(1, min(20, int(self.children[1].value)))  # Entre 1 et 20
            time_window = max(5, min(60, int(self.children[2].value)))   # Entre 5 et 60 secondes
            filter_words = [word.strip().lower() for word in self.children[3].value.split(",") if word.strip()]
            anti_links = self.children[4].value.lower() == "true"
            
            # Mettre à jour la configuration complète
            config = self.config_system.load_config(interaction.guild.id)
            config["automod"] = {
                "enabled": enabled,
                "anti_spam": {
                    "enabled": enabled,
                    "max_messages": max_messages,
                    "time_window": time_window,
                    "action": "timeout"  # Action par défaut
                },
                "anti_links": {
                    "enabled": anti_links,
                    "whitelist": ["discord.gg", "youtube.com", "spotify.com"],  # Liens autorisés
                    "action": "delete"
                },
                "anti_invites": {
                    "enabled": enabled,
                    "action": "delete"
                },
                "anti_nsfw": {
                    "enabled": enabled,
                    "action": "delete"
                },
                "filter_words": {
                    "enabled": len(filter_words) > 0,
                    "words": filter_words,
                    "action": "delete"
                },
                "logs_channel": config.get("automod", {}).get("logs_channel"),
                "bypass_roles": [],  # Rôles qui contournent l'automod
                "strict_mode": enabled  # Mode strict
            }
            
            # Sauvegarder
            self.config_system.save_config(interaction.guild.id, config)
            
            # Embed de confirmation détaillé
            embed = discord.Embed(
                title="✅ **AutoMod Arsenal Configuré !**",
                description="🛡️ **Système de modération automatique Arsenal activé**\n\n"
                           f"🎯 **Protection niveau:** {'🔴 MAXIMUM' if enabled else '🟢 DÉSACTIVÉ'}",
                color=discord.Color.green() if enabled else discord.Color.red()
            )
            
            embed.add_field(
                name="🛡️ **Statut Protection**",
                value=f"{'🟢 **ACTIVÉ**' if enabled else '🔴 **DÉSACTIVÉ**'}\n"
                      f"Mode: {'Strict' if enabled else 'Permissif'}",
                inline=True
            )
            
            embed.add_field(
                name="⚡ **Anti-Spam**",
                value=f"Max: **{max_messages}** messages\n"
                      f"Période: **{time_window}** secondes\n"
                      f"Action: **Timeout**",
                inline=True
            )
            
            embed.add_field(
                name="🚫 **Filtrage**",
                value=f"Mots interdits: **{len(filter_words)}**\n"
                      f"Anti-liens: {'✅ ON' if anti_links else '❌ OFF'}\n"
                      f"Anti-invites: {'✅ ON' if enabled else '❌ OFF'}",
                inline=True
            )
            
            embed.add_field(
                name="🎯 **Actions Automatiques**",
                value="• 🗑️ Suppression de contenu\n"
                      "• ⏰ Timeout automatique\n"
                      "• 📊 Logs détaillés\n"
                      "• ⚠️ Avertissements",
                inline=True
            )
            
            embed.add_field(
                name="🔧 **Configuration Avancée**",
                value="• 🌟 Rôles exempts disponibles\n"
                      "• 📝 Whitelist personnalisable\n"
                      "• 🎚️ Niveaux de sévérité\n"
                      "• 📊 Statistiques temps réel",
                inline=True
            )
            
            embed.add_field(
                name="💡 **Conseils**",
                value="• Testez les paramètres graduellement\n"
                      "• Ajustez selon votre communauté\n"
                      "• Surveillez les logs régulièrement",
                inline=True
            )
            
            embed.set_footer(text="Arsenal AutoMod V4.5.1 | Protection intelligente active")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ **Erreur configuration AutoMod:** ```{e}```", ephemeral=True)

class EconomyArsenalModal(discord.ui.Modal):
    """Modal Économie Arsenal avec configuration complète ArsenalCoin"""
    
    def __init__(self, config_system, current_config):
        super().__init__(title="💰 Économie Arsenal - Configuration ArsenalCoin", timeout=300)
        self.config_system = config_system
        self.current_config = current_config
        
        economy_config = current_config.get("economy", {})
        
        self.add_item(discord.ui.TextInput(
            label="💳 Activer ArsenalCoin (true/false)",
            placeholder="true = Système économique ON | false = Système OFF",
            default=str(economy_config.get("enabled", True)).lower(),
            min_length=4,
            max_length=5
        ))
        
        self.add_item(discord.ui.TextInput(
            label="🎁 Récompense quotidienne (/daily)",
            placeholder="ArsenalCoins donnés chaque jour (recommandé: 100-500)",
            default=str(economy_config.get("daily_reward", 100)),
            min_length=1,
            max_length=5
        ))
        
        self.add_item(discord.ui.TextInput(
            label="💬 Gains par message",
            placeholder="AC gagnés par message écrit (recommandé: 2-10)",
            default=str(economy_config.get("message_reward", 5)),
            min_length=1,
            max_length=3
        ))
        
        self.add_item(discord.ui.TextInput(
            label="🎤 Gains vocal (par minute)",
            placeholder="AC gagnés par minute en vocal (recommandé: 5-15)",
            default=str(economy_config.get("voice_reward", 10)),
            min_length=1,
            max_length=3
        ))
        
        self.add_item(discord.ui.TextInput(
            label="🛒 Boutique & Transferts (true/false)",
            placeholder="true = /shop et /pay activés | false = Désactivés",
            default=str(economy_config.get("shop_enabled", True)).lower(),
            min_length=4,
            max_length=5
        ))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            enabled = self.children[0].value.lower() == "true"
            daily_reward = max(50, min(2000, int(self.children[1].value)))    # Entre 50 et 2000
            message_reward = max(1, min(50, int(self.children[2].value)))      # Entre 1 et 50
            voice_reward = max(1, min(100, int(self.children[3].value)))       # Entre 1 et 100
            shop_enabled = self.children[4].value.lower() == "true"
            
            config = self.config_system.load_config(interaction.guild.id)
            config["economy"] = {
                "enabled": enabled,
                "daily_reward": daily_reward,
                "message_reward": message_reward,
                "voice_reward": voice_reward,
                "shop_enabled": shop_enabled and enabled,  # Shop nécessite économie
                "transfer_enabled": shop_enabled and enabled,
                "gambling_enabled": enabled,  # Casino/loterie
                "leaderboard_enabled": enabled,
                "weekly_bonus": daily_reward * 7,  # Bonus hebdomadaire
                "currency_symbol": "AC",
                "max_daily_messages": 100,  # Limite pour éviter le spam
                "max_daily_voice": 480     # 8h maximum par jour
            }
            
            self.config_system.save_config(interaction.guild.id, config)
            
            embed = discord.Embed(
                title="💰 **Économie Arsenal Configurée !**",
                description="🪙 **Système ArsenalCoin mis à jour avec succès**\n\n"
                           f"💎 **Statut:** {'🟢 SYSTÈME ACTIVÉ' if enabled else '🔴 SYSTÈME DÉSACTIVÉ'}",
                color=discord.Color.gold() if enabled else discord.Color.red()
            )
            
            embed.add_field(
                name="💳 **Système ArsenalCoin**",
                value=f"Status: {'✅ **ACTIF**' if enabled else '❌ **INACTIF**'}\n"
                      f"Devise: **{config['economy']['currency_symbol']}**\n"
                      f"Mode: **{'Complet' if enabled else 'Désactivé'}**",
                inline=True
            )
            
            embed.add_field(
                name="🎁 **Récompenses**",
                value=f"Quotidien: **{daily_reward} AC**/jour\n"
                      f"Messages: **{message_reward} AC**/msg\n"
                      f"Vocal: **{voice_reward} AC**/min",
                inline=True
            )
            
            embed.add_field(
                name="🛒 **Boutique & Transferts**",
                value=f"Boutique: {'✅ **OUVERTE**' if shop_enabled and enabled else '❌ **FERMÉE**'}\n"
                      f"Transferts: {'✅ **/pay actif**' if shop_enabled and enabled else '❌ **Désactivés**'}\n"
                      f"Casino: {'🎰 **Disponible**' if enabled else '❌ **Fermé**'}",
                inline=True
            )
            
            embed.add_field(
                name="📊 **Limites & Sécurité**",
                value=f"Messages/jour: **{config['economy']['max_daily_messages']}**\n"
                      f"Vocal/jour: **{config['economy']['max_daily_voice']}min**\n"
                      f"Bonus hebdo: **{config['economy']['weekly_bonus']} AC**",
                inline=True
            )
            
            embed.add_field(
                name="🎮 **Commandes Disponibles**",
                value="• `/balance` - Voir son solde\n"
                      "• `/daily` - Récompense quotidienne\n"
                      "• `/shop` - Boutique serveur\n"
                      "• `/pay @user <montant>` - Transférer\n"
                      "• `/leaderboard money` - Classement",
                inline=True
            )
            
            embed.add_field(
                name="💡 **Recommandations**",
                value="• Ajustez les gains selon l'activité\n"
                      "• Surveillez l'inflation ArsenalCoin\n"
                      "• Créez des objets boutique attractifs",
                inline=True
            )
            
            embed.set_footer(text="Arsenal Economy V4.5.1 | Système économique intelligent")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ **Erreur configuration Économie:** ```{e}```", ephemeral=True)

class TempChannelsArsenalModal(discord.ui.Modal):
    """Modal Salons Temporaires Arsenal avec configuration complète"""
    
    def __init__(self, config_system, current_config):
        super().__init__(title="🗣️ Salons Temporaires Arsenal", timeout=300)
        self.config_system = config_system
        self.current_config = current_config
        
        temp_config = current_config.get("temp_channels", {})
        
        self.add_item(discord.ui.TextInput(
            label="🗣️ Activer Salons Temporaires (true/false)",
            placeholder="true = Système ON | false = Système OFF",
            default=str(temp_config.get("enabled", False)).lower(),
            min_length=4,
            max_length=5
        ))
        
        self.add_item(discord.ui.TextInput(
            label="📁 ID Catégorie (optionnel)",
            placeholder="ID de catégorie où créer les salons (laisser vide = auto)",
            default=str(temp_config.get("category", "")) if temp_config.get("category") else "",
            required=False,
            max_length=20
        ))
        
        self.add_item(discord.ui.TextInput(
            label="🏷️ Format nom salon",
            placeholder="Utilisez {user} pour le pseudo. Ex: 🎵 Salon de {user}",
            default=temp_config.get("channel_name", "🎵 {user}'s Channel"),
            max_length=50
        ))
        
        self.add_item(discord.ui.TextInput(
            label="👥 Limite utilisateurs (0 = illimité)",
            placeholder="Nombre max d'utilisateurs par salon temporaire",
            default=str(temp_config.get("user_limit", 0)),
            min_length=1,
            max_length=2
        ))
        
        self.add_item(discord.ui.TextInput(
            label="🗑️ Suppression auto (true/false)",
            placeholder="true = Supprimer quand vide | false = Garder",
            default=str(temp_config.get("auto_delete", True)).lower(),
            min_length=4,
            max_length=5
        ))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            enabled = self.children[0].value.lower() == "true"
            category_id = int(self.children[1].value) if self.children[1].value.strip() else None
            channel_name = self.children[2].value if self.children[2].value else "🎵 {user}'s Channel"
            user_limit = max(0, min(99, int(self.children[3].value)))  # Entre 0 et 99
            auto_delete = self.children[4].value.lower() == "true"
            
            # Validation du nom de salon
            if "{user}" not in channel_name:
                channel_name = f"🎵 {channel_name} - {{user}}"
            
            config = self.config_system.load_config(interaction.guild.id)
            config["temp_channels"] = {
                "enabled": enabled,
                "category": category_id,
                "channel_name": channel_name,
                "user_limit": user_limit,
                "auto_delete": auto_delete,
                "creator_permissions": ["manage_channels", "move_members"],
                "auto_move_creator": True,
                "timeout_empty": 300,  # 5 minutes avant suppression si vide
                "max_channels_per_user": 1,
                "allowed_roles": [],    # Rôles autorisés à créer des salons
                "blacklisted_users": []  # Utilisateurs bannis du système
            }
            
            self.config_system.save_config(interaction.guild.id, config)
            
            embed = discord.Embed(
                title="🗣️ **Salons Temporaires Arsenal Configurés !**",
                description="🎵 **Système de salons vocaux temporaires mis à jour**\n\n"
                           f"🎯 **Statut:** {'🟢 SYSTÈME ACTIVÉ' if enabled else '🔴 SYSTÈME DÉSACTIVÉ'}",
                color=discord.Color.purple() if enabled else discord.Color.red()
            )
            
            embed.add_field(
                name="📢 **Système Temp Channels**",
                value=f"Status: {'✅ **ACTIF**' if enabled else '❌ **INACTIF**'}\n"
                      f"Mode: **{'Automatique' if enabled else 'Désactivé'}**\n"
                      f"Max/user: **{config['temp_channels']['max_channels_per_user']}**",
                inline=True
            )
            
            embed.add_field(
                name="📁 **Localisation**",
                value=f"Catégorie: {f'<#{category_id}>' if category_id else '🏠 **Auto-détection**'}\n"
                      f"Timeout: **{config['temp_channels']['timeout_empty']}s**\n"
                      f"Permissions: **Automatiques**",
                inline=True
            )
            
            embed.add_field(
                name="🏷️ **Nom des Salons**",
                value=f"Format: `{channel_name}`\n"
                      f"Exemple: `{channel_name.replace('{user}', 'XeRoX')}`\n"
                      f"Variable: **{{user}}** = pseudo",
                inline=True
            )
            
            embed.add_field(
                name="👥 **Paramètres Utilisateurs**",
                value=f"Limite: {f'**{user_limit}** utilisateurs' if user_limit > 0 else '♾️ **Illimité**'}\n"
                      f"Créateur: **Propriétaire auto**\n"
                      f"Déplacement: **Automatique**",
                inline=True
            )
            
            embed.add_field(
                name="🗑️ **Gestion Automatique**",
                value=f"Suppression: {'✅ **Auto-nettoyage**' if auto_delete else '❌ **Manuel**'}\n"
                      f"Vide depuis: **5 minutes**\n"
                      f"Nettoyage: **Intelligent**",
                inline=True
            )
            
            embed.add_field(
                name="💡 **Comment utiliser**",
                value="1️⃣ Rejoindre un salon marqué 🔗\n"
                      "2️⃣ Un salon personnel se crée\n"
                      "3️⃣ Vous êtes automatiquement propriétaire\n"
                      "4️⃣ Salon supprimé quand vide",
                inline=True
            )
            
            embed.set_footer(text="Arsenal Temp Channels V4.5.1 | Système intelligent activé")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ **Erreur configuration Salons Temp:** ```{e}```", ephemeral=True)

# ===== VUE PRINCIPALE AVEC BOUTONS =====

class ArsenalConfigModalView(discord.ui.View):
    """Vue principale Arsenal avec boutons modals"""
    
    def __init__(self, config_system):
        super().__init__(timeout=300)
        self.config_system = config_system

    @discord.ui.button(label="🛡️ AutoMod", style=discord.ButtonStyle.red, row=0)
    async def automod_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = self.config_system.load_config(interaction.guild.id)
        modal = AutoModArsenalModal(self.config_system, config)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="💰 ArsenalCoin", style=discord.ButtonStyle.green, row=0)
    async def economy_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = self.config_system.load_config(interaction.guild.id)
        modal = EconomyArsenalModal(self.config_system, config)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🗣️ Salons Temp", style=discord.ButtonStyle.blurple, row=0)
    async def temp_channels_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = self.config_system.load_config(interaction.guild.id)
        modal = TempChannelsArsenalModal(self.config_system, config)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="📊 Voir Config", style=discord.ButtonStyle.gray, row=1)
    async def view_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = self.config_system.load_config(interaction.guild.id)
        
        embed = discord.Embed(
            title="📊 **Configuration Arsenal - Vue d'Ensemble**",
            description=f"🏠 **Serveur:** {interaction.guild.name}\n"
                       "📋 **Récapitulatif complet de votre configuration**",
            color=discord.Color.blue()
        )
        
        # AutoMod
        automod = config.get("automod", {})
        automod_status = "🟢 ACTIVÉ" if automod.get("enabled") else "🔴 DÉSACTIVÉ"
        embed.add_field(
            name="🛡️ AutoMod Arsenal",
            value=f"**Statut:** {automod_status}\n"
                  f"**Anti-spam:** {automod.get('anti_spam', {}).get('max_messages', 5)} msg/{automod.get('anti_spam', {}).get('time_window', 10)}s\n"
                  f"**Filtres:** {len(automod.get('filter_words', {}).get('words', []))} mots bloqués\n"
                  f"**Anti-liens:** {'ON' if automod.get('anti_links', {}).get('enabled') else 'OFF'}",
            inline=True
        )
        
        # Économie
        economy = config.get("economy", {})
        economy_status = "🟢 ACTIVÉ" if economy.get("enabled") else "🔴 DÉSACTIVÉ"
        embed.add_field(
            name="💰 Économie Arsenal",
            value=f"**Statut:** {economy_status}\n"
                  f"**Quotidien:** {economy.get('daily_reward', 100)} AC/jour\n"
                  f"**Messages:** {economy.get('message_reward', 5)} AC/msg\n"
                  f"**Vocal:** {economy.get('voice_reward', 10)} AC/min\n"
                  f"**Boutique:** {'OUVERTE' if economy.get('shop_enabled') else 'FERMÉE'}",
            inline=True
        )
        
        # Salons temporaires
        temp = config.get("temp_channels", {})
        temp_status = "🟢 ACTIVÉ" if temp.get("enabled") else "🔴 DÉSACTIVÉ"
        embed.add_field(
            name="🗣️ Salons Temporaires",
            value=f"**Statut:** {temp_status}\n"
                  f"**Format:** `{temp.get('channel_name', 'Non défini')}`\n"
                  f"**Limite:** {temp.get('user_limit', 0) if temp.get('user_limit', 0) > 0 else '♾️ Illimité'}\n"
                  f"**Auto-suppression:** {'ON' if temp.get('auto_delete', True) else 'OFF'}",
            inline=True
        )
        
        # Statistiques
        enabled_systems = sum([
            automod.get("enabled", False),
            economy.get("enabled", True),
            temp.get("enabled", False)
        ])
        
        embed.add_field(
            name="📈 Statistiques Globales",
            value=f"**Systèmes actifs:** {enabled_systems}/3\n"
                  f"**Taux d'activation:** {(enabled_systems/3*100):.0f}%\n"
                  f"**Configuration:** {'✅ Optimale' if enabled_systems >= 2 else '⚠️ Basique'}",
            inline=True
        )
        
        embed.set_footer(text="Arsenal V4.5.1 - Configuration Modal | Cliquez sur les boutons pour modifier")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    """Charge le module Configuration Modal Arsenal"""
    await bot.add_cog(ArsenalConfigSystemModal(bot))
    print("⚙️ [Arsenal Config Modal] Système de configuration moderne avec modals chargé !")
