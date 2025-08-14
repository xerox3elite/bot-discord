"""
🔧 Arsenal Configuration Views
Vues interactives complètes pour tous les modules de configuration
Développé par XeRoX - Arsenal Bot V4.5
"""

import discord
from discord.ext import commands
import json
import os
import datetime
from typing import Dict, Any, Optional, List

class EconomyConfigView(discord.ui.View):
    """Vue de configuration interactive pour le système d'économie"""
    
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=300)
        self.config = config
        self.guild_id = guild_id

    @discord.ui.button(label="🔄 Activer/Désactiver", style=discord.ButtonStyle.primary, row=0)
    async def toggle_economy(self, interaction: discord.Interaction, button):
        """Activer ou désactiver le système économique"""
        self.config["enabled"] = not self.config.get("enabled", True)
        status = "✅ Activé" if self.config["enabled"] else "❌ Désactivé"
        await interaction.response.send_message(f"💰 Système économique : {status}", ephemeral=True)

    @discord.ui.button(label="💎 Récompenses", style=discord.ButtonStyle.secondary, row=0)
    async def configure_rewards(self, interaction: discord.Interaction, button):
        """Configurer les récompenses quotidiennes et hebdomadaires"""
        await interaction.response.send_modal(RewardsConfigModal(self.config))

    @discord.ui.button(label="🎰 Jeux & Casino", style=discord.ButtonStyle.secondary, row=0)
    async def configure_games(self, interaction: discord.Interaction, button):
        """Configurer les jeux et casinos"""
        view = GamesConfigView(self.config)
        await interaction.response.send_message("🎰 Configuration des jeux", view=view, ephemeral=True)

    @discord.ui.button(label="🛒 Boutique", style=discord.ButtonStyle.secondary, row=0)
    async def configure_shop(self, interaction: discord.Interaction, button):
        """Configurer la boutique ArsenalCoin"""
        await interaction.response.send_modal(ShopConfigModal(self.config))

    @discord.ui.button(label="🏦 Taxes & Frais", style=discord.ButtonStyle.secondary, row=1)
    async def configure_taxes(self, interaction: discord.Interaction, button):
        """Configurer les taxes et frais"""
        await interaction.response.send_modal(TaxesConfigModal(self.config))

    @discord.ui.button(label="🔒 Limites", style=discord.ButtonStyle.secondary, row=1)
    async def configure_limits(self, interaction: discord.Interaction, button):
        """Configurer les limites et cooldowns"""
        await interaction.response.send_modal(LimitsConfigModal(self.config))

    @discord.ui.button(label="💾 Sauvegarder", style=discord.ButtonStyle.success, row=1)
    async def save_config(self, interaction: discord.Interaction, button):
        """Sauvegarder la configuration économique"""
        await self.save_economy_config()
        await interaction.response.send_message("✅ Configuration économique sauvegardée!", ephemeral=True)

    async def save_economy_config(self):
        """Sauvegarder la configuration dans un fichier"""
        config_dir = "data/economy"
        os.makedirs(config_dir, exist_ok=True)
        config_file = f"{config_dir}/guild_{self.guild_id}.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

class RewardsConfigModal(discord.ui.Modal):
    """Modal pour configurer les récompenses"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="💎 Configuration Récompenses")
        self.config = config

    daily_reward = discord.ui.TextInput(
        label="Récompense quotidienne",
        placeholder="100",
        required=False,
        max_length=10
    )

    work_min = discord.ui.TextInput(
        label="Work minimum",
        placeholder="50",
        required=False,
        max_length=10
    )

    work_max = discord.ui.TextInput(
        label="Work maximum",
        placeholder="200",
        required=False,
        max_length=10
    )

    weekly_bonus = discord.ui.TextInput(
        label="Bonus hebdomadaire",
        placeholder="500",
        required=False,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.daily_reward.value:
            try:
                self.config["daily_reward"] = int(self.daily_reward.value)
            except ValueError:
                pass

        if self.work_min.value and self.work_max.value:
            try:
                work_min = int(self.work_min.value)
                work_max = int(self.work_max.value)
                if work_min < work_max:
                    self.config["work_reward_range"] = [work_min, work_max]
            except ValueError:
                pass

        if self.weekly_bonus.value:
            try:
                self.config["weekly_bonus"] = int(self.weekly_bonus.value)
            except ValueError:
                pass

        await interaction.response.send_message("✅ Récompenses configurées!", ephemeral=True)

class GamesConfigView(discord.ui.View):
    """Vue pour configurer les jeux"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(timeout=180)
        self.config = config

    @discord.ui.button(label="🪙 Coinflip", style=discord.ButtonStyle.primary)
    async def configure_coinflip(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(CoinflipConfigModal(self.config))

    @discord.ui.button(label="🎰 Slots", style=discord.ButtonStyle.primary)
    async def configure_slots(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(SlotsConfigModal(self.config))

    @discord.ui.button(label="🏆 Jackpot", style=discord.ButtonStyle.success)
    async def configure_jackpot(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(JackpotConfigModal(self.config))

class ShopConfigModal(discord.ui.Modal):
    """Modal pour configurer la boutique"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="🛒 Configuration Boutique")
        self.config = config

    role_price = discord.ui.TextInput(
        label="Prix rôle custom",
        placeholder="5000",
        required=False,
        max_length=10
    )

    vip_price = discord.ui.TextInput(
        label="Prix badge VIP",
        placeholder="10000",
        required=False,
        max_length=10
    )

    boost_price = discord.ui.TextInput(
        label="Prix boost XP",
        placeholder="2500",
        required=False,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.role_price.value:
            try:
                self.config["custom_role_price"] = int(self.role_price.value)
            except ValueError:
                pass

        if self.vip_price.value:
            try:
                self.config["vip_badge_price"] = int(self.vip_price.value)
            except ValueError:
                pass

        if self.boost_price.value:
            try:
                self.config["xp_boost_price"] = int(self.boost_price.value)
            except ValueError:
                pass

        await interaction.response.send_message("✅ Boutique configurée!", ephemeral=True)

class TaxesConfigModal(discord.ui.Modal):
    """Modal pour configurer les taxes"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="🏦 Configuration Taxes")
        self.config = config

    transfer_tax = discord.ui.TextInput(
        label="Taxe transfert (%)",
        placeholder="2",
        required=False,
        max_length=5
    )

    shop_fee = discord.ui.TextInput(
        label="Frais boutique (%)",
        placeholder="1",
        required=False,
        max_length=5
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.transfer_tax.value:
            try:
                tax = float(self.transfer_tax.value)
                if 0 <= tax <= 100:
                    self.config["transfer_tax"] = tax
            except ValueError:
                pass

        if self.shop_fee.value:
            try:
                fee = float(self.shop_fee.value)
                if 0 <= fee <= 100:
                    self.config["shop_fee"] = fee
            except ValueError:
                pass

        await interaction.response.send_message("✅ Taxes configurées!", ephemeral=True)

class LimitsConfigModal(discord.ui.Modal):
    """Modal pour configurer les limites"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="🔒 Configuration Limites")
        self.config = config

    max_transfer = discord.ui.TextInput(
        label="Transfert maximum",
        placeholder="100000",
        required=False,
        max_length=10
    )

    daily_cooldown = discord.ui.TextInput(
        label="Cooldown daily (heures)",
        placeholder="24",
        required=False,
        max_length=3
    )

    work_cooldown = discord.ui.TextInput(
        label="Cooldown work (heures)",
        placeholder="1",
        required=False,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.max_transfer.value:
            try:
                self.config["max_transfer"] = int(self.max_transfer.value)
            except ValueError:
                pass

        if self.daily_cooldown.value:
            try:
                self.config["daily_cooldown"] = int(self.daily_cooldown.value)
            except ValueError:
                pass

        if self.work_cooldown.value:
            try:
                self.config["work_cooldown"] = int(self.work_cooldown.value)
            except ValueError:
                pass

        await interaction.response.send_message("✅ Limites configurées!", ephemeral=True)

# Modals pour les jeux
class CoinflipConfigModal(discord.ui.Modal):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="🪙 Configuration Coinflip")
        self.config = config

    min_bet = discord.ui.TextInput(
        label="Mise minimum",
        placeholder="10",
        required=False,
        max_length=10
    )

    max_bet = discord.ui.TextInput(
        label="Mise maximum",
        placeholder="50000",
        required=False,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.min_bet.value:
            try:
                self.config["coinflip_min"] = int(self.min_bet.value)
            except ValueError:
                pass

        if self.max_bet.value:
            try:
                self.config["coinflip_max"] = int(self.max_bet.value)
            except ValueError:
                pass

        await interaction.response.send_message("✅ Coinflip configuré!", ephemeral=True)

class SlotsConfigModal(discord.ui.Modal):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="🎰 Configuration Slots")
        self.config = config

    multiplier = discord.ui.TextInput(
        label="Multiplicateur de gain",
        placeholder="2",
        required=False,
        max_length=5
    )

    jackpot_chance = discord.ui.TextInput(
        label="Chance jackpot (%)",
        placeholder="1",
        required=False,
        max_length=5
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.multiplier.value:
            try:
                self.config["slots_multiplier"] = float(self.multiplier.value)
            except ValueError:
                pass

        if self.jackpot_chance.value:
            try:
                chance = float(self.jackpot_chance.value)
                if 0 <= chance <= 100:
                    self.config["jackpot_chance"] = chance
            except ValueError:
                pass

        await interaction.response.send_message("✅ Slots configurés!", ephemeral=True)

class JackpotConfigModal(discord.ui.Modal):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="🏆 Configuration Jackpot")
        self.config = config

    jackpot_amount = discord.ui.TextInput(
        label="Montant jackpot",
        placeholder="10000",
        required=False,
        max_length=10
    )

    jackpot_tax = discord.ui.TextInput(
        label="Taxe jackpot (%)",
        placeholder="5",
        required=False,
        max_length=5
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.jackpot_amount.value:
            try:
                self.config["jackpot_amount"] = int(self.jackpot_amount.value)
            except ValueError:
                pass

        if self.jackpot_tax.value:
            try:
                tax = float(self.jackpot_tax.value)
                if 0 <= tax <= 100:
                    self.config["jackpot_tax"] = tax
            except ValueError:
                pass

        await interaction.response.send_message("✅ Jackpot configuré!", ephemeral=True)

# ===========================================
# LEVELING SYSTEM CONFIG
# ===========================================

class LevelingConfigView(discord.ui.View):
    """Vue de configuration pour le système de niveaux"""
    
    def __init__(self, config: Dict[str, Any], guild_id: int):
        super().__init__(timeout=300)
        self.config = config
        self.guild_id = guild_id

    @discord.ui.button(label="🔄 Activer/Désactiver", style=discord.ButtonStyle.primary, row=0)
    async def toggle_leveling(self, interaction: discord.Interaction, button):
        self.config["enabled"] = not self.config.get("enabled", True)
        status = "✅ Activé" if self.config["enabled"] else "❌ Désactivé"
        await interaction.response.send_message(f"📊 Système de niveaux : {status}", ephemeral=True)

    @discord.ui.button(label="⚡ XP & Gains", style=discord.ButtonStyle.secondary, row=0)
    async def configure_xp(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(XPConfigModal(self.config))

    @discord.ui.button(label="🏆 Récompenses", style=discord.ButtonStyle.secondary, row=0)
    async def configure_level_rewards(self, interaction: discord.Interaction, button):
        view = LevelRewardsView(self.config)
        await interaction.response.send_message("🏆 Configuration des récompenses de niveau", view=view, ephemeral=True)

    @discord.ui.button(label="📊 Leaderboard", style=discord.ButtonStyle.secondary, row=0)
    async def configure_leaderboard(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(LeaderboardConfigModal(self.config))

    @discord.ui.button(label="🚫 Exclusions", style=discord.ButtonStyle.danger, row=1)
    async def configure_exclusions(self, interaction: discord.Interaction, button):
        view = ExclusionsView(self.config)
        await interaction.response.send_message("🚫 Configuration des exclusions", view=view, ephemeral=True)

    @discord.ui.button(label="💾 Sauvegarder", style=discord.ButtonStyle.success, row=1)
    async def save_config(self, interaction: discord.Interaction, button):
        await self.save_leveling_config()
        await interaction.response.send_message("✅ Configuration du système de niveaux sauvegardée!", ephemeral=True)

    async def save_leveling_config(self):
        config_dir = "data/leveling"
        os.makedirs(config_dir, exist_ok=True)
        config_file = f"{config_dir}/guild_{self.guild_id}.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

class XPConfigModal(discord.ui.Modal):
    """Modal pour configurer l'XP"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="⚡ Configuration XP")
        self.config = config

    xp_per_message = discord.ui.TextInput(
        label="XP par message",
        placeholder="15",
        required=False,
        max_length=5
    )

    xp_per_minute_voice = discord.ui.TextInput(
        label="XP par minute vocal",
        placeholder="10",
        required=False,
        max_length=5
    )

    cooldown_seconds = discord.ui.TextInput(
        label="Cooldown entre messages (secondes)",
        placeholder="60",
        required=False,
        max_length=5
    )

    multiplier_boost = discord.ui.TextInput(
        label="Multiplicateur boost",
        placeholder="2.0",
        required=False,
        max_length=5
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.xp_per_message.value:
            try:
                self.config["xp_per_message"] = int(self.xp_per_message.value)
            except ValueError:
                pass

        if self.xp_per_minute_voice.value:
            try:
                self.config["xp_per_minute_voice"] = int(self.xp_per_minute_voice.value)
            except ValueError:
                pass

        if self.cooldown_seconds.value:
            try:
                self.config["message_cooldown"] = int(self.cooldown_seconds.value)
            except ValueError:
                pass

        if self.multiplier_boost.value:
            try:
                self.config["boost_multiplier"] = float(self.multiplier_boost.value)
            except ValueError:
                pass

        await interaction.response.send_message("✅ Configuration XP mise à jour!", ephemeral=True)

class LevelRewardsView(discord.ui.View):
    """Vue pour configurer les récompenses de niveau"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(timeout=180)
        self.config = config

    @discord.ui.button(label="🎁 Ajouter Récompense", style=discord.ButtonStyle.success)
    async def add_reward(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(AddLevelRewardModal(self.config))

    @discord.ui.button(label="🗑️ Supprimer Récompense", style=discord.ButtonStyle.danger)
    async def remove_reward(self, interaction: discord.Interaction, button):
        rewards = self.config.get("level_rewards", {})
        if not rewards:
            await interaction.response.send_message("❌ Aucune récompense configurée!", ephemeral=True)
            return
        
        view = RemoveLevelRewardSelect(self.config, rewards)
        await interaction.response.send_message("🗑️ Sélectionnez la récompense à supprimer:", view=view, ephemeral=True)

    @discord.ui.button(label="📋 Voir Récompenses", style=discord.ButtonStyle.secondary)
    async def view_rewards(self, interaction: discord.Interaction, button):
        rewards = self.config.get("level_rewards", {})
        if not rewards:
            await interaction.response.send_message("❌ Aucune récompense configurée!", ephemeral=True)
            return

        embed = discord.Embed(title="🏆 Récompenses de Niveau", color=0xffd700)
        for level, reward_data in sorted(rewards.items(), key=lambda x: int(x[0])):
            reward_type = reward_data.get("type", "unknown")
            reward_value = reward_data.get("value", "N/A")
            
            if reward_type == "role":
                embed.add_field(
                    name=f"Niveau {level}",
                    value=f"🎭 Rôle: <@&{reward_value}>",
                    inline=True
                )
            elif reward_type == "coins":
                embed.add_field(
                    name=f"Niveau {level}",
                    value=f"💰 {reward_value:,} ArsenalCoin",
                    inline=True
                )

        await interaction.response.send_message(embed=embed, ephemeral=True)

class AddLevelRewardModal(discord.ui.Modal):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="🎁 Ajouter Récompense")
        self.config = config

    level = discord.ui.TextInput(
        label="Niveau",
        placeholder="10",
        required=True,
        max_length=3
    )

    reward_type = discord.ui.TextInput(
        label="Type (role/coins)",
        placeholder="role",
        required=True,
        max_length=10
    )

    reward_value = discord.ui.TextInput(
        label="Valeur (ID rôle ou montant)",
        placeholder="123456789012345678",
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            level_num = int(self.level.value)
            reward_type = self.reward_type.value.lower()
            
            if reward_type not in ["role", "coins"]:
                await interaction.response.send_message("❌ Type invalide! Utilisez 'role' ou 'coins'", ephemeral=True)
                return

            if reward_type == "role":
                try:
                    role_id = int(self.reward_value.value)
                    # Vérifier que le rôle existe
                    role = interaction.guild.get_role(role_id)
                    if not role:
                        await interaction.response.send_message("❌ Rôle introuvable!", ephemeral=True)
                        return
                    reward_value = role_id
                except ValueError:
                    await interaction.response.send_message("❌ ID de rôle invalide!", ephemeral=True)
                    return
            else:  # coins
                try:
                    reward_value = int(self.reward_value.value)
                    if reward_value < 0:
                        await interaction.response.send_message("❌ Montant invalide!", ephemeral=True)
                        return
                except ValueError:
                    await interaction.response.send_message("❌ Montant invalide!", ephemeral=True)
                    return

            # Ajouter la récompense
            if "level_rewards" not in self.config:
                self.config["level_rewards"] = {}
                
            self.config["level_rewards"][str(level_num)] = {
                "type": reward_type,
                "value": reward_value
            }

            await interaction.response.send_message(f"✅ Récompense ajoutée pour le niveau {level_num}!", ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Niveau invalide!", ephemeral=True)

class LeaderboardConfigModal(discord.ui.Modal):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="📊 Configuration Leaderboard")
        self.config = config

    leaderboard_size = discord.ui.TextInput(
        label="Taille du classement",
        placeholder="10",
        required=False,
        max_length=3
    )

    reset_frequency = discord.ui.TextInput(
        label="Reset (never/weekly/monthly)",
        placeholder="never",
        required=False,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.leaderboard_size.value:
            try:
                size = int(self.leaderboard_size.value)
                if 1 <= size <= 100:
                    self.config["leaderboard_size"] = size
            except ValueError:
                pass

        if self.reset_frequency.value:
            freq = self.reset_frequency.value.lower()
            if freq in ["never", "weekly", "monthly"]:
                self.config["reset_frequency"] = freq

        await interaction.response.send_message("✅ Configuration leaderboard mise à jour!", ephemeral=True)

class ExclusionsView(discord.ui.View):
    """Vue pour configurer les exclusions du système de niveaux"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(timeout=180)
        self.config = config

    @discord.ui.button(label="📝 Exclure Canal", style=discord.ButtonStyle.secondary)
    async def exclude_channel(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(ExcludeChannelModal(self.config))

    @discord.ui.button(label="👤 Exclure Rôle", style=discord.ButtonStyle.secondary)
    async def exclude_role(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(ExcludeRoleModal(self.config))

    @discord.ui.button(label="📋 Voir Exclusions", style=discord.ButtonStyle.primary)
    async def view_exclusions(self, interaction: discord.Interaction, button):
        excluded_channels = self.config.get("excluded_channels", [])
        excluded_roles = self.config.get("excluded_roles", [])
        
        embed = discord.Embed(title="🚫 Exclusions du Système de Niveaux", color=0xff6b6b)
        
        if excluded_channels:
            channels_text = "\n".join([f"<#{ch_id}>" for ch_id in excluded_channels])
            embed.add_field(name="📝 Canaux Exclus", value=channels_text, inline=False)
        
        if excluded_roles:
            roles_text = "\n".join([f"<@&{role_id}>" for role_id in excluded_roles])
            embed.add_field(name="👤 Rôles Exclus", value=roles_text, inline=False)
        
        if not excluded_channels and not excluded_roles:
            embed.description = "Aucune exclusion configurée"
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ExcludeChannelModal(discord.ui.Modal):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="📝 Exclure Canal")
        self.config = config

    channel_id = discord.ui.TextInput(
        label="ID du canal",
        placeholder="123456789012345678",
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            ch_id = int(self.channel_id.value)
            channel = interaction.guild.get_channel(ch_id)
            
            if not channel:
                await interaction.response.send_message("❌ Canal introuvable!", ephemeral=True)
                return

            if "excluded_channels" not in self.config:
                self.config["excluded_channels"] = []
            
            if ch_id not in self.config["excluded_channels"]:
                self.config["excluded_channels"].append(ch_id)
                await interaction.response.send_message(f"✅ Canal {channel.mention} exclu du système de niveaux!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Ce canal est déjà exclu!", ephemeral=True)
                
        except ValueError:
            await interaction.response.send_message("❌ ID de canal invalide!", ephemeral=True)

class ExcludeRoleModal(discord.ui.Modal):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(title="👤 Exclure Rôle")
        self.config = config

    role_id = discord.ui.TextInput(
        label="ID du rôle",
        placeholder="123456789012345678",
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            r_id = int(self.role_id.value)
            role = interaction.guild.get_role(r_id)
            
            if not role:
                await interaction.response.send_message("❌ Rôle introuvable!", ephemeral=True)
                return

            if "excluded_roles" not in self.config:
                self.config["excluded_roles"] = []
            
            if r_id not in self.config["excluded_roles"]:
                self.config["excluded_roles"].append(r_id)
                await interaction.response.send_message(f"✅ Rôle {role.mention} exclu du système de niveaux!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Ce rôle est déjà exclu!", ephemeral=True)
                
        except ValueError:
            await interaction.response.send_message("❌ ID de rôle invalide!", ephemeral=True)

class RemoveLevelRewardSelect(discord.ui.View):
    def __init__(self, config: Dict[str, Any], rewards: Dict[str, Any]):
        super().__init__(timeout=60)
        self.config = config
        
        options = []
        for level, reward_data in sorted(rewards.items(), key=lambda x: int(x[0])):
            reward_type = reward_data.get("type", "unknown")
            if reward_type == "role":
                label = f"Niveau {level} - Rôle"
            elif reward_type == "coins":
                label = f"Niveau {level} - {reward_data.get('value', 0):,} AC"
            else:
                label = f"Niveau {level} - {reward_type}"
            
            options.append(discord.SelectOption(
                label=label,
                value=level,
                description=f"Supprimer la récompense du niveau {level}"
            ))

        if options:
            self.add_item(RemoveLevelRewardSelectDropdown(self.config, options))

class RemoveLevelRewardSelectDropdown(discord.ui.Select):
    def __init__(self, config: Dict[str, Any], options: List[discord.SelectOption]):
        super().__init__(placeholder="Choisir la récompense à supprimer...", options=options[:25])  # Max 25 options
        self.config = config

    async def callback(self, interaction: discord.Interaction):
        level = self.values[0]
        if "level_rewards" in self.config and level in self.config["level_rewards"]:
            del self.config["level_rewards"][level]
            await interaction.response.send_message(f"🗑️ Récompense du niveau {level} supprimée!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Récompense introuvable!", ephemeral=True)

async def setup(bot):
    """Setup function pour le chargement du module"""
    pass
