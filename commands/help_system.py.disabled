"""
Arsenal Help System Complete V4.5.2
Système d'aide complet avec toutes les commandes
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class HelpSystem:
    """Système d'aide complet"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    def get_all_commands(self) -> Dict[str, List]:
        """Récupère toutes les commandes du bot"""
        categories = {
            "💰 Économie": [],
            "📈 Niveaux": [],
            "🛡️ Modération": [],
            "🎫 Tickets": [],
            "🔧 Configuration": [],
            "🎮 Jeux": [],
            "🎵 Musique": [],
            "📊 Informations": [],
            "🔄 Utilitaires": []
        }
        
        # Commandes slash
        for command in self.bot.tree.get_commands():
            if hasattr(command, 'description'):
                desc = command.description or "Aucune description"
                cmd_info = f"`/{command.name}` - {desc}"
                
                # Catégorisation
                if any(word in command.name.lower() for word in ['balance', 'daily', 'coins', 'money', 'eco']):
                    categories["💰 Économie"].append(cmd_info)
                elif any(word in command.name.lower() for word in ['level', 'xp', 'rank']):
                    categories["📈 Niveaux"].append(cmd_info)
                elif any(word in command.name.lower() for word in ['warn', 'ban', 'kick', 'timeout', 'sanction', 'casier']):
                    categories["🛡️ Modération"].append(cmd_info)
                elif any(word in command.name.lower() for word in ['ticket', 'support']):
                    categories["🎫 Tickets"].append(cmd_info)
                elif any(word in command.name.lower() for word in ['config', 'setup', 'setting']):
                    categories["🔧 Configuration"].append(cmd_info)
                elif any(word in command.name.lower() for word in ['game', 'play', 'hunt']):
                    categories["🎮 Jeux"].append(cmd_info)
                elif any(word in command.name.lower() for word in ['music', 'play', 'song']):
                    categories["🎵 Musique"].append(cmd_info)
                elif any(word in command.name.lower() for word in ['info', 'stats', 'ping', 'about']):
                    categories["📊 Informations"].append(cmd_info)
                else:
                    categories["🔄 Utilitaires"].append(cmd_info)
        
        # Commandes préfixe
        for command in self.bot.commands:
            if not command.hidden:
                desc = command.help or command.brief or "Aucune description"
                cmd_info = f"`!{command.name}` - {desc}"
                
                # Catégorisation similaire
                if any(word in command.name.lower() for word in ['balance', 'daily', 'coins', 'money', 'eco']):
                    categories["💰 Économie"].append(cmd_info)
                elif any(word in command.name.lower() for word in ['level', 'xp', 'rank']):
                    categories["📈 Niveaux"].append(cmd_info)
                elif any(word in command.name.lower() for word in ['warn', 'ban', 'kick', 'timeout', 'sanction', 'casier']):
                    categories["🛡️ Modération"].append(cmd_info)
                elif any(word in command.name.lower() for word in ['ticket', 'support']):
                    categories["🎫 Tickets"].append(cmd_info)
                elif any(word in command.name.lower() for word in ['config', 'setup', 'setting']):
                    categories["🔧 Configuration"].append(cmd_info)
                elif any(word in command.name.lower() for word in ['game', 'play', 'hunt']):
                    categories["🎮 Jeux"].append(cmd_info)
                elif any(word in command.name.lower() for word in ['music', 'play', 'song']):
                    categories["🎵 Musique"].append(cmd_info)
                elif any(word in command.name.lower() for word in ['info', 'stats', 'ping', 'about']):
                    categories["📊 Informations"].append(cmd_info)
                else:
                    categories["🔄 Utilitaires"].append(cmd_info)
        
        return categories

class HelpView(discord.ui.View):
    """Vue interactive pour l'aide"""
    
    def __init__(self, help_system: HelpSystem):
        super().__init__(timeout=300)
        self.help_system = help_system
        
    @discord.ui.select(
        placeholder="📚 Choisir une catégorie d'aide...",
        options=[
            discord.SelectOption(label="💰 Économie", value="economy", description="Commandes économiques"),
            discord.SelectOption(label="📈 Niveaux", value="levels", description="Système de niveaux"),
            discord.SelectOption(label="🛡️ Modération", value="moderation", description="Outils de modération"),
            discord.SelectOption(label="🎫 Tickets", value="tickets", description="Système de support"),
            discord.SelectOption(label="🔧 Configuration", value="config", description="Paramètres du serveur"),
            discord.SelectOption(label="🎮 Jeux", value="games", description="Jeux et divertissement"),
            discord.SelectOption(label="🎵 Musique", value="music", description="Commandes musicales"),
            discord.SelectOption(label="📊 Informations", value="info", description="Informations et statistiques"),
            discord.SelectOption(label="🔄 Utilitaires", value="utils", description="Outils utilitaires")
        ]
    )
    async def help_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        category = select.values[0]
        categories = self.help_system.get_all_commands()
        
        category_map = {
            "economy": "💰 Économie",
            "levels": "📈 Niveaux", 
            "moderation": "🛡️ Modération",
            "tickets": "🎫 Tickets",
            "config": "🔧 Configuration",
            "games": "🎮 Jeux",
            "music": "🎵 Musique",
            "info": "📊 Informations",
            "utils": "🔄 Utilitaires"
        }
        
        category_name = category_map.get(category, "🔄 Utilitaires")
        commands = categories.get(category_name, [])
        
        embed = discord.Embed(
            title=f"📚 Aide - {category_name}",
            color=0x3498DB
        )
        
        if commands:
            # Diviser en chunks de 10 commandes max par embed
            for i in range(0, len(commands), 10):
                chunk = commands[i:i+10]
                field_name = f"Commandes ({i+1}-{min(i+10, len(commands))})" if len(commands) > 10 else "Commandes"
                embed.add_field(
                    name=field_name,
                    value="\n".join(chunk),
                    inline=False
                )
            
            embed.set_footer(text=f"Total: {len(commands)} commandes dans cette catégorie")
        else:
            embed.description = "Aucune commande trouvée dans cette catégorie."
        
        await interaction.response.edit_message(embed=embed, view=self)

class HelpCog(commands.Cog):
    """Cog système d'aide"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.help_system = HelpSystem(bot)
    
    @app_commands.command(name="help", description="📚 Afficher l'aide du bot")
    async def help_command(self, interaction: discord.Interaction):
        """Commande d'aide principale"""
        categories = self.help_system.get_all_commands()
        total_commands = sum(len(cmds) for cmds in categories.values())
        
        embed = discord.Embed(
            title="📚 Arsenal Bot - Aide",
            description=f"**{total_commands} commandes** disponibles dans **{len(categories)} catégories**",
            color=0x3498DB
        )
        
        # Aperçu des catégories
        for category, commands in categories.items():
            if commands:  # Seulement si la catégorie a des commandes
                embed.add_field(
                    name=category,
                    value=f"{len(commands)} commandes",
                    inline=True
                )
        
        embed.add_field(
            name="🔗 Liens utiles",
            value="[Support](https://discord.gg/your-server) | [Documentation](https://your-docs.com)",
            inline=False
        )
        
        embed.set_footer(text="Sélectionnez une catégorie pour voir les commandes détaillées")
        
        view = HelpView(self.help_system)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="commands", description="📋 Liste complète des commandes")
    async def commands_list(self, interaction: discord.Interaction):
        """Liste toutes les commandes"""
        categories = self.help_system.get_all_commands()
        
        embed = discord.Embed(
            title="📋 Toutes les commandes",
            color=0x3498DB
        )
        
        for category, commands in categories.items():
            if commands:
                # Limiter à 5 commandes par catégorie pour l'aperçu
                display_commands = commands[:5]
                value = "\n".join(display_commands)
                if len(commands) > 5:
                    value += f"\n... et {len(commands) - 5} autres"
                
                embed.add_field(
                    name=f"{category} ({len(commands)})",
                    value=value,
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)
    
    @commands.command(name="helpme")
    async def help_prefix(self, ctx, *, command: str = None):
        """Commande help pour préfixe"""
        if command:
            # Aide pour une commande spécifique
            cmd = self.bot.get_command(command)
            if cmd:
                embed = discord.Embed(
                    title=f"📚 Aide - !{cmd.name}",
                    description=cmd.help or cmd.brief or "Aucune description disponible",
                    color=0x3498DB
                )
                
                if cmd.usage:
                    embed.add_field(name="Utilisation", value=f"`!{cmd.name} {cmd.usage}`", inline=False)
                if cmd.aliases:
                    embed.add_field(name="Alias", value=", ".join(f"`{alias}`" for alias in cmd.aliases), inline=False)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ Commande `{command}` introuvable.")
        else:
            # Aide générale - rediriger vers la commande slash
            embed = discord.Embed(
                title="📚 Aide Arsenal Bot",
                description="Utilisez `/help` pour une aide interactive complète !",
                color=0x3498DB
            )
            embed.add_field(
                name="Commandes rapides",
                value="`/help` - Aide complète\n`/commands` - Liste des commandes\n`/config` - Configuration",
                inline=False
            )
            await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    """Setup function"""
    await bot.add_cog(HelpCog(bot))
    logger.info("✅ Arsenal Help System Complete V4.5.2 chargé")

async def teardown(bot: commands.Bot):
    """Teardown function"""
    logger.info("🔄 Arsenal Help System Complete déchargé")
