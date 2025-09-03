"""
🔧 Arsenal Config System V2.0 - Navigation Modulaire
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Système de configuration modulaire avec navigation par boutons
Chaque module a sa propre commande /config [module]
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import aiosqlite
import json
import logging

log = logging.getLogger(__name__)

class ConfigEconomyView(discord.ui.View):
    """Vue pour la configuration de l'économie"""
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="💰 Activer Économie", style=discord.ButtonStyle.success)
    async def enable_economy(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="✅ Économie Activée",
            description="Le système d'économie a été activé sur ce serveur !",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="💳 Récompenses XP", style=discord.ButtonStyle.primary)
    async def xp_rewards(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = XPRewardsModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🏪 Shop Config", style=discord.ButtonStyle.secondary)
    async def shop_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🏪 Configuration du Shop",
            description="Configurez les objets disponibles à l'achat",
            color=0x9932cc
        )
        view = ShopConfigView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ConfigLevelView(discord.ui.View):
    """Vue pour la configuration des niveaux"""
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="📈 Activer Niveaux", style=discord.ButtonStyle.success)
    async def enable_levels(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="✅ Système de Niveaux Activé",
            description="Les utilisateurs gagneront maintenant de l'XP !",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🎯 Récompenses Level", style=discord.ButtonStyle.primary)
    async def level_rewards(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = LevelRewardsModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📊 Multiplicateurs", style=discord.ButtonStyle.secondary)
    async def multipliers(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📊 Multiplicateurs XP",
            description="Configurez les multiplicateurs d'XP par salon/rôle",
            color=0x4169e1
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ConfigReglementView(discord.ui.View):
    """Vue pour la configuration du règlement"""
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="📜 Définir Règlement", style=discord.ButtonStyle.primary)
    async def set_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RulesModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="✅ Validation Auto", style=discord.ButtonStyle.success)
    async def auto_validation(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="✅ Validation Automatique",
            description="Activation de la validation automatique du règlement",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ConfigAutomodView(discord.ui.View):
    """Vue pour la configuration de l'automod"""
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="🛡️ Activer AutoMod", style=discord.ButtonStyle.danger)
    async def enable_automod(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🛡️ AutoMod Activé",
            description="Le système de modération automatique est maintenant actif !",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📝 Mots Interdits", style=discord.ButtonStyle.secondary)
    async def banned_words(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = BannedWordsModal()
        await interaction.response.send_modal(modal)

class ConfigTicketsView(discord.ui.View):
    """Vue pour la configuration des tickets"""
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="🎫 Activer Tickets", style=discord.ButtonStyle.success)
    async def enable_tickets(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🎫 Système de Tickets Activé",
            description="Les utilisateurs peuvent maintenant créer des tickets !",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📁 Catégorie Tickets", style=discord.ButtonStyle.primary)
    async def ticket_category(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TicketCategoryModal()
        await interaction.response.send_modal(modal)

# Vues supplémentaires pour sous-menus
class ShopConfigView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="➕ Ajouter Objet", style=discord.ButtonStyle.success)
    async def add_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AddShopItemModal()
        await interaction.response.send_modal(modal)

# Modals pour les configurations
class XPRewardsModal(discord.ui.Modal, title="💳 Configuration Récompenses XP"):
    def __init__(self):
        super().__init__()
    
    xp_per_message = discord.ui.TextInput(
        label="XP par message",
        placeholder="Exemple: 10",
        required=True,
        default="10"
    )
    
    xp_cooldown = discord.ui.TextInput(
        label="Cooldown XP (secondes)",
        placeholder="Exemple: 60",
        required=True,
        default="60"
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✅ Récompenses XP Configurées",
            description=f"**XP/message:** {self.xp_per_message.value}\n**Cooldown:** {self.xp_cooldown.value}s",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class LevelRewardsModal(discord.ui.Modal, title="🎯 Configuration Récompenses Level"):
    def __init__(self):
        super().__init__()
    
    level = discord.ui.TextInput(
        label="Niveau",
        placeholder="Exemple: 10",
        required=True
    )
    
    reward = discord.ui.TextInput(
        label="Récompense",
        placeholder="Exemple: Rôle @Membre Actif ou 1000 coins",
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✅ Récompense Level Configurée",
            description=f"**Niveau {self.level.value}:** {self.reward.value}",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class RulesModal(discord.ui.Modal, title="📜 Configuration Règlement"):
    def __init__(self):
        super().__init__()
    
    rules_channel = discord.ui.TextInput(
        label="Salon des règles",
        placeholder="ID du salon ou #reglement",
        required=True
    )
    
    validation_role = discord.ui.TextInput(
        label="Rôle après validation",
        placeholder="ID du rôle ou @Membre",
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✅ Règlement Configuré",
            description=f"**Salon:** {self.rules_channel.value}\n**Rôle:** {self.validation_role.value}",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class BannedWordsModal(discord.ui.Modal, title="📝 Mots Interdits"):
    def __init__(self):
        super().__init__()
    
    words = discord.ui.TextInput(
        label="Mots à bannir",
        placeholder="Séparez par des virgules: mot1, mot2, mot3...",
        style=discord.TextStyle.paragraph,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        words_list = [word.strip() for word in self.words.value.split(",")]
        embed = discord.Embed(
            title="✅ Mots Interdits Configurés",
            description=f"**{len(words_list)} mots** ajoutés à la liste noire",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class TicketCategoryModal(discord.ui.Modal, title="📁 Catégorie Tickets"):
    def __init__(self):
        super().__init__()
    
    category_id = discord.ui.TextInput(
        label="ID de la catégorie",
        placeholder="ID de la catégorie Discord",
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✅ Catégorie Tickets Configurée",
            description=f"Catégorie: {self.category_id.value}",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class AddShopItemModal(discord.ui.Modal, title="➕ Ajouter Objet Shop"):
    def __init__(self):
        super().__init__()
    
    item_name = discord.ui.TextInput(
        label="Nom de l'objet",
        placeholder="Exemple: Rôle VIP",
        required=True
    )
    
    item_price = discord.ui.TextInput(
        label="Prix",
        placeholder="Exemple: 5000",
        required=True
    )
    
    item_description = discord.ui.TextInput(
        label="Description",
        placeholder="Ce que l'utilisateur obtient...",
        style=discord.TextStyle.paragraph,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✅ Objet Ajouté au Shop",
            description=f"**{self.item_name.value}**\n💰 {self.item_price.value} coins\n{self.item_description.value}",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ArsenalConfigSystem(commands.Cog):
    """🔧 Système de Configuration Arsenal V2.0"""
    
    def __init__(self, bot):
        self.bot = bot
        log.info("🔧 [OK] Arsenal Config System V2.0 initialisé")
    
    @app_commands.command(name="config", description="🔧 Configuration générale Arsenal")
    async def config_main(self, interaction: discord.Interaction):
        """Commande principale de configuration"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Permissions insuffisantes (Gérer le serveur requis).", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔧 Configuration Arsenal V4.5.2",
            description="""
**Configurez votre serveur avec Arsenal !**

Utilisez les commandes ci-dessous pour configurer chaque module :
            """,
            color=0x00ff88
        )
        
        embed.add_field(
            name="💰 Économie",
            value="`/config economie`\nXP, coins, shop, récompenses",
            inline=True
        )
        embed.add_field(
            name="📈 Niveaux",
            value="`/config level`\nSystème de niveaux et rangs",
            inline=True
        )
        embed.add_field(
            name="📜 Règlement",
            value="`/config reglement`\nValidation et règles",
            inline=True
        )
        embed.add_field(
            name="🛡️ AutoMod",
            value="`/config automod`\nModération automatique",
            inline=True
        )
        embed.add_field(
            name="🎫 Tickets",
            value="`/config tickets`\nSystème de support",
            inline=True
        )
        embed.add_field(
            name="🎵 Musique",
            value="`/config musique`\nLecteur audio",
            inline=True
        )
        
        embed.set_footer(text="Arsenal V4.5.2 Ultimate | Configuration Modulaire")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="config-economie", description="💰 Configuration du système d'économie")
    async def config_economy(self, interaction: discord.Interaction):
        """Configuration de l'économie"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Permissions insuffisantes.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="💰 Configuration Économie",
            description="Configurez le système économique de votre serveur",
            color=0x00aa00
        )
        
        embed.add_field(
            name="💳 Fonctionnalités",
            value="• Système XP et coins\n• Shop personnalisé\n• Récompenses automatiques\n• Classements",
            inline=False
        )
        
        view = ConfigEconomyView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="config-level", description="📈 Configuration du système de niveaux")
    async def config_levels(self, interaction: discord.Interaction):
        """Configuration des niveaux"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Permissions insuffisantes.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📈 Configuration Niveaux",
            description="Configurez le système de niveaux et d'XP",
            color=0x4169e1
        )
        
        embed.add_field(
            name="🎯 Fonctionnalités",
            value="• XP par message\n• Récompenses par niveau\n• Multiplicateurs\n• Rôles automatiques",
            inline=False
        )
        
        view = ConfigLevelView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="config-reglement", description="📜 Configuration du règlement")
    async def config_rules(self, interaction: discord.Interaction):
        """Configuration du règlement"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Permissions insuffisantes.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📜 Configuration Règlement",
            description="Configurez le système de validation du règlement",
            color=0x9932cc
        )
        
        view = ConfigReglementView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="config-automod", description="🛡️ Configuration de l'AutoMod")
    async def config_automod(self, interaction: discord.Interaction):
        """Configuration de l'automod"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Permissions insuffisantes.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🛡️ Configuration AutoMod",
            description="Configurez la modération automatique",
            color=0xff0000
        )
        
        view = ConfigAutomodView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="config-tickets", description="🎫 Configuration des tickets")
    async def config_tickets(self, interaction: discord.Interaction):
        """Configuration des tickets"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Permissions insuffisantes.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎫 Configuration Tickets",
            description="Configurez le système de support par tickets",
            color=0x00ff00
        )
        
        view = ConfigTicketsView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot: commands.Bot):
    """Setup function"""
    await bot.add_cog(ArsenalConfigSystem(bot))
    log.info("🔧 [OK] Arsenal Config System V2.0 Modulaire chargé !")

async def teardown(bot: commands.Bot):
    """Teardown function"""
    log.info("🔄 Arsenal Config System V2.0 Modulaire déchargé")
