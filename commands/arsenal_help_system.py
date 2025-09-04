# 🔥 Arsenal V4 - Help System
import discord
from discord.ext import commands
from discord import app_commands

class ArsenalHelpSystem(commands.Cog):
    """Système d'aide Arsenal"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="🔥 Aide complète Arsenal")
    async def help_command(self, interaction: discord.Interaction):
        """Commande d'aide principale"""
        embed = discord.Embed(
            title="🔥 Arsenal V4 - Aide Complète",
            description="Guide complet des commandes Arsenal",
            color=0xFF6B35
        )
        
        embed.add_field(
            name="📋 Commandes de Base",
            value="`/ping` - Test de connexion\n`/serverinfo` - Infos serveur\n`/userinfo` - Infos utilisateur",
            inline=False
        )
        
        embed.add_field(
            name="🔐 Système Arsenal",
            value="`/register` - S'enregistrer\n`/profile` - Voir son profil\n`/arsenal-config` - Configuration",
            inline=False
        )
        
        embed.add_field(
            name="💰 Économie",
            value="`/balance` - Voir solde\n`/daily` - Récompense quotidienne\n`/shop` - Boutique",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ArsenalHelpSystem(bot))
    print("📚 [Arsenal Help System] Module chargé avec succès!")
