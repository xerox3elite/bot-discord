#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Arsenal V4 - Système de Configuration avec MODALS
Configuration ultra-moderne avec formulaires interactifs complets
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from typing import Optional, Dict, Any
import asyncio

class ConfigurationSystem(commands.Cog):
    """Système de configuration Arsenal V4 avec modals"""
    
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

    @app_commands.command(name="config", description="⚙️ Configuration complète d'Arsenal Bot")
    async def config_main(self, interaction: discord.Interaction):
        """Menu principal de configuration avec boutons modals"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Permission requise: `Gérer le serveur`", ephemeral=True)
            return

        embed = discord.Embed(
            title="⚙️ **CONFIGURATION ARSENAL BOT**",
            description=f"**Serveur:** {interaction.guild.name}\n\n"
                       "🎮 **Configuration moderne avec formulaires interactifs**\n"
                       "Sélectionnez le système à configurer ci-dessous :",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="🛡️ **AutoMod & Sécurité**",
            value="Anti-spam, filtres, modération automatique",
            inline=True
        )
        
        embed.add_field(
            name="💰 **Économie & Récompenses**", 
            value="ArsenalCoins, boutique, récompenses quotidiennes",
            inline=True
        )
        
        embed.add_field(
            name="📈 **Système de Niveaux**",
            value="XP, niveaux, récompenses de niveaux",
            inline=True
        )
        
        embed.add_field(
            name="🎵 **Système Musical**",
            value="Configuration audio, permissions DJ",
            inline=True
        )
        
        embed.add_field(
            name="🗣️ **Salons Temporaires**",
            value="Salons vocaux automatiques personnalisés",
            inline=True
        )
        
        embed.add_field(
            name="📊 **Système de Logs**",
            value="Logs de modération, messages, activités",
            inline=True
        )

        view = ConfigMainView(self)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# ===== MODALS DE CONFIGURATION =====

class AutoModConfigModal(discord.ui.Modal):
    """Modal de configuration AutoMod"""
    
    def __init__(self, config_system, current_config):
        super().__init__(title="🛡️ Configuration AutoMod", timeout=300)
        self.config_system = config_system
        self.current_config = current_config
        
        # Champs du formulaire
        self.add_item(discord.ui.TextInput(
            label="Activé (true/false)",
            placeholder="true pour activer, false pour désactiver",
            default=str(current_config.get("automod", {}).get("enabled", False)).lower(),
            min_length=4,
            max_length=5
        ))
        
        self.add_item(discord.ui.TextInput(
            label="Messages max anti-spam",
            placeholder="Nombre max de messages par période (ex: 5)",
            default=str(current_config.get("automod", {}).get("anti_spam", {}).get("max_messages", 5)),
            min_length=1,
            max_length=2
        ))
        
        self.add_item(discord.ui.TextInput(
            label="Fenêtre de temps (secondes)",
            placeholder="Durée de la fenêtre anti-spam (ex: 10)",
            default=str(current_config.get("automod", {}).get("anti_spam", {}).get("time_window", 10)),
            min_length=1,
            max_length=3
        ))
        
        self.add_item(discord.ui.TextInput(
            label="Mots filtrés (séparés par ,)",
            placeholder="mot1, mot2, mot3...",
            default=", ".join(current_config.get("automod", {}).get("filter_words", {}).get("words", [])),
            required=False,
            max_length=1000
        ))
        
        self.add_item(discord.ui.TextInput(
            label="Anti-liens (true/false)",
            placeholder="Bloquer les liens externes",
            default=str(current_config.get("automod", {}).get("anti_links", {}).get("enabled", False)).lower(),
            min_length=4,
            max_length=5
        ))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Récupérer les valeurs
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
                title="✅ **AutoMod Configuré !**",
                description="Configuration AutoMod sauvegardée avec succès",
                color=discord.Color.green()
            )
            
            embed.add_field(name="🛡️ Statut", value="Activé" if enabled else "Désactivé", inline=True)
            embed.add_field(name="📨 Anti-spam", value=f"{max_messages} msg/{time_window}s", inline=True)
            embed.add_field(name="🔗 Anti-liens", value="Activé" if anti_links else "Désactivé", inline=True)
            embed.add_field(name="🚫 Mots filtrés", value=f"{len(filter_words)} mot(s)", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur de configuration: {e}", ephemeral=True)

class EconomyConfigModal(discord.ui.Modal):
    """Modal de configuration Économie"""
    
    def __init__(self, config_system, current_config):
        super().__init__(title="💰 Configuration Économie", timeout=300)
        self.config_system = config_system
        self.current_config = current_config
        
        economy_config = current_config.get("economy", {})
        
        self.add_item(discord.ui.TextInput(
            label="Activé (true/false)",
            placeholder="true pour activer le système économique",
            default=str(economy_config.get("enabled", True)).lower(),
            min_length=4,
            max_length=5
        ))
        
        self.add_item(discord.ui.TextInput(
            label="Récompense quotidienne",
            placeholder="ArsenalCoins reçus par jour (ex: 100)",
            default=str(economy_config.get("daily_reward", 100)),
            min_length=1,
            max_length=5
        ))
        
        self.add_item(discord.ui.TextInput(
            label="Récompense par message",
            placeholder="AC par message (ex: 5)",
            default=str(economy_config.get("message_reward", 5)),
            min_length=1,
            max_length=3
        ))
        
        self.add_item(discord.ui.TextInput(
            label="Récompense vocal (par minute)",
            placeholder="AC par minute en vocal (ex: 10)",
            default=str(economy_config.get("voice_reward", 10)),
            min_length=1,
            max_length=3
        ))
        
        self.add_item(discord.ui.TextInput(
            label="Boutique & Transferts (true/false)",
            placeholder="Activer shop et /pay",
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
                title="💰 **Économie Configurée !**",
                description="Système économique Arsenal mis à jour",
                color=discord.Color.gold()
            )
            
            embed.add_field(name="💳 Statut", value="Activé" if enabled else "Désactivé", inline=True)
            embed.add_field(name="🎁 Récompense quotidienne", value=f"{daily_reward} AC", inline=True)
            embed.add_field(name="💬 Par message", value=f"{message_reward} AC", inline=True)
            embed.add_field(name="🎤 Par minute vocal", value=f"{voice_reward} AC", inline=True)
            embed.add_field(name="🛒 Boutique", value="Activée" if shop_enabled else "Désactivée", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur de configuration: {e}", ephemeral=True)

class TempChannelsConfigModal(discord.ui.Modal):
    """Modal de configuration Salons Temporaires"""
    
    def __init__(self, config_system, current_config):
        super().__init__(title="🗣️ Configuration Salons Temporaires", timeout=300)
        self.config_system = config_system
        self.current_config = current_config
        
        temp_config = current_config.get("temp_channels", {})
        
        self.add_item(discord.ui.TextInput(
            label="Activé (true/false)",
            placeholder="true pour activer les salons temporaires",
            default=str(temp_config.get("enabled", False)).lower(),
            min_length=4,
            max_length=5
        ))
        
        self.add_item(discord.ui.TextInput(
            label="ID Catégorie (optionnel)",
            placeholder="ID de la catégorie pour les salons temp",
            default=str(temp_config.get("category", "")) if temp_config.get("category") else "",
            required=False,
            max_length=20
        ))
        
        self.add_item(discord.ui.TextInput(
            label="Format nom salon",
            placeholder="{user} sera remplacé par le pseudo (ex: 🎵 {user}'s Channel)",
            default=temp_config.get("channel_name", "🎵 {user}'s Channel"),
            max_length=50
        ))
        
        self.add_item(discord.ui.TextInput(
            label="Limite utilisateurs (0 = illimité)",
            placeholder="Nombre max d'utilisateurs par salon",
            default=str(temp_config.get("user_limit", 0)),
            min_length=1,
            max_length=2
        ))
        
        self.add_item(discord.ui.TextInput(
            label="Suppression auto (true/false)",
            placeholder="Supprimer le salon quand vide",
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
                description="Configuration des salons vocaux temporaires mise à jour",
                color=discord.Color.purple()
            )
            
            embed.add_field(name="📢 Statut", value="Activé" if enabled else "Désactivé", inline=True)
            embed.add_field(name="📁 Catégorie", value=f"<#{category_id}>" if category_id else "Aucune", inline=True)
            embed.add_field(name="🏷️ Format nom", value=channel_name, inline=True)
            embed.add_field(name="👥 Limite", value=f"{user_limit} utilisateurs" if user_limit > 0 else "Illimité", inline=True)
            embed.add_field(name="🗑️ Suppression auto", value="Activée" if auto_delete else "Désactivée", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur de configuration: {e}", ephemeral=True)

class MusicConfigModal(discord.ui.Modal):
    """Modal de configuration Système Musical"""
    
    def __init__(self, config_system, current_config):
        super().__init__(title="🎵 Configuration Système Musical", timeout=300)
        self.config_system = config_system
        self.current_config = current_config
        
        music_config = current_config.get("music", {})
        
        self.add_item(discord.ui.TextInput(
            label="Activé (true/false)",
            placeholder="true pour activer la musique",
            default=str(music_config.get("enabled", True)).lower(),
            min_length=4,
            max_length=5
        ))
        
        self.add_item(discord.ui.TextInput(
            label="Taille max file d'attente",
            placeholder="Nombre max de musiques en file (ex: 50)",
            default=str(music_config.get("max_queue", 50)),
            min_length=1,
            max_length=3
        ))
        
        self.add_item(discord.ui.TextInput(
            label="Durée max (secondes)",
            placeholder="Durée max par musique (ex: 7200 = 2h)",
            default=str(music_config.get("max_duration", 7200)),
            min_length=1,
            max_length=5
        ))
        
        self.add_item(discord.ui.TextInput(
            label="Volume par défaut (0-100)",
            placeholder="Volume de départ (ex: 50)",
            default=str(music_config.get("default_volume", 50)),
            min_length=1,
            max_length=3
        ))
        
        self.add_item(discord.ui.TextInput(
            label="ID Rôle DJ (optionnel)",
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
            default_volume = max(0, min(100, int(self.children[3].value)))
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
                title="🎵 **Système Musical Configuré !**",
                description="Configuration audio Arsenal mise à jour",
                color=discord.Color.red()
            )
            
            embed.add_field(name="🎶 Statut", value="Activé" if enabled else "Désactivé", inline=True)
            embed.add_field(name="📝 File d'attente max", value=f"{max_queue} musiques", inline=True)
            embed.add_field(name="⏱️ Durée max", value=f"{max_duration//60}min", inline=True)
            embed.add_field(name="🔊 Volume par défaut", value=f"{default_volume}%", inline=True)
            embed.add_field(name="🎧 Rôle DJ", value=f"<@&{dj_role}>" if dj_role else "Aucun", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur de configuration: {e}", ephemeral=True)

# ===== VUE PRINCIPALE =====

class ConfigMainView(discord.ui.View):
    """Vue principale avec boutons pour chaque système"""
    
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
            title="⚙️ **Configuration Actuelle**",
            description=f"**Serveur:** {interaction.guild.name}",
            color=discord.Color.blue()
        )
        
        # AutoMod
        automod = config.get("automod", {})
        embed.add_field(
            name="🛡️ AutoMod",
            value=f"**Statut:** {'✅ Activé' if automod.get('enabled') else '❌ Désactivé'}\n"
                  f"**Anti-spam:** {automod.get('anti_spam', {}).get('max_messages', 5)} msg/{automod.get('anti_spam', {}).get('time_window', 10)}s\n"
                  f"**Mots filtrés:** {len(automod.get('filter_words', {}).get('words', []))}",
            inline=True
        )
        
        # Économie
        economy = config.get("economy", {})
        embed.add_field(
            name="💰 Économie",
            value=f"**Statut:** {'✅ Activé' if economy.get('enabled') else '❌ Désactivé'}\n"
                  f"**Quotidien:** {economy.get('daily_reward', 100)} AC\n"
                  f"**Par message:** {economy.get('message_reward', 5)} AC",
            inline=True
        )
        
        # Musique
        music = config.get("music", {})
        embed.add_field(
            name="🎵 Musique",
            value=f"**Statut:** {'✅ Activé' if music.get('enabled') else '❌ Désactivé'}\n"
                  f"**File max:** {music.get('max_queue', 50)}\n"
                  f"**Volume:** {music.get('default_volume', 50)}%",
            inline=True
        )
        
        # Salons temporaires
        temp = config.get("temp_channels", {})
        embed.add_field(
            name="🗣️ Salons Temp",
            value=f"**Statut:** {'✅ Activé' if temp.get('enabled') else '❌ Désactivé'}\n"
                  f"**Format:** {temp.get('channel_name', 'Non défini')}\n"
                  f"**Limite:** {temp.get('user_limit', 0) if temp.get('user_limit', 0) > 0 else 'Illimité'}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    """Charge le module Configuration"""
    await bot.add_cog(ConfigurationSystem(bot))
    print("⚙️ [Configuration System] Système de configuration avec modals chargé !")
