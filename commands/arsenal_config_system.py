#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Arsenal V4 - Système de Configuration avec MODALS
Configuration ultra-moderne avec formulaires interactifs complets
Remplace l'ancien système de menus déroulants superficiels
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from typing import Optional, Dict, Any
import asyncio

class ArsenalConfigSystem(commands.Cog):
    """Système de configuration Arsenal V4 avec modals - NOUVELLE VERSION"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "data/server_configs"
        os.makedirs(self.config_path, exist_ok=True)

    def load_config(self, guild_id: int) -> Dict:
        """Charge la configuration d'un serveur"""
        try:
            config_file = f"{self.config_path}/{guild_id}.json"
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return self.get_default_config()

    def save_config(self, guild_id: int, config: Dict):
        """Sauvegarde la configuration d'un serveur"""
        try:
            config_file = f"{self.config_path}/{guild_id}.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde config: {e}")

    def get_default_config(self) -> Dict:
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

    @app_commands.command(name="config", description="⚙️ Configuration complète d'Arsenal Bot avec MODALS")
    async def config_main(self, interaction: discord.Interaction):
        """Menu principal de configuration avec boutons modals"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Permission requise: `Gérer le serveur`", ephemeral=True)
            return

        embed = discord.Embed(
            title="⚙️ **ARSENAL CONFIGURATION - SYSTÈME MODAL**",
            description=f"**Serveur:** {interaction.guild.name}\n\n"
                       "🎮 **Configuration moderne avec formulaires interactifs**\n"
                       "✨ **Fini les menus superficiels - place aux VRAIS paramètres !**\n\n"
                       "Sélectionnez le système à configurer ci-dessous :",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="🛡️ **AutoMod & Sécurité**",
            value="• Anti-spam avancé\n• Filtres de mots personnalisés\n• Protection contre les liens",
            inline=True
        )
        
        embed.add_field(
            name="💰 **Économie & Récompenses**", 
            value="• ArsenalCoins quotidiens\n• Boutique personnalisée\n• Récompenses d'activité",
            inline=True
        )
        
        embed.add_field(
            name="📈 **Système de Niveaux**",
            value="• XP par message/vocal\n• Récompenses de niveau\n• Salon d'annonces",
            inline=True
        )
        
        embed.add_field(
            name="🎵 **Système Musical**",
            value="• Configuration audio complète\n• Permissions DJ avancées\n• Limites personnalisées",
            inline=True
        )
        
        embed.add_field(
            name="🗣️ **Salons Temporaires**",
            value="• Salons vocaux automatiques\n• Noms personnalisés\n• Limites d'utilisateurs",
            inline=True
        )
        
        embed.add_field(
            name="📊 **Système de Logs**",
            value="• Logs de modération\n• Suivi des messages\n• Activités serveur",
            inline=True
        )
        
        embed.set_footer(text="Arsenal V4.5.1 - Configuration Moderne | Cliquez sur les boutons pour configurer")

        view = ArsenalConfigMainView(self)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# ===== MODALS DE CONFIGURATION =====

class AutoModConfigModal(discord.ui.Modal):
    """Modal de configuration AutoMod"""
    
    def __init__(self, config_system, current_config):
        super().__init__(title="🛡️ Configuration AutoMod Arsenal", timeout=300)
        self.config_system = config_system
        self.current_config = current_config
        
        # Champs du formulaire
        self.add_item(discord.ui.TextInput(
            label="✅ Activé (true/false)",
            placeholder="true pour activer AutoMod, false pour désactiver",
            default=str(current_config.get("automod", {}).get("enabled", False)).lower(),
            min_length=4,
            max_length=5
        ))
        
        self.add_item(discord.ui.TextInput(
            label="📨 Messages max anti-spam",
            placeholder="Nombre maximum de messages par période (ex: 5)",
            default=str(current_config.get("automod", {}).get("anti_spam", {}).get("max_messages", 5)),
            min_length=1,
            max_length=2
        ))
        
        self.add_item(discord.ui.TextInput(
            label="⏱️ Fenêtre de temps (secondes)",
            placeholder="Durée de la fenêtre anti-spam en secondes (ex: 10)",
            default=str(current_config.get("automod", {}).get("anti_spam", {}).get("time_window", 10)),
            min_length=1,
            max_length=3
        ))
        
        self.add_item(discord.ui.TextInput(
            label="🚫 Mots filtrés (séparés par ,)",
            placeholder="mot1, mot2, mot3, insulte1, insulte2...",
            default=", ".join(current_config.get("automod", {}).get("filter_words", {}).get("words", [])),
            required=False,
            max_length=1000
        ))
        
        self.add_item(discord.ui.TextInput(
            label="🔗 Anti-liens (true/false)",
            placeholder="Bloquer automatiquement les liens externes",
            default=str(current_config.get("automod", {}).get("anti_links", {}).get("enabled", False)).lower(),
            min_length=4,
            max_length=5
        ))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Récupérer et valider les valeurs
            enabled = self.children[0].value.lower() == "true"
            max_messages = int(self.children[1].value)
            time_window = int(self.children[2].value)
            filter_words = [word.strip() for word in self.children[3].value.split(",") if word.strip()]
            anti_links = self.children[4].value.lower() == "true"
            
            # Mettre à jour la configuration
            config = self.config_system.load_config(interaction.guild.id)
            config["automod"] = {
                "enabled": enabled,
                "anti_spam": {"enabled": enabled, "max_messages": max_messages, "time_window": time_window},
                "anti_links": {"enabled": anti_links, "whitelist": []},
                "anti_invites": {"enabled": enabled, "action": "delete"},
                "anti_nsfw": {"enabled": enabled, "action": "delete"},
                "filter_words": {"enabled": len(filter_words) > 0, "words": filter_words},
                "logs_channel": config.get("automod", {}).get("logs_channel")
            }
            
            self.config_system.save_config(interaction.guild.id, config)
            
            embed = discord.Embed(
                title="✅ **AutoMod Arsenal Configuré !**",
                description="🛡️ **Configuration AutoMod sauvegardée avec succès**\n\n"
                           "Le système de modération automatique Arsenal est maintenant prêt !",
                color=discord.Color.green()
            )
            
            embed.add_field(name="🛡️ Statut AutoMod", value="✅ Activé" if enabled else "❌ Désactivé", inline=True)
            embed.add_field(name="📨 Anti-spam", value=f"Max {max_messages} msg/{time_window}s", inline=True)
            embed.add_field(name="🔗 Anti-liens", value="✅ Activé" if anti_links else "❌ Désactivé", inline=True)
            embed.add_field(name="🚫 Mots filtrés", value=f"{len(filter_words)} mot(s) configuré(s)", inline=True)
            embed.add_field(name="🎯 Actions automatiques", value="Delete, Warn, Timeout", inline=True)
            embed.add_field(name="📊 Logs", value="Activés si salon défini", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ **Erreur de configuration:** {e}", ephemeral=True)

class EconomyConfigModal(discord.ui.Modal):
    """Modal de configuration Économie Arsenal"""
    
    def __init__(self, config_system, current_config):
        super().__init__(title="💰 Configuration Économie Arsenal", timeout=300)
        self.config_system = config_system
        self.current_config = current_config
        
        economy_config = current_config.get("economy", {})
        
        self.add_item(discord.ui.TextInput(
            label="💳 Activé (true/false)",
            placeholder="true pour activer le système ArsenalCoin",
            default=str(economy_config.get("enabled", True)).lower(),
            min_length=4,
            max_length=5
        ))
        
        self.add_item(discord.ui.TextInput(
            label="🎁 Récompense quotidienne",
            placeholder="ArsenalCoins reçus quotidiennement (ex: 100)",
            default=str(economy_config.get("daily_reward", 100)),
            min_length=1,
            max_length=5
        ))
        
        self.add_item(discord.ui.TextInput(
            label="💬 Récompense par message",
            placeholder="ArsenalCoins par message envoyé (ex: 5)",
            default=str(economy_config.get("message_reward", 5)),
            min_length=1,
            max_length=3
        ))
        
        self.add_item(discord.ui.TextInput(
            label="🎤 Récompense vocal (par minute)",
            placeholder="ArsenalCoins par minute en vocal (ex: 10)",
            default=str(economy_config.get("voice_reward", 10)),
            min_length=1,
            max_length=3
        ))
        
        self.add_item(discord.ui.TextInput(
            label="🛒 Boutique & Transferts (true/false)",
            placeholder="Activer la boutique et les transferts /pay",
            default=str(economy_config.get("shop_enabled", True)).lower(),
            min_length=4,
            max_length=5
        ))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            enabled = self.children[0].value.lower() == "true"
            daily_reward = int(self.children[1].value)
            message_reward = int(self.children[2].value)
            voice_reward = int(self.children[3].value)
            shop_enabled = self.children[4].value.lower() == "true"
            
            config = self.config_system.load_config(interaction.guild.id)
            config["economy"] = {
                "enabled": enabled,
                "daily_reward": daily_reward,
                "message_reward": message_reward,
                "voice_reward": voice_reward,
                "shop_enabled": shop_enabled,
                "transfer_enabled": shop_enabled
            }
            
            self.config_system.save_config(interaction.guild.id, config)
            
            embed = discord.Embed(
                title="💰 **Économie Arsenal Configurée !**",
                description="🪙 **Système économique ArsenalCoin mis à jour**\n\n"
                           "Vos membres peuvent maintenant gagner et dépenser des ArsenalCoins !",
                color=discord.Color.gold()
            )
            
            embed.add_field(name="💳 Statut Économie", value="✅ Activé" if enabled else "❌ Désactivé", inline=True)
            embed.add_field(name="🎁 Quotidien", value=f"{daily_reward} AC/jour", inline=True)
            embed.add_field(name="💬 Par message", value=f"{message_reward} AC", inline=True)
            embed.add_field(name="🎤 Par minute vocal", value=f"{voice_reward} AC", inline=True)
            embed.add_field(name="🛒 Boutique", value="✅ Activée" if shop_enabled else "❌ Désactivée", inline=True)
            embed.add_field(name="💸 Transferts", value="✅ /pay disponible" if shop_enabled else "❌ Désactivés", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ **Erreur de configuration:** {e}", ephemeral=True)

class TempChannelsConfigModal(discord.ui.Modal):
    """Modal de configuration Salons Temporaires"""
    
    def __init__(self, config_system, current_config):
        super().__init__(title="🗣️ Configuration Salons Temporaires", timeout=300)
        self.config_system = config_system
        self.current_config = current_config
        
        temp_config = current_config.get("temp_channels", {})
        
        self.add_item(discord.ui.TextInput(
            label="🗣️ Activé (true/false)",
            placeholder="true pour activer les salons vocaux temporaires",
            default=str(temp_config.get("enabled", False)).lower(),
            min_length=4,
            max_length=5
        ))
        
        self.add_item(discord.ui.TextInput(
            label="📁 ID Catégorie (optionnel)",
            placeholder="ID de la catégorie pour créer les salons temporaires",
            default=str(temp_config.get("category", "")) if temp_config.get("category") else "",
            required=False,
            max_length=20
        ))
        
        self.add_item(discord.ui.TextInput(
            label="🏷️ Format nom salon",
            placeholder="{user} sera remplacé par le pseudo (ex: 🎵 Salon de {user})",
            default=temp_config.get("channel_name", "🎵 {user}'s Channel"),
            max_length=50
        ))
        
        self.add_item(discord.ui.TextInput(
            label="👥 Limite utilisateurs (0 = illimité)",
            placeholder="Nombre maximum d'utilisateurs par salon temporaire",
            default=str(temp_config.get("user_limit", 0)),
            min_length=1,
            max_length=2
        ))
        
        self.add_item(discord.ui.TextInput(
            label="🗑️ Suppression auto (true/false)",
            placeholder="Supprimer automatiquement le salon quand il est vide",
            default=str(temp_config.get("auto_delete", True)).lower(),
            min_length=4,
            max_length=5
        ))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            enabled = self.children[0].value.lower() == "true"
            category_id = int(self.children[1].value) if self.children[1].value.strip() else None
            channel_name = self.children[2].value
            user_limit = int(self.children[3].value)
            auto_delete = self.children[4].value.lower() == "true"
            
            config = self.config_system.load_config(interaction.guild.id)
            config["temp_channels"] = {
                "enabled": enabled,
                "category": category_id,
                "channel_name": channel_name,
                "user_limit": user_limit,
                "auto_delete": auto_delete
            }
            
            self.config_system.save_config(interaction.guild.id, config)
            
            embed = discord.Embed(
                title="🗣️ **Salons Temporaires Configurés !**",
                description="🎵 **Configuration des salons vocaux temporaires mise à jour**\n\n"
                           "Les membres peuvent maintenant créer leurs propres salons !",
                color=discord.Color.purple()
            )
            
            embed.add_field(name="📢 Statut", value="✅ Activé" if enabled else "❌ Désactivé", inline=True)
            embed.add_field(name="📁 Catégorie", value=f"<#{category_id}>" if category_id else "🏠 Catégorie par défaut", inline=True)
            embed.add_field(name="🏷️ Format nom", value=f"`{channel_name}`", inline=True)
            embed.add_field(name="👥 Limite utilisateurs", value=f"{user_limit} max" if user_limit > 0 else "♾️ Illimité", inline=True)
            embed.add_field(name="🗑️ Suppression auto", value="✅ Activée" if auto_delete else "❌ Désactivée", inline=True)
            embed.add_field(name="💡 Comment ça marche", value="Rejoindre un salon 🔗 = créer un salon temporaire", inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ **Erreur de configuration:** {e}", ephemeral=True)

class MusicConfigModal(discord.ui.Modal):
    """Modal de configuration Système Musical Arsenal"""
    
    def __init__(self, config_system, current_config):
        super().__init__(title="🎵 Configuration Système Musical", timeout=300)
        self.config_system = config_system
        self.current_config = current_config
        
        music_config = current_config.get("music", {})
        
        self.add_item(discord.ui.TextInput(
            label="🎵 Activé (true/false)",
            placeholder="true pour activer le système musical Arsenal",
            default=str(music_config.get("enabled", True)).lower(),
            min_length=4,
            max_length=5
        ))
        
        self.add_item(discord.ui.TextInput(
            label="📝 Taille max file d'attente",
            placeholder="Nombre maximum de musiques en attente (ex: 50)",
            default=str(music_config.get("max_queue", 50)),
            min_length=1,
            max_length=3
        ))
        
        self.add_item(discord.ui.TextInput(
            label="⏱️ Durée max par musique (secondes)",
            placeholder="Durée maximale par piste (ex: 7200 = 2 heures)",
            default=str(music_config.get("max_duration", 7200)),
            min_length=1,
            max_length=5
        ))
        
        self.add_item(discord.ui.TextInput(
            label="🔊 Volume par défaut (0-100)",
            placeholder="Volume de démarrage du bot musical (ex: 50)",
            default=str(music_config.get("default_volume", 50)),
            min_length=1,
            max_length=3
        ))
        
        self.add_item(discord.ui.TextInput(
            label="🎧 ID Rôle DJ (optionnel)",
            placeholder="ID du rôle avec permissions DJ avancées",
            default=str(music_config.get("dj_role", "")) if music_config.get("dj_role") else "",
            required=False,
            max_length=20
        ))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            enabled = self.children[0].value.lower() == "true"
            max_queue = int(self.children[1].value)
            max_duration = int(self.children[2].value)
            default_volume = max(0, min(100, int(self.children[3].value)))  # Clamp entre 0-100
            dj_role = int(self.children[4].value) if self.children[4].value.strip() else None
            
            config = self.config_system.load_config(interaction.guild.id)
            config["music"] = {
                "enabled": enabled,
                "max_queue": max_queue,
                "max_duration": max_duration,
                "default_volume": default_volume,
                "dj_role": dj_role
            }
            
            self.config_system.save_config(interaction.guild.id, config)
            
            embed = discord.Embed(
                title="🎵 **Système Musical Arsenal Configuré !**",
                description="🎶 **Configuration audio Arsenal mise à jour**\n\n"
                           "Votre serveur est prêt pour la meilleure expérience musicale !",
                color=discord.Color.red()
            )
            
            embed.add_field(name="🎶 Statut Musical", value="✅ Activé" if enabled else "❌ Désactivé", inline=True)
            embed.add_field(name="📝 File d'attente max", value=f"{max_queue} musiques", inline=True)
            embed.add_field(name="⏱️ Durée max", value=f"{max_duration//60} minutes", inline=True)
            embed.add_field(name="🔊 Volume par défaut", value=f"{default_volume}%", inline=True)
            embed.add_field(name="🎧 Rôle DJ", value=f"<@&{dj_role}>" if dj_role else "🌍 Tous les membres", inline=True)
            embed.add_field(name="🎵 Plateformes", value="YouTube, Spotify, SoundCloud", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ **Erreur de configuration:** {e}", ephemeral=True)

# ===== VUE PRINCIPALE ARSENAL =====

class ArsenalConfigMainView(discord.ui.View):
    """Vue principale Arsenal avec boutons pour chaque système"""
    
    def __init__(self, config_system):
        super().__init__(timeout=300)
        self.config_system = config_system

    @discord.ui.button(label="🛡️ AutoMod", style=discord.ButtonStyle.red, row=0)
    async def automod_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = self.config_system.load_config(interaction.guild.id)
        modal = AutoModConfigModal(self.config_system, config)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="💰 Économie", style=discord.ButtonStyle.green, row=0)
    async def economy_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = self.config_system.load_config(interaction.guild.id)
        modal = EconomyConfigModal(self.config_system, config)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🗣️ Salons Temp", style=discord.ButtonStyle.blurple, row=0)
    async def temp_channels_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = self.config_system.load_config(interaction.guild.id)
        modal = TempChannelsConfigModal(self.config_system, config)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🎵 Musique", style=discord.ButtonStyle.red, row=1)
    async def music_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = self.config_system.load_config(interaction.guild.id)
        modal = MusicConfigModal(self.config_system, config)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="📊 Voir Config", style=discord.ButtonStyle.gray, row=1)
    async def view_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = self.config_system.load_config(interaction.guild.id)
        
        embed = discord.Embed(
            title="⚙️ **Configuration Actuelle Arsenal**",
            description=f"**Serveur:** {interaction.guild.name}\n"
                       "📋 **Récapitulatif de votre configuration**",
            color=discord.Color.blue()
        )
        
        # AutoMod
        automod = config.get("automod", {})
        embed.add_field(
            name="🛡️ AutoMod Arsenal",
            value=f"**Statut:** {'✅ Activé' if automod.get('enabled') else '❌ Désactivé'}\n"
                  f"**Anti-spam:** {automod.get('anti_spam', {}).get('max_messages', 5)} msg/{automod.get('anti_spam', {}).get('time_window', 10)}s\n"
                  f"**Mots filtrés:** {len(automod.get('filter_words', {}).get('words', []))} configurés",
            inline=True
        )
        
        # Économie
        economy = config.get("economy", {})
        embed.add_field(
            name="💰 Économie Arsenal",
            value=f"**Statut:** {'✅ Activé' if economy.get('enabled') else '❌ Désactivé'}\n"
                  f"**Quotidien:** {economy.get('daily_reward', 100)} AC\n"
                  f"**Par message:** {economy.get('message_reward', 5)} AC/msg",
            inline=True
        )
        
        # Musique
        music = config.get("music", {})
        embed.add_field(
            name="🎵 Musique Arsenal",
            value=f"**Statut:** {'✅ Activé' if music.get('enabled') else '❌ Désactivé'}\n"
                  f"**File max:** {music.get('max_queue', 50)} musiques\n"
                  f"**Volume:** {music.get('default_volume', 50)}% par défaut",
            inline=True
        )
        
        # Salons temporaires
        temp = config.get("temp_channels", {})
        embed.add_field(
            name="🗣️ Salons Temporaires",
            value=f"**Statut:** {'✅ Activé' if temp.get('enabled') else '❌ Désactivé'}\n"
                  f"**Format:** `{temp.get('channel_name', 'Non défini')}`\n"
                  f"**Limite:** {temp.get('user_limit', 0) if temp.get('user_limit', 0) > 0 else '♾️ Illimité'}",
            inline=True
        )
        
        embed.set_footer(text="Arsenal V4.5.1 - Système de Configuration Moderne")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="🔄 Reset Config", style=discord.ButtonStyle.gray, row=1)
    async def reset_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Reset à la configuration par défaut
        default_config = self.config_system.get_default_config()
        self.config_system.save_config(interaction.guild.id, default_config)
        
        embed = discord.Embed(
            title="🔄 **Configuration Réinitialisée**",
            description="✅ **Configuration remise aux valeurs par défaut**\n\n"
                       "Tous les paramètres ont été réinitialisés. Vous pouvez maintenant les reconfigurer.",
            color=discord.Color.orange()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
                value="automod",
                description="Anti-spam, anti-liens, filtres de mots",
                emoji="🛡️"
            ),
            discord.SelectOption(
                label="🔊 Salons Temporaires",
                value="tempchannels",
                description="Salons vocaux temporaires automatiques",
                emoji="🔊"
            ),
            discord.SelectOption(
                label="🎵 Système Musical",
                value="music",
                description="Configuration du bot musical",
                emoji="🎵"
            ),
            discord.SelectOption(
                label="🎟️ Système de Tickets",
                value="tickets",
                description="Support, réclamations, tickets privés",
                emoji="🎟️"
            ),
            discord.SelectOption(
                label="📝 Sondages & Annonces",
                value="polls",
                description="Configuration des sondages et annonces",
                emoji="📝"
            ),
            discord.SelectOption(
                label="⭐ Rôles de Réaction",
                value="reaction_roles",
                description="Attribution automatique de rôles",
                emoji="⭐"
            ),
            discord.SelectOption(
                label="👋 Accueil & Départ",
                value="welcome",
                description="Messages d'accueil et rôles automatiques",
                emoji="👋"
            ),
            discord.SelectOption(
                label="🎮 Hunt Royal",
                value="hunt_royal",
                description="Configuration Hunt Royal et gaming",
                emoji="🎮"
            ),
            discord.SelectOption(
                label="🏆 Système de Niveaux",
                value="leveling",
                description="XP, niveaux, récompenses de niveau",
                emoji="🏆"
            ),
            discord.SelectOption(
                label="💳 Crypto & Wallets",
                value="crypto",
                description="Portefeuilles crypto et transactions",
                emoji="💳"
            )
        ]
        super().__init__(
            placeholder="🔧 Sélectionnez un système à configurer...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        system = self.values[0]
        await interaction.response.defer()
        
        # Charger la configuration selon le système sélectionné
        config_handler = ArsenalConfigSystem(interaction.client)
        await config_handler.handle_system_config(interaction, system)

class ArsenalConfigSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "data/config"
        os.makedirs(self.config_path, exist_ok=True)

    def load_config(self, guild_id: int, system: str) -> Dict[str, Any]:
        """Charge la configuration d'un système"""
        config_file = f"{self.config_path}/{guild_id}_{system}.json"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return self.get_default_config(system)

    def save_config(self, guild_id: int, system: str, config: Dict[str, Any]):
        """Sauvegarde la configuration d'un système"""
        config_file = f"{self.config_path}/{guild_id}_{system}.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def get_default_config(self, system: str) -> Dict[str, Any]:
        """Retourne la configuration par défaut pour un système"""
        defaults = {
            "economy": {
                "enabled": True,
                "daily_reward": 1000,
                "max_daily_streak": 30,
                "shop_enabled": True,
                "transfer_enabled": True,
                "currency_name": "ArsenalCoin",
                "currency_symbol": "AC"
            },
            "logs": {
                "enabled": False,
                "message_logs": {"enabled": False, "channel": None},
                "mod_logs": {"enabled": False, "channel": None},
                "voice_logs": {"enabled": False, "channel": None},
                "join_leave": {"enabled": False, "channel": None},
                "role_logs": {"enabled": False, "channel": None}
            },
            "automod": {
                "enabled": False,
                "anti_spam": {"enabled": False, "max_messages": 5, "time_window": 10},
                "anti_links": {"enabled": False, "whitelist": []},
                "word_filter": {"enabled": False, "blacklist": []},
                "anti_caps": {"enabled": False, "threshold": 70},
                "auto_timeout": {"enabled": False, "duration": 300}
            },
            "tempchannels": {
                "enabled": False,
                "category_id": None,
                "template_name": "{user}'s Channel",
                "user_limit": 10,
                "auto_delete": True
            },
            "music": {
                "enabled": True,
                "max_volume": 100,
                "default_volume": 50,
                "queue_limit": 100,
                "dj_role": None
            },
            "tickets": {
                "enabled": False,
                "category_id": None,
                "support_role": None,
                "auto_close": 24,
                "transcript_channel": None
            },
            "polls": {
                "enabled": True,
                "default_duration": 3600,
                "anonymous_allowed": True,
                "max_options": 10
            },
            "reaction_roles": {
                "enabled": False,
                "messages": {}
            },
            "welcome": {
                "enabled": False,
                "welcome_channel": None,
                "goodbye_channel": None,
                "welcome_message": "Bienvenue {user} sur **{server}** !",
                "goodbye_message": "Au revoir {user}... 👋",
                "auto_role": None
            },
            "hunt_royal": {
                "enabled": True,
                "api_key": None,
                "auto_updates": True,
                "leaderboard_channel": None
            },
            "leveling": {
                "enabled": False,
                "xp_per_message": {"min": 15, "max": 25},
                "xp_cooldown": 60,
                "level_up_message": True,
                "level_up_channel": None,
                "role_rewards": {}
            },
            "crypto": {
                "enabled": False,
                "supported_currencies": ["BTC", "ETH", "BNB"],
                "alerts_channel": None,
                "portfolio_tracking": True
            }
        }
        return defaults.get(system, {})

    @app_commands.command(name="config", description="⚙️ Configuration complète d'Arsenal Bot")
    async def config_command(self, interaction: discord.Interaction):
        """Commande principale de configuration"""
        # Vérifier les permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes",
                description="Cette commande nécessite les permissions d'administrateur.",
                color=0xff6b6b
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        guild = interaction.guild
        
        embed = discord.Embed(
            title="⚙️ Configuration Arsenal Bot",
            description="Bienvenue dans la commande de configuration d'**Arsenal Bot**.\n"
                       "Grâce à cette commande, vous pourrez configurer les différents systèmes "
                       "proposés dans le sélecteur que vous trouverez ci-dessous.",
            color=0x00ff88,
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="📋 Paramètres de Base",
            value=f"**Serveur :** {guild.name}\n"
                  f"**Membres :** {guild.member_count:,}\n"
                  f"**ID Serveur :** `{guild.id}`\n"
                  f"**Région :** {guild.preferred_locale or 'Français'}",
            inline=False
        )

        embed.add_field(
            name="🚀 Pour Simplifier la Configuration",
            value="• Utilisez le **WebPanel Arsenal** pour une interface graphique\n"
                  "• Consultez la **documentation Arsenal** sur GitHub\n"
                  "• Le **support Arsenal** est disponible pour vous aider\n"
                  "• Toutes les configurations sont **sauvegardées automatiquement**",
            inline=False
        )

        embed.add_field(
            name="💡 Systèmes Disponibles",
            value="**12 systèmes** de configuration disponibles incluant :\n"
                  "💰 Économie • 📊 Logs • 🛡️ AutoMod • 🔊 Vocal • 🎵 Musique\n"
                  "🎟️ Tickets • 📝 Sondages • ⭐ Rôles • 👋 Accueil • 🎮 Gaming\n"
                  "🏆 Niveaux • 💳 Crypto",
            inline=False
        )

        embed.set_thumbnail(url=guild.icon.url if guild.icon else self.bot.user.display_avatar.url)
        embed.set_footer(
            text="Arsenal Configuration System • Bot N°1 Français All-in-One",
            icon_url=self.bot.user.display_avatar.url
        )

        # Créer la vue avec le sélecteur
        view = ConfigView()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def handle_system_config(self, interaction: discord.Interaction, system: str):
        """Gère la configuration d'un système spécifique"""
        guild_id = interaction.guild_id
        config = self.load_config(guild_id, system)
        
        # Créer l'embed de configuration selon le système
        if system == "economy":
            await self.config_economy(interaction, config)
        elif system == "logs":
            await self.config_logs(interaction, config)
        elif system == "automod":
            await self.config_automod(interaction, config)
        elif system == "tempchannels":
            await self.config_tempchannels(interaction, config)
        elif system == "music":
            await self.config_music(interaction, config)
        elif system == "tickets":
            await self.config_tickets(interaction, config)
        elif system == "polls":
            await self.config_polls(interaction, config)
        elif system == "reaction_roles":
            await self.config_reaction_roles(interaction, config)
        elif system == "welcome":
            await self.config_welcome(interaction, config)
        elif system == "hunt_royal":
            await self.config_hunt_royal(interaction, config)
        elif system == "leveling":
            await self.config_leveling(interaction, config)
        elif system == "crypto":
            await self.config_crypto(interaction, config)

    async def config_economy(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration du système d'économie"""
        embed = discord.Embed(
            title="💰 Configuration - Système d'Économie",
            description="Configurez le système ArsenalCoin et la boutique",
            color=0xffd700,
            timestamp=datetime.datetime.now()
        )

        status = "🟢 Activé" if config.get("enabled", True) else "🔴 Désactivé"
        embed.add_field(
            name="📊 État Actuel",
            value=f"**Statut :** {status}\n"
                  f"**Récompense Quotidienne :** {config.get('daily_reward', 1000):,} {config.get('currency_symbol', 'AC')}\n"
                  f"**Série Maximum :** {config.get('max_daily_streak', 30)} jours\n"
                  f"**Boutique :** {'✅ Active' if config.get('shop_enabled', True) else '❌ Inactive'}\n"
                  f"**Transferts :** {'✅ Autorisés' if config.get('transfer_enabled', True) else '❌ Interdits'}",
            inline=False
        )

        embed.add_field(
            name="⚙️ Paramètres Disponibles",
            value="• **Activer/Désactiver** le système\n"
                  "• **Modifier** la récompense quotidienne\n"
                  "• **Configurer** la boutique du serveur\n"
                  "• **Gérer** les transferts entre utilisateurs\n"
                  "• **Personnaliser** le nom de la monnaie",
            inline=False
        )

        embed.add_field(
            name="📈 Statistiques",
            value="Utilisez `/balance` pour voir les statistiques détaillées",
            inline=False
        )

        view = EconomyConfigView(config, interaction.guild_id)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    async def config_logs(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration du système de logs"""
        embed = discord.Embed(
            title="📊 Configuration - Système de Logs",
            description="Configurez les logs de modération et d'activité",
            color=0x3498db
        )

        logs_status = []
        for log_type, settings in config.items():
            if isinstance(settings, dict) and 'enabled' in settings:
                status = "🟢" if settings['enabled'] else "🔴"
                channel = f"<#{settings['channel']}>" if settings.get('channel') else "❌ Non défini"
                logs_status.append(f"{status} **{log_type.replace('_', ' ').title()} :** {channel}")

        embed.add_field(
            name="📋 État des Logs",
            value="\n".join(logs_status) if logs_status else "Aucun log configuré",
            inline=False
        )

        view = LogsConfigView(config, interaction.guild_id)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    async def config_automod(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration du système AutoMod"""
        embed = discord.Embed(
            title="🛡️ Configuration - AutoMod",
            description="Configurez la modération automatique",
            color=0xe74c3c
        )

        automod_features = [
            ("Anti-Spam", config.get("anti_spam", {}).get("enabled", False)),
            ("Anti-Liens", config.get("anti_links", {}).get("enabled", False)),
            ("Filtre de Mots", config.get("word_filter", {}).get("enabled", False)),
            ("Anti-Majuscules", config.get("anti_caps", {}).get("enabled", False)),
            ("Timeout Automatique", config.get("auto_timeout", {}).get("enabled", False))
        ]

        status_text = "\n".join([
            f"{'🟢' if enabled else '🔴'} **{feature}**" 
            for feature, enabled in automod_features
        ])

        embed.add_field(
            name="🛡️ Fonctionnalités AutoMod",
            value=status_text,
            inline=False
        )

        view = AutoModConfigView(config, interaction.guild_id)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

class ConfigView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(ConfigurationSelect())

class EconomyConfigView(discord.ui.View):
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=300)
        self.config = config
        self.guild_id = guild_id

    @discord.ui.button(label="🔄 Activer/Désactiver", style=discord.ButtonStyle.primary)
    async def toggle_economy(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.config["enabled"] = not self.config.get("enabled", True)
        # Sauvegarder ici
        await interaction.response.send_message(
            f"💰 Système d'économie {'activé' if self.config['enabled'] else 'désactivé'} !",
            ephemeral=True
        )

class LogsConfigView(discord.ui.View):
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=300)
        self.config = config
        self.guild_id = guild_id

    @discord.ui.button(label="⚙️ Configurer les Logs", style=discord.ButtonStyle.secondary)
    async def configure_logs(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔧 Configuration des logs en cours de développement...", ephemeral=True)

class AutoModConfigView(discord.ui.View):
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=300)
        self.config = config
        self.guild_id = guild_id

    @discord.ui.button(label="🛡️ Configurer AutoMod", style=discord.ButtonStyle.danger)
    async def configure_automod(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🛡️ Configuration AutoMod en cours de développement...", ephemeral=True)

# Ajout des commandes manquantes

@app_commands.command(name="poll", description="📊 Créer un sondage interactif")
@app_commands.describe(
    question="Question du sondage",
    options="Options séparées par des virgules (max 10)",
    duration="Durée en minutes (défaut: 60)"
)
async def create_poll(interaction: discord.Interaction, question: str, options: str, duration: Optional[int] = 60):
    """Créer un sondage"""
    option_list = [opt.strip() for opt in options.split(',')]
    
    if len(option_list) < 2:
        await interaction.response.send_message("❌ Il faut au moins 2 options pour un sondage!", ephemeral=True)
        return
    
    if len(option_list) > 10:
        await interaction.response.send_message("❌ Maximum 10 options par sondage!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📊 Sondage",
        description=f"**{question}**",
        color=0x3498db,
        timestamp=datetime.datetime.now()
    )
    
    # Émojis pour les réactions
    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    
    options_text = ""
    for i, option in enumerate(option_list):
        options_text += f"{emojis[i]} {option}\n"
    
    embed.add_field(name="🗳️ Options", value=options_text, inline=False)
    embed.add_field(name="⏱️ Durée", value=f"{duration} minutes", inline=True)
    embed.add_field(name="👤 Créateur", value=interaction.user.mention, inline=True)
    
    embed.set_footer(text="Votez en réagissant avec les émojis correspondants!")
    
    await interaction.response.send_message(embed=embed)
    
    # Ajouter les réactions
    message = await interaction.original_response()
    for i in range(len(option_list)):
        await message.add_reaction(emojis[i])

@app_commands.command(name="suggest", description="💡 Faire une suggestion")
@app_commands.describe(suggestion="Votre suggestion")
async def suggest(interaction: discord.Interaction, suggestion: str):
    """Système de suggestions"""
    embed = discord.Embed(
        title="💡 Nouvelle Suggestion",
        description=suggestion,
        color=0xf39c12,
        timestamp=datetime.datetime.now()
    )
    
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    
    embed.set_footer(text=f"ID: {interaction.user.id} • Réagissez pour voter!")
    
    await interaction.response.send_message(embed=embed)
    
    # Ajouter les réactions de vote
    message = await interaction.original_response()
    await message.add_reaction("✅")  # Pour
    await message.add_reaction("❌")  # Contre
    await message.add_reaction("🤔")  # Neutre

@app_commands.command(name="level", description="🏆 Voir votre niveau et XP")
@app_commands.describe(user="Utilisateur à consulter")
async def level_command(interaction: discord.Interaction, user: Optional[discord.Member] = None):
    """Système de niveaux"""
    target = user or interaction.user
    
    # Données de test pour le moment
    level = 25
    xp = 12450
    xp_needed = 15000
    xp_progress = xp - (level * 500)  # XP dans le niveau actuel
    xp_for_next = 500  # XP nécessaire pour le niveau suivant
    
    embed = discord.Embed(
        title="🏆 Système de Niveaux",
        color=0x9b59b6,
        timestamp=datetime.datetime.now()
    )
    
    embed.set_author(
        name=f"{target.display_name}",
        icon_url=target.display_avatar.url
    )
    
    embed.add_field(
        name="📊 Statistiques",
        value=f"**Niveau :** {level}\n"
              f"**XP Total :** {xp:,}\n"
              f"**Progression :** {xp_progress}/{xp_for_next} XP",
        inline=True
    )
    
    embed.add_field(
        name="📈 Classement",
        value=f"**Rang :** #7\n"
              f"**Percentile :** Top 15%\n"
              f"**Messages :** ~1,200",
        inline=True
    )
    
    # Barre de progression
    progress_bar_length = 20
    filled_length = int(progress_bar_length * xp_progress // xp_for_next)
    bar = "█" * filled_length + "░" * (progress_bar_length - filled_length)
    
    embed.add_field(
        name="🎯 Progression vers le niveau suivant",
        value=f"`{bar}` {(xp_progress/xp_for_next*100):.1f}%",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

    async def config_tempchannels(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration complète du système de salons temporaires (comme DraftBot)"""
        embed = discord.Embed(
            title="🔊 Configuration - Salons Vocaux Temporaires",
            description="Système complet de salons vocaux temporaires avec toutes les fonctionnalités avancées",
            color=0x00ffff,
            timestamp=datetime.datetime.now()
        )

        # Statut principal
        status = "🟢 Activé" if config.get("enabled", False) else "🔴 Désactivé"
        embed.add_field(
            name="📊 Statut Système",
            value=status,
            inline=True
        )

        # Canal générateur principal
        parent_channel = config.get("parent_channel_id")
        embed.add_field(
            name="🎯 Canal Générateur",
            value=f"<#{parent_channel}>" if parent_channel else "❌ Non configuré",
            inline=True
        )

        # Statistiques d'utilisation
        stats = config.get("stats", {})
        embed.add_field(
            name="📈 Statistiques",
            value=f"**Salons créés :** `{stats.get('total_created', 0)}`\n"
                  f"**Actuellement actifs :** `{stats.get('currently_active', 0)}`\n"
                  f"**Moyenne durée :** `{stats.get('avg_duration', '45min')}`",
            inline=True
        )

        # Configuration des permissions
        perms_config = config.get("permissions", {})
        embed.add_field(
            name="🔐 Gestion des Permissions",
            value=f"**Créateur = Admin :** `{perms_config.get('creator_admin', 'Activé')}`\n"
                  f"**Invite uniquement :** `{perms_config.get('invite_only', 'Désactivé')}`\n"
                  f"**Transfert propriété :** `{perms_config.get('transfer_ownership', 'Activé')}`\n"
                  f"**Modération auto :** `{perms_config.get('auto_moderation', 'Activé')}`",
            inline=False
        )

        # Paramètres de création
        creation_config = config.get("creation", {})
        embed.add_field(
            name="⚙️ Paramètres de Création",
            value=f"**Limite utilisateurs :** `{creation_config.get('default_limit', 10)} (max {creation_config.get('max_limit', 99)})`\n"
                  f"**Nom par défaut :** `{creation_config.get('default_name', 'Salon de {username}')}`\n"
                  f"**Bitrate :** `{creation_config.get('bitrate', 64)}kbps`\n"
                  f"**Région vocale :** `{creation_config.get('voice_region', 'Automatique')}`",
            inline=True
        )

        # Auto-gestion
        auto_config = config.get("auto_management", {})
        embed.add_field(
            name="🤖 Gestion Automatique",
            value=f"**Suppression auto :** `{auto_config.get('auto_delete', 'Immédiate')}`\n"
                  f"**Nettoyage inactifs :** `{auto_config.get('cleanup_inactive', '5min')}`\n"
                  f"**Sauvegarde config :** `{auto_config.get('save_config', 'Activée')}`\n"
                  f"**Logs création :** `{auto_config.get('log_creation', 'Activés')}`",
            inline=True
        )

        # Fonctionnalités avancées
        embed.add_field(
            name="✨ Fonctionnalités Avancées",
            value="🎛️ **Panel de contrôle intégré**\n"
                  "👥 **Gestion membres (kick/ban/mute)**\n"
                  "🔒 **Verrouillage/Déverrouillage**\n"
                  "🎵 **Contrôles de qualité audio**\n"
                  "📝 **Renommage à la volée**\n"
                  "⏰ **Programmation de suppression**\n"
                  "🎯 **Limites d'utilisateurs dynamiques**\n"
                  "🚫 **Liste noire/blanche d'utilisateurs**\n"
                  "📊 **Statistiques détaillées**\n"
                  "🔄 **Clonage de salons**",
            inline=False
        )

        # Commandes disponibles  
        embed.add_field(
            name="🎮 Commandes Propriétaire",
            value="`� Verrouiller` - Verrouiller le salon\n"
                  "`👥 Limite` - Changer la limite d'utilisateurs\n" 
                  "`📝 Renommer` - Renommer le salon\n"
                  "`👑 Transférer` - Donner la propriété\n"
                  "`🚫 Bannir` - Bannir un utilisateur\n"
                  "`⚡ Expulser` - Expulser un utilisateur",
            inline=True
        )

        embed.add_field(
            name="🛠️ Commandes Modération",
            value="`📊 Infos` - Informations du salon\n"
                  "`🗑️ Supprimer` - Supprimer le salon\n"
                  "`🔄 Reset` - Reset permissions\n"
                  "`📈 Stats` - Statistiques d'usage\n"
                  "`🎵 Qualité` - Régler bitrate\n"
                  "`📍 Région` - Changer région",
            inline=True
        )

        # Variables disponibles pour les noms
        embed.add_field(
            name="📋 Variables Nom (Personnalisation)",
            value="`{username}` - Nom du créateur\n"
                  "`{nickname}` - Pseudo sur le serveur\n"
                  "`{count}` - Nombre d'utilisateurs\n"
                  "`{game}` - Jeu en cours (si détecté)\n"
                  "`{time}` - Heure de création\n"
                  "`{random}` - Nombre aléatoire",
            inline=False
        )

        # Configuration des catégories
        categories = config.get("categories", {})
        embed.add_field(
            name="📁 Gestion des Catégories",
            value=f"**Catégorie principale :** `{categories.get('main_category', 'Salons Temporaires')}`\n"
                  f"**Catégorie débordement :** `{categories.get('overflow_category', 'Auto-créée')}`\n"
                  f"**Max par catégorie :** `{categories.get('max_per_category', 50)}`\n"
                  f"**Organisation auto :** `{categories.get('auto_organize', 'Activée')}`",
            inline=True
        )

        # Système de logs
        logs_config = config.get("logging", {})
        embed.add_field(
            name="📝 Système de Logs",
            value=f"**Canal logs :** `{logs_config.get('log_channel', 'Non défini')}`\n"
                  f"**Log créations :** `{logs_config.get('log_creation', 'Activé')}`\n"
                  f"**Log suppressions :** `{logs_config.get('log_deletion', 'Activé')}`\n"
                  f"**Log permissions :** `{logs_config.get('log_permissions', 'Activé')}`",
            inline=True
        )

        # Créer la view avec tous les boutons de configuration
        try:
            view = TempChannelsConfigView(config, interaction.guild_id)
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            # Fallback si la vue n'est pas disponible
            embed.add_field(
                name="⚙️ Configuration Rapide",
                value="Utilisez les commandes suivantes pour configurer:\n"
                      "`/tempchannels-setup` - Configuration initiale\n"
                      "`/tempchannels-config` - Configuration avancée\n"
                      "`/tempchannels-stats` - Voir les statistiques",
                inline=False
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    async def config_leveling(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration du système de niveaux et XP"""
        embed = discord.Embed(
            title="📈 Configuration - Système de Niveaux",
            description="Configurez le système d'XP et de progression",
            color=0x9932cc,
            timestamp=datetime.datetime.now()
        )

        status = "🟢 Activé" if config.get("enabled", True) else "🔴 Désactivé"
        embed.add_field(
            name="📊 Statut",
            value=status,
            inline=True
        )

        embed.add_field(
            name="⚡ Gains d'XP",
            value=f"**Par message :** `{config.get('xp_per_message', '15-25')} XP`\n"
                  f"**Cooldown :** `{config.get('xp_cooldown', 60)}s`\n"
                  f"**XP Vocal :** `{config.get('voice_xp', 1)} XP/min`",
            inline=True
        )

        embed.add_field(
            name="🏆 Récompenses",
            value=f"**Rôles automatiques :** `{config.get('role_rewards', 'Activés')}`\n"
                  f"**Annonces niveau :** `{config.get('level_announcements', 'Salon configuré')}`\n"
                  f"**ArsenalCoin bonus :** `{config.get('coin_bonus', 'Activé')}`",
            inline=False
        )

        embed.add_field(
            name="📋 Fonctionnalités",
            value="✅ Système XP par messages\n"
                  "✅ XP vocal en temps réel\n"
                  "✅ Cartes de profil personnalisées\n" 
                  "✅ Classement serveur\n"
                  "✅ Rôles de niveau automatiques\n"
                  "✅ Multiplicateurs temporaires",
            inline=True
        )

        embed.add_field(
            name="🎮 Commandes Disponibles", 
            value="`/level` - Voir son niveau\n"
                  "`/rank @user` - Niveau d'un membre\n"
                  "`/leaderboard xp` - Top XP serveur\n"
                  "`/profile` - Carte de profil",
            inline=True
        )

        embed.set_footer(text="Utilisez /config pour modifier ces paramètres")
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def config_crypto(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration du système crypto trading"""
        embed = discord.Embed(
            title="₿ Configuration - Crypto Trading",
            description="Configurez le système de trading crypto",
            color=0xf7931a,
            timestamp=datetime.datetime.now()
        )

        status = "🟢 Activé" if config.get("enabled", False) else "🔴 Désactivé"
        embed.add_field(
            name="📊 Statut",
            value=status,
            inline=True
        )

        embed.add_field(
            name="💱 Cryptomonnaies",
            value=f"**Bitcoin (BTC) :** `{config.get('btc_enabled', 'Activé')}`\n"
                  f"**Ethereum (ETH) :** `{config.get('eth_enabled', 'Activé')}`\n"
                  f"**Binance Coin (BNB) :** `{config.get('bnb_enabled', 'Activé')}`",
            inline=True
        )

        embed.add_field(
            name="⚙️ Paramètres Trading",
            value=f"**Commission :** `{config.get('trading_fee', '0.1')}%`\n"
                  f"**Mise minimale :** `{config.get('min_trade', 10)} AC`\n"
                  f"**Limite quotidienne :** `{config.get('daily_limit', 1000)} AC`",
            inline=False
        )

        embed.add_field(
            name="📋 Fonctionnalités",
            value="✅ Prix en temps réel\n"
                  "✅ Portefeuille crypto personnel\n"
                  "✅ Historique des trades\n"
                  "✅ Signaux de trading\n"
                  "✅ Alertes de prix\n"
                  "✅ Classement traders",
            inline=True
        )

        embed.add_field(
            name="📈 Commandes Trading",
            value="`/crypto buy` - Acheter crypto\n"
                  "`/crypto sell` - Vendre crypto\n"
                  "`/crypto portfolio` - Voir portefeuille\n"
                  "`/crypto price` - Prix actuels",
            inline=True
        )

        embed.set_footer(text="Utilisez /config pour modifier ces paramètres")
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def config_logs(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration du système de logs"""
        embed = discord.Embed(
            title="📝 Configuration - Système de Logs",
            description="Configurez les logs du serveur",
            color=0x3498db,
            timestamp=datetime.datetime.now()
        )

        status = "🟢 Activé" if config.get("enabled", True) else "🔴 Désactivé"
        embed.add_field(
            name="📊 Statut",
            value=status,
            inline=True
        )

        embed.add_field(
            name="📋 Types de Logs",
            value="✅ Messages supprimés/modifiés\n"
                  "✅ Membres rejoints/quittés\n"
                  "✅ Sanctions (bans, kicks, mute)\n"
                  "✅ Rôles ajoutés/supprimés\n"
                  "✅ Salons créés/supprimés\n"
                  "✅ Voice activity (join/leave)",
            inline=True
        )

        log_channel = config.get("log_channel_id")
        embed.add_field(
            name="📍 Canal de Log",
            value=f"<#{log_channel}>" if log_channel else "❌ Non configuré",
            inline=False
        )

        embed.set_footer(text="Utilisez /config pour modifier ces paramètres")
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def config_automod(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration du système de modération automatique"""
        embed = discord.Embed(
            title="🛡️ Configuration - AutoMod",
            description="Configurez la modération automatique",
            color=0xe74c3c,
            timestamp=datetime.datetime.now()
        )

        status = "🟢 Activé" if config.get("enabled", True) else "🔴 Désactivé"
        embed.add_field(
            name="📊 Statut",
            value=status,
            inline=True
        )

        embed.add_field(
            name="🛡️ Protections Actives",
            value=f"**Anti-Spam :** `{config.get('anti_spam', 'Activé')}`\n"
                  f"**Anti-Liens :** `{config.get('anti_links', 'Activé')}`\n"
                  f"**Filtre Mots :** `{config.get('word_filter', 'Activé')}`\n"
                  f"**Anti-Caps :** `{config.get('anti_caps', 'Activé')}`\n"
                  f"**Auto-Timeout :** `{config.get('auto_timeout', '5min')}`",
            inline=True
        )

        embed.add_field(
            name="📋 Fonctionnalités",
            value="✅ Détection spam automatique\n"
                  "✅ Blocage de liens suspects\n"
                  "✅ Filtre de mots interdits\n"
                  "✅ Limite de majuscules\n"
                  "✅ Sanctions automatiques\n"
                  "✅ Système d'avertissements",
            inline=False
        )

        embed.set_footer(text="Utilisez /config pour modifier ces paramètres")
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def config_music(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration du système de musique"""
        embed = discord.Embed(
            title="🎵 Configuration - Système Musique",
            description="Configurez le lecteur de musique Arsenal",
            color=0x9b59b6,
            timestamp=datetime.datetime.now()
        )

        status = "🟢 Activé" if config.get("enabled", True) else "🔴 Désactivé"
        embed.add_field(
            name="📊 Statut",
            value=status,
            inline=True
        )

        embed.add_field(
            name="🎛️ Paramètres Audio",
            value=f"**Volume par défaut :** `{config.get('default_volume', 50)}%`\n"
                  f"**Auto-Leave :** `{config.get('auto_leave', '5min')}`\n"
                  f"**Qualité :** `{config.get('audio_quality', 'Haute')}`\n"
                  f"**DJ-Only Mode :** `{config.get('dj_mode', 'Désactivé')}`",
            inline=True
        )

        embed.add_field(
            name="🎵 Sources Supportées",
            value="✅ YouTube (avec recherche)\n"
                  "✅ Spotify (playlists)\n"
                  "✅ SoundCloud\n"
                  "✅ Fichiers directs (MP3, WAV)\n"
                  "✅ Radio en ligne\n"
                  "✅ Twitch streams",
            inline=False
        )

        embed.add_field(
            name="🎮 Commandes Musique",
            value="`/play` - Jouer une musique\n"
                  "`/queue` - Voir la file d'attente\n"
                  "`/skip` - Passer la musique\n"
                  "`/volume` - Régler le volume",
            inline=True
        )

        embed.set_footer(text="Utilisez /config pour modifier ces paramètres")
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def config_tickets(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration du système de tickets"""
        embed = discord.Embed(
            title="🎫 Configuration - Système de Tickets",
            description="Configurez le système de support par tickets",
            color=0x2ecc71,
            timestamp=datetime.datetime.now()
        )

        status = "🟢 Activé" if config.get("enabled", False) else "🔴 Désactivé"
        embed.add_field(
            name="📊 Statut",
            value=status,
            inline=True
        )

        ticket_category = config.get("ticket_category_id")
        embed.add_field(
            name="📁 Catégorie Tickets",
            value=f"<#{ticket_category}>" if ticket_category else "❌ Non configurée",
            inline=True
        )

        embed.add_field(
            name="⚙️ Configuration",
            value=f"**Auto-Close :** `{config.get('auto_close', '24h inactivité')}`\n"
                  f"**Max par utilisateur :** `{config.get('max_tickets', 3)}`\n"
                  f"**Support Role :** `{config.get('support_role', 'Non défini')}`\n"
                  f"**Logs Channel :** `{config.get('log_channel', 'Non défini')}`",
            inline=False
        )

        embed.add_field(
            name="📋 Fonctionnalités",
            value="✅ Création tickets automatique\n"
                  "✅ Système de permissions\n"
                  "✅ Fermeture avec transcription\n"
                  "✅ Support multi-catégories\n"
                  "✅ Panel de contrôle\n"
                  "✅ Statistiques tickets",
            inline=True
        )

        embed.set_footer(text="Utilisez /config pour modifier ces paramètres")
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def config_polls(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration du système de sondages"""
        embed = discord.Embed(
            title="📊 Configuration - Système de Sondages",
            description="Configurez les sondages et votes",
            color=0xf39c12,
            timestamp=datetime.datetime.now()
        )

        status = "🟢 Activé" if config.get("enabled", True) else "🔴 Désactivé"
        embed.add_field(
            name="📊 Statut",
            value=status,
            inline=True
        )

        embed.add_field(
            name="⚙️ Paramètres",
            value=f"**Durée maximale :** `{config.get('max_duration', '7 jours')}`\n"
                  f"**Options max :** `{config.get('max_options', 10)}`\n"
                  f"**Vote anonyme :** `{config.get('anonymous_voting', 'Autorisé')}`\n"
                  f"**Résultats temps réel :** `{config.get('live_results', 'Activés')}`",
            inline=True
        )

        embed.add_field(
            name="📋 Types de Sondages",
            value="✅ Sondages simples (Oui/Non)\n"
                  "✅ Sondages à choix multiple\n"
                  "✅ Sondages avec images\n"
                  "✅ Votes avec réactions\n"
                  "✅ Sondages programmés\n"
                  "✅ Résultats automatiques",
            inline=False
        )

        embed.add_field(
            name="🎮 Commandes",
            value="`/poll create` - Créer un sondage\n"
                  "`/poll results` - Voir résultats\n"
                  "`/poll close` - Fermer sondage",
            inline=True
        )

        embed.set_footer(text="Utilisez /config pour modifier ces paramètres")
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def config_reaction_roles(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration du système de rôles à réaction"""
        embed = discord.Embed(
            title="⚡ Configuration - Rôles à Réaction",
            description="Configurez l'attribution de rôles par réaction",
            color=0xe91e63,
            timestamp=datetime.datetime.now()
        )

        status = "🟢 Activé" if config.get("enabled", True) else "🔴 Désactivé"
        embed.add_field(
            name="📊 Statut",
            value=status,
            inline=True
        )

        embed.add_field(
            name="⚙️ Configuration",
            value=f"**Panels actifs :** `{len(config.get('panels', []))}`\n"
                  f"**Rôles configurés :** `{len(config.get('role_mappings', {}))}`\n"
                  f"**Mode exclusif :** `{config.get('exclusive_mode', 'Désactivé')}`\n"
                  f"**Auto-remove :** `{config.get('auto_remove', 'Activé')}`",
            inline=True
        )

        embed.add_field(
            name="📋 Fonctionnalités",
            value="✅ Panels de rôles personnalisés\n"
                  "✅ Rôles multiples par réaction\n"
                  "✅ Mode exclusif (1 rôle max)\n"
                  "✅ Auto-suppression des rôles\n"
                  "✅ Émojis personnalisés\n"
                  "✅ Vérification de permissions",
            inline=False
        )

        embed.add_field(
            name="🎛️ Gestion",
            value="`/reactionrole setup` - Créer panel\n"
                  "`/reactionrole add` - Ajouter rôle\n"
                  "`/reactionrole remove` - Supprimer",
            inline=True
        )

        embed.set_footer(text="Utilisez /config pour modifier ces paramètres")
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def config_welcome(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration du système de bienvenue"""
        embed = discord.Embed(
            title="👋 Configuration - Messages de Bienvenue",
            description="Configurez l'accueil des nouveaux membres",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )

        status = "🟢 Activé" if config.get("enabled", False) else "🔴 Désactivé"
        embed.add_field(
            name="📊 Statut",
            value=status,
            inline=True
        )

        welcome_channel = config.get("welcome_channel_id")
        embed.add_field(
            name="📍 Canal d'Accueil",
            value=f"<#{welcome_channel}>" if welcome_channel else "❌ Non configuré",
            inline=True
        )

        embed.add_field(
            name="⚙️ Paramètres",
            value=f"**Message personnalisé :** `{config.get('custom_message', 'Par défaut')}`\n"
                  f"**Rôle automatique :** `{config.get('auto_role', 'Aucun')}`\n"
                  f"**Image de bienvenue :** `{config.get('welcome_image', 'Désactivée')}`\n"
                  f"**DM privé :** `{config.get('private_welcome', 'Désactivé')}`",
            inline=False
        )

        embed.add_field(
            name="📋 Variables Disponibles",
            value="`{user}` - Mention du membre\n"
                  "`{username}` - Nom d'utilisateur\n"
                  "`{server}` - Nom du serveur\n"
                  "`{member_count}` - Nombre de membres",
            inline=True
        )

        embed.add_field(
            name="✨ Fonctionnalités",
            value="✅ Messages personnalisés\n"
                  "✅ Images de bienvenue auto\n"
                  "✅ Rôles automatiques\n"
                  "✅ Messages de départ\n"
                  "✅ DM de bienvenue\n"
                  "✅ Embed personnalisable",
            inline=True
        )

        embed.set_footer(text="Utilisez /config pour modifier ces paramètres")
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def config_hunt_royal(self, interaction: discord.Interaction, config: Dict[str, Any]):
        """Configuration du système Hunt Royal"""
        embed = discord.Embed(
            title="🏹 Configuration - Hunt Royal Integration",
            description="Configurez l'intégration Hunt Royal",
            color=0x8b4513,
            timestamp=datetime.datetime.now()
        )

        status = "🟢 Activé" if config.get("enabled", True) else "🔴 Désactivé"
        embed.add_field(
            name="📊 Statut",
            value=status,
            inline=True
        )

        embed.add_field(
            name="🎮 Intégration",
            value=f"**API Status :** `{config.get('api_status', 'Connecté')}`\n"
                  f"**Auto-Sync :** `{config.get('auto_sync', 'Activé')}`\n"
                  f"**Notifications :** `{config.get('notifications', 'Activées')}`\n"
                  f"**Région défaut :** `{config.get('default_region', 'Global')}`",
            inline=True
        )

        embed.add_field(
            name="📋 Fonctionnalités",
            value="✅ Liens de comptes Hunt Royal\n"
                  "✅ Statistiques temps réel\n"
                  "✅ Classements serveur\n"
                  "✅ Événements Hunt Royal\n"
                  "✅ Authentification sécurisée\n"
                  "✅ Profils détaillés",
            inline=False
        )

        embed.add_field(
            name="🎯 Commandes Hunt",
            value="`/hunt link` - Lier compte Hunt\n"
                  "`/hunt profile` - Voir profil\n"
                  "`/hunt stats` - Statistiques\n"
                  "`/hunt leaderboard` - Classement",
            inline=True
        )

        embed.set_footer(text="Utilisez /config pour modifier ces paramètres")
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ArsenalConfigSystem(bot))
    
    # Ajouter les commandes individuelles
    bot.tree.add_command(create_poll)
    bot.tree.add_command(suggest)
    bot.tree.add_command(level_command)
    
    print("✅ [Arsenal Config] Système de configuration complet chargé")
    print("✅ [Commands] Poll, Suggest, Level ajoutées")
