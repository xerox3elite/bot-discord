"""
🛡️ Arsenal Command Protection System V1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Protection contre les conflits et doublons de commandes
Évite les "Command already registered" errors
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging

log = logging.getLogger(__name__)

class CommandProtectionSystem:
    """Système de protection des commandes"""
    
    def __init__(self):
        self.registered_commands = set()
        self.registered_groups = set()
        self.bot_instance = None
        
    def set_bot(self, bot):
        """Définir l'instance du bot"""
        self.bot_instance = bot
        
    def safe_add_command(self, command_tree, command, command_name=None):
        """Ajouter une commande de façon sécurisée"""
        if command_name is None:
            command_name = getattr(command, 'name', str(command))
            
        if command_name in self.registered_commands:
            log.warning(f"🔒 Commande {command_name} déjà enregistrée, ignorée")
            return False
            
        try:
            command_tree.add_command(command)
            self.registered_commands.add(command_name)
            log.info(f"✅ Commande {command_name} enregistrée avec succès")
            return True
        except Exception as e:
            log.error(f"❌ Erreur ajout commande {command_name}: {e}")
            return False
    
    def safe_remove_command(self, command_tree, command_name):
        """Supprimer une commande de façon sécurisée"""
        try:
            command_tree.remove_command(command_name)
            self.registered_commands.discard(command_name)
            log.info(f"🗑️ Commande {command_name} supprimée")
            return True
        except Exception as e:
            log.error(f"❌ Erreur suppression commande {command_name}: {e}")
            return False
    
    def safe_add_cog(self, bot, cog):
        """Ajouter un cog de façon sécurisée"""
        cog_name = cog.__class__.__name__
        
        # Vérifier si le cog existe déjà
        if cog_name in [existing_cog.__class__.__name__ for existing_cog in bot.cogs.values()]:
            log.warning(f"🔒 Cog {cog_name} déjà chargé, rechargement...")
            try:
                # Supprimer l'ancien cog
                bot.remove_cog(cog_name)
                log.info(f"🗑️ Ancien cog {cog_name} supprimé")
            except Exception as e:
                log.error(f"❌ Erreur suppression ancien cog {cog_name}: {e}")
        
        try:
            # Ajouter le nouveau cog
            bot.add_cog(cog)
            log.info(f"✅ Cog {cog_name} chargé avec succès")
            return True
        except Exception as e:
            log.error(f"❌ Erreur chargement cog {cog_name}: {e}")
            return False
    
    def clear_registry(self):
        """Vider le registre des commandes"""
        self.registered_commands.clear()
        self.registered_groups.clear()
        log.info("🧹 Registre des commandes vidé")
    
    def get_status(self):
        """Obtenir le statut du système de protection"""
        return {
            "registered_commands": len(self.registered_commands),
            "registered_groups": len(self.registered_groups),
            "commands_list": list(self.registered_commands),
            "groups_list": list(self.registered_groups)
        }

# Instance globale du système de protection
protection_system = CommandProtectionSystem()

class ProtectionCog(commands.Cog):
    """Cog pour gérer la protection des commandes"""
    
    def __init__(self, bot):
        self.bot = bot
        protection_system.set_bot(bot)
        log.info("🛡️ [OK] Command Protection System initialisé")
    
    @app_commands.command(name="protection-status", description="🛡️ Statut du système de protection")
    async def protection_status(self, interaction: discord.Interaction):
        """Afficher le statut du système de protection"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Permissions insuffisantes.", ephemeral=True)
            return
        
        status = protection_system.get_status()
        
        embed = discord.Embed(
            title="🛡️ Command Protection System",
            description="Statut du système de protection des commandes",
            color=0x00ff00
        )
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"**Commandes:** {status['registered_commands']}\n**Groupes:** {status['registered_groups']}",
            inline=True
        )
        
        if status['commands_list']:
            commands_text = ", ".join(status['commands_list'][:10])
            if len(status['commands_list']) > 10:
                commands_text += f"... (+{len(status['commands_list']) - 10} autres)"
            embed.add_field(name="🎯 Commandes protégées", value=commands_text, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="clear-protection", description="🧹 Vider le cache de protection")
    async def clear_protection(self, interaction: discord.Interaction):
        """Vider le cache de protection"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Permissions administrateur requises.", ephemeral=True)
            return
        
        protection_system.clear_registry()
        
        embed = discord.Embed(
            title="🧹 Cache Vidé",
            description="Le cache du système de protection a été vidé.",
            color=0x00ff00
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    """Setup function"""
    await bot.add_cog(ProtectionCog(bot))
    log.info("🛡️ [OK] Command Protection System chargé")

async def teardown(bot: commands.Bot):
    """Teardown function"""
    log.info("🔄 Command Protection System déchargé")
